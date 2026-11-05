# QT-08 — Xử lý sự cố bản quyền

Quy trình dùng khi kênh nhận khiếu nại, cảnh cáo, yêu cầu gỡ bỏ, hoặc khi có bên thứ ba liên hệ
về bản quyền.

Đây là tài liệu bạn đọc vào lúc hoảng nhất. Nó được viết ngắn và theo thứ tự hành động, không
phải để đọc cho hiểu — mà để làm theo.

> **Không phải tư vấn pháp lý.** Tài liệu này giúp bạn phản ứng có trật tự và không làm tình hình
> xấu đi. Thủ tục cụ thể của từng nền tảng thay đổi thường xuyên — luôn đối chiếu với điều khoản
> hiện hành. Vụ việc có tranh chấp thật thì hỏi luật sư.

**Nguyên tắc bao trùm: phản ứng trong 24 giờ đầu quyết định đây là chuyện nhỏ hay chuyện lớn.**
Phần lớn thiệt hại trong các sự cố loại này không đến từ bản thân sự cố, mà đến từ phản ứng vội.

---

## Bước 0 — Phân loại. Làm trước mọi thứ khác.

**Lỗi phổ biến nhất là nhầm khiếu nại thường với cảnh cáo vi phạm.** Hai thứ này hậu quả khác
nhau hoàn toàn. Hoảng loạn với loại nhẹ gây hại nhiều hơn chính sự cố.

| Loại | Dấu hiệu | Mức | Hậu quả điển hình |
|---|---|---|---|
| **Khiếu nại bản quyền thường** (Content ID) | Thông báo tự động, video vẫn còn | **P2** | Doanh thu video đó chuyển cho bên khiếu nại. Thường **không** phải cảnh cáo |
| **Cảnh cáo vi phạm bản quyền** (strike) | Ghi rõ là cảnh cáo, có thời hạn | **P0** | Tích luỹ đủ số lần → **mất kênh** |
| **Cảnh cáo nguyên tắc cộng đồng** | Hệ thống khác, không phải bản quyền | **P1** | Hạn chế tính năng, tích luỹ cũng mất kênh |
| **Khiếu nại trên Facebook** | Từ hệ thống quản lý quyền của Facebook | **P1** | Nền tảng khác, quy trình khác, hồ sơ riêng |
| **Yêu cầu gỡ bỏ chính thức** (DMCA) | Do người thật gửi, không phải hệ thống tự động | **P0** | Thường kèm cảnh cáo |
| **Bên thứ ba liên hệ trực tiếp** | Email, thư luật sư, tin nhắn | **P0** | Có thể thành vụ pháp lý |

Phân loại sai ở bước này làm sai toàn bộ các bước sau. Nếu không chắc, coi như mức cao hơn.

---

## Bước 1 — Giờ đầu tiên: cầm máu

**Làm ngay, theo đúng thứ tự:**

1. **Dừng toàn bộ lịch đăng của kênh đó.** Không chờ họp, không chờ ai duyệt. Nếu nguyên nhân là
   một tư liệu dùng chung, các video đang chờ đăng có thể dính cùng vấn đề.
2. **Chụp màn hình và lưu nguyên văn toàn bộ thông báo**, kèm thời điểm nhận.
3. **Mở hồ sơ sự cố** theo [mẫu](./incident-log-template.md).

**Tuyệt đối KHÔNG làm trong giờ đầu:**

| Đừng làm | Vì sao |
|---|---|
| ❌ Xoá video | Xoá có thể huỷ bằng chứng của chính bạn. Với cảnh cáo, **xoá video thường không gỡ được cảnh cáo** — bạn mất video mà vẫn giữ hậu quả |
| ❌ Phản đối ngay | Xem Bước 3. Phản đối sai có thể làm sự cố leo thang thành vụ pháp lý |
| ❌ Trả lời bên khiếu nại | Chưa biết mình đúng hay sai thì chưa nói gì |
| ❌ Đăng bài giải thích công khai | Phát ngôn lúc chưa có thông tin đầy đủ gần như luôn gây hại |
| ❌ Để agent tự xử lý | Mọi văn bản gửi ra ngoài đều do người gửi |

---

## Bước 2 — 24 giờ đầu: truy nguồn

Ba câu hỏi, theo thứ tự.

