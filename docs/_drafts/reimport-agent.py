#!/usr/bin/env python3
"""Cập nhật prompt của agent từ file payload, TẠI CHỖ.

Sửa prompt KHÔNG cần xoá agent. Xoá rồi import lại là cách sai: nó bỏ lại tool
uỷ quyền mồ côi (agent__*) khiến việc nối lại sơ đồ đụng lỗi 409, và làm mất
mọi tool đã gán cho agent đó.

Script này gửi PUT lên agent đang có, nên ID, liên kết uỷ quyền và tool giữ nguyên.
Agent chưa tồn tại thì mới import mới.

  python3 reimport-agent.py --agent "Phong Chinh sach Noi dung"
  python3 reimport-agent.py --agent "GD Tuan thu" --agent "Phong Chinh sach Noi dung" --apply

Mặc định chỉ xem trước. Mật khẩu quản trị: ARCHESTRA_ADMIN_PASSWORD.
"""
import argparse, glob, json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def call(base, method, path, payload=None, key=None):
    req = urllib.request.Request(base.rstrip("/") + path,
        data=json.dumps(payload).encode() if payload is not None else None, method=method)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if key:
        req.add_header("Authorization", key)
    try:
        with op.open(req, timeout=120) as r:
            return json.loads(r.read() or b"{}"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:220]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def rows(d):
    if d is None: return []
    if isinstance(d, list): return d
    for k in ("data", "items", "results"):
        if isinstance(d.get(k), list): return d[k]
    return []


def get_key(base):
    k = os.environ.get("ARCHESTRA_API_KEY")
    if k:
        try: k.encode("ascii")
        except UnicodeEncodeError:
            sys.exit("ARCHESTRA_API_KEY chứa ký tự tiếng Việt — có vẻ bạn dán chỗ trống ví dụ.")
        return k
    email = os.environ.get("ARCHESTRA_ADMIN_EMAIL", "admin@example.com")
    pw = os.environ.get("ARCHESTRA_ADMIN_PASSWORD", "password")
    _, err = call(base, "POST", "/api/auth/sign-in/email", {"email": email, "password": pw})
    if err:
        sys.exit(f"Không đăng nhập được bằng {email}.\n"
                 "  Đã đổi mật khẩu? Chạy lại kèm:\n"
                 "    ARCHESTRA_ADMIN_PASSWORD='mật-khẩu' python3 reimport-agent.py ...")
    d, err = call(base, "POST", "/api/api-keys", {"name": "reimport-" + uuid.uuid4().hex[:6]})
    if err or not (d or {}).get("key"):
        sys.exit(f"Không tạo được khoá API: {err}")
    print(f"(tự tạo khoá API: {d['key'][:14]}...)\n")
    return d["key"]


def find_payload(agent_name):
    """Tìm file payload chứa agent có đúng tên này."""
    for f in sorted(glob.glob(os.path.join(HERE, "ai-company-media-*", "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if d.get("agent", {}).get("name") == agent_name:
            return f
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:9000")
    p.add_argument("--agent", action="append", default=[], required=True,
                   help="Tên agent cần nạp lại. Lặp lại để làm nhiều agent.")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    B = a.base_url

    print("=" * 62)
    print("CẬP NHẬT PROMPT AGENT" + ("" if a.apply else "  —  XEM TRƯỚC (chưa thay đổi gì)"))
    print("=" * 62)

    key = get_key(B)
    d, err = call(B, "GET", "/api/agents", key=key)
    if err: sys.exit(f"Không đọc được danh sách agent: {err}")
    existing = {x["name"]: x["id"] for x in rows(d) if x.get("agentType") == "agent"}

    plan = []
    for name in a.agent:
        f = find_payload(name)
        if not f:
            print(f"❌ Không thấy file payload cho agent '{name}'.")
            print("   Chạy script này từ trong thư mục docs/_drafts.")
            sys.exit(1)
        plan.append((name, f, existing.get(name)))

    print("Sẽ làm:")
    for name, f, old_id in plan:
        state = "cập nhật prompt tại chỗ" if old_id else "chưa có — import mới"
        print(f"  · {name}")
        print(f"      từ file : {os.path.relpath(f, HERE)}")
        print(f"      thao tác: {state}")
    print("\n  Liên kết uỷ quyền và tool đã gán được giữ nguyên.")

    if not a.apply:
        print("\nChạy lại với --apply để thực thi.")
        return

    print()
    done = 0
    for name, f, old_id in plan:
        payload = json.load(open(f, encoding="utf-8"))
        ag = payload["agent"]
        if old_id:
            # Cập nhật TẠI CHỖ. Giữ nguyên ID, liên kết uỷ quyền và tool đã gán.
            body = {"systemPrompt": ag.get("systemPrompt"),
                    "description": ag.get("description"),
                    "icon": ag.get("icon")}
            body = {k: v for k, v in body.items() if v is not None}
            _, err = call(B, "PUT", f"/api/agents/{old_id}", body, key=key)
            if err:
                print(f"  ❌ {name}: {err[:160]}")
                continue
            done += 1
            print(f"  ✅ đã cập nhật tại chỗ: {name}  ({len(ag.get('systemPrompt') or '')} ký tự)")
        else:
            d, err = call(B, "POST", "/api/agents/import", payload, key=key)
            if err:
                print(f"  ❌ import '{name}' thất bại: {err[:160]}")
                continue
            done += 1
            warns = (d or {}).get("warnings") or []
            print(f"  ✅ đã import mới: {name}" + (f"  ({len(warns)} warning)" if warns else ""))

    print(f"\nXong {done}/{len(plan)} agent.")
    print("Liên kết uỷ quyền và tool đã gán được giữ nguyên — không cần nối lại sơ đồ.")
    print("Kiểm chứng: Agents trong giao diện, cột Subagents của CEO vẫn phải là 5.")


if __name__ == "__main__":
    main()
