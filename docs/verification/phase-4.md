# Ma trận kiểm chứng Phase 4 (`Test Contract v1.3` — Phát hành `v1.0.0`)

| AC | Hạng mục kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| `AC-P4-01` · Contract `v1.3` | Khai `contract_version: "1.3"`, `bench_cmd`, `soak_cmd`, `extensions: ["burn", "leaderboard"]` | `game.contract.json`, `chonoi/contract.py`, `tests/test_phase4_v13.py` | Đạt |
| `AC-P4-02` · Benchmark 1280×720 (`bench_cmd`) | Làm nóng 3s + đo 30s cảnh lặn sáng mặc định (`seed 42`) | [bench.json](../proof/phase-4/bench.json) | Đạt (`avg_fps: 2665.49`, `p1_low_fps: 1719.53`, `frames: 79867`, `measured_s: 29.9634`, `load_ms: 2.42`) |
| `AC-P4-03` · Soak 10 ngày (`soak_cmd`) | Bot tất định chạy 10 ngày lặp D1–D5 trong 1 tiến trình (`seed 7`), không ghi leaderboard | [soak.json](../proof/phase-4/soak.json), `tests/test_phase4_v13.py` | Đạt (`days: 10`, `days_completed: 10`, `crashes: 0`, `duration_s: 4.423s`) |
| `AC-P4-04` · Mở rộng `leaderboard` | Top 10 cục bộ bền vững, hòa giữ người trước qua reload, Unicode khác rỗng, cặp `--leaderboard`+`--player-name`, `--export-leaderboard`, không đổi JSONL | `chonoi/leaderboard.py`, [leaderboard.json](../proof/phase-4/leaderboard.json), `tests/test_phase4_v13.py` | Đạt |
| `AC-P4-05` · 3 cảnh báo & Tương phản cao | `⚠ Thủy quái!`, `🫧 Hết hơi!`, `😠 Khách sắp giận!`, nút **Tương phản cao (C)**, menu Chơi/Pause/Shop, phụ đề SFX | `chonoi/web/index.html`, `tests/test_phase4_v13.py` | Đạt |
| `AC-P4-06` · Hồi quy & Hồ sơ phát hành | Chạy lại toàn bộ P1–P4 + clone sạch `<= 3` lệnh + retro P2/P4 + `check_team.py` + 6/6 phản tư `<= 200` từ | `README.md`, `CHANGELOG.md`, `CREDITS.md`, `docs/retro.md`, `docs/members/*.md` | Đạt |
