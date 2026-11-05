#!/usr/bin/env python3
"""Dựng toàn bộ công ty AI trên một instance Archestra trống, bằng một lệnh.

Làm tuần tự: đăng nhập -> tạo khoá API -> tạo 11 Knowledge Base ->
import 17 agent đúng thứ tự -> nối sơ đồ tổ chức -> (tuỳ chọn) nạp khoá LLM.

Chạy lại nhiều lần được: thứ đã có thì bỏ qua, không tạo trùng.

    python3 bootstrap.py                      # xem trước, không thay đổi gì
    python3 bootstrap.py --apply              # thực thi
    OPENROUTER_KEY='sk-or-...' python3 bootstrap.py --apply   # kèm nạp khoá LLM

Yêu cầu: Archestra đang chạy, và thư mục này có đủ các thư mục ai-company-media-*.
"""
import argparse, json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar

HERE = os.path.dirname(os.path.abspath(__file__))

KBS = ["KB Nghien cuu Ngach", "KB Packaging", "KB Dieu hanh Media", "KB Tuan thu",
       "KB Kich ban", "KB Ban dia hoa", "KB Hau ky", "KB Tai su dung",
       "KB Xuat ban", "KB Phan tich", "KB Cong dong"]

# Thứ tự QUAN TRỌNG: agent được tham chiếu phải tồn tại trước.
AGENTS = [
    ("ai-company-media-phase0", "01-research-agent.json"),
    ("ai-company-media-phase0", "02-packaging-agent.json"),
    ("ai-company-media-wave2",  "01-compliance-agent.json"),
    ("ai-company-media-wave2",  "02-asset-agent.json"),
    ("ai-company-media-wave3",  "01-script-agent.json"),
    ("ai-company-media-wave3",  "02-localization-agent.json"),
    ("ai-company-media-wave3",  "03-post-production-agent.json"),
    ("ai-company-media-wave3",  "04-repurpose-agent.json"),
    ("ai-company-media-wave4",  "01-publishing-agent.json"),
    ("ai-company-media-wave4",  "02-analytics-agent.json"),
    ("ai-company-media-wave4",  "03-community-agent.json"),
    ("ai-company-media-wave5",  "01-director-content.json"),
    ("ai-company-media-wave5",  "02-director-production.json"),
    ("ai-company-media-wave5",  "03-director-growth.json"),
    ("ai-company-media-wave5",  "04-director-compliance.json"),
    ("ai-company-media-wave5",  "05-cfo.json"),
    ("ai-company-media-phase0", "03-ceo-agent.json"),
]

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def call(base, method, path, payload=None, key=None):
    req = urllib.request.Request(base.rstrip("/") + path,
        data=json.dumps(payload).encode() if payload is not None else None, method=method)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if key:
        req.add_header("Authorization", key)
    try:
        with opener.open(req, timeout=120) as r:
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


