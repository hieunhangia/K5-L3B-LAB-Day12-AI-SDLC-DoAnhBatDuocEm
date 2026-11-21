# Kiểm chứng Phase 2 — phần Thành viên 4

| Tiêu chí | Bằng chứng | Kết quả |
|---|---|---|
| Khách đến theo lịch và ngồi đúng bàn | `test_arrival_tick_interval_and_full_tables`, `test_fixture_can_disable_arrivals`, `test_new_id_continues_after_highest_fixture_id` | Đạt. Bàn được ưu tiên theo ID; lượt đến khi đầy bàn bị bỏ qua. |
| Chỉ đặt món đủ nguyên liệu khả dụng | `test_reservation_blocks_other_tables_without_spending_stock`, `test_preloaded_order_reserves_its_recipe`, `test_multi_dish_choice_is_seeded_and_independent_of_menu_order` | Đạt. Kho vật lý giữ nguyên khi đặt món; khách không gọi được món phát `no_dish`, để bàn trống. |
| Khách hết kiên nhẫn nhường bàn và chỗ giữ | `test_new_customer_waits_full_patience_then_leaves`, `test_expiry_releases_reservation_before_same_tick_arrival`, `test_simultaneous_timeouts_are_sorted_and_eating_customer_stays` | Đạt. Fixture headless cho thấy C9 rời trước, C10 nhận cùng bàn và 1 cá lóc tại tick 120; uy tín từ 3,0 xuống 2,5. [JSONL](../proof/phase-2/member-4/same-tick.jsonl) |
| Kiểm tra fixture và tính tất định | `test_invalid_fixture_types_are_rejected_before_first_tick`, fixture JSONL chạy hai lần với cùng seed | Đạt. Hai lần chạy cho cùng SHA-256 `8ff3e363089b777f17d20d867de124b1768233e017726eeebcd9320d29c0d9e8`. |
| Hồi quy sau khi đồng bộ TV3 | Suite repo trên Windows với Python 3.13.9, smoke headless `gather` và `quan` | Đạt 63/63 test, gồm 8 test TV3 và 10 test TV4. Quán không có kho phát `no_dish` tại tick 120. |
| Bàn giao kho TV3 → TV4 | Headless thực hiện `catch`, trồi lên và cập bến, rồi chạy quán với `--inventory` | Đạt. `fish_caught` và `docked` xuất 1 cá lóc; khách C1 gọi `ca_loc_nuong_trui` và giữ 1 cá lóc tại tick 120. |
| Hồ sơ đội | `python tools/check_team.py` | Chưa đạt. `TEAM.md` còn chỗ trống ở TV5 và TV6. |

## Chạy lại bằng PowerShell

```powershell
python -m unittest tests.test_quan_customers -v
$proof = 'docs/proof/phase-2/member-4'
python -m chonoi.headless --mode quan --seed 1 --ticks 121 --snapshot-every 120 --scenario "$proof/same-tick.scenario.json" --out "$env:TEMP/chonoi-tv4-quan.jsonl"
Get-FileHash "$env:TEMP/chonoi-tv4-quan.jsonl" -Algorithm SHA256
```

Suite tổng trên Windows dùng `PYTHONPATH='tests;.'`, chế độ UTF-8 và launcher `python3.exe` tạm cho lệnh headless trong contract. Trên Bash dùng `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`.

Kết quả này áp dụng cho lát TV4. Việc xác nhận Phase 2 và gắn tag theo quy trình nhóm diễn ra sau khi tích hợp phần Phase 1 và đối chiếu các câu hỏi trong [nhật ký PO](../clarify.md).

## Kiểm chứng tích hợp của TV6

Mười test khách hàng qua khi ghép mã TV4 với TV5. Fixture toàn trình nhận khách ở tick 120 và thanh toán ở tick 1462. [Kết quả](../proof/phase-1/member-6/checks.txt), [JSONL](../proof/phase-1/member-6/quan_e2e_run.jsonl).
