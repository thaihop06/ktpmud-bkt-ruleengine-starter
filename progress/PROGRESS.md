# PROGRESS — nhom62 — Track A

- Starter: ktpmud-bkt-ruleengine-starter · tag bkt-2026-v1.1
- Fork: https://github.com/thaihop06/ktpmud-bkt-ruleengine-starter

## PC-1 — 11/11/2026

### 1.1. Tiến độ theo acceptance criteria
<!-- Track A: A-01…A-11 · Track B: B-01…B-12 (đề thi Mục 7.3 / 8.3). Đủ mọi mã. -->
| Mã | Trạng thái (Chưa / Đang / Xong) | Bằng chứng (commit / CI / file) | Ghi chú |
|---|---|---|---|
| A-01 | Xong | `REQUIREMENTS.md`, `docs/acceptance-criteria.md`, `rule_engine/classifier.py` | Đặc tả và khởi tạo hàm `classify(ca_benh)` trả về 3 khóa `muc_do`, `rule_id`, `ly_do` |
| A-02 | Xong | `docs/decision-table.md`, `rule_engine/classifier.py` | Thiết kế và cài đặt quy tắc `R01-PV` (da/niêm mạc kèm hô hấp hoặc tuần hoàn) |
| A-03 | Xong | `docs/decision-table.md`, `rule_engine/classifier.py` | Thiết kế và cài đặt quy tắc `R02-PV` (dị nguyên nghi ngờ kèm $\ge 2/4$ cơ quan) |
| A-04 | Xong | `docs/decision-table.md`, `rule_engine/classifier.py` | Thiết kế và cài đặt quy tắc `R03-PV` (dị nguyên không qua đường hít + hô hấp, hoặc tuần hoàn) |
| A-05 | Xong | `docs/decision-table.md`, `rule_engine/classifier.py` | Quy tắc Tầng 1 `R-SOC` theo ngưỡng HATT theo tuổi và giảm > 30% HATT nền |
| A-06 | Xong | `REQUIREMENTS.md`, `docs/decision-table.md` | Thứ tự ưu tiên đơn trị `R-SOC > R01-PV > R02-PV > R03-PV` |
| A-07 | Đang | `docs/adr/ADR-001-rule-based-engine.md`, `rule_engine/classifier.py` | Kiểm tra biên tuổi `0..120`, HATT `1..300` và nguyên tắc Không hạ mức (No-Downgrade) |
| A-08 | Đang | `docs/adr/ADR-001-rule-based-engine.md`, `rule_engine/classifier.py` | Lọc trắng 9 trường đầu vào (Zero-PII), không đưa chỉ số thô/liều thuốc vào `ly_do` |
| A-09 | Đang | `rule_engine/classifier.py` | Khung ghi nhận Audit Trail 4 trường `[Timestamp, User_UUID, Action_Type, Status]` |
| A-10 | Đang | `tests/test_classifier.py`, `docs/TEST_REPORT.md` | Khởi tạo bộ kiểm thử tự động và kế hoạch kiểm thử hàm Oracle |
| A-11 | Đang | `.github/workflows/test.yml`, `README.md` | Cấu hình GitHub Actions CI và bổ sung tuyên bố giới hạn sử dụng |

### 1.2. Sửa đổi bắt buộc từ Checkpoint 1
<!-- Các mục ❗ trong nhận xét Checkpoint 1 của nhóm. Nếu không có, ghi "Không có". -->
| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| Đồng bộ thứ tự ưu tiên `R-SOC > R01-PV > R02-PV > R03-PV` và nguyên tắc "Không hạ mức" theo Issue #15 | Xong | `REQUIREMENTS.md`, `docs/decision-table.md`, `docs/adr/ADR-001-rule-based-engine.md` |

### 1.3. Timeline dự kiến đến khi hoàn thành
| Việc | Vai trò phụ trách | Mốc (CP2 15/11 · M3 · Freeze 19/11 · M4 20/11) | Ngày dự kiến |
|---|---|---|---|
| Hoàn thiện `TC01–TC60` và hàm Oracle duyệt 64 tổ hợp boolean trong `tests/test_classifier.py` | `huyvanle04112006` (Dev / Test) | CP2 15/11 | 15/11/2026 |
| Đo kiểm hiệu năng `benchmarks/run_benchmark.py` (`p95 < 100 ms`) và cập nhật `TEST_REPORT.md` | `thaihop06` (QA / Spec) & `huyvanle04112006` | M3 | 17/11/2026 |
| Rà soát `SECURITY_PRIVACY_CHECKLIST.md`, `AI_USE.md`, `CONTRIBUTIONS.md` và mở Draft PR #23 | `thaihop06` & `huyvanle04112006` | M3 | 18/11/2026 |
| Kiểm tra clean checkout, đóng băng mã nguồn và gắn tag `bkt-2026-nhom62-rc1` | `thaihop06` & `huyvanle04112006` | Freeze 19/11 | 19/11/2026 |
| Cập nhật SHA cuối cùng và chuyển Draft PR #23 sang `Ready for review` | `thaihop06` | M4 20/11 | 20/11/2026 |

