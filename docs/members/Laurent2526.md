# Laurent2526 — phản tư cá nhân

Tôi là Đỗ Thanh Mai, phụ trách QA và chuẩn bị release.

- Tôi bổ sung kiểm tra kịch bản và bài test từ giỏ rỗng đến thanh toán, sau đó lưu bằng chứng từ bản tích hợp. [Commit kiểm thử](https://github.com/hieunhangia/K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm/commit/161d6a0), [commit bằng chứng](https://github.com/hieunhangia/K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm/commit/e220224).
- Tôi đối chiếu hợp đồng kho và kiểm tra cả [mã khách hàng của TV4](https://github.com/hieunhangia/K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm/commit/5d8b1d7) lẫn [mã phục vụ của TV5](https://github.com/hieunhangia/K5-L3B-LAB-Day12-AI-SDLC-DoAnhBatDuocEm/commit/7c85aac). Bản tích hợp qua 73/73 test.
- AI ban đầu bỏ sót trạng thái `waiting` và yêu cầu mọi khách đang ăn có giá và boa ghi sẵn. Đối chiếu fixture cho thấy có thể suy ra các giá trị đó từ menu và kiên nhẫn.
- Tôi học được cách dùng cùng file kho để kiểm riêng phần phục vụ rồi kiểm cả luồng. Chạy lại bằng cùng seed và input giúp tôi xác nhận kết quả từng byte.
