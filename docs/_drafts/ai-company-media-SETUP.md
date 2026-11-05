# Chuẩn bị hạ tầng — cần gì trước khi import

Trả lời hai câu hỏi hay gặp: **lấy URL và API key ở đâu**, và **cần những tool gì**.

---

## 1. Hai lớp khoá API khác nhau — đừng nhầm

Đây là chỗ hay nhầm nhất khi bắt đầu.

| | **Khoá nhà cung cấp LLM** | **Khoá API Archestra** |
|---|---|---|
| Là gì | Khoá của OpenRouter, Anthropic, OpenAI… | Khoá do chính Archestra của bạn cấp |
| Để làm gì | Cho agent **suy nghĩ** | Cho script **gọi vào Archestra** |
| Lấy ở đâu | Trang của nhà cung cấp đó | `/llm/model-providers/api-keys` |
| Dùng ở đâu | Nhập vào Archestra một lần | Biến `ARCHESTRA_API_KEY` trong script |
| Tạo tại | — | `/settings/api-keys` |

**OpenRouter và Claude thuộc lớp thứ nhất.** Chúng cung cấp *mô hình*, không cung cấp *tool*.
Hai thứ này ở hai tầng khác nhau:

```
  Nhà cung cấp LLM  →  bộ não  →  agent suy nghĩ, viết, phán đoán
  MCP server        →  bàn tay →  agent đọc số liệu, tra sổ, đăng video
```

Không thể "lấy tool từ OpenRouter". Nhưng **có thể** dùng OpenRouter làm nhà cung cấp mô hình cho
toàn bộ 17 agent — điều đó hoàn toàn ổn, và còn tiện vì đổi model giữa các agent dễ hơn.

Gợi ý phân bổ model theo vai trò, khi đã có OpenRouter:

| Nhóm agent | Nên dùng | Vì sao |
|---|---|---|
| Kịch bản, Packaging, Bản địa hoá | Model mạnh nhất | Đây là nơi chất lượng đầu ra quyết định kết quả kinh doanh |
| Bản quyền, Phân tích | Model mạnh | Sai ở đây tốn kém |
| CEO, các giám đốc | Model trung bình | Việc chính là định tuyến, không phải sáng tạo |
| Tài sản số, Cộng đồng, Xuất bản | Model rẻ | Việc lặp, khuôn mẫu rõ |

Archestra có sẵn cơ chế tối ưu chi phí ở `/llm/cost/optimization-rules` — làm sau, khi đã chạy ổn.

---

## 2. Địa chỉ Archestra

Tuỳ cách bạn cài:

| Cách cài | Backend (dùng cho script) | Giao diện |
|---|---|---|
| Docker quickstart | `http://localhost:9000` | `http://localhost:3000` |
| Helm / Kubernetes | host bạn expose, cổng 9000 | host bạn expose, cổng 3000 |

Script trong bộ tài liệu này mặc định `http://localhost:9000`, đổi bằng `--base-url`.

### Tạo khoá API Archestra

1. Mở giao diện → **Settings → API Keys** (`/settings/api-keys`)
2. Tạo khoá mới, **sao chép ngay** — thường chỉ hiện một lần
3. Đặt vào biến môi trường:

```bash
export ARCHESTRA_API_KEY='khoa-cua-ban'
```

Kiểm tra thông được:

```bash
curl -s http://localhost:9000/api/agents -H "Authorization: $ARCHESTRA_API_KEY" | head -c 200
```

> Lưu ý định dạng header: Archestra dùng `Authorization: <khoá>` **không có chữ `Bearer`** cho
> khoá API. Đây là khác biệt so với phần lớn API khác và là nguyên nhân lỗi 401 phổ biến nhất.

---

## 3. Thật ra cần bao nhiêu tool?

Ít hơn bạn nghĩ nhiều. **12 trong 17 agent không cần tool nào cả** — chúng chỉ cần Knowledge
Base và khả năng suy luận.

