# Besoi2004 — phản tư cá nhân

Tôi là Nguyễn Huy Tấn (`Besoi2004`), phụ trách Dev Gather Items trong nhóm DoAnhBatDuocEm.

- **Tôi đã làm:** hoàn thành Lát 2 Phase 1 (`test_gather_items.py`) và chuyển đổi Phase 3 (`v1.2`) sang kho cá thể: viết [ADR 0003](../adr/0003-inventory-v12-freshness.md), nâng cấp [inventory.py](../../chonoi/inventory.py) dùng số nguyên `240 đv/điểm`, cập nhật [scenario.py](../../chonoi/scenario.py), triển khai hao độ tươi `-2/tick` & `spoiled` ở [gather.py](../../chonoi/sim/gather.py), cùng [test_freshness_gather_v12.py](../../tests/test_freshness_gather_v12.py).
- **Tôi đã review & hỗ trợ:** rà Retro Phase 2, làm adapter cho `quan.py`/`day.py` và thêm commit `16a2e5a` khôi phục đủ luật PR #7/#8 (95/95 test OK) trước khi TV5 làm `burn`.
- **AI sai ở đâu và cách phát hiện:** AI suýt dùng số thực kiểm ngưỡng `< 30` (dễ làm tròn `29.999` thành `30`); kiểm chứng cả `24.001` mức nguyên đã chặn sai lệch biên.
- **Điều tôi học được:** viết ADR và đối chiếu đủ luật các PR trước khi đổi schema giúp giữ `main` luôn xanh.
