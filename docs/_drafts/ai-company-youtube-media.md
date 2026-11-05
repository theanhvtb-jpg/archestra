# Mô hình công ty AI cho studio sản xuất video YouTube (thị trường Mỹ)

Bản thiết kế tổ chức dành riêng cho công ty media sản xuất video đăng YouTube nhắm khán giả Mỹ.
Kế thừa nguyên tắc nền và cách ánh xạ vào Archestra tại
[ai-company-multi-department.md](./ai-company-multi-department.md).

---

## 1. Ba sự thật quyết định cách chia phòng ban

Đừng sao chép sơ đồ phòng ban của một công ty phần mềm. Ngành này có ba đặc thù, và cả cơ cấu
tổ chức dưới đây sinh ra từ chúng.

**ST1 — Packaging quyết định nhiều hơn chất lượng sản xuất.**
Tiêu đề và thumbnail quyết định có ai bấm vào hay không. Video dựng đẹp mà packaging kém thì
không ai xem; video dựng vừa phải mà packaging tốt vẫn chạy. Hệ quả tổ chức: **Packaging phải là
một phòng riêng, và phải làm việc TRƯỚC phòng kịch bản** — không phải khâu trang trí cuối cùng.

**ST2 — Khoảng cách văn hoá là nút thắt thật, không phải ngôn ngữ.**
Đội Việt làm nội dung cho khán giả Mỹ. Vấn đề không nằm ở ngữ pháp mà ở nhịp kể, tham chiếu văn
hoá, kiểu hài, cách mở đầu, thứ gì bị coi là sáo rỗng. Đây lại đúng là chỗ AI giúp được nhiều
nhất. Hệ quả tổ chức: **Bản địa hoá là một phòng riêng có quyền chặn**, không phải một bước
dịch thuật.

**ST3 — Bản quyền là rủi ro tồn vong, không phải rủi ro vận hành.**
Một sự cố pháp lý nghiêm trọng có thể làm mất kênh, tức mất toàn bộ tài sản đã xây. Hệ quả tổ
chức: **Tuân thủ phải có quyền phủ quyết tuyệt đối**, đứng ngoài và đứng trên áp lực deadline.
Phòng này không bao giờ báo cáo cho người chịu trách nhiệm về sản lượng — nếu không nó sẽ bị
ép duyệt cho kịp lịch.

> **Cảnh báo phải đọc trước khi đầu tư.** YouTube có chính sách về nội dung "thiếu tính nguyên
> bản" và nội dung sản xuất hàng loạt, lặp lại. Mô hình "dùng AI đẩy sản lượng thật cao" là mô
> hình rủi ro cao đối với kiếm tiền. Hãy thiết kế hệ thống này theo hướng **AI làm nghiên cứu,
> bản nháp và kiểm tra; con người đóng góp góc nhìn, giọng điệu và quyết định** — chứ không phải
> dây chuyền in video. Chính sách nền tảng thay đổi thường xuyên, hãy kiểm tra điều khoản hiện
> hành của YouTube Partner Program trước khi chốt mô hình kinh doanh.

---

## 2. Sơ đồ tổ chức

```
┌──────────────────────────────────────────────────────────────┐
│  TẦNG 0 — BẠN: duyệt ngân sách, chốt hướng kênh, bấm publish │
└───────────────────────────┬──────────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │   CEO Agent        │  điều phối, không làm chuyên môn
                  └─────────┬──────────┘
        ┌───────────┬───────┴────┬────────────┬──────────────┐
        │           │            │            │              │
   ┌────▼────┐ ┌────▼─────┐ ┌───▼─────┐ ┌────▼─────┐  ┌─────▼──────┐
   │ GĐ Nội  │ │ GĐ Sản   │ │ GĐ Tăng │ │ GĐ Tuân  │  │ CFO        │
   │ dung    │ │ xuất     │ │ trưởng  │ │ thủ ⛔VETO│ │            │
   └────┬────┘ └────┬─────┘ └───┬─────┘ └────┬─────┘  └────────────┘
        │           │           │            │
   ┌────▼────────┐ ┌▼──────────┐│      ┌─────▼──────────┐
   │ Nghiên cứu  │ │ Hậu kỳ    ││      │ Bản quyền &    │
   │ & Ý tưởng   │ │ (Edit)    ││      │ Chính sách     │
   ├─────────────┤ ├───────────┤│      └────────────────┘
   │ Packaging   │ │ Tài sản số││
   │ (Title+Thumb)│ │ (Asset)   ││
   ├─────────────┤ └───────────┘│
   │ Kịch bản    │              │
   ├─────────────┤        ┌─────▼──────┐
   │ Bản địa hoá │        │ Phân tích  │
   │ & Giọng đọc │        ├────────────┤
   └─────────────┘        │ Xuất bản & │
                          │ Tối ưu     │
                          ├────────────┤
                          │ Cộng đồng  │
                          └────────────┘
```

