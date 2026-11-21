# Ducbaynao — phản tư cá nhân

Tôi là Phạm Lý Ngọc Đức (`Ducbaynao`), Dev Lead Gather trong nhóm DoAnhBatDuocEm.

- **Tôi đã làm:** hoàn thiện Gather Phase 1 (oxy, chuyển vùng, ngạt/ngất LIFO) và nâng cấp Phase 2 `v1.1` tại [contract.py](../../chonoi/contract.py), [scenario.py](../../chonoi/scenario.py) và [gather.py](../../chonoi/sim/gather.py): 6 nguyên liệu, 8 đàn cá bơi `1.5 m/s`, đổi hướng bước 120, phản xạ mép, sinh thêm mỗi 360 tick, Cá Sấu Năm Chèo (`M1`/`M2`) tuần tra/rượt đuổi/hit LIFO/recoil 60 và [test_gather_v11.py](../../tests/test_gather_v11.py).
- **Tôi đã review & hỗ trợ:** rà soát PRD-0 với [contracts/README.md](../contracts/README.md) và giữ tương thích `_store_in_hold` cho TV3 khi thêm 6 nguyên liệu.
- **AI sai ở đâu và cách phát hiện:** ngoài lỗi payload ở Phase 1, sang Phase 2 khi thêm phản xạ độ sâu cá bơi, test cũ đặt `ca_loc` ở `d = 6` với `random_fish` mặc định bị phản xạ ra ngoài; chạy suite đã phát hiện và khóa `random_fish: false`.
- **Điều tôi học được:** đổi luật vật lý cần rà lại ngay các fixture test cũ nhưng giữ nguyên bộ kiểm RNG qua `Streams`.
