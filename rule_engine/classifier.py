"""
Rule Engine phân loại nguy cơ phản vệ theo bảng quyết định WAO/EAACI V1.
Tuân thủ đặc tả tại docs/decision-table.md, REQUIREMENTS.md và Issue #15:
- Thứ tự ưu tiên: R-SOC > R01-PV > R02-PV > R03-PV
- Nguyên tắc "Không hạ mức" (No-Downgrade) và Zero PII.
"""
from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import uuid

DEFAULT_OPERATOR_UUID = "00000000-0000-4000-8000-000000000062"

KNOWN_FIELDS = {
    "tuoi",
    "huyet_ap_tam_thu",
    "huyet_ap_tam_thu_nen",
    "co_di_nguyen_nghi_ngo",
    "di_nguyen_qua_duong_hit",
    "co_ton_thuong_da_niem_mac",
    "co_trieu_chung_ho_hap",
    "co_trieu_chung_tuan_hoan",
    "co_trieu_chung_tieu_hoa_nang",
}

BOOL_FIELDS = (
    "co_di_nguyen_nghi_ngo",
    "di_nguyen_qua_duong_hit",
    "co_ton_thuong_da_niem_mac",
    "co_trieu_chung_ho_hap",
    "co_trieu_chung_tuan_hoan",
    "co_trieu_chung_tieu_hoa_nang",
)

REASON_MESSAGES = {
    "R-SOC": "Thỏa tiêu chí phản vệ kèm tụt huyết áp theo ngưỡng tuổi hoặc huyết áp nền (R-SOC).",
    "R01-PV": "Khởi phát cấp tính ở da/niêm mạc kèm triệu chứng hô hấp hoặc tuần hoàn (R01-PV).",
    "R02-PV": "Tiếp xúc dị nguyên nghi ngờ kèm tổn thương từ hai hệ cơ quan trở lên (R02-PV).",
    "R03-PV": "Tiếp xúc dị nguyên nghi ngờ kèm triệu chứng hô hấp (không qua đường hít) hoặc tuần hoàn (R03-PV).",
    "THEO_DOI": "Chưa đủ tiêu chí chẩn đoán phản vệ theo bảng quyết định hiện hành.",
    "INVALID_INPUT": "Dữ liệu đầu vào thiếu trường bắt buộc hoặc sai kiểu/miền giá trị quy định.",
}

_AUDIT_LOGS: List[Dict[str, str]] = []


def _record_audit(user_uuid: Optional[str], status: str) -> None:
    valid_uuid = DEFAULT_OPERATOR_UUID
    if isinstance(user_uuid, str):
        try:
            uuid.UUID(user_uuid)
            valid_uuid = user_uuid
        except ValueError:
            valid_uuid = DEFAULT_OPERATOR_UUID

    _AUDIT_LOGS.append(
        {
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "User_UUID": valid_uuid,
            "Action_Type": "CLASSIFY_ANAPHYLAXIS",
            "Status": status,
        }
    )


def get_audit_logs() -> List[Dict[str, str]]:
    """Trả về bản sao danh sách bản ghi kiểm toán."""
    return list(_AUDIT_LOGS)


def clear_audit_logs() -> None:
    """Xóa danh sách bản ghi kiểm toán (phục vụ kiểm thử và benchmark)."""
    _AUDIT_LOGS.clear()


def _is_valid_age(tuoi: Any) -> bool:
    if tuoi is None or isinstance(tuoi, bool) or not isinstance(tuoi, (int, float)):
        return False
    if isinstance(tuoi, float) and (math.isnan(tuoi) or math.isinf(tuoi)):
        return False
    return 0 <= tuoi <= 120


def _parse_bp(val: Any) -> tuple[Optional[int], bool]:
    """
    Kiểm tra trường huyết áp (nullable, int trong miền 1..300).
    Trả về (giá_trị_hợp_lệ_hoặc_None, cờ_lỗi).
    """
    if val is None:
        return None, False
    if isinstance(val, bool) or not isinstance(val, int):
        return None, True
    if not (1 <= val <= 300):
        return None, True
    return val, False


def _is_hypotension(tuoi: float | int, hatt: Optional[int], nen: Optional[int]) -> bool:
    if hatt is None:
        return False
    if tuoi < 1:
        return hatt < 70
    if tuoi < 11:
        return hatt < (70 + 2 * tuoi)
    if tuoi < 18:
        return hatt < 90
    if hatt < 90:
        return True
    if nen is not None and (10 * hatt < 7 * nen):
        return True
    return False