**Điểm khác biệt quan trọng:** Giám đốc Tuân thủ **không** nằm dưới Giám đốc Sản xuất. Người lo
deadline không được quyền gây sức ép lên người lo rủi ro mất kênh.

---

## 3. Chức năng, nhiệm vụ từng phòng

### Tầng 1 — Ban điều hành

| Chức vụ | Quyết định thứ gì | Quyền đặc biệt |
|---|---|---|
| **CEO Agent** | Nhận yêu cầu của bạn, định tuyến, tổng hợp | Delegate toàn tầng 1 |
| **GĐ Nội dung** | *Làm video gì* — chốt ý tưởng, chốt packaging, chốt kịch bản | Quyết định tại Gate 0, 1, 2 |
| **GĐ Sản xuất** | *Làm kịp không* — lịch, năng lực, tắc ở đâu | Quyết định tại Gate 4 |
| **GĐ Tăng trưởng** | *Có hiệu quả không* — đọc số, quyết hướng tiếp | Quyết định tại Gate 6 |
| **GĐ Tuân thủ** | *Có được đăng không* | ⛔ **Phủ quyết tuyệt đối, mọi gate** |
| **CFO** | Chi phí mỗi video, biên lợi nhuận, trần ngân sách | Veto chi tiêu |

### Tầng 2 — Phòng ban

#### 1. Phòng Nghiên cứu & Ý tưởng
- **Nhiệm vụ:** theo dõi kênh đối thủ cùng ngách, phát hiện video bứt phá bất thường (outlier) và lý giải *vì sao* nó chạy, bám trend, đề xuất ý tưởng kèm điểm số.
- **Đầu ra:** backlog ý tưởng có chấm điểm theo: tiềm năng xem / độ khó sản xuất / rủi ro bản quyền / độ phù hợp kênh.
- **Tuyệt đối không:** đề xuất sao chép video cụ thể của kênh khác. Nhiệm vụ là rút ra *nguyên lý vì sao nó chạy*, rồi áp vào góc nhìn riêng của mình.
- **KB:** hồ sơ ngách, chân dung khán giả, lịch sử video đã làm, thư viện ý tưởng đã loại và lý do.
- **KPI:** tỉ lệ ý tưởng qua được Gate 1; tỉ lệ ý tưởng thành video đạt trên trung vị kênh.

#### 2. Phòng Packaging (Tiêu đề & Thumbnail) — *quan trọng nhất*
- **Nhiệm vụ:** với mỗi ý tưởng, sinh 10–15 phương án tiêu đề và 3–5 ý tưởng thumbnail (mô tả bố cục, biểu cảm, chữ trên ảnh, tương phản màu), rồi tự phản biện và chọn top 3.
- **Làm TRƯỚC phòng kịch bản.** Đây là điểm mấu chốt của cả mô hình: nếu không nghĩ ra nổi một tiêu đề khiến người ta muốn bấm, thì ý tưởng đó chưa đáng để viết kịch bản. Loại bỏ ở đây tốn vài phút; loại bỏ sau khi dựng xong tốn vài ngày.
- **Tuyệt đối không:** hứa trong tiêu đề điều mà video không thực hiện. Câu view sai lệch kéo thời lượng xem xuống và bị thuật toán trừng phạt — lợi trước mắt, hại lâu dài.
- **KB:** thư viện tiêu đề/thumbnail đã chạy kèm CTR thực tế, bộ quy tắc nhận diện thương hiệu kênh.
- **KPI:** CTR trung bình; độ lệch giữa CTR dự đoán và CTR thật (đo khả năng tự đánh giá).

