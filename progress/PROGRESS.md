# BÁO CÁO TIẾN ĐỘ — PROGRESS CHECK 2 (PC-2)

* **Mã nhóm:** Nhóm 62 (`Nhom_62`)
* **Track:** Track A — Dr May Day: Rule Engine Sprint
* **Repository:** `https://github.com/thaihop06/ktpmud-bkt-ruleengine-starter` (nhánh `develop`)
* **Ngày cập nhật:** 18/11/2026

---

## 1. Trạng thái các hạng mục bàn giao (PC-1 -> PC-2)

- [x] **Đặc tả yêu cầu, Tiêu chí nghiệm thu & ADR (M1 / CP1): Xong**
  * *Bằng chứng:*
    - `REQUIREMENTS.md`: Đồng bộ thứ tự ưu tiên `R-SOC > R01-PV > R02-PV > R03-PV` và nguyên tắc "Không hạ mức" theo Issue #15.
    - `docs/acceptance-criteria.md`: Đầy đủ 26 tiêu chí nghiệm thu (`AC01–AC26`) ánh xạ tới `A-01..A-11`.
    - `docs/adr/ADR-001-rule-based-engine.md`: Phân tích đánh đổi giữa an toàn PII (Whitelist Sanitization) và rủi ro hạ mức lâm sàng.
- [x] **Hiện thực hóa Rule Engine & Audit Trail (M2): Xong**
  * *Bằng chứng:* File `rule_engine/classifier.py` hiện thực đầy đủ phân loại 2 tầng, tính giảm > 30% HATT bằng số nguyên (`10 * HATT < 7 * NEN`), chống `OverflowError` với số nguyên cực lớn (`10**400`), lọc trắng 9 trường và ghi Audit Trail 4 trường `[Timestamp, User_UUID, Action_Type, Status]`.
- [x] **Bộ kiểm thử tự động TC01–TC64 & Hàm Oracle độc lập (CP2): Xong**
  * *Bằng chứng:* File `tests/test_classifier.py` bao phủ đầy đủ `TC01–TC60` (66 lượt thực thi parametrized, bao gồm kiểm thử giảm 30% HATT nền `TC42–TC45`, các nhánh `TC03/TC05/TC08/TC14`, hàm Oracle duyệt vét cạn 64 tổ hợp cờ bool `TC54`) đạt 100% PASSED qua `pytest -q` trên cả máy cục bộ và GitHub Actions CI.
- [x] **Benchmark độ trễ (Latency < 100 ms): Xong**
  * *Bằng chứng:* Script `benchmarks/run_benchmark.py` (đã cấu hình `sys.path` chạy độc lập) và báo cáo `TEST_REPORT.md` (100 lần warm-up + 1.000 lần đo, `p50 ~ 0.005 ms`, `p95 ~ 0.015 ms < 100 ms`).
- [x] **Rà soát bộ tài liệu bàn giao PC-2 (`SECURITY_PRIVACY_CHECKLIST.md`, `AI_USE.md`, `CONTRIBUTIONS.md`, `TEST_REPORT.md`): Xong**
  * *Bằng chứng:* Cả 4 tài liệu ở thư mục gốc và `docs/TEST_REPORT.md` đã được hai thành viên rà soát chéo, khớp 100% với mã nguồn thực tế.

---

## 2. Timeline dự kiến đến khi hoàn thành (18/11 – 21/11/2026)

| Mốc thời gian | Nội dung công việc | Đầu ra dự kiến |
| :--- | :--- | :--- |
| **11/11 (PC-1)** | Báo cáo tiến độ PC-1 tại lớp và xác nhận commit SHA trên Issue #17. | Đã hoàn thành PC-1. |
| **12/11 – 15/11 (CP2)** | Rà soát kiểm thử chéo toàn bộ tài liệu và bổ sung đầy đủ `TC01–TC60` + hàm Oracle trong `tests/test_classifier.py`. | Đã hoàn thành Checkpoint 2. |
| **16/11 – 18/11 (PC-2)** | Rà soát `SECURITY_PRIVACY_CHECKLIST.md`, `AI_USE.md`, `CONTRIBUTIONS.md`, `TEST_REPORT.md`; báo cáo PC-2 (18/11) trên Issue #18. | Hoàn thành PC-2. |
| **19/11 (23:59 — Freeze)** | Kiểm tra lần cuối clean checkout, đóng băng mã nguồn trên fork, gắn release tag `bkt-2026-nhom62-rc1`. | Tag & Commit SHA cuối cùng. |
| **20/11 (M4 — Submit)** | Mở Pull Request mới vào `fossbk-spec/ktpmud-project` theo đúng erratum #25 (chỉ thay đổi trong `submissions/may_day_sprint_nhom62/`). | Pull Request xanh CI. |
| **21/11 (Demo/Viva)** | Demo công khai (7 phút) và vấn đáp cá nhân (8 phút). | Slide & Kịch bản demo. |

---

## 3. Câu hỏi của nhóm gửi Giảng viên / TA tại buổi PC-2

1. Nhóm em đã hoàn thiện đầy đủ bộ kiểm thử `TC01–TC60` (kèm hàm Oracle và chống `OverflowError`) cùng bộ tài liệu rà soát PC-2, mong thầy/TA kiểm tra giúp nhóm ạ.