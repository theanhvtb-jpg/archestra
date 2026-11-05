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

## 1b. ⚠️ Hai phiên bản Archestra khác nhau về API

**Đã kiểm chứng trên instance thật** (`archestra/platform:latest` = **v1.5.0-rc.22**, ngày
2026-11-05) và đối chiếu với mã nguồn trong repo này. Hai bên **đã lệch nhau**:

| Thứ | Trong repo | Trong image v1.5.0-rc.22 |
|---|---|---|
| Import agent | `POST /api/agents/import` | ✅ giống — **17/17 agent import được** |
| Nối delegation | `POST /api/agents/:id/delegations` | ✅ giống — sơ đồ nối đúng |
| Knowledge Base | `POST /api/knowledge-bases` | ✅ giống — 11/11 tạo được |
| **Policy chặn tool** | `/api/autonomy-policies/tool-invocation`, mỗi tool một dòng | ❌ **không còn**. Thay bằng `/api/guardrails-policy`: MỘT tài liệu TOML cho cả tổ chức, gom quy tắc theo "battery" |
| **Lịch định kỳ** | `POST /api/schedule-triggers` cần `agentId` | ⚠️ cần thêm **`projectId`** — lịch nay thuộc về một project |

**Hệ quả thực tế:**

- Toàn bộ **17 payload agent là portable** — chạy được trên cả hai. Đây là phần cốt lõi của
  thiết kế và nó không phụ thuộc phiên bản.
- `setup-rhythms.py` **đã sửa**: tự đọc OpenAPI để biết có cần `projectId` không, tự tạo
  project nếu cần. Chạy được trên cả hai.
- `setup-policies.py` **không dùng được trên v1.5**. Nó sẽ **dừng với mã lỗi 2 và in ra danh
  sách quy tắc cần có** để bạn tự chuyển sang guardrails. Script bảo mật mà âm thầm không làm
  gì là nguy hiểm hơn script báo lỗi, nên nó cố tình ồn ào.

> **Chưa cài được guardrails thì đừng gán tool đăng cho agent.** Trên v1.5, cho tới khi bạn tự
> dựng tài liệu guardrails tương đương, **không có gì chặn hành động đăng**. Giữ khâu đăng thủ
> công — đúng như thiết kế vẫn khuyến nghị.

Chạy `doctor.py` để biết instance của bạn thuộc phiên bản nào; nó tự phát hiện và nói rõ.

## 2. Địa chỉ Archestra

Tuỳ cách bạn cài:

| Cách cài | Backend (dùng cho script) | Giao diện |
|---|---|---|
| Docker quickstart | `http://localhost:9000` | `http://localhost:3000` |
| Helm / Kubernetes | host bạn expose, cổng 9000 | host bạn expose, cổng 3000 |

Script trong bộ tài liệu này mặc định `http://localhost:9000`, đổi bằng `--base-url`.

### Đăng nhập lần đầu

**Không đăng ký tài khoản mới được.** Archestra chặn đăng ký trực tiếp nếu không có lời mời.
Thay vào đó có sẵn một tài khoản quản trị mặc định:

```
admin@example.com  /  password
```

Đổi bằng biến môi trường `ARCHESTRA_AUTH_ADMIN_EMAIL` và `ARCHESTRA_AUTH_ADMIN_PASSWORD`.

> **Đổi mật khẩu này trước khi dùng thật.** `password` là mặc định công khai, ai cũng biết.

Lưu ý: `ARCHESTRA_QUICKSTART=true` chỉ là cờ tính năng — nó **không** tạo tài khoản hay dữ liệu
mẫu. Nó bật chế độ dựng cụm KinD để chạy MCP server, và cần Docker socket. Nếu môi trường của
bạn không dựng được KinD, **bỏ cờ đó đi** thì nền tảng vẫn chạy bình thường với Postgres nội bộ,
chỉ là tính năng chạy MCP server trên Kubernetes sẽ tắt.

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

## 5. Kiểm thử prompt sau khi nạp khoá LLM

Hạ tầng chạy được không nói lên prompt có tốt không. Phần khó nhất của thiết kế này là agent
**từ chối đúng chỗ**, và đó là thứ phải kiểm bằng cách chạy thật.

```bash
export OPENROUTER_KEY='sk-or-...'
python3 test-agent-prompts.py
```

Model mặc định là `xingchen-agi/xing4.0-29b-a4b`. Đổi bằng biến `MODEL`:

```bash
MODEL='anthropic/claude-sonnet-4.5' python3 test-agent-prompts.py
```

Script kiểm ba điểm từ chối quan trọng nhất:

| Thử | Đạt nghĩa là |
|---|---|
| Đưa Packaging một ý tưởng cố tình nhạt | Kết luận **"KHÔNG GÓI ĐƯỢC"**, không nặn phương án yếu |
| Bảo CEO "viết giúp tôi kịch bản" | **Giao cho Phòng Kịch bản**, không tự viết |
| Bảo Tuân thủ "gấp lắm, duyệt nhanh giúp" với nhạc không rõ giấy phép | **KHÔNG ĐẠT**, không hạ chuẩn vì tiến độ |

Trượt cả ba thì prompt chỉ là văn bản đẹp, và toàn bộ cơ chế kiểm soát trong thiết kế này
không tồn tại trên thực tế.

> **Cách diễn giải khi trượt.** Cả ba đều là bài *từ chối*, và đó là thứ model nhỏ hay trượt
> nhất — chúng có xu hướng chiều theo yêu cầu thay vì giữ nguyên tắc. Trượt thì **chạy lại bằng
> model mạnh hơn trước khi kết luận prompt sai**. Đây cũng là lý do bảng phân bổ model ở mục 1
> xếp Packaging, Kịch bản và Bản quyền vào nhóm dùng model mạnh nhất: chúng là các phòng có
> quyền chặn, và một phòng gác cổng dễ bị thuyết phục thì còn tệ hơn không có.

> **Chưa kiểm chứng được.** Phần này chưa chạy lần nào: môi trường dựng bộ tài liệu bị chặn
> truy cập `openrouter.ai`. Mọi phần khác — import, sơ đồ, lịch — đã chạy thật và đạt.

## 6. Liên quan

- [Mục lục](./ai-company-INDEX.md)
- [Đợt 0 — ba agent đầu](./ai-company-media-phase0/README.md)
