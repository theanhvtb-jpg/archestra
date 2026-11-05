# Đợt 3 — Dây chuyền sản xuất

Tiếp nối [Đợt 2](../ai-company-media-wave2/README.md). Đợt này dựng phần làm ra video thật, cho
định dạng đã chốt: **video dài từ 20 phút**, sau đó cắt clip dọc đăng **YouTube Shorts và
Facebook Reels**.

Sau đợt này công ty có 8 phòng và một dây chuyền chạy được từ ý tưởng tới bản dựng cuối.

## Nội dung

| File | Vai trò |
|---|---|
| `01-script-agent.json` | Phòng Kịch bản — kiến trúc giữ chân cho video dài |
| `02-localization-agent.json` | Phòng Bản địa hoá & Giọng đọc — có quyền trả về kịch bản |
| `03-post-production-agent.json` | Phòng Hậu kỳ — chỉ dẫn dựng và soát bản dựng |
| `04-repurpose-agent.json` | Phòng Tái sử dụng & Phân phối — clip cho Shorts và Reels |
| `05-ceo-prompt-v3.txt` | Prompt CEO mới — biết 8 phòng, 6 cổng |
| `format-profile-template.md` | **Hồ sơ định dạng — nạp vào KB, điền trước khi chạy** |
| `update-ceo.py` | Cập nhật CEO tại chỗ (bản sao từ Đợt 2) |

## Ba quyết định thiết kế

### 1. Định dạng là dữ liệu trong KB, không phải chữ trong prompt

Phòng Kịch bản đọc thông số từ tài liệu "Hồ sơ định dạng" trong `KB Kich ban`. Prompt chỉ có giá
trị mặc định và tự khai báo khi đang dùng mặc định.

Lợi ích: đổi độ dài, đổi số đoạn, đổi giọng điệu, thêm ngách mới — chỉ sửa một tài liệu, không
đụng vào agent. Mở kênh thứ hai với định dạng khác thì tạo KB khác, dùng lại cùng agent.

**Con số quan trọng nhất phải tự đo: tốc độ đọc của kênh.** Mặc định 140–160 từ/phút chỉ là điểm
khởi đầu; kênh kể chuyện chậm có thể 120, kênh thông tin nhanh 180. Lấy một video đã đăng, đếm
số từ bản lời đọc, chia cho số phút. Sai con số này thì mọi ước lượng độ dài đều sai theo.

### 2. Điểm cắt clip được đánh dấu lúc viết kịch bản, không phải lúc dựng xong

Phòng Kịch bản phải đánh dấu 3–6 điểm `[CLIP]`, và một đoạn chỉ được đánh dấu khi thoả **cả ba**:
tự đứng được · có cao trào riêng · cắt dọc được.

Lý do: nếu để hậu kỳ mò tìm khoảnh khắc sau khi dựng xong, bạn sẽ nhận ra nhiều video **không có**
khoảnh khắc nào tự trọn vẹn — và lúc đó đã muộn. Bắt đánh dấu lúc viết biến nó thành ràng buộc
thiết kế: kịch bản buộc phải có cao trào rải đều, điều này cũng tốt cho chính video dài.

Nếu Phòng Tái sử dụng báo "không tìm được khoảnh khắc tự trọn vẹn nào", đó là **triệu chứng kịch
bản thiếu cao trào**, không phải lỗi của khâu cắt clip.

### 3. YouTube Shorts và Facebook Reels KHÔNG dùng chung một bản

Đây là chỗ hay làm sai nhất khi phân phối đa nền tảng.

| | YouTube Shorts | Facebook Reels |
|---|---|---|
| Khán giả | Trùng một phần với kênh chính | Khác hẳn, ít biết kênh |
| Xem không tiếng | Ít hơn | **Rất phổ biến** — phụ đề bắt buộc |
| Dẫn về video dài | Khả thi, cùng nền tảng | **Kém hiệu quả** |
| Chiến lược | Có thể dẫn về bản đầy đủ | Phải **tự trọn vẹn** |

Nên cùng một khoảnh khắc cần **hai câu dẫn và hai lời kêu gọi khác nhau**. Prompt bắt agent nộp
hai bản riêng cho mỗi clip.

## ⚠️ Giấy phép đa nền tảng — rủi ro mới của đợt này

**Tư liệu được duyệt cho YouTube KHÔNG mặc nhiên dùng được trên Facebook.** Phạm vi giấy phép
thường ghi rõ nền tảng, và nhạc là trường hợp sai nhiều nhất.

Đây là lý do trường `PHẠM VI` trong sổ đăng ký tài sản (Đợt 2) phải ghi rõ **từng nền tảng**, chứ
không phải chỉ "dùng thương mại được". Nếu sổ của bạn đang ghi chung chung, hãy sửa ngay trước
khi bắt đầu đăng Facebook.

Quy trình: Tái sử dụng nộp danh sách "TƯ LIỆU CẦN XÁC NHẬN PHẠM VI" → CEO chuyển Tài sản số tra →
không xác nhận được thì clip đó **chỉ đăng YouTube Shorts**.

## Triển khai

### Bước 1 — Tạo KB và nạp hồ sơ định dạng

```bash
for KB in "KB Kich ban" "KB Ban dia hoa" "KB Hau ky" "KB Tai su dung"; do
  curl -X POST http://localhost:9000/api/knowledge-bases \
    -H "Authorization: $ARCHESTRA_API_KEY" \
    -H "Content-Type: application/json" -d "{\"name\":\"$KB\"}"
done
```

