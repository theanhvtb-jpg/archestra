#!/usr/bin/env python3
"""Xoá agent an toàn: gỡ tool uỷ quyền trỏ tới nó, xoá agent, nối lại sơ đồ.

Xoá agent trong giao diện KHÔNG gỡ tool uỷ quyền (agent__*) mà cấp trên đang giữ.
Tool mồ côi đó chiếm chỗ tên, khiến việc nối lại sơ đồ đụng lỗi 409, và CEO
mất cấp dưới mà giao diện vẫn hiện đủ agent — rất khó phát hiện.

  python3 remove-agent.py --agent "GD Tuan thu"
  python3 remove-agent.py --agent "GD Tuan thu" --apply

Trước khi chạy, sửa sơ đồ trong wire-org.py cho khớp, nếu không nó sẽ nối lại y như cũ.
"""
import argparse, json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar, uuid

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
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
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
                 "  Đổi mật khẩu rồi? Chạy lại kèm:\n"
                 "    ARCHESTRA_ADMIN_PASSWORD='mật-khẩu' python3 remove-agent.py ...")
    d, err = call(base, "POST", "/api/api-keys", {"name": "rm-" + uuid.uuid4().hex[:6]})
    if err or not (d or {}).get("key"):
        sys.exit(f"Không tạo được khoá API: {err}")
    print(f"(tự tạo khoá API: {d['key'][:14]}...)\n")
    return d["key"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:9000")
    p.add_argument("--agent", action="append", default=[], required=True)
    p.add_argument("--skip-wire", action="store_true")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    B = a.base_url

    print("=" * 62)
    print("XOÁ AGENT" + ("" if a.apply else "  —  XEM TRƯỚC (chưa thay đổi gì)"))
    print("=" * 62)

    key = get_key(B)
    d, err = call(B, "GET", "/api/agents", key=key)
    if err: sys.exit(f"Không đọc được danh sách agent: {err}")
    agents = [x for x in rows(d) if x.get("agentType") == "agent"]
    by_name = {x["name"]: x["id"] for x in agents}

    missing = [n for n in a.agent if n not in by_name]
    if missing:
        print("❌ Không thấy agent:")
        for m in missing: print(f"  · {m}")
        print("\n  Agent hiện có:")
        for n in sorted(by_name): print(f"    · {n}")
        sys.exit(1)

    # Tìm tool uỷ quyền trỏ tới agent sắp xoá, và ai đang giữ chúng
    orphans = []
    for name in a.agent:
        for holder in agents:
            ts, e = call(B, "GET", f"/api/agents/{holder['id']}/tools", key=key)
            if e: continue
            for t in rows(ts):
                tn = t.get("name") or ""
                if tn.startswith("agent__") and t.get("targetAgentId") == by_name[name]:
                    orphans.append((holder["name"], holder["id"], tn, t["id"]))

    print("Sẽ xoá:")
    for n in a.agent:
        print(f"  · {n}")
    if orphans:
        print(f"\nGỡ {len(orphans)} tool uỷ quyền đang trỏ tới chúng:")
        for hn, _, tn, _ in orphans:
            print(f"  · {hn} đang giữ {tn}")
    else:
        print("\n(không thấy tool uỷ quyền nào trỏ tới — sẽ dọn lại sau khi xoá)")
    if not a.skip_wire:
        print("\nSau đó nối lại sơ đồ theo wire-org.py.")
        print("⚠️  Nhớ đã sửa ORG trong wire-org.py cho khớp, nếu không nó nối lại y như cũ.")

    if not a.apply:
        print("\nChạy lại với --apply để thực thi.")
        return

    print()
    for hn, hid, tn, tid in orphans:
        _, e = call(B, "DELETE", f"/api/agents/{hid}/tools/{tid}", key=key)
        print(("  ✅ gỡ " if not e else "  ⚠️  không gỡ được ") + f"{tn} khỏi {hn}" + (f": {e[:90]}" if e else ""))

    for name in a.agent:
        _, e = call(B, "DELETE", f"/api/agents/{by_name[name]}", key=key)
        print(("  🗑  đã xoá: " if not e else "  ❌ không xoá được: ") + name + (f" — {e[:90]}" if e else ""))

    # Dọn nốt tool uỷ quyền mồ côi còn sót (trỏ tới agent không còn tồn tại)
    d, _ = call(B, "GET", "/api/agents", key=key)
    alive = {x["id"] for x in rows(d) if x.get("agentType") == "agent"}
    swept = 0
    for holder in rows(d):
        if holder.get("agentType") != "agent": continue
        ts, e = call(B, "GET", f"/api/agents/{holder['id']}/tools", key=key)
        if e: continue
        for t in rows(ts):
            tn = t.get("name") or ""
            tgt = t.get("targetAgentId")
            if tn.startswith("agent__") and tgt and tgt not in alive:
                _, e2 = call(B, "DELETE", f"/api/agents/{holder['id']}/tools/{t['id']}", key=key)
                if not e2: swept += 1
    if swept:
        print(f"  🧹 dọn thêm {swept} tool uỷ quyền mồ côi")

    if a.skip_wire:
        print("\n⚠️  Bỏ qua nối sơ đồ — nhớ chạy wire-org.py --apply.")
        return

    print("\nNối lại sơ đồ:")
    wire = os.path.join(HERE, "ai-company-media-wave5", "wire-org.py")
    env = dict(os.environ, ARCHESTRA_API_KEY=key)
    args = [sys.executable, "-I", wire, "--base-url", B, "--apply"]
    for cand in ("06-ceo-prompt-v6.txt", "06-ceo-prompt-v5.txt"):
        if os.path.isfile(os.path.join(os.path.dirname(wire), cand)):
            args += ["--ceo-prompt", cand]
            break
    r = subprocess.run(args, cwd=os.path.dirname(wire), env=env, capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("✓") or "⚠️" in line or "DỪNG" in line:
            print(f"  {line}")
    if r.returncode != 0:
        print(f"  ❌ wire-org.py lỗi:\n{(r.stderr or r.stdout)[-400:]}")
        sys.exit(1)
    print("\nXong. Kiểm chứng trong giao diện: Agents -> cột Subagents.")


if __name__ == "__main__":
    main()