#### 3. Phòng Kịch bản
- **Nhiệm vụ:** viết theo cấu trúc giữ chân — hook 15–30 giây đầu, lý do ở lại, các điểm mở vòng lặp tò mò, nhịp chuyển cảnh, kết có call-to-action.
- **Bắt buộc:** mỗi luận điểm phải nêu nguồn; kịch bản nộp kèm danh sách nguồn để Phòng Tuân thủ rà.
- **Tuyệt đối không:** bịa số liệu, trích dẫn, sự kiện, phát ngôn. Trong nội dung cho khán giả Mỹ, một con số bịa bị khán giả bắt trong phần bình luận là đủ mất uy tín kênh.
- **KB:** kịch bản cũ kèm đường cong giữ chân, thư viện mẫu hook, cẩm nang giọng điệu kênh.
- **KPI:** tỉ lệ giữ chân tại giây 30; thời lượng xem trung bình (AVD).

#### 4. Phòng Bản địa hoá & Giọng đọc
- **Nhiệm vụ:** rà kịch bản dưới góc nhìn khán giả Mỹ — thành ngữ, nhịp câu, tham chiếu văn hoá, đơn vị đo, cách viết ngày tháng, thứ gì nghe "không phải người bản xứ viết". Chỉ dẫn cách đọc: nhấn nhá, tốc độ, chỗ ngắt, cảm xúc.
- **Có quyền chặn:** trả kịch bản về nếu phát hiện lỗi văn hoá nghiêm trọng (đùa vô duyên trong bối cảnh Mỹ, chạm chủ đề nhạy cảm sai cách, giọng điệu sai với ngách).
- **KB:** cẩm nang khác biệt Việt–Mỹ, danh sách cụm từ cấm, hồ sơ giọng đọc chuẩn của kênh.
- **KPI:** tỉ lệ kịch bản bị người bản xứ sửa lại sau khi đã qua phòng này — chỉ số này phải giảm dần.

#### 5. Phòng Hậu kỳ
- **Nhiệm vụ:** chuyển kịch bản thành bản chỉ dẫn dựng (edit brief): cảnh nào dùng tư liệu gì, chèn đồ hoạ ở đâu, nhịp cắt, nhạc nền, phụ đề. Soát bản dựng theo checklist kỹ thuật.
- **Phần việc người làm:** dựng thật. Agent làm brief và QC, không thay thế người dựng.
- **KPI:** số giờ dựng mỗi video; tỉ lệ phải dựng lại.

#### 6. Phòng Tài sản số
- **Nhiệm vụ:** quản thư viện tư liệu, nhạc, đồ hoạ. Mỗi tài sản phải có hồ sơ giấy phép: nguồn, loại giấy phép, phạm vi dùng, hạn dùng, có cần ghi công không.
- **Vì sao cần riêng:** phần lớn sự cố bản quyền đến từ "dùng lại file cũ trong máy mà không ai nhớ nó ở đâu ra".
- **KPI:** tỉ lệ tài sản có hồ sơ giấy phép đầy đủ — mục tiêu 100%.

#### 7. Phòng Bản quyền & Chính sách ⛔
- **Nhiệm vụ:** rà hai lần — trước khi dựng (tránh phí công) và trước khi đăng (chặn rủi ro). Kiểm: nguồn tư liệu, giấy phép nhạc, tỉ lệ nội dung của người khác và mức độ biến đổi, rủi ro bị khiếu nại bản quyền, chính sách quảng cáo của YouTube, chủ đề nhạy cảm, tuyên bố y tế/tài chính.
- **Quyền:** chặn xuất bản. Không ai được ghi đè trừ bạn, và việc ghi đè phải ghi vào nhật ký.
- **KB:** điều khoản YouTube, hướng dẫn nội dung phù hợp quảng cáo, lịch sử sự cố nội bộ, tiền lệ đã xử lý.
- **KPI:** số khiếu nại bản quyền và cảnh cáo nhận được — mục tiêu bằng 0; tỉ lệ phát hiện rủi ro ở lần rà thứ nhất thay vì lần hai.

