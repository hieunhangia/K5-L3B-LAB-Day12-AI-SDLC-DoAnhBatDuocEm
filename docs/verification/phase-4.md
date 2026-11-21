# Kiểm chứng Phase 4

| Tiêu chí | Kết quả |
|---|---|
| Hái, bắt, xuất và nạp kho | Đạt từ giỏ rỗng. [Bằng chứng](../proof/phase-1/member-6/README.md) |
| Khách tự đến, phục vụ và trả tiền | Đạt trên bản ghép TV4/TV5 để kiểm thử. Khách thanh toán 144 gồm 24 tiền boa. Uy tín 3.2, điểm 444. [JSONL](../proof/phase-1/member-6/quan_e2e_run.jsonl) |
| Kiểm kịch bản sai | Bốn test qua, gồm kho file đủ hoặc thiếu, giữ chỗ mặc định và tổng giữ chỗ của hai bàn. [Test](../../tests/test_e2e_pipeline.py) |
| Hồ sơ nhóm và release | `check_team.py` xác nhận đủ sáu thành viên. Mã TV4 và TV5 đã vào `origin/main` tại `6103c8f`. Các thành viên xác nhận phản tư và Integrator đối chiếu mốc Git trước khi phát hành. [Kết quả test](../proof/phase-1/member-6/checks.txt) |

## Đối soát mốc Git

Các mốc dưới đây đã vượt suite và smoke headless cả hai mode. Bảng ghi nhận commit có thể dùng khi nhóm duyệt và gắn tag.

| Tag dự kiến | Commit hoặc nhánh | Kiểm thử |
|---|---|---|
| `phase-1` | `47927f9` | 53/53 test. |
| `phase-2` | `5d8b1d7` | 63/63 test. |
| `phase-3` | `6103c8f` | 68/68 test. |
| `phase-4`, `v1.0.0` | Commit release cuối trên nhánh QA | 73/73 test, smoke, kho tất định và đủ sáu thành viên. |

Mã TV4 và TV5 đã vào `origin/main` qua PR #3 và #4. Ba commit QA được đặt trên mốc này. Khi đối soát, `origin` chưa công bố tag. Nhóm duyệt phản tư cá nhân và Integrator gắn tag theo phân công trong TEAM.md.
