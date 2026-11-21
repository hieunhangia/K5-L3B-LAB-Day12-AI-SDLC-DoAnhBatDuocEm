# Retro nhóm

## Phase 2 (nhanh)
- Qua kiểm tra Phase 4, đầu ra Gather đủ để kiểm thử Quán với kho thu hoạch thật.
- Lần kiểm tra đầu tiên diễn ra trước lúc nhánh TV4 xuất hiện, nên ca khách tự đến chưa có đủ mã để chạy.
- Hành động đề xuất khi tích hợp TV4 và TV5 là chạy fixture kho chung qua toàn bộ vòng đời khách.

## Phase 4 (cuối)
- Kho Gather đã chạy được qua phần bếp của TV5 với khách dựng sẵn. Sau khi có nhánh TV4, bản ghép QA cũng chạy qua ca khách tự đến và thanh toán.
- Runner cho phép phát lại cùng input và thu được JSONL và file kho khớp từng byte.
- Đối soát lịch sử nhánh gốc trước lượt QA: TV1, TV2, TV4 và TV5 có ba commit nghiệp vụ mỗi người. TV3 có ba commit tính năng/kiểm thử và hai commit bổ sung minh chứng, hồ sơ. Kết quả tính theo nội dung và tác giả Git, tách commit merge. Các số liệu AI có nguồn nằm trong [nhật ký](ai-usage-log.md).
- Khi so với fixture thật của TV5, QA phát hiện bộ kiểm tra đầu tiên bỏ sót trạng thái `waiting` và cách suy ra giá/boa. Đã điều chỉnh và chạy lại test TV5.
- Đề xuất lần sau chốt fixture quán và tên trường trạng thái trong hợp đồng trước khi tách hai lát triển khai. Nhóm xác nhận retro trước khi dùng để nộp.
