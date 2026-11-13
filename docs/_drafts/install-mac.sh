#!/bin/bash
# Cài Archestra + dựng công ty 17 agent bằng một lệnh. Chạy trên macOS.
#
#   bash install-mac.sh
#
# Chạy lại nhiều lần được: thứ đã có thì bỏ qua.
set -uo pipefail

RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; BLD=$'\033[1m'; RST=$'\033[0m'
ok(){   echo "${GRN}✅${RST} $*"; }
warn(){ echo "${YEL}⚠️ ${RST} $*"; }
die(){  echo "${RED}❌ $*${RST}"; exit 1; }
step(){ echo; echo "${BLD}── $* ──${RST}"; }

REPO_URL="https://github.com/theanhvtb-jpg/archestra.git"
BRANCH="claude/multi-department-company-ai-agents-ykp3jp"
WORKDIR="${ARCHESTRA_DOCS_DIR:-$HOME/Documents/archestra-docs}"
IMAGE="archestra/platform:latest"
NAME="archestra"

step "1/6 Kiểm tra môi trường"
command -v docker >/dev/null 2>&1 || die "Chưa cài Docker Desktop. Tải tại docker.com rồi chạy lại."
docker info >/dev/null 2>&1 || die "Docker Desktop chưa chạy. Mở ứng dụng Docker (Cmd+Space, gõ Docker), chờ biểu tượng cá voi đứng yên, rồi chạy lại."
ok "Docker đang chạy"

command -v python3 >/dev/null 2>&1 || die "Chưa có python3. Chạy 'xcode-select --install' rồi thử lại."
ok "python3 có sẵn"

AVAIL=$(df -g /System/Volumes/Data 2>/dev/null | tail -1 | awk '{print $4}')
if [ -n "${AVAIL:-}" ]; then
  if [ "$AVAIL" -lt 20 ]; then
    die "Chỉ còn ${AVAIL}GB trống, cần ít nhất 20GB. Dọn ổ đĩa rồi chạy lại."
  fi
  ok "Còn ${AVAIL}GB trống"
fi

step "2/6 Tải image (4.4GB, có thể lâu)"
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  ok "Image đã có sẵn"
else
  for i in 1 2 3; do
    docker pull "$IMAGE" && break
    [ "$i" = 3 ] && die "Tải thất bại sau 3 lần. Kiểm tra mạng và dung lượng đĩa."
    warn "Lần $i thất bại, thử lại sau 10 giây..."
    sleep 10
  done
  ok "Đã tải xong"
fi

wait_ready() {
  for _ in $(seq 1 90); do
    code=$(curl -s -o /dev/null --max-time 5 -w "%{http_code}" http://localhost:9000/api/agents 2>/dev/null)
    case "$code" in 401|200) return 0;; esac
    docker ps -q --filter "name=^${NAME}$" | grep -q . || return 1
    sleep 5
  done
  return 1
}

step "3/6 Khởi động Archestra"
if docker ps -q --filter "name=^${NAME}$" | grep -q . && wait_ready; then
  ok "Đã chạy sẵn"
else
  docker rm -f "$NAME" >/dev/null 2>&1
  echo "   thử chế độ đầy đủ (có Kubernetes cho MCP server)..."
  docker run -d --name "$NAME" -p 9000:9000 -p 3000:3000 \
    -e ARCHESTRA_QUICKSTART=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v archestra-postgres-data:/var/lib/postgresql/data \
    -v archestra-app-data:/app/data \
    "$IMAGE" >/dev/null 2>&1

  if wait_ready; then
    ok "Chạy ở chế độ đầy đủ"
  else
    warn "Không dựng được cụm Kubernetes — chuyển sang chế độ gọn (vẫn đủ dùng)"
    docker logs "$NAME" 2>&1 | grep -iE "failed to create cluster|error" | head -2
    docker rm -f "$NAME" >/dev/null 2>&1
    docker volume rm archestra-postgres-data archestra-app-data >/dev/null 2>&1
    docker run -d --name "$NAME" -p 9000:9000 -p 3000:3000 \
      -v archestra-postgres-data:/var/lib/postgresql/data \
      -v archestra-app-data:/app/data \
      "$IMAGE" >/dev/null 2>&1
    wait_ready || { docker logs "$NAME" 2>&1 | tail -15; die "Không khởi động được. Log ở trên."; }
    ok "Chạy ở chế độ gọn"
  fi
fi

step "4/6 Lấy bộ tài liệu"
if [ -d "$WORKDIR/.git" ]; then
  git -C "$WORKDIR" fetch origin "$BRANCH" --quiet 2>/dev/null
  git -C "$WORKDIR" checkout "$BRANCH" --quiet 2>/dev/null
  git -C "$WORKDIR" pull origin "$BRANCH" --quiet 2>/dev/null
  ok "Đã cập nhật: $WORKDIR"
else
  git clone --quiet "$REPO_URL" "$WORKDIR" || die "Không tải được mã nguồn. Kiểm tra mạng."
  git -C "$WORKDIR" checkout "$BRANCH" --quiet || die "Không thấy nhánh $BRANCH"
  ok "Đã tải về: $WORKDIR"
fi

step "5/6 Dựng 17 agent"
cd "$WORKDIR/docs/_drafts" || die "Không thấy thư mục tài liệu"
python3 bootstrap.py --apply || die "bootstrap.py thất bại. Dán thông báo lỗi ở trên để được hỗ trợ."

step "6/6 Xong"
echo
echo "  ${BLD}Mở giao diện:${RST}  http://localhost:3000"
echo "  ${BLD}Đăng nhập:${RST}     admin@example.com / password"
echo "  ${RED}${BLD}Đổi mật khẩu này ngay sau khi vào.${RST}"
echo
echo "  Việc tiếp theo:"
echo "    1. Nạp dữ liệu vào Knowledge Base — không ai làm thay được"
echo "    2. Nạp khoá OpenRouter tại http://localhost:3000/llm/model-providers/api-keys"
echo "    3. python3 test-agent-prompts.py   (kiểm agent có từ chối đúng chỗ không)"
echo
echo "  Tắt:      docker stop $NAME"
echo "  Chạy lại: docker start $NAME"
