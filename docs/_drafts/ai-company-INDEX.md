# Công ty AI cho studio YouTube — mục lục

Bộ tài liệu dựng một studio sản xuất video YouTube cho khán giả Mỹ, trong đó mỗi phòng ban là
một AI agent chạy trên Archestra. Định dạng: video dài từ 20 phút, cắt clip đăng YouTube Shorts
và Facebook Reels.

Kết quả cuối: **17 agent** (1 CEO, 5 giám đốc, 11 phòng), 7 cổng chặn, 7 nhịp vận hành tự động,
và khoá kỹ thuật trên mọi hành động không thể hoàn tác.

## Đọc theo thứ tự này

| # | Tài liệu | Nội dung |
|---|---|---|
| 0 | [Chuẩn bị hạ tầng](./ai-company-media-SETUP.md) | Khoá API, địa chỉ, cần bao nhiêu tool |
| 1 | [Nguyên tắc nền](./ai-company-multi-department.md) | Năm nguyên tắc, cách ánh xạ vào Archestra, rủi ro chung |
| 2 | [Thiết kế cho studio YouTube](./ai-company-youtube-media.md) | 11 phòng, 7 cổng, 10 quy trình, rủi ro ngành |
| 3 | [Đợt 0 — ba agent đầu](./ai-company-media-phase0/README.md) | Nghiên cứu, Packaging, CEO |
| 4 | [Đợt 2 — lá chắn](./ai-company-media-wave2/README.md) | Bản quyền, Tài sản số |
| 5 | [Đợt 3 — dây chuyền](./ai-company-media-wave3/README.md) | Kịch bản, Bản địa hoá, Hậu kỳ, Tái sử dụng |
| 6 | [Đợt 4 — vòng phản hồi](./ai-company-media-wave4/README.md) | Xuất bản, Phân tích, Cộng đồng, **policy** |
| 7 | [Đợt 5 — tầng giám đốc](./ai-company-media-wave5/README.md) | 5 giám đốc, nhịp vận hành |
| 8 | [QT-08 — xử lý sự cố bản quyền](./ai-company-media-qt08/README.md) | Quy trình khi nhận khiếu nại hoặc cảnh cáo |

> Không có "Đợt 1". Đánh số theo các đợt trong lộ trình gốc, và đợt đầu tiên gọi là Đợt 0 vì nó
> là bước chạy thử chứ chưa phải sản xuất thật.

Có [một bộ mẫu cho công ty thường](./ai-company-phase0/README.md) (CSKH + CEO) từ trước khi biết
bạn làm media — giữ lại để tham khảo cấu trúc, không dùng cho studio.

## Nếu chỉ đọc được một thứ

Ba quyết định chi phối toàn bộ thiết kế này:

**1. Packaging chạy trước kịch bản, và được quyền loại ý tưởng.**
Nếu không nghĩ ra nổi tiêu đề đáng bấm, ý tưởng đó chưa đáng viết kịch bản. Loại ở bàn Packaging
tốn vài phút; loại sau khi dựng xong tốn vài ngày.

**2. Tuân thủ không báo cáo cho Sản xuất.**
Người lo deadline không được quyền ép người lo rủi ro mất kênh. Nếu để chung một nhánh, đến lúc
trễ lịch là tuân thủ bị ép duyệt cho kịp.

**3. Lá chắn dựng trước khi tăng tốc.**
Bản quyền và Tài sản số làm ở Đợt 2, trước dây chuyền sản xuất ở Đợt 3. Dựng khi sản lượng còn
thấp thì rẻ; dựng sau khi đã tăng tốc thì luôn bị coi là cản trở và bị bỏ qua đúng lúc cần nhất.

## Script

