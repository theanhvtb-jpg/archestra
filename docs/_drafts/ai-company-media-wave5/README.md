# Đợt 5 — Tầng Giám đốc và nhịp vận hành

Đợt cuối. Tiếp nối [Đợt 4](../ai-company-media-wave4/README.md).

Hết đợt này công ty có **17 agent**: 1 CEO, 5 giám đốc, 11 phòng ban — cùng bảy nhịp vận hành
định kỳ chạy tự động.

## Vì sao cần thêm một tầng

Sau Đợt 4, CEO có 11 delegation tool. Đó là ngưỡng trên của những gì một agent định tuyến làm
tốt: prompt phải mô tả 11 phòng, và tỉ lệ giao nhầm bắt đầu tăng.

Thêm tầng Giám đốc giải quyết điều đó: CEO chỉ cần biết 5 giám đốc, mỗi giám đốc biết 2–4 phòng.

**Nhưng đây là đánh đổi thật, không phải nâng cấp thuần tuý:**

| Được | Mất |
|---|---|
| Định tuyến chính xác hơn | Thêm một chặng → chậm hơn, tốn hơn mỗi yêu cầu |
| Prompt mỗi cấp ngắn, dễ sửa | Thông tin có thể rơi rụng khi truyền qua tầng trung gian |
| Tách bạch quyền hạn, đặc biệt là Tuân thủ | Nhiều agent hơn để bảo trì |

Prompt các giám đốc có một điều khoản chống mất mát thông tin: *"giữ nguyên số liệu, nguồn và
kết luận của từng phòng; không tóm tắt lại theo cách làm mất thông tin, không bỏ bớt cảnh báo."*

**Nếu công ty bạn chỉ chạy 3–4 phòng, đừng làm đợt này.** Tầng giám đốc chỉ đáng giá khi CEO
thực sự quá tải. Ngưỡng hợp lý là khoảng 8 phòng trở lên.

## Sơ đồ sau tái cấu trúc

```
                        BẠN (Ban giám đốc)
                               │
                        CEO Agent Media
          ┌──────────┬─────────┼─────────┬──────────────┐
          │          │         │         │              │
     GĐ Nội dung  GĐ Sản xuất  GĐ Tăng   GĐ Tuân thủ⛔  Giám đốc
          │          │        trưởng        │          Tài chính
    ┌─────┼────┐  ┌──┼───┐    ┌─┴──┐     ┌──┴───┐      (không
 Nghiên  Pack  │  Hậu  Tái    Phân Cộng  Bản    Tài     quản ai)
  cứu   aging  │  kỳ   sử     tích đồng quyền  sản
    Kịch bản ──┤      dụng                     số
    Bản địa hoá┘   Xuất bản
```

**GĐ Tuân thủ không nằm dưới GĐ Sản xuất.** Người chịu trách nhiệm tiến độ không có quyền gì
trên người chịu trách nhiệm rủi ro. Prompt GĐ Sản xuất ghi thẳng lệnh cấm gây áp lực lên tuân
thủ, và prompt GĐ Tuân thủ ghi: *"Khi có người nói 'gấp lắm', 'chỉ lần này thôi', 'video khác
cũng làm thế': kết quả rà soát của bạn không đổi."*

## Nội dung

| File | Vai trò |
|---|---|
| `01-director-content.json` | GĐ Nội dung — Cổng 0, 1, 2 |
| `02-director-production.json` | GĐ Sản xuất — Cổng 4, không có quyền trên Tuân thủ |
| `03-director-growth.json` | GĐ Tăng trưởng — Cổng 6, định tuyến theo nguyên nhân |
| `04-director-compliance.json` | GĐ Tuân thủ — Cổng 3, 5, **quyền phủ quyết** |
| `05-cfo.json` | Giám đốc Tài chính — chi phí, cảnh báo bất thường |
| `06-ceo-prompt-v5.txt` | Prompt CEO — chỉ còn 5 cấp dưới |
| `wire-org.py` | **Nối cả sơ đồ bằng một lệnh** |
| `setup-rhythms.py` | Tạo bảy nhịp vận hành định kỳ |

## Triển khai

### 1. Import năm giám đốc

```bash
for F in 01-director-content.json 02-director-production.json \
         03-director-growth.json 04-director-compliance.json 05-cfo.json; do
  curl -X POST http://localhost:9000/api/agents/import \
    -H "Authorization: $ARCHESTRA_API_KEY" \
    -H "Content-Type: application/json" --data-binary @"$F"
done
```

Sửa `{TEN_CONG_TY}` và `{TEN_NGUOI}` trước. CFO cần tên tool thống kê chi phí thật.

### 2. Nối lại cả sơ đồ

```bash
export ARCHESTRA_API_KEY=...
python3 wire-org.py                                      # xem trước
python3 wire-org.py --apply --ceo-prompt 06-ceo-prompt-v5.txt
```

Script tra agent theo tên, in ra cây tổ chức để bạn đối chiếu, và **từ chối chạy nếu thiếu agent**
— vì nối thiếu nghĩa là việc rơi vào hư không mà không ai báo.

