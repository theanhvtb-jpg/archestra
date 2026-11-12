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

    key = _check_key(os.environ.get("ARCHESTRA_API_KEY"))

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

    print()
    done = 0
    for t in match:
        _, err = call(a.base_url, key, "POST", f"/api/agents/{target['id']}/tools/{t['id']}", {})
        if err:
            print(f"  ❌ {t.get('name')}: {err[:160]}")
        else:
            done += 1
            print(f"  ✅ {t.get('name')}")

    print(f"\nĐã gán {done}/{len(match)} tool.")
    print("Kiểm chứng: mở chat với agent đó và bảo nó dùng tool — nó phải gọi được.")


if __name__ == "__main__":
    main()