**a) Tư liệu nào bị khiếu nại, hồ sơ giấy phép ra sao?**
→ Phòng Tài sản số tra sổ đăng ký. Kết quả rơi vào đúng một trong ba trạng thái:

| Trạng thái | Nghĩa là |
|---|---|
| **CÓ GIẤY PHÉP ĐẦY ĐỦ** | Hồ sơ ghi rõ nguồn, loại giấy phép, phạm vi bao gồm nền tảng và mục đích thương mại |
| **CÓ NHƯNG THIẾU PHẠM VI** | Có giấy phép, nhưng không bao trùm nền tảng hoặc cách dùng này |
| **MỒ CÔI** | Không tra được hồ sơ |

**Đây là lúc sổ đăng ký tài sản (Đợt 2) trả nợ.** Nếu sổ trống, bạn không có cơ sở để làm gì
ngoài chấp nhận — và đó chính là lý do phòng Tài sản số được dựng trước dây chuyền sản xuất.

**b) Tư liệu đó đã dùng ở NHỮNG VIDEO NÀO KHÁC?**
→ Phòng Tài sản số truy vết ngược qua trường `ĐÃ DÙNG TẠI`.

**Đây là bước hay bị bỏ quên nhất, và là bước tốn kém nhất khi bỏ quên.** Một tư liệu có vấn đề
hiếm khi chỉ nằm ở một video.

**c) Nó lọt qua cổng nào?**
→ Phòng Bản quyền đối chiếu hồ sơ rà soát Lớp 1 và Lớp 2 của video đó. Để dành cho Bước 5.

---

## Bước 3 — Quyết định phản ứng

**Người quyết, không phải agent.** Agent soạn nháp; bạn đọc, sửa, và gửi.

| Trạng thái giấy phép | Phương án nên chọn | Rủi ro |
|---|---|---|
| CÓ ĐẦY ĐỦ | Phản đối, kèm bằng chứng từ sổ đăng ký | Thấp — nhưng đọc cảnh báo dưới |
| THIẾU PHẠM VI | **Sửa video**: thay nhạc, cắt đoạn, tắt tiếng đoạn đó | Mất chút chất lượng, an toàn |
| MỒ CÔI | **Chấp nhận**, gỡ tư liệu khỏi video | An toàn nhất |

> ⚠️ **Phản đối sai có thể làm sự cố leo thang.** Trong nhiều quy trình chính thức, việc phản đối
> một yêu cầu gỡ bỏ đồng nghĩa với cung cấp danh tính của bạn cho bên khiếu nại và chấp nhận thẩm
> quyền xét xử. Đó là một bước pháp lý, không phải một nút bấm.
>
> **Đừng phản đối cho bõ tức.** Chỉ phản đối khi có hồ sơ giấy phép chứng minh được. Với mọi sự
> cố mức P0, hỏi luật sư trước khi phản đối.

Chấp nhận một khiếu nại mức P2 thường là quyết định đúng về mặt kinh doanh: bạn mất doanh thu của
một video, đổi lấy việc không có rủi ro nào thêm.

---

## Bước 4 — Rà soát ngược và xử lý chủ động

Với danh sách video từ Bước 2b:

1. Liệt kê mọi video đã đăng có dùng cùng tư liệu, trên **mọi nền tảng** — kể cả clip Shorts và
   Reels cắt ra.
2. Xử lý chủ động: thay tư liệu, hoặc gỡ đoạn đó, trước khi bị khiếu nại tiếp.
3. Đánh dấu tư liệu đó trong sổ đăng ký là **CẤM DÙNG**, kèm lý do và ngày.

**Chủ động sửa luôn rẻ hơn nhận thêm cảnh cáo.** Mỗi cảnh cáo tiếp theo đẩy kênh gần hơn tới
ngưỡng mất kênh, và ngưỡng đó không cao.

---

## Bước 5 — Vá quy trình

Không làm bước này thì sự cố sẽ lặp lại. Trả lời bốn câu, ghi vào `KB Tuan thu`:

1. Tư liệu này **có trong sổ đăng ký** không? Không có → vì sao nó vào được bản dựng?
2. **Cổng 3** (rà trước dựng) có cơ hội bắt được không? Nếu có mà không bắt, thiếu ở đâu?
3. **Cổng 5** (rà trước đăng) tương tự.
4. Có ai đã **bỏ qua hoặc gây áp lực** lên một cảnh báo không? Nếu có, đây là sự cố quản trị,
   nghiêm trọng hơn chính sự cố bản quyền.

