#!/usr/bin/env python3
"""Gán tool của MCP server cho một agent.

Cài MCP server KHÔNG tự cho agent dùng tool — phải gán riêng cho từng agent.
Đây là chủ ý: mỗi phòng chỉ có đúng công cụ nó cần.

  # Xem có tool gì và agent nào
  python3 assign-tool.py --list

  # Gán (xem trước)
  python3 assign-tool.py --tool duckduck --agent "Phong Nghien cuu & Y tuong"

  # Gán thật
  python3 assign-tool.py --tool duckduck --agent "Phong Nghien cuu & Y tuong" --apply
"""
import argparse, json, os, sys, urllib.request, urllib.error


def call(base, key, method, path, payload=None):
    req = urllib.request.Request(base.rstrip("/") + path,
        data=json.dumps(payload).encode() if payload is not None else None, method=method)
    req.add_header("Authorization", key)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:250]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def rows(d):
    if d is None: return []
    if isinstance(d, list): return d
    for k in ("data", "items", "results"):
        if isinstance(d.get(k), list): return d[k]
    return []


def _auto_key(base):  # AUTO_KEY_MARKER
    """Không có ARCHESTRA_API_KEY thì tự đăng nhập bằng tài khoản quản trị
    và tạo khoá. Bỏ hẳn bước copy-dán khoá, vốn là chỗ hay vấp nhất."""
    import http.cookiejar, json as _j, os as _o, sys as _s, urllib.request as _u, uuid as _uu
    email = _o.environ.get("ARCHESTRA_ADMIN_EMAIL", "admin@example.com")
    pw = _o.environ.get("ARCHESTRA_ADMIN_PASSWORD", "password")
    cj = http.cookiejar.CookieJar()
    op = _u.build_opener(_u.HTTPCookieProcessor(cj))
    def post(path, payload):
        r = _u.Request(base.rstrip("/") + path, data=_j.dumps(payload).encode(), method="POST")
        r.add_header("Content-Type", "application/json")
        return _j.loads(op.open(r, timeout=60).read() or b"{}")
    try:
        post("/api/auth/sign-in/email", {"email": email, "password": pw})
    except Exception:
        _s.exit("Không đăng nhập được để tự lấy khoá.\n"
                f"  Đã thử: {email}\n"
                "  Nếu bạn đã đổi mật khẩu, chạy lại kèm mật khẩu:\n"
                "    ARCHESTRA_ADMIN_PASSWORD='mật-khẩu' python3 " + _o.path.basename(_s.argv[0]) + " ...\n"
                "  Hoặc đặt khoá sẵn: export ARCHESTRA_API_KEY='arch_...'")
    try:
        k = post("/api/api-keys", {"name": "auto-" + _uu.uuid4().hex[:6]}).get("key")
    except Exception as e:
        _s.exit(f"Đăng nhập được nhưng không tạo được khoá: {e}")
    if not k:
        _s.exit("Không tạo được khoá API.")
    print(f"(tự tạo khoá API: {k[:14]}...)\n")
    return k