### 1.4. Rủi ro / đang vướng
- Rủi ro sai số dấu phẩy động khi tính ngưỡng giảm 30% HATT nền và lỗi `OverflowError` khi kiểm thử biên với số nguyên cực lớn (`10**400`) -> Đã giải quyết bằng phép nhân nguyên `10 * HATT < 7 * NEN` và kiểm tra chặn biên trước khi ép kiểu.

### 1.5. Câu hỏi cho GV
- Q1: Nhóm sử dụng phép toán số nguyên `10 * huyet_ap_tam_thu < 7 * huyet_ap_tam_thu_nen` để kiểm tra giảm > 30% HATT nền nhằm tránh sai số số thực `float`, cách tiếp cận này đã hoàn toàn khớp với bộ chấm tự động chưa ạ?

### 1.6. Phân công (alias hoặc vai trò, KHÔNG ghi họ tên/MSSV)
| Alias / vai trò | Đầu việc chính | Commit/PR tiêu biểu |
|---|---|---|
| `thaihop06` (Spec / Architect / QA) | Đặc tả `REQUIREMENTS.md`, 26 tiêu chí nghiệm thu `docs/acceptance-criteria.md`, bảng quyết định `docs/decision-table.md`, viết `docs/adr/ADR-001-rule-based-engine.md`, lập `TEST_REPORT.md` và quản lý PR #23 trên `ktpmud-project` | `docs/acceptance-criteria.md`, `docs/adr/ADR-001-rule-based-engine.md`, PR `fossbk-spec/ktpmud-project#23` |
| `huyvanle04112006` (Core Dev / Test / CI) | Hiện thực `rule_engine/classifier.py` (phân loại 2 tầng, Whitelist Zero-PII, Audit Trail 4 trường), viết 66 lượt kiểm thử + hàm Oracle trong `tests/test_classifier.py`, script `benchmarks/run_benchmark.py`, cấu hình CI `.github/workflows/test.yml` và giao diện demo `dr_may_day_demo.html` | `rule_engine/classifier.py`, `tests/test_classifier.py`, `benchmarks/run_benchmark.py` |

## PC-2 — 18/11/2026

### 2.1. Đối chiếu timeline PC-1
| Việc (theo bảng 1.3) | Kế hoạch | Thực tế | Lệch & lý do |
|---|---|---|---|
| Hoàn thiện `TC01–TC60` và hàm Oracle duyệt 64 tổ hợp boolean trong `tests/test_classifier.py` | 15/11/2026 | 15/11/2026 | Đúng hạn (đạt 66/66 lượt test PASSED trên local và GitHub Actions CI) |
| Đo kiểm hiệu năng `benchmarks/run_benchmark.py` (`p95 < 100 ms`) và cập nhật `TEST_REPORT.md` | 17/11/2026 | 17/11/2026 | Đúng hạn (`p50 ~ 0.005 ms`, `p95 ~ 0.015 ms < 100 ms`) |
| Rà soát `SECURITY_PRIVACY_CHECKLIST.md`, `AI_USE.md`, `CONTRIBUTIONS.md` và mở Draft PR #23 | 18/11/2026 | 18/11/2026 | Đúng hạn (đã hoàn tất bộ tài liệu PC-2, chuyển PR #23 sang Draft và cập nhật `ci_run_url`) |
| Kiểm tra clean checkout, đóng băng mã nguồn và gắn tag `bkt-2026-nhom62-rc1` | 19/11/2026 | Chưa (theo lịch ngày 19/11) | Đúng lộ trình |
| Cập nhật SHA cuối cùng và chuyển Draft PR #23 sang `Ready for review` | 20/11/2026 | Chưa (theo lịch ngày 20/11) | Đúng lộ trình |