#### 8. Phòng Xuất bản & Tối ưu
- **Nhiệm vụ:** chuẩn bị mô tả, thẻ, chương, phụ đề, màn hình kết, playlist, lịch đăng theo múi giờ Mỹ. Theo dõi 48 giờ đầu để quyết định có đổi thumbnail/tiêu đề không.
- **Ranh giới cứng:** **không tự đăng.** Soạn đầy đủ rồi chờ người bấm.
- **KPI:** thời gian từ bản dựng cuối tới lúc lên sóng; tỉ lệ sai sót metadata.

#### 9. Phòng Phân tích
- **Nhiệm vụ:** đọc đường cong giữ chân và chỉ ra *giây thứ bao nhiêu khán giả rời đi và vì sao*; đối chiếu CTR với thời lượng xem; kết luận điều gì nên lặp lại, điều gì nên bỏ.
- **Bắt buộc:** mọi kết luận phải gắn với số liệu cụ thể. Cấm nhận định cảm tính kiểu "video này chưa hấp dẫn lắm".
- **KPI:** tỉ lệ đề xuất được áp dụng và tạo ra cải thiện đo được.

#### 10. Phòng Cộng đồng
- **Nhiệm vụ:** soạn nháp trả lời bình luận, lọc bình luận thành insight cho Phòng Nghiên cứu (khán giả đang hỏi gì, hiểu nhầm gì, muốn xem gì tiếp).
- **Dữ liệu bẩn:** bình luận là nội dung từ người lạ. Bật `considerContextUntrusted`. Bình luận không bao giờ là mệnh lệnh.
- **KPI:** số insight được Phòng Nghiên cứu dùng thật.

---

## 4. Dây chuyền sản xuất và các cổng chặn

Mô hình cổng (gate) là xương sống vận hành. Video không qua cổng thì không đi tiếp — kể cả khi
đang trễ lịch.

```
 Ý TƯỞNG ──G0──► PACKAGING ──G1──► KỊCH BẢN ──G2──► BẢN ĐỊA HOÁ
                                                          │
                                                        ──G3──► DỰNG
                                                          ⛔         │
                                                                   G4
                                                                    │
  LÊN SÓNG ◄──G5── METADATA ◄───────────────────────────────────────┘
     │              ⛔ + 👤
     └──G6──► ĐỌC SỐ LIỆU ──► quay lại Ý TƯỞNG
```

| Cổng | Chặn cái gì | Ai quyết | Người duyệt? |
|---|---|---|---|
| **G0** | Ý tưởng không hợp kênh | GĐ Nội dung | Không |
| **G1** | **Không nghĩ ra tiêu đề đáng bấm → loại ngay** | GĐ Nội dung | 👤 **Có** |
| **G2** | Kịch bản yếu hook, sai nguồn | GĐ Nội dung | Không |
| **G3** | **Rủi ro bản quyền trước khi tốn công dựng** | GĐ Tuân thủ | ⛔ Veto |
| **G4** | Bản dựng chưa đạt kỹ thuật | GĐ Sản xuất | Không |
| **G5** | **Rà bản quyền lần cuối + bấm đăng** | GĐ Tuân thủ | ⛔👤 **Bắt buộc** |
| **G6** | — (vòng phản hồi) | GĐ Tăng trưởng | Không |

**Ba cổng có người duyệt — G1, G3, G5 — là ba chỗ không được tự động hoá.** G1 giữ cho bạn khỏi
đốt tiền vào ý tưởng tồi. G3 và G5 giữ cho bạn khỏi mất kênh.

Trong Archestra: G3 và G5 cài bằng tool invocation policy `require_approval` trên mọi tool đăng
tải; `a2a_task_approval_request` là hàng chờ duyệt.

---

## 5. Mười quy trình cần có

