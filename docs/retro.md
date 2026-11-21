# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt: Đồng bộ được cả Gather v1.1 (cá bơi/sinh, Cá Sấu M1/M2) lẫn Day/Shop/Pause v1.1 theo chuỗi tích hợp tuần tự; 85/85 unit + black-box tests xanh trước khi tag `phase-2`.
- Điều tệ: Một số test P1 cũ ngầm giả định số bàn = 1 và đàn cá đứng yên nên phát sinh va chạm nhẹ khi chuyển sang v1.1.
- 1 hành động cho Phase 3: **TV3 (`Besoi2004`) và TV5 (`letuandat131`)** viết bảng phân tích tác động schema kho cá thể `v1.2` + danh sách test chịu ảnh hưởng trong `docs/adr/0003-inventory-v12-freshness.md` và `docs/plan/phase-3.md` NGAY trước khi sửa code mô phỏng để `main` luôn xanh ở mọi PR.

## Phase 4 (cuối)
- Rà lại hành động Phase 2: **Đã hoàn thành 100%.** TV3 (`Besoi2004`) và TV5 (`letuandat131`) đã lập [ADR 0003](adr/0003-inventory-v12-freshness.md) và bảng tác động [docs/plan/phase-3.md](plan/phase-3.md) ngay đầu Phase 3 trước khi sửa `inventory.py`/`gather.py`, kèm adapter cho `quan.py`/`day.py` nên mọi lượt nối tiếp ở Phase 3–4 đều giữ toàn bộ test suite xanh (`73 -> 78 -> 85 -> 95 -> 99 -> 106` tests).
- Điều tốt / điều tệ:
  - **Tốt:** Chuyền đuốc tuần tự 6 người đúng 3 commit mỗi lượt, không đụng hàng hay ghi đè nhánh; tách số học nguyên `240 đv/điểm` giúp loại bỏ hoàn toàn sai số làm tròn ở ngưỡng `fresh=30`.
  - **Tệ:** Trên Windows, alias `python3` của Microsoft Store gây lỗi khi chạy test nếu không tạo launcher; ở Phase 4 lượt đầu có phản tư vượt 200 từ (`Ducbaynao.md` 217 từ, `letuandat131.md` 203 từ) trước khi QA kiểm tự động.
- Số liệu:
  - Số commit theo lượt chuẩn hóa Phase 1–4: `hnib1908` (3), `Ducbaynao` (3 + các commit Phase 1), `hieunhangia` (3 + các commit nền), `Besoi2004` (3 + các commit Phase 1), `letuandat131` (3 + các commit Phase 1), `Laurent2526` (3).
  - Cách đọc code chéo: Người nhận đuốc đọc contract & test của lượt trước trước khi bắt đầu; mỗi thành viên tự viết phản tư cá nhân `<= 200` từ và được kiểm chứng tự động bằng unit test trong `test_phase4_v13.py`.
  - Token: không có công cụ đo tự động ở máy cục bộ (đã ghi trung thực tại [docs/ai-usage-log.md](ai-usage-log.md)).
- Một lần AI sai và cách nhóm phát hiện: ở Phase 3, `chonoi/jsonl.py` mặc định làm tròn 3 chữ số thập phân cho mọi `float`, khiến `fresh` trong `gather_end.data.inventory` ra `99.992` khác với `99.991667` trong `inventory.json` khi chạy test tích hợp. Nhóm phát hiện qua failure trong `test_smoke_p1.py` và cấu hình giữ 6 chữ số riêng cho khóa `"fresh"`.
- Nếu làm lại, đổi gì: chốt luôn định dạng số thập phân / `contract` kiểm chứng tự động cho từng khóa JSONL và thêm test kiểm số từ phản tư ngay từ Phase 1.
