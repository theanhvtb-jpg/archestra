#!/usr/bin/env python3
"""Nạp lại agent sau khi sửa prompt: xoá bản cũ -> import bản mới -> nối lại sơ đồ.

Import của Archestra LUÔN tạo agent mới, không ghi đè. Nên muốn cập nhật prompt
thì phải xoá bản cũ trước, nếu không sẽ có hai bản trùng tên.
Và xoá agent là mất mọi liên kết uỷ quyền của nó, nên phải nối lại sơ đồ.

  python3 reimport-agent.py --agent "Phong Ban quyen & Chinh sach"
  python3 reimport-agent.py --agent "GD Tuan thu" --agent "Phong Ban quyen & Chinh sach" --apply

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
    p.add_argument("--skip-wire", action="store_true", help="Không nối lại sơ đồ sau khi import")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    B = a.base_url

    print("=" * 62)
    print("NẠP LẠI AGENT" + ("" if a.apply else "  —  XEM TRƯỚC (chưa thay đổi gì)"))
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
        state = "xoá rồi import lại" if old_id else "chưa có — chỉ import"
        print(f"  · {name}")
        print(f"      từ file : {os.path.relpath(f, HERE)}")
        print(f"      thao tác: {state}")
    if not a.skip_wire:
        print("\n  · Nối lại toàn bộ sơ đồ tổ chức (wire-org.py)")
        print("    — bắt buộc, vì xoá agent làm mất mọi liên kết uỷ quyền của nó")

    if not a.apply:
        print("\nChạy lại với --apply để thực thi.")
        return

    print()
    for name, f, old_id in plan:
        if old_id:
            _, err = call(B, "DELETE", f"/api/agents/{old_id}", key=key)
            if err:
                print(f"  ❌ không xoá được '{name}': {err[:140]}")
                continue
            print(f"  🗑  đã xoá bản cũ: {name}")
        payload = json.load(open(f, encoding="utf-8"))
        d, err = call(B, "POST", "/api/agents/import", payload, key=key)
        if err:
            print(f"  ❌ import '{name}' thất bại: {err[:140]}")
            continue
        warns = (d or {}).get("warnings") or []
        print(f"  ✅ đã import: {name}" + (f"  ({len(warns)} warning)" if warns else ""))

    if a.skip_wire:
        print("\n⚠️  Bỏ qua nối sơ đồ — nhớ chạy wire-org.py --apply, nếu không agent vừa nạp sẽ mồ côi.")
        return

    print("\nNối lại sơ đồ tổ chức:")
    wire = os.path.join(HERE, "ai-company-media-wave5", "wire-org.py")
    env = dict(os.environ, ARCHESTRA_API_KEY=key)
    r = subprocess.run([sys.executable, "-I", wire, "--base-url", B, "--apply",
                        "--ceo-prompt", "06-ceo-prompt-v5.txt"],
                       cwd=os.path.dirname(wire), env=env, capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("✓") or "⚠️" in line or "DỪNG" in line:
            print(f"  {line}")
    if r.returncode != 0:
        print(f"  ❌ wire-org.py lỗi:\n{(r.stderr or r.stdout)[-400:]}")
        sys.exit(1)

    print("\nXong. Kiểm chứng: Agents trong giao diện — cột Subagents của CEO phải là 5.")


if __name__ == "__main__":
    main()