### 2.2. Tiến độ theo acceptance criteria (cập nhật toàn bộ bảng 1.1)
| Mã | Trạng thái | Bằng chứng | Ghi chú |
|---|---|---|---|
| A-01 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC01`, `TC46`) | Hàm `classify` trả về đủ 3 khóa `muc_do`, `rule_id`, `ly_do` với 3 mức `SOC_PHAN_VE`, `PHAN_VE`, `THEO_DOI` |
| A-02 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC15–TC18`) | Quy tắc `R01-PV`: khởi phát cấp tính da/niêm mạc kèm hô hấp hoặc tuần hoàn |
| A-03 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC19–TC21`) | Quy tắc `R02-PV`: tiếp xúc dị nguyên nghi ngờ kèm $\ge 2/4$ cơ quan |
| A-04 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC22–TC25`) | Quy tắc `R03-PV`: dị nguyên không qua đường hít + hô hấp, hoặc dị nguyên + tuần hoàn |
| A-05 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC27–TC45`) | Quy tắc Tầng 1 `R-SOC`: thỏa phản vệ kèm tụt HATT theo tuổi hoặc giảm > 30% HATT nền |
| A-06 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC33–TC36`) | Đảm bảo thứ tự ưu tiên cứng `R-SOC > R01-PV > R02-PV > R03-PV` |
| A-07 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC02–TC14`), `docs/adr/ADR-001-rule-based-engine.md` | Kiểm tra biên tuổi `0..120`, HATT `1..300`, chặn `bool`/`NaN`/`Inf`/`OverflowError`, giữ nguyên tắc Không hạ mức |
| A-08 | Xong | `rule_engine/classifier.py`, `SECURITY_PRIVACY_CHECKLIST.md`, `tests/test_classifier.py` (`TC11`, `TC49–TC52`) | Lọc trắng 9 trường đầu vào Zero-PII; `ly_do` không chứa số đo sinh hiệu thô hay khuyến nghị điều trị/liều thuốc |
| A-09 | Xong | `rule_engine/classifier.py`, `tests/test_classifier.py` (`TC56–TC59`) | Audit Trail lưu đúng 4 trường `[Timestamp, User_UUID, Action_Type, Status]`, không chứa PII |
| A-10 | Xong | `tests/test_classifier.py` (`TC53`, `TC54`, `TC55`) | Tất định qua 100 lần chạy, bất biến đầu vào và khớp 100% với hàm Oracle trên 64 tổ hợp cờ boolean |
| A-11 | Xong | `benchmarks/run_benchmark.py` (`TC60`), `README.md`, `.github/workflows/test.yml` | Độ trễ `p95 ~ 0.015 ms < 100 ms`, có cảnh báo `educational/synthetic — not for clinical use`, CI xanh |

### 2.3. Sẵn sàng nộp bài (đề thi Mục 6)
| Deliverable | Có / Chưa | Đường dẫn |
|---|---|---|
| README.md (cài đặt / chạy / test) | Có | `README.md` |
| REQUIREMENTS.md | Có | `REQUIREMENTS.md` |
| DECISIONS.md / ADR | Có | `docs/adr/ADR-001-rule-based-engine.md`, `docs/decision-table.md` |
| Test tự động + CI xanh | Có | `tests/test_classifier.py`, `.github/workflows/test.yml` |
| TEST_REPORT.md | Có | `TEST_REPORT.md`, `docs/TEST_REPORT.md` |
| SECURITY_PRIVACY_CHECKLIST.md | Có | `SECURITY_PRIVACY_CHECKLIST.md` |
| AI_USE.md | Có | `AI_USE.md` |
| CONTRIBUTIONS.md | Có | `CONTRIBUTIONS.md` |
| Slide / demo script ≤ 7 phút | Có | `demo.py`, `dr_may_day_demo.html` |
| Draft PR vào `ktpmud-project`, check `validate` xanh | Có | `https://github.com/fossbk-spec/ktpmud-project/pull/23` |

### 2.4. Việc còn lại đến Freeze (23:59 19/11)
| Việc | Vai trò phụ trách | Hạn |
|---|---|---|
| Kiểm tra clean checkout, chạy lại toàn bộ `pytest` và `benchmarks/run_benchmark.py` | `huyvanle04112006` | 22:00 19/11/2026 |
| Đóng băng mã nguồn trên nhánh `develop` và gắn tag `bkt-2026-nhom62-rc1` | `thaihop06` | 23:59 19/11/2026 |
| Cập nhật mã SHA/tag cuối cùng vào PR #23 và chuyển sang `Ready for review` | `thaihop06` | 20/11/2026 |

### 2.5. Rủi ro / câu hỏi cho GV
- Nhóm đã bổ sung đầy đủ bảng đối chiếu `A-01`–`A-11`, bảng phân công theo alias, chuyển PR #23 sang chế độ Draft và cập nhật `ci_run_url` thực tế theo đúng hướng dẫn rà soát tự động.

## Kết quả cuối — Freeze 19/11/2026
- Tag: bkt-2026-nhom62-rc1 · SHA:1b19251647d75c0d6d616ea75965bd18af69d48e
- Trạng thái cuối từng mã AC: như 2.2 (hoàn thành 11/11 mã từ A-01 đến A-11)
- Những việc trong timeline chưa hoàn thành và lý do: Không có