| Script | Ở đâu | Làm gì |
|---|---|---|
| `update-ceo.py` | wave2, wave3, wave4 | Cập nhật CEO **tại chỗ** |
| `setup-policies.py` | wave4 | Cài khoá kỹ thuật trên tool đăng/xoá/gửi |
| `wire-org.py` | wave5 | Nối cả sơ đồ CEO → giám đốc → phòng |
| `setup-rhythms.py` | wave5 | Tạo 7 nhịp vận hành định kỳ |
| `doctor.py` | `_drafts/` | **Chạy đầu tiên** — kiểm tra hiện trạng, chỉ đọc |
| `test-agent-prompts.py` | `_drafts/` | Kiểm thử agent có **từ chối đúng chỗ** không (cần khoá LLM) |

Bốn script đầu **mặc định dry-run**, phải thêm `--apply` mới thực thi. `doctor.py` chỉ đọc,
không bao giờ thay đổi gì — chạy nó trước tiên để biết đang thiếu gì.

## Ba cái bẫy đã gặp, ghi lại để khỏi vấp

**Import luôn TẠO MỚI, không ghi đè.** Trùng tên thì tự thêm hậu tố ` (imported)` và không báo
lỗi (`platform/backend/src/services/agent-import.ts`). Muốn sửa agent đã có thì dùng
`PUT /api/agents/:id`, đừng import lại. `wire-org.py` cảnh báo nếu phát hiện bản trùng.

**Warning không phải lỗi.** Thiếu tool, thiếu KB, thiếu delegation thì import vẫn trả 200. Bỏ qua
mảng `warnings` là cách phổ biến nhất để kết thúc với agent rỗng.

**Thứ tự import có ý nghĩa.** Agent được tham chiếu phải tồn tại trước. Phòng ban trước giám đốc,
giám đốc trước CEO.

## Khi có sự cố

[QT-08](./ai-company-media-qt08/README.md) là quy trình dùng khi kênh nhận khiếu nại, cảnh cáo
hoặc yêu cầu gỡ bỏ. Ba điều quan trọng nhất trong đó:

1. **Phân loại trước.** Nhầm khiếu nại thường với cảnh cáo vi phạm là lỗi phổ biến nhất, và
   hoảng loạn với loại nhẹ gây hại nhiều hơn chính sự cố.
2. **Đừng phản đối cho bõ tức.** Phản đối một yêu cầu gỡ bỏ là một bước pháp lý, không phải một
   nút bấm. Chỉ phản đối khi sổ đăng ký tài sản chứng minh được giấy phép.
3. **Truy vết ngược.** Một tư liệu có vấn đề hiếm khi chỉ nằm ở một video. Đây là bước hay bị bỏ
   quên nhất và tốn kém nhất khi bỏ quên.

**Diễn tập một lần mỗi quý, khi chưa có sự cố.** Quy trình chưa từng chạy thì không phải quy
trình, chỉ là tài liệu.

## Ba thứ con người giữ, và nên giữ mãi

1. **Cổng 1** — chốt packaging. Đây là quyết định đốt tiền vào ý tưởng nào.
2. **Cổng 5** — bấm đăng. Không thể hoàn tác.
3. **Ghi đè kết luận Tuân thủ.** Hiếm khi nên làm, và phải ghi vào nhật ký.

## Cảnh báo cần đọc lại định kỳ

YouTube có chính sách về nội dung thiếu tính nguyên bản và sản xuất hàng loạt, lặp lại. Mô hình
"dùng AI đẩy sản lượng thật cao" là mô hình **rủi ro cao** với việc kiếm tiền.

Bộ thiết kế này cố ý đặt AI vào vai nghiên cứu, bản nháp và kiểm tra — còn góc nhìn, giọng điệu
và quyết định vẫn thuộc về con người. Nếu bạn vận hành nó như dây chuyền in video, cơ cấu này
sẽ cản bạn, và đó là chủ ý.

Chính sách nền tảng thay đổi thường xuyên hơn tài liệu này. Hãy kiểm tra điều khoản YouTube
Partner Program hiện hành thay vì tin bản ghi chép cũ.