| Mã | Quy trình | Nhịp | Vì sao cần |
|---|---|---|---|
| QT-01 | Tuyển chọn ý tưởng | Hằng tuần | Luôn có hàng chờ, không bao giờ sản xuất trong trạng thái cạn ý tưởng |
| QT-02 | Chốt packaging trước kịch bản | Mỗi video | Loại ý tưởng tồi khi còn rẻ |
| QT-03 | Sản xuất video | Mỗi video | Dây chuyền chuẩn, ai cũng biết mình đứng ở đâu |
| QT-04 | **Rà bản quyền hai lớp** | Mỗi video | Bảo vệ tài sản lớn nhất là cái kênh |
| QT-05 | Xuất bản | Mỗi video | Metadata sai làm hỏng cả video tốt |
| QT-06 | Đọc số liệu 48h / 7 ngày / 28 ngày | Mỗi video | Biến dữ liệu thành quyết định |
| QT-07 | Thử nghiệm tiêu đề & thumbnail | Khi video dưới kỳ vọng | Cứu video đang chạy kém |
| QT-08 | **Xử lý sự cố bản quyền** | Khi phát sinh | Phản ứng sai trong 24h đầu làm hỏng việc |
| QT-09 | Mở kênh/ngách mới | Mỗi quý | Mở rộng có kiểm soát |
| QT-10 | Quản lý tài sản & giấy phép | Liên tục | Chặn sự cố từ gốc |

### Chi tiết 4 quy trình quan trọng nhất

**QT-02 — Chốt packaging trước kịch bản**
1. Nghiên cứu đưa ý tưởng qua G0 → chuyển Packaging.
2. Packaging sinh 10–15 tiêu đề + 3–5 ý tưởng thumbnail.
3. Packaging **tự phản biện**: với mỗi phương án, nêu lý do khán giả sẽ *không* bấm.
4. Chọn top 3, đối chiếu thư viện tiêu đề cũ kèm CTR thật.
5. Trình bạn duyệt (G1). **Bạn không chọn được phương án nào → bỏ ý tưởng.** Đây là tính năng, không phải trục trặc.
6. Packaging đã chốt trở thành **lời hứa ràng buộc**: kịch bản phải thực hiện đúng điều tiêu đề hứa.

**QT-04 — Rà bản quyền hai lớp**
- *Lớp 1 (G3, trước khi dựng):* soát nguồn trong kịch bản; mọi tư liệu dự định dùng phải có hồ sơ giấy phép trong Phòng Tài sản số; đánh dấu đoạn dùng nội dung người khác và nêu rõ mức độ biến đổi; cảnh báo chủ đề nhạy cảm với quảng cáo.
- *Lớp 2 (G5, trước khi đăng):* đối chiếu bản dựng cuối với danh mục tài sản đã duyệt; kiểm nhạc nền; soát thumbnail (ảnh người, logo, nhãn hiệu); soát tiêu đề/mô tả.
- **Nguyên tắc:** không chắc về giấy phép thì coi như **không có giấy phép**. Thay tư liệu khác.
- Kết quả rà ghi vào nhật ký, giữ kèm video — về sau tranh chấp thì đây là hồ sơ tự bảo vệ.

**QT-06 — Đọc số liệu ba mốc**
- *48 giờ:* CTR thấp hơn mức nền của kênh → kích hoạt QT-07 đổi thumbnail/tiêu đề. CTR ổn mà thời lượng xem thấp → lỗi ở kịch bản hoặc dựng, ghi nhận cho video sau.
- *7 ngày:* đọc đường cong giữ chân, chỉ ra các điểm rơi và nguyên nhân. Đối chiếu với các video cùng định dạng.
- *28 ngày:* chốt kết luận — định dạng này nên nhân rộng hay dừng. Cập nhật KB của Packaging và Kịch bản bằng số liệu thật.

**QT-08 — Xử lý sự cố bản quyền**
1. Phát hiện → **dừng toàn bộ lịch đăng của kênh đó ngay**, không chờ họp.
2. Tuân thủ phân loại: khiếu nại bản quyền thông thường hay cảnh cáo vi phạm — hai thứ này khác nhau về mức độ nghiêm trọng và cách xử lý.
3. Truy nguồn: tài sản nào, lấy ở đâu, ai đưa vào, qua cổng nào mà lọt.
4. Soạn phương án xử lý → **bạn quyết**, không agent nào được tự gửi khiếu nại hay phản hồi.
5. Rà soát ngược toàn bộ video đã đăng có dùng cùng nguồn tài sản đó.
6. Vá quy trình để không lặp lại, ghi vào KB Tuân thủ.

---

## 6. Lộ trình triển khai

