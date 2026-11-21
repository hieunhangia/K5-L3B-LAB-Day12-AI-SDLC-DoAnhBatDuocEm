# Laurent2526 — phản tư cá nhân

Tôi là Đỗ Thanh Mai (`Laurent2526`), QA Lead & Release trong nhóm DoAnhBatDuocEm.

- **Tôi đã làm:** nâng cấp `game.contract.json` sang `v1.3`, xây dựng module benchmark 1280×720 [bench.py](../../chonoi/bench.py), chạy soak 10 ngày tất định [soak.py](../../chonoi/soak.py), mở rộng bảng xếp hạng top-10 [leaderboard.py](../../chonoi/leaderboard.py), tích hợp 3 cảnh báo + chế độ **Tương phản cao** + phụ đề SFX trong [index.html](../../chonoi/web/index.html), bộ test [test_phase4_v13.py](../../tests/test_phase4_v13.py), proof `bench.json`/`soak.json`/`leaderboard.json` và tài liệu phát hành `v1.0.0`.
- **Tôi đã kiểm chứng & hỗ trợ:** đối chiếu retro Phase 2, rà soát độ dài phản tư 6/6 thành viên (chủ động nhắc rút gọn bản >200 từ), verify hồi quy toàn suite từ Phase 1 đến Phase 4.
- **AI sai ở đâu và cách phát hiện:** bot soak lúc đầu đọc `snap["time_left_ticks"]` gây `KeyError` do trường này nằm ở `runner._common` ngoài `DaySim.snapshot()`; chạy thực tế `chonoi.soak` đã bắt lỗi và sửa ngay.
- **Điều tôi học được:** chạy đo thực `bench`/`soak` trên bản tích hợp mới chứng minh được FPS thực và độ ổn định qua 10 ngày.
