# Kiểm chứng Phase 3

| Tiêu chí | Cách kiểm chứng | Kết quả |
|---|---|---|
| Nấu, nhặt món, phục vụ, thanh toán, hết ca | Nạp kho thực từ Gather và dựng một khách chờ trong fixture. Chạy mã TV5 tại `0f31dcd`. | Đạt ca kiểm thử riêng. Tiền 144, boa 24, uy tín 3.2, điểm 444. [JSONL](../proof/phase-1/member-6/quan_tv5_run.jsonl) |
| Hồi quy mã phục vụ | Chạy `test_quan_service` cùng suite. | 5/5 test TV5 qua trên bản thử nghiệm. [Kết quả](../proof/phase-1/member-6/checks.txt) |