def list_names(base, key, path, page_size=100):
    """Đọc hết danh sách theo trang. Trả (tập tên, lỗi).
    limit tối đa của API là 100 — xin nhiều hơn sẽ bị từ chối 400."""
    names, offset = set(), 0
    while True:
        d, err = call(base, "GET", f"{path}?limit={page_size}&offset={offset}", key=key)
        if err:
            return names, err
        batch = rows(d)
        names |= {x.get("name") for x in batch}
        if len(batch) < page_size:
            return names, None
        offset += page_size


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:9000")
    p.add_argument("--email", default=os.environ.get("ARCHESTRA_ADMIN_EMAIL", "admin@example.com"))
    p.add_argument("--password", default=os.environ.get("ARCHESTRA_ADMIN_PASSWORD", "password"))
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    B = a.base_url
    DRY = not a.apply

    print("=" * 62)
    print("DỰNG CÔNG TY AI" + ("  —  XEM TRƯỚC (chưa thay đổi gì)" if DRY else ""))
    print("=" * 62)

    # 1. Đăng nhập
    print("\n[1/5] Đăng nhập")
    d, err = call(B, "POST", "/api/auth/sign-in/email", {"email": a.email, "password": a.password})
    if err:
        print(f"  ❌ {err}")
        print("\n  Archestra chặn đăng ký trực tiếp; phải dùng tài khoản quản trị mặc định.")
        print("  Mặc định: admin@example.com / password")
        print("  Đổi bằng --email và --password, hoặc biến ARCHESTRA_ADMIN_EMAIL/PASSWORD.")
        sys.exit(1)
    print(f"  ✅ {a.email}")

    # 2. Khoá API
    print("\n[2/5] Khoá API")
    if DRY:
        print("  (sẽ tạo khoá API mới)")
        KEY = None
    else:
        d, err = call(B, "POST", "/api/api-keys", {"name": "bootstrap"})
        KEY = (d or {}).get("key")
        if not KEY:
            sys.exit(f"  ❌ không tạo được khoá: {err}")
        print(f"  ✅ đã tạo ({KEY[:12]}...)")
        print(f"     Lưu lại để dùng cho các script khác:")
        print(f"     export ARCHESTRA_API_KEY='{KEY}'")

    # 3. Knowledge Base
    print("\n[3/5] Knowledge Base")
    have = set()
    if KEY:
        have, err = list_names(B, KEY, "/api/knowledge-bases")
        if err:
            print(f"  ❌ không đọc được danh sách KB: {err}")
            print("     DỪNG — đọc không được mà vẫn tạo thì sẽ tạo trùng.")
            sys.exit(1)
    todo = [k for k in KBS if k not in have]
    print(f"  đã có {len(have & set(KBS))}/{len(KBS)}, cần tạo {len(todo)}")
    if not DRY:
        made = 0
        for name in todo:
            _, err = call(B, "POST", "/api/knowledge-bases", {"name": name}, key=KEY)
            if err is None: made += 1
            else: print(f"     ⚠️ {name}: {err[:90]}")
        print(f"  ✅ tạo thêm {made}")

    # 4. Import agent
    print("\n[4/5] Import agent")
    have_ag = set()
    if KEY:
        d, err = call(B, "GET", "/api/agents", key=KEY)
        if err:
            print(f"  ❌ không đọc được danh sách agent: {err}")
            print("     DỪNG — import khi không biết đã có gì sẽ tạo agent trùng.")
            sys.exit(1)
        have_ag = {x.get("name") for x in rows(d) if x.get("agentType") == "agent"}
    missing_files = [f"{f}/{n}" for f, n in AGENTS if not os.path.isfile(os.path.join(HERE, f, n))]
    if missing_files:
        print("  ❌ thiếu file:")
        for m in missing_files: print(f"     · {m}")
        print("\n  Chạy script này từ bên trong thư mục docs/_drafts của repo.")
        sys.exit(1)
    print(f"  tìm đủ {len(AGENTS)} file payload")
    if not DRY:
        ok, warns = 0, 0
        for folder, fn in AGENTS:
            payload = json.load(open(os.path.join(HERE, folder, fn), encoding="utf-8"))
            if payload["agent"]["name"] in have_ag:
                print(f"     · bỏ qua (đã có): {payload['agent']['name']}")
                continue
            d, err = call(B, "POST", "/api/agents/import", payload, key=KEY)
            if err:
                print(f"     ❌ {fn}: {err[:110]}")
            else:
                ok += 1
                w = (d or {}).get("warnings") or []
                warns += len(w)
        print(f"  ✅ import {ok} agent (warning: {warns} — thiếu tool/KB là bình thường)")

        # CEO trong file phase0 tên là "CEO Agent"; wire-org.py cần "CEO Agent Media"
        d, _ = call(B, "GET", "/api/agents", key=KEY)
        ags = {x["name"]: x["id"] for x in rows(d) if x.get("agentType") == "agent"}
        if "CEO Agent" in ags and "CEO Agent Media" not in ags:
            call(B, "PUT", f"/api/agents/{ags['CEO Agent']}", {"name": "CEO Agent Media"}, key=KEY)
            print("     · đổi tên 'CEO Agent' -> 'CEO Agent Media'")

    # 5. Nối sơ đồ
    print("\n[5/5] Nối sơ đồ tổ chức")
    wire = os.path.join(HERE, "ai-company-media-wave5", "wire-org.py")
    if DRY:
        print("  (sẽ chạy wire-org.py --apply)")
    else:
        env = dict(os.environ, ARCHESTRA_API_KEY=KEY)
        r = subprocess.run([sys.executable, "-I", wire, "--base-url", B, "--apply",
                            "--ceo-prompt", "06-ceo-prompt-v5.txt"],
                           cwd=os.path.dirname(wire), env=env, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if line.startswith("✓") or "⚠️" in line or "DỪNG" in line:
                print(f"  {line}")
        if r.returncode != 0:
            print(f"  ❌ wire-org.py lỗi:\n{(r.stderr or r.stdout)[-400:]}")

    # Tuỳ chọn: khoá LLM
    or_key = os.environ.get("OPENROUTER_KEY")
    if or_key and not DRY:
        print("\n[+] Nạp khoá OpenRouter")
        d, err = call(B, "POST", "/api/llm-provider-api-keys",
                      {"name": "OpenRouter", "provider": "openrouter",
                       "apiKey": or_key, "shared": True, "isPrimary": True}, key=KEY)
        if err:
            print(f"  ⚠️ {err[:200]}")
            print("     (máy này có ra được openrouter.ai không?)")
        else:
            print("  ✅ đã nạp")
            call(B, "POST", "/api/llm-models/sync", {}, key=KEY)
            d, _ = call(B, "GET", "/api/llm-models", key=KEY)
            print(f"  ✅ đồng bộ {len(rows(d))} model")
    elif not or_key:
        print("\n[+] Bỏ qua khoá LLM (đặt OPENROUTER_KEY nếu muốn nạp luôn)")

    print("\n" + "=" * 62)
    if DRY:
        print("Chạy lại với --apply để thực thi.")
    else:
        print("XONG. Việc tiếp theo:")
        print("  1. Nạp dữ liệu vào Knowledge Base — không ai làm thay được")
        print("  2. python3 doctor.py                 — kiểm tra lại hiện trạng")
        print("  3. python3 test-agent-prompts.py     — kiểm agent có từ chối đúng chỗ không")
        print("  4. ai-company-media-wave5/setup-rhythms.py --apply   — bật nhịp định kỳ")
    print("=" * 62)


if __name__ == "__main__":
    main()