def _check_key(k):  # CHECK_KEY_MARKER
    """Khoá API phải là ASCII — header HTTP không chứa được tiếng Việt."""
    import sys as _s
    if not k:
        _s.exit("Thiếu ARCHESTRA_API_KEY.\n"
                "  Lấy khoá: chạy 'python3 bootstrap.py --apply' (nó in ra khoá mới),\n"
                "  hoặc giao diện -> Settings -> API Keys.\n"
                "  Rồi: export ARCHESTRA_API_KEY='arch_...'")
    try:
        k.encode("ascii")
    except UnicodeEncodeError:
        _s.exit("ARCHESTRA_API_KEY chứa ký tự tiếng Việt.\n"
                "  Có vẻ bạn đã dán chỗ trống ví dụ thay vì khoá thật.\n"
                "  Khoá thật luôn bắt đầu bằng 'arch_'.\n"
                "  Chạy 'python3 bootstrap.py --apply' rồi copy nguyên dòng\n"
                "  export ARCHESTRA_API_KEY='arch_...' mà nó in ra.")
    if not k.startswith("arch_"):
        print("⚠️  Khoá không bắt đầu bằng 'arch_' — có thể sai khoá.\n")
    return k


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:9000")
    p.add_argument("--list", action="store_true", help="Chỉ liệt kê tool và agent")
    p.add_argument("--tool", help="Khớp một phần tên tool, ví dụ: duckduck, search, fetch")
    p.add_argument("--agent", help="Tên agent chính xác")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()

    key = os.environ.get("ARCHESTRA_API_KEY")
    key = _check_key(key) if key else _auto_key(a.base_url)

    tools, err = call(a.base_url, key, "GET", "/api/tools")
    if err: sys.exit(f"Không đọc được danh sách tool: {err}")
    tools = rows(tools)

    agents, err = call(a.base_url, key, "GET", "/api/agents")
    if err: sys.exit(f"Không đọc được danh sách agent: {err}")
    agents = [x for x in rows(agents) if x.get("agentType") == "agent"]

    if a.list or not (a.tool and a.agent):
        def kind(t):
            n = t.get("name") or ""
            if n.startswith("agent__"): return "deleg"
            if n.startswith("archestra__"): return "builtin"
            return "mcp"
        mcp = [t for t in tools if kind(t) == "mcp"]
        builtin = [t for t in tools if kind(t) == "builtin"]
        deleg = [t for t in tools if kind(t) == "deleg"]

        print(f"TOOL TỪ MCP SERVER ({len(mcp)}) — đây là thứ bạn gán:")
        for t in sorted(mcp, key=lambda x: x.get("name") or ""):
            print(f"  · {t.get('name')}")
        if not mcp:
            print("  (chưa có — cài MCP server ở /mcp/registry trước)")
        if builtin:
            print(f"\nTOOL CÓ SẴN CỦA ARCHESTRA ({len(builtin)}):")
            for t in sorted(builtin, key=lambda x: x.get("name") or "")[:8]:
                print(f"  · {t.get('name')}")
        if deleg:
            print(f"\n({len(deleg)} tool uỷ quyền agent__* là sơ đồ tổ chức — không gán tay)")
        print(f"\nAGENT ({len(agents)}):")
        for x in sorted(agents, key=lambda y: y.get("name") or ""):
            print(f"  · {x.get('name')}")
        if not (a.tool and a.agent):
            print("\nDùng: --tool <một phần tên> --agent \"<tên agent>\" [--apply]")
        return

    target = next((x for x in agents if x.get("name") == a.agent), None)
    if not target:
        print(f"❌ Không thấy agent tên chính xác '{a.agent}'. Agent hiện có:")
        for x in sorted(agents, key=lambda y: y.get("name") or ""):
            print(f"  · {x.get('name')}")
        sys.exit(1)

    match = [t for t in tools if a.tool.lower() in (t.get("name") or "").lower()]
    deleg_hit = [t for t in match if (t.get("name") or "").startswith("agent__")]
    if deleg_hit and len(deleg_hit) == len(match):
        print(f"⚠️  '{a.tool}' chỉ khớp tool uỷ quyền (agent__*), vốn là sơ đồ tổ chức.")
        print("   Dùng wire-org.py để sửa sơ đồ, không gán tay ở đây.")
        sys.exit(1)
    match = [t for t in match if not (t.get("name") or "").startswith("agent__")]
    if not match:
        print(f"❌ Không thấy tool nào khớp '{a.tool}'. Chạy --list để xem danh sách.")
        sys.exit(1)

    print(f"{'SẼ GÁN' if a.apply else 'XEM TRƯỚC (chưa thay đổi gì)'} cho agent: {a.agent}\n")
    for t in match:
        print(f"  · {t.get('name')}")

    if not a.apply:
        print("\nChạy lại với --apply để thực thi.")
        return

    # Tool của MCP server chạy nội bộ cần biết DÙNG BẢN CÀI NÀO.
    # Một server có thể có nhiều bản cài (riêng bạn / dùng chung nhóm).
    installs = []
    d, err = call(a.base_url, key, "GET", "/api/mcp_server")
    if not err:
        installs = rows(d)

    def install_for(tool_name):
        """Đoán bản cài theo tiền tố tên tool, ví dụ duckduckgo__search -> duckduckgo."""
        prefix = (tool_name or "").split("__")[0].lower()
        if not prefix:
            return None
        for inst in installs:
            hay = " ".join(str(inst.get(k) or "") for k in ("name", "catalogName", "slug")).lower()
            if prefix in hay or hay.replace("-", "") .find(prefix.replace("-", "")) >= 0:
                return inst.get("id")
        return None

    print()
    done = 0
    for t in match:
        name = t.get("name")
        path = f"/api/agents/{target['id']}/tools/{t['id']}"
        attempts = [("mặc định", {})]
        inst_id = install_for(name)
        if inst_id:
            attempts.append(("gắn bản cài", {"mcpServerId": inst_id}))
        attempts.append(("giải quyết lúc gọi", {"resolveAtCallTime": True}))

        last = None
        for label, body in attempts:
            _, err = call(a.base_url, key, "POST", path, body)
            if not err:
                done += 1
                extra = "" if label == "mặc định" else f"  ({label})"
                print(f"  ✅ {name}{extra}")
                break
            last = err
        else:
            print(f"  ❌ {name}")
            print(f"       {last[:200]}")
            if "installation" in (last or ""):
                print("       Server này chạy nội bộ và cần chỉ rõ bản cài.")
                print("       Thử gán trong giao diện: trang MCP server -> nút Connect.")

    print(f"\nĐã gán {done}/{len(match)} tool.")
    print("Kiểm chứng: mở chat với agent đó và bảo nó dùng tool — nó phải gọi được.")


if __name__ == "__main__":
    main()