| Agent | Tool cần | Trạng thái |
|---|---|---|
| CEO + 5 giám đốc | — | ✅ không cần gì |
| Packaging | — | ✅ không cần gì |
| Kịch bản | — | ✅ không cần gì |
| Bản địa hoá | — | ✅ không cần gì |
| Hậu kỳ | — | ✅ không cần gì |
| Tái sử dụng | — | ✅ không cần gì |
| Bản quyền & Chính sách | — | ✅ không cần gì |
| **Giám đốc Tài chính** | thống kê token | ✅ **đã có sẵn trong Archestra** |
| Nghiên cứu & Ý tưởng | tìm kiếm web, dữ liệu YouTube | ⬜ cần nối |
| Tài sản số | sổ đăng ký tài sản | ⬜ cần nối |
| Phân tích | số liệu YouTube | ⬜ cần nối |
| Xuất bản & Tối ưu | đăng video, sửa metadata | ⬜ cần nối |
| Cộng đồng | đọc bình luận | ⬜ cần nối |

Gộp lại chỉ còn **bốn tích hợp**:

1. **Tìm kiếm web** — cho Nghiên cứu. Có nhiều MCP server sẵn trong registry.
2. **Sổ đăng ký tài sản** — một bảng tính hoặc cơ sở dữ liệu. Dùng MCP server tương ứng.
3. **YouTube Data API** — đọc bình luận, đăng video, sửa metadata.
4. **YouTube Analytics API** — số liệu giữ chân, CTR, thời lượng xem.

Mục 3 và 4 có thể chưa có MCP server sẵn trong registry; nếu vậy phải tự viết. Đó là phần việc
nặng nhất, nhưng cũng là phần **làm sau cùng** — xem thứ tự dưới.

### Tool có sẵn, không phải nối gì

Archestra tự đăng ký sẵn một bộ tool nội bộ với tiền tố `archestra__`. Đáng chú ý cho mô hình này:

| Tool | Dùng cho |
|---|---|
| `archestra__get_agent_token_usage` | Chi phí token theo từng agent — CFO dùng |
| `archestra__get_limits` | Trần ngân sách đang đặt — CFO dùng |
| `archestra__query_knowledge_sources` | Tra cứu Knowledge Base |

File `05-cfo.json` đã dùng sẵn hai tool đầu, **không còn placeholder**.

---

## 4. Thứ tự nên làm

Quan trọng: **bạn chạy được Đợt 0 mà chưa cần tích hợp YouTube nào.**

| Bước | Cần gì | Chạy được phần nào |
|---|---|---|
| 1 | Cài Archestra + khoá LLM provider | — |
| 2 | Tạo KB, nạp dữ liệu | — |
| 3 | Import CEO + Packaging | **Packaging chạy đầy đủ** (không cần tool) |
| 4 | Nối tìm kiếm web | Nghiên cứu chạy được |
| 5 | Import Đợt 2–3 | Kịch bản, Bản địa hoá, Hậu kỳ chạy đầy đủ |
| 6 | Nối sổ tài sản (bảng tính) | Tài sản số chạy được |
| 7 | Nối YouTube API | Phân tích, Cộng đồng, Xuất bản chạy được |
| 8 | Chạy `setup-policies.py` **trước khi** gán tool đăng | Khoá kỹ thuật |

**Bước 3 là mốc đáng để tới sớm.** Phòng Packaging — phòng tạo giá trị lớn nhất trong cả thiết
kế — không cần một tool nào. Bạn có thể kiểm chứng ý tưởng cốt lõi của mô hình chỉ với một khoá
LLM provider và một Knowledge Base.

Đừng chờ nối xong YouTube API mới bắt đầu.

---

## 5. Liên quan

- [Mục lục](./ai-company-INDEX.md)
- [Đợt 0 — ba agent đầu](./ai-company-media-phase0/README.md)
