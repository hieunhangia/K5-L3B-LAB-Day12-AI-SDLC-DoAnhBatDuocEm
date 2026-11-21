# Quán Ăn Chợ Nổi — `v1.0.0` (Nhóm `DoAnhBatDuocEm`)

Game mô phỏng 2D miền Tây qua 4 phase (`contract_version: "1.3"`): Út Sen lặn bắt cá/hái rau buổi sáng (`gather`), quản lý bếp/khách buổi tối (`quan`), mua nâng cấp cuối ngày (`shop`) xuyên suốt 5 ngày (`day`). Không dùng thư viện ngoài — chỉ cần **Python 3.12+**.

---

## Chạy nhanh từ clone sạch (≤ 3 lệnh trên macOS / Linux)

```bash
git clone https://github.com/hieunhangia/K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm.git && cd K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm
python3 -m chonoi.live --mode day --port 8000
# Mở trình duyệt tại http://127.0.0.1:8000/ để chơi ngay (hoặc chạy kiểm thử bên dưới)
```

- **Yêu cầu môi trường:** Python `3.12+` (chỉ dùng thư viện chuẩn), trình duyệt web hiện đại cho chế độ chơi có đồ họa. *(Trên Windows PowerShell dùng `python` nếu hệ thống chưa trỏ `python3`.)*

## Điều khiển (khi chơi trên trình duyệt)

| Phím / Nút | Chức năng |
|---|---|
| `WASD` / Mũi tên | Bơi (Lặn & Hái) hoặc đi lại (Mở Quán) |
| `E` | Cập bến / hái bông (`gather`), nấu / nhặt món / bưng cho bàn (`quan`) |
| `Space` | Bắt trọn đàn cá khi ở dưới nước (`gather`) |
| `Esc` / `P` | Tạm dừng (`pause`) và mở Menu tạm dừng |
| `C` (nút **Tương phản cao**) | Bật/tắt chế độ Tương phản cao |
| `M` | Bật/tắt âm thanh SFX (phụ đề luôn hiển thị trên màn hình) |
| `R` | Chơi lại từ đầu |

## Lệnh kiểm thử, Headless, Benchmark & Soak

```bash
# 1. Toàn bộ unit + black-box tests (P1–P4) + kiểm danh sách thành viên
python3 tools/check_team.py && PYTHONPATH=tests:. python3 -m unittest discover -s tests -v

# 2. Chế độ headless 5 Ngày
python3 -m chonoi.headless --mode day --days 5 --seed 42 --ticks 120000 --out out.jsonl

# 3. Benchmark render 1280x720 (3s làm nóng + 30s đo)
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json

# 4. Soak bot tất định 10 Ngày liên tiếp trong một tiến trình
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

## Mở rộng đã làm (`extensions: ["burn", "leaderboard"]`)

1. **`burn` (Cháy món):** cấu hình `quan.burn_s: 20` (`1200` tick). Món chín quá `1200` tick phát `dish_burnt`, dọn bếp và tự thử tái giữ chỗ một lần (`reserved` hoặc `unfulfillable`). Bằng chứng tại [`docs/proof/phase-3/burn.jsonl`](docs/proof/phase-3/burn.jsonl) và [`tests/test_quan_v12_burn.py`](tests/test_quan_v12_burn.py).
2. **`leaderboard` (Bảng xếp hạng cục bộ top-10):** hỗ trợ `--leaderboard <store.json> --player-name <tên>` ở headless `--mode day --days 5` chuẩn và `python3 -m chonoi.live --export-leaderboard <out.json>`. Hòa điểm giữ nguyên người đạt trước qua mọi lần mở lại; không làm thay đổi JSONL hay chạy trong `soak`. Bằng chứng tại [`docs/proof/phase-4/leaderboard.json`](docs/proof/phase-4/leaderboard.json) và [`tests/test_phase4_v13.py`](tests/test_phase4_v13.py).

## Sáng tạo của nhóm

- **Phụ đề SFX trực quan trên Canvas:** kết hợp Web Audio synthesizer không cần asset ngoài cùng thanh phụ đề tiếng Việt thời gian thực cho mọi sự kiện quan trọng (`hái`, `bắt cá`, `thủy quái chạm`, `nguyên liệu ươn`, `cháy món`, `thanh toán`), có công tắc tắt tiếng `M` mà vẫn giữ phụ đề — hoàn toàn tách khỏi chế độ headless và không ảnh hưởng Test Contract.

## Bằng chứng & Hồ sơ nhóm

- Thành viên & thỏa thuận: [`TEAM.md`](TEAM.md) · Phản tư 6 thành viên: [`docs/members/`](docs/members/)
- Ma trận truy vết từng phase: [`phase-1.md`](docs/verification/phase-1.md), [`phase-2.md`](docs/verification/phase-2.md), [`phase-3.md`](docs/verification/phase-3.md), [`phase-4.md`](docs/verification/phase-4.md)
- Benchmark & Soak thực đo `v1.0.0`: [`bench.json`](docs/proof/phase-4/bench.json) · [`soak.json`](docs/proof/phase-4/soak.json)
- Retro & Changelog: [`docs/retro.md`](docs/retro.md) · [`CHANGELOG.md`](CHANGELOG.md) · [`CREDITS.md`](CREDITS.md)
