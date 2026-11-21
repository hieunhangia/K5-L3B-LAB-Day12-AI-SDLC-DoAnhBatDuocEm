# Bằng chứng kiểm thử của TV6

Ca chẩn đoán ban đầu chạy trên `main` tại `47927f9` và mã phục vụ TV5 tại `0f31dcd`. Bằng chứng toàn trình và log mới nhất chạy lại trên `6103c8f`, sau khi PR TV4 và TV5 đã gộp vào `main`.

| Ca | Kết quả | Bằng chứng |
|---|---|---|
| Thu hoạch từ giỏ rỗng | Hái bông tick 1, bắt cá tick 30, kết thúc tick 31. File kho có 1 bông điên điển và 3 cá linh. | [Gather](gather_run.jsonl), [kho](inventory.json) |
| Nạp kho và chờ khách tự đến | Snapshot tick 0 đọc đủ kho. Đến tick 1463 chỉ có `quan_end`, tiền 0. Ca toàn trình chưa đạt. | [Quán trên nền main](quan_run.jsonl) |
| Phục vụ khách được dựng sẵn | Bắt đầu nấu tick 122, bếp chín 722, nhặt món 723, phục vụ 862, thanh toán 1462. Tiền 144 (120 + 24 boa), uy tín 3.2, điểm 444, kho rỗng. | [Quán với mã TV5](quan_tv5_run.jsonl) |
| Khách tự đến và thanh toán trên bản tích hợp | Khách đến tick 120, nhận món tick 862 và thanh toán tick 1462. Tiền 144, uy tín 3.2, điểm 444, kho rỗng. | [Quán tích hợp](quan_e2e_run.jsonl), [suite và smoke](checks.txt) |

Chạy lại với cùng đầu vào và seed 1 cho kết quả giống nhau từng byte. Hai lệnh smoke gather/quan 120 ticks đều thoát 0. `tools/check_team.py` xác nhận đủ sáu thành viên trong bản QA.

## Tái tạo từ thư mục gốc repo

```bash
python3 -m chonoi.headless --mode gather --seed 1 --ticks 31 --snapshot-every 120 --scenario docs/proof/phase-1/member-6/gather.scenario.json --inputs docs/proof/phase-1/member-6/gather.inputs.json --inventory-out qa-inventory.json --out qa-gather.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 1463 --snapshot-every 120 --scenario docs/proof/phase-1/member-6/quan.scenario.json --inputs docs/proof/phase-1/member-6/quan.inputs.json --inventory qa-inventory.json --out qa-quan.jsonl
```

Để tái tạo riêng ca TV5, dùng bản QA có `chonoi/sim/quan.py` từ `0f31dcd` và chạy lệnh quán với `quan_tv5.scenario.json`. Dùng cùng `quan.inputs.json` và file kho thu từ lượt sáng.

Với bản ghép TV4 và TV5, dùng nguyên hai lệnh trên để tái tạo ca tích hợp.