Đừng dựng cả 10 phòng. Thứ tự dưới đây theo đúng mức độ tạo ra giá trị.

**Đợt 1 (tuần 1–3) — Dựng phần quyết định thắng thua:**
`Nghiên cứu & Ý tưởng` + `Packaging` + CEO Agent.
Chưa đụng tới sản xuất. Mục tiêu đợt này là có một hàng chờ ý tưởng **đã chốt packaging**. Chỉ
riêng phần này đã cải thiện kết quả rõ rệt, vì nó chặn việc sản xuất những video không ai bấm.

**Đợt 2 (tuần 4–6) — Dựng phần bảo vệ tài sản:**
`Bản quyền & Chính sách` + `Tài sản số`.
Làm sớm, trước khi tăng sản lượng. Dựng lá chắn trước khi tăng tốc, không phải sau khi dính sự cố.

**Đợt 3 (tuần 7–10) — Dựng dây chuyền:**
`Kịch bản` + `Bản địa hoá & Giọng đọc` + `Hậu kỳ`.

**Đợt 4 (tuần 11+) — Dựng vòng phản hồi:**
`Phân tích` + `Xuất bản & Tối ưu` + `Cộng đồng`. Đây là lúc hệ thống bắt đầu tự học từ số liệu.

---

## 7. Rủi ro đặc thù ngành

| Rủi ro | Hậu quả | Cách chặn |
|---|---|---|
| Nội dung bị coi là sản xuất hàng loạt, thiếu nguyên bản | Mất quyền kiếm tiền | Con người đóng góp góc nhìn thật ở mỗi video; không chạy dây chuyền in video; đa dạng hoá định dạng |
| Vi phạm bản quyền tích tụ | Mất kênh | QT-04 hai lớp, QT-10, Tuân thủ có veto |
| Lệch văn hoá Việt–Mỹ | Giữ chân thấp dù sản xuất tốt | Phòng Bản địa hoá có quyền chặn; định kỳ nhờ người bản xứ soát |
| Tiêu đề hứa quá lời | Thuật toán trừng phạt, mất niềm tin | Packaging là lời hứa ràng buộc với kịch bản |
| Bịa số liệu trong kịch bản | Mất uy tín công khai | Bắt buộc trích nguồn, Tuân thủ rà nguồn |
| Prompt injection qua bình luận | Rò dữ liệu | `considerContextUntrusted` cho Phòng Cộng đồng, Dual-LLM |
| Mọi kênh dùng chung một công thức | Hỏng cùng lúc | Tách KB và cẩm nang giọng điệu riêng từng kênh |
| Chi phí AI vượt doanh thu | Lỗ âm thầm | CFO theo dõi chi phí AI mỗi video, đối chiếu doanh thu thực tế |

---

## 8. Bảng chỉ số điều hành

Theo dõi ở cấp công ty, đọc hằng tuần:

| Nhóm | Chỉ số | Ý nghĩa |
|---|---|---|
| Đầu vào | Số ý tưởng qua G1 / tổng đề xuất | Chất lượng khâu nghiên cứu |
| Packaging | CTR trung bình, độ lệch dự đoán–thực tế | Năng lực phán đoán khán giả |
| Nội dung | Giữ chân tại giây 30, thời lượng xem trung bình | Chất lượng hook và kịch bản |
| Vận hành | Số ngày từ ý tưởng tới lên sóng | Năng suất dây chuyền |
| An toàn | Số khiếu nại / cảnh cáo | **Phải bằng 0** |
| Tài chính | Chi phí AI mỗi video, chi phí mỗi 1000 lượt xem | Mô hình có lãi hay không |
| Tự động hoá | Tỉ lệ việc cần người can thiệp | Phải giảm dần theo tuần |

---

## 9. Bước tiếp theo

Giai đoạn 0 cho công ty media nên là **CEO Agent + Phòng Nghiên cứu & Ý tưởng + Phòng Packaging**
— ba agent, không phải hai, vì Nghiên cứu và Packaging chỉ có nghĩa khi đi cùng nhau.

Quy trình triển khai, định dạng file import và cách cài cổng duyệt: xem
[ai-company-phase0/README.md](./ai-company-phase0/README.md).
