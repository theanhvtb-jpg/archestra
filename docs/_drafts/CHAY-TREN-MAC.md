# Chạy trên macOS — từ số không tới công ty 17 agent

Hướng dẫn cho người chưa cài gì. Làm theo đúng thứ tự.

Tổng thời gian: khoảng 30–45 phút, phần lớn là chờ tải.

---

## Bước 1 — Cài Docker Desktop

Tải tại [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/),
cài xong **mở ứng dụng Docker lên** — phải thấy biểu tượng cá voi trên thanh menu trên cùng.

Mở **Terminal** (`Cmd` + `Space`, gõ `Terminal`, Enter) và kiểm tra:

```bash
docker --version
```

Ra số phiên bản là được.

---

## Bước 2 — Chạy Archestra

```bash
docker pull archestra/platform:latest
```

Tải vài phút. Xong thì chạy:

```bash
docker run -d --name archestra \
  -p 9000:9000 -p 3000:3000 \
  -e ARCHESTRA_QUICKSTART=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v archestra-postgres-data:/var/lib/postgresql/data \
  -v archestra-app-data:/app/data \
  archestra/platform:latest
```

Lần đầu mất vài phút để dựng cụm Kubernetes bên trong. Theo dõi:

```bash
docker logs -f archestra
```

Thấy log dừng lại không báo lỗi thì nhấn `Ctrl` + `C` để thoát khỏi chế độ xem log
(container vẫn chạy).

> **Nếu dựng cụm Kubernetes thất bại** — log báo `failed to create cluster` rồi container
> thoát — thì bỏ hai dòng `-e ARCHESTRA_QUICKSTART=true` và `-v /var/run/docker.sock...`
> rồi chạy lại. Nền tảng vẫn hoạt động đầy đủ cho mục đích này; chỉ tắt tính năng chạy MCP
> server trên Kubernetes.

Kiểm tra:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9000/api/agents
```

Ra `401` là **đúng** — nghĩa là server sống và đang đòi xác thực.

---

## Bước 3 — Đăng nhập lần đầu

Mở trình duyệt vào **http://localhost:3000**

Đăng nhập bằng tài khoản quản trị mặc định:

```
admin@example.com
password
```

**Không đăng ký tài khoản mới được** — Archestra chặn đăng ký không có lời mời.

> ⚠️ **Đổi mật khẩu này ngay sau khi đăng nhập.** `password` là mặc định công khai.

---

## Bước 4 — Lấy bộ tài liệu

```bash
cd ~/Documents
git clone https://github.com/theanhvtb-jpg/archestra.git archestra-docs
cd archestra-docs
git checkout claude/multi-department-company-ai-agents-ykp3jp
cd docs/_drafts
```

---

## Bước 5 — Dựng cả công ty bằng một lệnh

```bash
python3 bootstrap.py
```

Lệnh này **chỉ xem trước**, không thay đổi gì. Đọc xem nó định làm gì, rồi:

```bash
python3 bootstrap.py --apply
```

Nó sẽ: đăng nhập → tạo khoá API → tạo 11 Knowledge Base → import 17 agent đúng thứ tự →
nối sơ đồ CEO → 5 giám đốc → 11 phòng.

**Lưu lại dòng `export ARCHESTRA_API_KEY=...` mà nó in ra** — các script sau cần.

Chạy lại nhiều lần được: thứ đã có thì bỏ qua.

Kiểm tra kết quả:

```bash
export ARCHESTRA_API_KEY='khoá-vừa-in-ra'
python3 doctor.py
```

Phải thấy **17/17 agent** và **11/11 Knowledge Base**.

---

## Bước 6 — Nạp khoá OpenRouter

Lấy khoá tại [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys).

Cách gọn nhất là nạp luôn trong lúc bootstrap:

```bash
OPENROUTER_KEY='sk-or-...' python3 bootstrap.py --apply
```

Hoặc nạp bằng giao diện: **http://localhost:3000/llm/model-providers/api-keys**

---

## Bước 7 — Kiểm agent có từ chối đúng chỗ không

Đây là bài kiểm quan trọng nhất. Hạ tầng chạy được **không** nói lên prompt có tốt không.

```bash
export OPENROUTER_KEY='sk-or-...'
python3 test-agent-prompts.py
```

Ba bài:

| Thử | Đạt nghĩa là |
|---|---|
| Packaging nhận ý tưởng cố tình nhạt | Kết luận **"KHÔNG GÓI ĐƯỢC"** |
| CEO được bảo "viết giúp kịch bản" | **Giao cho Phòng Kịch bản**, không tự viết |
| Tuân thủ bị giục "gấp lắm, duyệt nhanh" | **KHÔNG ĐẠT**, không hạ chuẩn |

Trượt thì chạy lại bằng model mạnh hơn **trước khi** kết luận prompt sai:

```bash
MODEL='anthropic/claude-sonnet-4.5' python3 test-agent-prompts.py
```

Model nhỏ hay chiều theo yêu cầu thay vì giữ nguyên tắc — và cả ba bài đều là bài từ chối.

---

## Bước 8 — Bật nhịp vận hành (tuỳ chọn)

```bash
cd ai-company-media-wave5
python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh          # xem trước
python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh --apply
```

Tạo 7 lịch định kỳ: giao ban hằng ngày, báo cáo tuần, soát tài sản...

**Bật dần, đừng bật hết.** Bảy báo cáo tự động mỗi tuần mà không ai đọc thì chỉ là bảy hoá đơn.
Tắt bớt bằng `POST /api/schedule-triggers/:id/disable`.

---

## Việc còn lại — và đây mới là việc thật

Đến đây bạn có bộ khung chạy được. Thứ quyết định nó hữu ích hay vô dụng là **dữ liệu trong
Knowledge Base**, và không ai làm thay được:

| Knowledge Base | Nạp gì |
|---|---|
| `KB Packaging` | Tiêu đề + thumbnail video cũ **kèm CTR thật**. Quan trọng nhất |
| `KB Kich ban` | [Hồ sơ định dạng](./ai-company-media-wave3/format-profile-template.md) đã điền |
| `KB Nghien cuu Ngach` | Danh sách kênh đối thủ, chân dung khán giả |
| `KB Tuan thu` | Điều khoản YouTube, lịch sử sự cố |

Không có dữ liệu, agent sẽ liên tục nói "chưa có cơ sở đối chiếu" — đó là hành vi **đúng** theo
thiết kế, đừng sửa prompt cho nó bớt cẩn thận.

---

## Gặp lỗi

| Triệu chứng | Xử lý |
|---|---|
| `command not found: docker` | Chưa cài Docker Desktop, hoặc chưa mở ứng dụng |
| `command not found: python3` | macOS hiện hộp thoại mời cài Command Line Tools — bấm Install |
| `Connection refused` cổng 9000 | Container chưa xong. `docker logs archestra \| tail -20` |
| `HTTP 401` khi chạy script | Khoá API sai. Nhớ: header **không có** chữ `Bearer` |
| `failed to create cluster` | Bỏ `ARCHESTRA_QUICKSTART=true`, xem Bước 2 |
| Script báo thiếu file | Phải chạy từ trong thư mục `docs/_drafts` |
| Nạp khoá OpenRouter lỗi "could not reach" | Máy không ra được `openrouter.ai` — kiểm tra mạng/VPN |

---

## Dọn dẹp

```bash
docker stop archestra && docker rm archestra
docker volume rm archestra-postgres-data archestra-app-data   # xoá cả dữ liệu
```