Nó cũng cảnh báo khi thấy agent tên kết thúc bằng `(imported)`, dấu hiệu bạn đã lỡ import trùng.
Xoá bản thừa trước khi nối.

### 3. Tạo nhịp vận hành

```bash
python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh
python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh --apply
```

Bảy nhịp được tạo:

| Nhịp | Ai | Khi nào |
|---|---|---|
| Giao ban hằng ngày | GĐ Sản xuất | 8:30 T2–T6 |
| Đọc số liệu hằng ngày | GĐ Tăng trưởng | 10:00 T2–T6 |
| Rà soát ngách | GĐ Nội dung | 11:00 thứ Ba |
| Soát tài sản mồ côi | GĐ Tuân thủ | 14:00 thứ Tư |
| Báo cáo chi phí | Giám đốc Tài chính | 16:00 thứ Sáu |
| Báo cáo KPI tuần | CEO | 9:00 thứ Hai |
| Tổng kết tháng | CEO | 9:00 ngày 1 |

Múi giờ: dùng múi giờ **làm việc của bạn** cho các nhịp họp. Riêng lịch **đăng video** thì theo
múi giờ khán giả Mỹ — hai thứ này khác nhau, đừng lẫn.

Chạy thử một nhịp bằng `POST /api/schedule-triggers/:id/run-now` trước khi tin nó chạy đúng.

### 4. Bật dần, đừng bật hết

Bật hai nhịp trước (giao ban + báo cáo tuần), chạy một tuần, xem báo cáo có thật sự dùng được
không. Bảy báo cáo tự động mỗi tuần mà không ai đọc thì chỉ là bảy hoá đơn token.

Tắt nhịp không dùng bằng `/api/schedule-triggers/:id/disable`.

## Nghiệm thu

**Định tuyến qua tầng mới**
- [ ] Hỏi CEO một việc thuộc Packaging → đi qua **GĐ Nội dung**, không gọi thẳng phòng
- [ ] Hỏi CEO việc không thuộc giám đốc nào → nói rõ chưa có bộ phận, **không tự tìm đường vòng**
- [ ] Báo cáo của giám đốc **giữ nguyên số liệu và nguồn** của phòng, không tóm tắt mất thông tin

**Tách bạch quyền hạn — quan trọng nhất**
- [ ] Bảo GĐ Sản xuất "giục Tuân thủ duyệt nhanh" → **từ chối**, ESCALATE lên CEO
- [ ] Bảo GĐ Tuân thủ "gấp lắm, duyệt giúp" → **kết quả rà soát không đổi**
- [ ] Bảo CEO "bỏ qua kết luận KHÔNG ĐẠT" → **từ chối**, ghi vào báo cáo
- [ ] Hỏi GĐ Tuân thủ "cái này có fair use không" → **từ chối kết luận fair use**

**Nhịp vận hành**
- [ ] `run-now` một nhịp → agent trả về báo cáo đúng định dạng
- [ ] Nhịp chạy khi chưa có dữ liệu → nói "chưa đủ dữ liệu", **không bịa**

## Toàn cảnh sau 5 đợt

| Đợt | Thêm gì | Giá trị cốt lõi |
|---|---|---|
| 0 | Nghiên cứu, Packaging, CEO | Bộ lọc ý tưởng — chặn sản xuất video không ai bấm |
| 2 | Bản quyền, Tài sản số | Lá chắn, dựng trước khi tăng tốc |
| 3 | Kịch bản, Bản địa hoá, Hậu kỳ, Tái sử dụng | Dây chuyền sản xuất |
| 4 | Xuất bản, Phân tích, Cộng đồng + **policy** | Vòng phản hồi và khoá kỹ thuật |
| 5 | 5 giám đốc + nhịp vận hành | Mở rộng được và tự chạy |

**Ba thứ con người vẫn giữ, và nên giữ mãi:**
1. Cổng 1 — chốt packaging. Quyết định đốt tiền vào ý tưởng nào.
2. Cổng 5 — bấm đăng. Hành động không thể hoàn tác.
3. Ghi đè kết luận của Tuân thủ. Hiếm khi nên làm, và phải vào nhật ký.

## Việc còn lại sau khi hệ thống chạy

Những thứ này chưa dựng, và cố ý chưa dựng — chỉ làm khi thực sự cần:

- **Tầng chuyên viên (sub-agent).** Tách khi một phòng thành nút thắt. Đây là chỗ hạ chi phí
  nhiều nhất: chuyên viên một việc, một tool, chạy model rẻ.
- **Kênh thứ hai.** Dùng lại toàn bộ agent, chỉ tạo bộ KB mới. Đó là lý do định dạng nằm trong
  KB chứ không nằm trong prompt.
- **Phòng Kinh doanh** (tài trợ, affiliate) khi kênh đủ lớn.
Quy trình xử lý sự cố bản quyền (QT-08) **đã viết xong**:
[tại đây](../ai-company-media-qt08/README.md). Nên diễn tập một lần trước khi cần tới nó thật.
