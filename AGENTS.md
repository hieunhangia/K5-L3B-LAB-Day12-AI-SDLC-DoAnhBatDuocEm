# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Phase 4 (contract v1.3): `python -m chonoi.bench --seed 42 --duration 30 --out bench.json` và `python -m chonoi.soak --seed 7 --days 10 --out soak.json`. Bằng chứng ở `docs/proof/phase-4/`.
- Kiểm chứng TV2 Gather v1.1: `python docs/proof/phase-2/member-2/verify.py` (suite, headless, tất định; ghi riêng trạng thái TEAM).
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)
- Kiểm tra thành viên: `python3 tools/check_team.py`
- Kiểm chứng Gather Core và tái tạo bằng chứng TV2: `python docs/proof/phase-1/member-2/verify.py` (Windows dùng `python`; máy khác có thể dùng `python3`).
- Bằng chứng TV2 sau hiệu chỉnh PRD ở `docs/proof/phase-1/member-2/prd-correction/`; test CLI payload ở `tests/test_gather_core_contract.py` (PRD-0 E/F/G, ADR 0001).
- Kiểm tra khách quán (TV4) trên PowerShell: `python -m unittest tests.test_quan_customers -v`. Fixture và lệnh headless ở `docs/verification/phase-2.md`.

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `.agents/skills/run-smoke`: Tự động chạy toàn bộ suite test và kịch bản headless trước khi commit / push để đảm bảo nhánh chính luôn xanh.
- `.agents/skills/check-scenario`: Kiểm tra tính hợp lệ của kịch bản và file kho trước khi nạp vào sim nhằm bắt lỗi sai miền giá trị (mã 2).