Mục "lịch sử sự cố" trong `KB Tuan thu` tồn tại chính là để chứa kết quả bước này. Lần sau Phòng
Bản quyền rà soát, nó đọc được tiền lệ này.

---

## Bước 6 — Mở lại lịch đăng

Chỉ mở lại khi **đủ cả bốn**:

- [ ] Đã quyết xong phương án cho sự cố gốc và đã thực hiện
- [ ] Đã rà soát ngược xong toàn bộ video dùng cùng tư liệu
- [ ] Tư liệu có vấn đề đã bị đánh dấu CẤM DÙNG trong sổ
- [ ] Các video đang chờ đăng đã được rà lại, xác nhận không dùng tư liệu đó

Với sự cố P0, thêm một điều kiện: **bạn đích thân xác nhận**, không uỷ quyền.

---

## Ai làm gì

| Việc | Ai |
|---|---|
| Dừng lịch đăng | CEO Agent — được phép làm ngay, không chờ duyệt |
| Phân loại sự cố | Phòng Bản quyền & Chính sách |
| Tra giấy phép, truy vết ngược | Phòng Tài sản số |
| Soạn nháp văn bản phản hồi | Phòng Bản quyền & Chính sách |
| **Quyết định phương án** | **Bạn** |
| **Gửi bất kỳ văn bản nào ra ngoài** | **Bạn** |
| Rà soát ngược video liên quan | Phòng Tài sản số + Hậu kỳ |
| Viết bài học vào KB | GĐ Tuân thủ |
| Mở lại lịch đăng | **Bạn** (P0) hoặc GĐ Tuân thủ (P1, P2) |

Không agent nào được tự gửi khiếu nại, phản đối, hay liên hệ bên thứ ba. Điều này đã nằm trong
prompt của Phòng Bản quyền và GĐ Tuân thủ.

---

## Ngưỡng báo động

| Tình huống | Nghĩa là |
|---|---|
| 1 cảnh cáo vi phạm | P0. Dừng mọi thứ, rà toàn bộ thư viện tài sản |
| 2 cảnh cáo còn hiệu lực cùng lúc | **Dừng sản xuất.** Xem lại toàn bộ mô hình nội dung, không chỉ xử lý sự cố |
| Nhiều khiếu nại trong một tháng | Quy trình đang hỏng, **không phải xui**. Lỗi nằm ở Cổng 3 hoặc ở sổ tài sản |
| Khiếu nại trên tư liệu mà sổ ghi "có giấy phép" | Hồ sơ trong sổ sai hoặc giấy phép đã hết hạn. Rà lại **toàn bộ** sổ, không chỉ tư liệu này |

Hàng cuối là tình huống nguy hiểm nhất, vì nó nghĩa là nguồn sự thật của bạn không đáng tin.

---

## Diễn tập

**Chạy một lần mỗi quý, khi chưa có sự cố.** Quy trình chưa từng chạy thì không phải quy trình,
chỉ là tài liệu.

Kịch bản diễn tập:

> Giả định: video đã đăng 3 tuần trước nhận khiếu nại bản quyền về nhạc nền.
> Không báo trước cho ai.

Bấm giờ và đo:

| Câu hỏi | Mục tiêu |
|---|---|
| Mất bao lâu để phân loại đúng là khiếu nại hay cảnh cáo? | < 15 phút |
| Phòng Tài sản số tra được hồ sơ giấy phép không? | Có |
| Có liệt kê được **mọi** video khác dùng cùng bản nhạc không? | Có — đây là chỗ hay trượt nhất |
| Có ai định xoá video hoặc phản đối ngay không? | Không được có |
| Mất bao lâu để dừng lịch đăng? | < 5 phút |

Trượt mục nào thì vá chỗ đó. Thường mục trượt là truy vết ngược — và đó là dấu hiệu sổ đăng ký
tài sản chưa đầy đủ trường `ĐÃ DÙNG TẠI`.

---

## Liên quan

- [Đợt 2 — Bản quyền & Tài sản số](../ai-company-media-wave2/README.md) — sổ đăng ký mà quy trình này dựa vào
- [Thiết kế gốc](../ai-company-youtube-media.md) — QT-04, rà soát hai lớp phòng ngừa
- [Mục lục](../ai-company-INDEX.md)
