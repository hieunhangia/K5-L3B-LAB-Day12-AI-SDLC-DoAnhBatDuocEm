# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| TV2 — chuyển vùng và oxy | `GatherCore.test_dive_surface_use_end_position_and_emit_once`, `test_surface_boundary_refills_and_clamps_oxygen`, `test_oxygen_empty_only_on_positive_to_zero`, `test_oxygen_refill_reads_tuning` | [Chu trình oxy](../proof/phase-1/member-2/oxygen-cycle.jsonl), [log test](../proof/phase-1/member-2/commit-6-checks.txt) | Tôi xác nhận đạt trong phạm vi TV2: ngưỡng mặt nước tính cả dấu bằng; sự kiện chỉ phát khi chuyển trạng thái; oxy dựa trên vị trí cuối bước. |
| TV2 — ngạt và ngất | `GatherCore.test_choking_starts_on_tick_oxygen_reaches_zero`, `test_surface_resets_choking_before_damage`, `test_choke_interval_reads_tuning`, `test_faint_clears_hold_before_end_and_precedes_docking_and_time` | [Phiên ngất](../proof/phase-1/member-2/faint.jsonl) | Tôi xác nhận đạt: choke tại tick 60/120/180; tick 180 phát choke → faint → gather_end, giỏ rỗng. |
| TV2 — giỏ LIFO và snapshot | 4 test g?m `test_hold_*`, `test_snapshot_keeps_player_and_hold_values_after_next_step`, `test_scenario_accepts_full_hold_and_rejects_over_capacity` trong `GatherCore` | [Log 45 test](../proof/phase-1/member-2/commit-6-checks.txt) | Tôi xác nhận đạt với helper giỏ: giữ thứ tự nhặt, trả số món nhận thực tế, không vượt tuning, snapshot giữ dữ liệu player/hold sau bước tiếp theo. Hái/bắt cá chưa được tích hợp. |
| TV2 — kho khi ngất và hồi quy cập bến | `GatherCore.test_faint_writes_empty_inventory_through_runner`, fixture faint/dock và smoke tích hợp có sẵn | [Kho ngất](../proof/phase-1/member-2/faint.inventory.json), [kho cập bến](../proof/phase-1/member-2/dock.inventory.json) | Tôi xác nhận đạt: ngất xuất `items: {}`; cập bến giữ đúng 1 cá lóc và 2 bông súng. |
| TV2 — tất định và hồi quy | Chạy cùng fixture ngất hai lần, so byte; toàn suite + headless gather/quan 600 ticks | [Hash và sự kiện](../proof/phase-1/member-2/summary.json), [log](../proof/phase-1/member-2/commit-6-checks.txt) | Tôi xác nhận đạt: output ngất giống từng byte; 45/45 test qua; hai chế độ CLI thoát 0. |
| Hồ sơ đội | `python tools/check_team.py` | [Kết quả kiểm tra](../proof/phase-1/member-2/commit-6-checks.txt) | Tôi ghi nhận chưa đạt: GitHub handle của TV3–6 chưa điền. |
| Gather Items và toàn bộ Phase 1 | Cần kiểm thử hái/bắt cá sau lượt TV3 | [Bàn giao TV3](../proof/phase-1/member-2/README.md) | Tôi chưa xác nhận hoàn thành lát 2 hoặc toàn bộ Phase 1. |
| Lát 2 · Hái nút ready gần nhất ở mặt nước, tính đúng mép bán kính, hòa theo id | `tests/test_gather_items.py::Harvest` | [tests.txt](../proof/phase-1/gather-items/tests.txt) | đạt |
| Lát 2 · Giỏ thiếu chỗ → `hold_full`, nút giữ nguyên; dưới nước không hái | `Harvest.test_hold_full_keeps_node`, `test_no_harvest_under_water` | [tests.txt](../proof/phase-1/gather-items/tests.txt) | đạt |
| Lát 2 · Bắt cá dưới nước, hòa theo id, hồi chiêu `catch_cooldown_s`; mặt nước không bắt | `tests/test_gather_items.py::Catch` | [tests.txt](../proof/phase-1/gather-items/tests.txt) | đạt |
| Lát 2 · Thiếu chỗ khi bắt → `hold_full`, giữ đàn, không hồi chiêu, không thử đàn khác | `Catch.test_hold_full_no_cooldown_no_other_fish` | [tests.txt](../proof/phase-1/gather-items/tests.txt) | đạt |
| Lát 2 · Cập bến ghi kho đúng giỏ; chạm `--ticks` trước khi xong thì không ghi kho | `tests/test_gather_items.py::DockInventory` | [tests.txt](../proof/phase-1/gather-items/tests.txt) | đạt |
| Smoke hai tiến trình: quán tick 0 có `stock {"bong_sung":2,"ca_loc":1}` | Lệnh smoke mục G PRD-0 (seed 42) | [catch.json](../proof/phase-1/gather-items/catch.json), [quan.jsonl](../proof/phase-1/gather-items/quan.jsonl) | đạt (trên nhánh lát 2, chưa có luật quán) |

## Đánh giá ngắn
- Tôi đã kiểm chứng Gather Core và các đường hồi quy sẵn có; chưa kết luận về cơ chế hái/bắt cá hay nghiệp vụ quán còn TODO.
- Tôi bàn giao helper giỏ và bằng chứng tái chạy cho TV3. Nhóm cần điền đủ TEAM.md, tích hợp lát 2 rồi kiểm chứng lại trước khi gắn tag phase-1.

## Kiểm chứng lại của TV6

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| Hái bông và bắt cá từ giỏ rỗng, chuyển kho sang quán | Headless gather chạy đến hết giờ, rồi headless quan dùng `--inventory` | [Gather](../proof/phase-1/member-6/gather_run.jsonl), [kho](../proof/phase-1/member-6/inventory.json), [snapshot quán](../proof/phase-1/member-6/quan_run.jsonl) | Đạt. Quán nhận đúng 1 bông điên điển và 3 cá linh. |
| Kịch bản quán mâu thuẫn trả mã 2 | `QuanScenario` kiểm món, đơn, giữ chỗ suy ra và cả kho từ file | [Test](../../tests/test_e2e_pipeline.py), [kết quả](../proof/phase-1/member-6/checks.txt) | Đạt. |
| Chạy cùng seed và đầu vào | So sánh byte JSONL và file kho sau hai lần chạy | [Ca chạy và cách tái tạo](../proof/phase-1/member-6/README.md) | Đạt. |
| Luồng sáng đến tối, khách tự đến và trả tiền | `Pipeline.test_harvest_to_paid_order` qua hai tiến trình headless | [Quán tích hợp](../proof/phase-1/member-6/quan_e2e_run.jsonl), [Phase 4](phase-4.md) | Đạt trên bản ghép TV4/TV5 để kiểm thử. |
