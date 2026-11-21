# Changelog

## [1.0.0] — Phase 4 (`contract_version: "1.3"`, tags `phase-4`, `v1.0.0`)
### Release Notes
- **Phát hành chính thức `v1.0.0`** của trò chơi *Quán Ăn Chợ Nổi* (6 thành viên nhóm `DoAnhBatDuocEm`): chạy hoàn toàn trên Python 3.12+ thư viện chuẩn từ clone sạch trong `<= 3` lệnh.
- **Có gì mới:**
  - `chonoi/bench.py` (`bench_cmd`): benchmark offscreen `1280×720` cảnh lặn sáng mặc định (3s làm nóng + 30s đo), đạt `2665.49 avg FPS`, `1719.53 1% low FPS`, `2.42 ms load` ([bench.json](docs/proof/phase-4/bench.json)).
  - `chonoi/soak.py` (`soak_cmd`): bot tất định chơi lặp 10 ngày (`D1–D5`) liên tiếp trong một tiến trình (`10/10` ngày hoàn tất, `0 crashes`, `4.423s` tại [soak.json](docs/proof/phase-4/soak.json)).
  - **Mở rộng `leaderboard`** (`extensions: ["burn", "leaderboard"]`): lưu bền vững top-10 cục bộ cho lượt chuẩn đủ 5 Ngày, hỗ trợ `--leaderboard`, `--player-name` Unicode và `--export-leaderboard`, giữ nguyên thứ tự khi hòa điểm qua mọi lần mở lại.
  - **UI & Trợ năng:** Menu `Chơi`/`Thoát`, `Shop` tương tác, `Esc`/`P` tạm dừng, đủ 3 cảnh báo rõ (`⚠ Thủy quái!`, `🫧 Hết hơi!`, `😠 Khách sắp giận!`), chế độ **Tương phản cao (`C`)** và phụ đề hiệu ứng âm thanh (`M` tắt tiếng).
- **Giới hạn đã biết:** giao diện chơi trực tiếp phục vụ qua HTML5 Canvas trên trình duyệt mặc định thay vì cửa sổ native SDL/Pygame; trên Windows cần `python3` alias (hoặc chạy `python -m ...` nếu dùng trực tiếp tay).

## [Phase 3] — `v1.2` (tag `phase-3`)
### Breaking Changes
- **Schema file kho `v1.2` (`inventory.json`, `gather.hold`, `quan.stock`, `customers[].reserved`):**
  - Chuyển từ kho đếm số lượng (`{"items": {"ca_loc": 2}}`) sang **danh sách cá thể có độ tươi** (`{"items": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]}`).
  - `customers[].reserved` chuyển sang mảng `id` cá thể (`["I1"]`), giữ theo độ tươi cao nhất và hòa theo `id`.
  - File kho hoặc scenario dùng map đếm kiểu cũ bị từ chối với mã thoát `2`.
- **Cách cập nhật fixture cũ:** thay mảng chuỗi ở `gather.hold` thành `[{"id": "I1", "kind": "...", "fresh": 100}]` và `quan.stock` tương tự; đơn `reserved` dùng danh sách id cá thể chưa ươn (`fresh >= 30`).

### Added
- Độ tươi `240 đv/điểm` (`gather -2/tick`, `quan -1/tick`, ươn `< 30` -> `spoiled`), tái giữ chỗ 1 lần (`unfulfillable`), giá món theo độ tươi trung bình.
- **Mở rộng `burn`:** `quan.burn_s = 20` (`1200` tick), cháy ở `> 1200` phát `dish_burnt` và thử tái giữ chỗ ngay.

## [Phase 2] — `v1.1` (tag `phase-2`)
### Added
- Số liệu chuẩn `v1.1`: 6 nguyên liệu, 6 món, 2 bếp `B1–B2`, 4 bàn `T1–T4`, `day_plan` D1–D5, `shop` nâng cấp `oxygen`/`hp`.
- Cá bơi `1.5 m/s`, đổi hướng bước `120`, phản xạ mép, sinh thêm mỗi `360` tick (trần 12) và Cá Sấu Năm Chèo (`M1`/`M2`).
- Vòng lặp 5 ngày (`DaySim`), `ShopSim`, `pause`/`resumed` cả 3 chế độ.
- Chi tiết tích hợp Gather `v1.1` và bằng chứng TV2 tại `docs/proof/phase-2/member-2/`.

## [Phase 1] — `v1.0` (tag `phase-1`)
### Added
- Chế độ Lặn & Hái (`gather`) và Mở Quán (`quan`) chuẩn hóa đầy đủ PRD-0 E/F/G, cùng 6 thành viên hợp lệ trong `TEAM.md`.