def classify(data: Dict[str, Any], user_uuid: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Phân loại mức độ phản vệ theo bảng quyết định WAO/EAACI V1.
    """
    if not isinstance(data, dict):
        _record_audit(user_uuid, "INVALID_INPUT")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": REASON_MESSAGES["INVALID_INPUT"],
        }

    # 1. Whitelist Sanitization: chỉ lấy 9 trường chuẩn, bỏ qua mọi trường lạ (Zero PII)
    clean: Dict[str, Any] = {k: data[k] for k in KNOWN_FIELDS if k in data}

    # 2. Kiểm tra tuổi bắt buộc
    if "tuoi" not in clean or not _is_valid_age(clean["tuoi"]):
        _record_audit(user_uuid, "INVALID_INPUT")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": REASON_MESSAGES["INVALID_INPUT"],
        }
    tuoi = clean["tuoi"]

    # 3. Kiểm tra 6 cờ bool: nếu sai kiểu ("true", 1, 0) -> từ chối ngay; nếu thiếu/None -> ghi nhận
    has_missing_bool = False
    for bf in BOOL_FIELDS:
        if bf not in clean or clean[bf] is None:
            has_missing_bool = True
        elif not isinstance(clean[bf], bool):
            _record_audit(user_uuid, "INVALID_INPUT")
            return {
                "muc_do": "THEO_DOI",
                "rule_id": None,
                "ly_do": REASON_MESSAGES["INVALID_INPUT"],
            }

    # 4. Kiểm tra huyết áp tâm thu và huyết áp nền
    hatt, hatt_invalid = _parse_bp(clean.get("huyet_ap_tam_thu", None))
    nen, nen_invalid = _parse_bp(clean.get("huyet_ap_tam_thu_nen", None))

    # 5. Đánh giá các quy tắc Tầng 2 theo thứ tự ưu tiên: R01-PV > R02-PV > R03-PV
    nn = clean.get("co_di_nguyen_nghi_ngo")
    hit = clean.get("di_nguyen_qua_duong_hit")
    da = clean.get("co_ton_thuong_da_niem_mac")
    hh = clean.get("co_trieu_chung_ho_hap")
    th = clean.get("co_trieu_chung_tuan_hoan")
    td = clean.get("co_trieu_chung_tieu_hoa_nang")

    r01 = (nn is False) and (da is True) and ((hh is True) or (th is True))
    organ_count = sum(1 for flag in (da, hh, th, td) if flag is True)
    r02 = (nn is True) and (organ_count >= 2)
    r03 = (nn is True) and (((hit is False) and (hh is True)) or (th is True))

    tier2_rule: Optional[str] = None
    if r01:
        tier2_rule = "R01-PV"
    elif r02:
        tier2_rule = "R02-PV"
    elif r03:
        tier2_rule = "R03-PV"

    # 6. Nếu đã thỏa Tầng 2 -> Không hạ mức (No-Downgrade), kiểm tra tiếp Tầng 1 (R-SOC)
    if tier2_rule is not None:
        if _is_hypotension(tuoi, hatt, nen):
            _record_audit(user_uuid, "CLASSIFIED_SOC_PHAN_VE")
            return {
                "muc_do": "SOC_PHAN_VE",
                "rule_id": "R-SOC",
                "ly_do": REASON_MESSAGES["R-SOC"],
            }
        _record_audit(user_uuid, "CLASSIFIED_PHAN_VE")
        return {
            "muc_do": "PHAN_VE",
            "rule_id": tier2_rule,
            "ly_do": REASON_MESSAGES[tier2_rule],
        }

    # 7. Nếu không thỏa Tầng 2 nào và có lỗi thiếu trường bool hoặc HATT/NEN sai miền/kiểu
    if has_missing_bool or hatt_invalid or nen_invalid:
        _record_audit(user_uuid, "INVALID_INPUT")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": REASON_MESSAGES["INVALID_INPUT"],
        }

    # 8. Đầu vào hợp lệ hoàn toàn nhưng chưa đủ tiêu chí phản vệ
    _record_audit(user_uuid, "CLASSIFIED_THEO_DOI")
    return {
        "muc_do": "THEO_DOI",
        "rule_id": None,
        "ly_do": REASON_MESSAGES["THEO_DOI"],
    }