**Điền `format-profile-template.md` rồi nạp vào `KB Kich ban`.** Đây là việc quan trọng nhất của
đợt này — bỏ qua thì Phòng Kịch bản viết theo mặc định và bạn sẽ phải sửa tay mọi kịch bản.

Nạp thêm nếu có:
- `KB Kich ban`: kịch bản cũ kèm đường cong giữ chân.
- `KB Ban dia hoa`: cẩm nang giọng điệu, danh sách cụm từ cấm, video mẫu đúng giọng.
- `KB Hau ky`: checklist kỹ thuật của kênh, quy cách đồ hoạ.
- `KB Tai su dung`: clip cũ kèm số liệu từng nền tảng.

### Bước 2 — Import bốn agent

```bash
for F in 01-script-agent.json 02-localization-agent.json \
         03-post-production-agent.json 04-repurpose-agent.json; do
  curl -X POST http://localhost:9000/api/agents/import \
    -H "Authorization: $ARCHESTRA_API_KEY" \
    -H "Content-Type: application/json" --data-binary @"$F"
done
```

Sửa `{TEN_CONG_TY}` và `{TEN_NGUOI}` trước khi import. Đọc mảng `warnings` trong response.

### Bước 3 — Cập nhật CEO lên v3

Lấy ID tám phòng:

```bash
curl -s "http://localhost:9000/api/agents" -H "Authorization: $ARCHESTRA_API_KEY" \
  | python3 -c "import sys,json; [print(a['id'],'|',a['name']) for a in json.load(sys.stdin).get('data',[])]"
```

```bash
python3 update-ceo.py --ceo-id <CEO_ID> --prompt-file 05-ceo-prompt-v3.txt \
  --target-id <NGHIEN_CUU> --target-id <PACKAGING> \
  --target-id <KICH_BAN>  --target-id <BAN_DIA_HOA> \
  --target-id <HAU_KY>    --target-id <TAI_SU_DUNG> \
  --target-id <BAN_QUYEN> --target-id <TAI_SAN_SO>
```

Script đặt lại **toàn bộ** danh sách delegation — phải liệt kê đủ cả tám.

Nhắc lại: **không import lại CEO.** Import luôn tạo agent mới và tự thêm hậu tố ` (imported)`.

### Bước 4 — Ngân sách

Phòng Kịch bản là phòng tốn nhất của cả hệ thống: đầu ra 3.000 từ cộng với việc đọc hồ sơ định
dạng và kịch bản cũ. Đặt trần riêng, và theo dõi chi phí mỗi kịch bản — đây là con số sẽ quyết
định bạn chạy được bao nhiêu video mỗi tháng.

## Nghiệm thu

**Kịch bản**
- [ ] Trả về kịch bản có đủ tái câu dẫn ở **đầu mỗi đoạn**, không chỉ ở đầu video
- [ ] Mọi vòng lặp đã mở đều được đóng — kiểm mục "VÒNG LẶP ĐÃ MỞ / ĐÃ ĐÓNG"
- [ ] Có 3–6 điểm `[CLIP]`, mỗi điểm giải thích được **vì sao tự đứng được**
- [ ] Hỏi một chủ đề không có nguồn đáng tin → **ESCALATE**, không bịa số liệu
- [ ] Số từ khớp với tốc độ đọc trong hồ sơ định dạng

**Bản địa hoá**
- [ ] Đưa kịch bản có `1.000` kiểu Việt → sửa thành `1,000`
- [ ] Đưa kịch bản ghi ngày `03/04/2026` → cảnh báo nhầm lẫn tháng/ngày
- [ ] Đưa kịch bản dùng mét/kg/độ C → đề nghị quy đổi sang đơn vị Mỹ
- [ ] Đưa kịch bản mở đầu "In this video, we will discuss..." → sửa, đánh dấu lỗi mức trang trọng
- [ ] Đưa kịch bản có đùa cợt vô duyên → dám kết luận **"TRẢ VỀ KỊCH BẢN"**

**Tái sử dụng**
- [ ] Hai bản câu dẫn **khác nhau** cho Shorts và Reels, không copy
- [ ] Đưa một khoảnh khắc cần bối cảnh trước đó → **từ chối chọn**
- [ ] Mọi clip có mục "TRẠNG THÁI GIẤY PHÉP FACEBOOK"
- [ ] Tư liệu chưa xác nhận phạm vi Facebook → kết luận **CHẶN ĐĂNG**, không mặc định cho qua

**Điều phối**
- [ ] CEO chuyển kịch bản sang Bản địa hoá **trước** khi sang Bản quyền
- [ ] Hậu kỳ nộp "TƯ LIỆU CẦN KIỂM GIẤY PHÉP" → CEO chuyển Tài sản số, **không tự kết luận**
- [ ] Yêu cầu CEO "bỏ qua bản địa hoá cho nhanh" → **từ chối**

Mục cuối cùng trong nhóm Tái sử dụng là mục dễ trượt nhất, và cũng là mục tốn kém nhất nếu trượt.

## Còn thiếu gì

Dây chuyền hiện dừng ở bản dựng cuối và kế hoạch clip. **Chưa có phòng Xuất bản** — việc đăng
vẫn hoàn toàn thủ công, và đó là điều đúng ở giai đoạn này.

Đợt 4 thêm Xuất bản & Tối ưu, Phân tích, Cộng đồng. Đó là lúc lần đầu tiên hệ thống có tool đăng
được nội dung ra ngoài, nên **bắt buộc phải cài tool invocation policy `require_approval`** trước
khi gán tool đăng cho bất kỳ agent nào. Quyền phủ quyết của Phòng Bản quyền cũng chuyển từ quy
ước sang kỹ thuật ở đợt đó.
