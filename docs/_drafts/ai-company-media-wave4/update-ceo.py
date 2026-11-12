#!/usr/bin/env python3
"""Cập nhật CEO Agent tại chỗ (prompt v2 + delegation tới 4 phòng).

KHÔNG import lại file CEO cũ: import luôn TẠO AGENT MỚI và thêm hậu tố
" (imported)" khi trùng tên, nên bạn sẽ có hai CEO và không biết cái nào đang chạy.

Dùng:
  export ARCHESTRA_API_KEY=...
  python3 update-ceo.py --base-url http://localhost:9000 \
      --ceo-id <CEO_ID> --target-id <ID1> --target-id <ID2> ...
"""
import argparse, json, os, sys, urllib.request

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



def call(base, key, method, path, payload=None):
    url = base.rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", key)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"LỖI {method} {path} -> HTTP {e.code}: {e.read().decode()[:400]}")

p = argparse.ArgumentParser()
p.add_argument("--base-url", default="http://localhost:9000")
p.add_argument("--ceo-id", required=True)
p.add_argument("--target-id", action="append", default=[], help="ID phòng ban, lặp lại nhiều lần")
p.add_argument("--prompt-file", default="03-ceo-prompt-v2.txt")
a = p.parse_args()

key = _check_key(os.environ.get("ARCHESTRA_API_KEY"))
if not key:
    sys.exit("Thiếu biến môi trường ARCHESTRA_API_KEY")
if not a.target_id:
    sys.exit("Cần ít nhất một --target-id")

prompt = open(a.prompt_file, encoding="utf-8").read()

call(a.base_url, key, "PUT", f"/api/agents/{a.ceo_id}", {"systemPrompt": prompt})
print(f"✓ Đã cập nhật system prompt ({len(prompt)} ký tự)")

call(a.base_url, key, "POST", f"/api/agents/{a.ceo_id}/delegations",
     {"targetAgentIds": a.target_id})
print(f"✓ Đã đặt {len(a.target_id)} delegation target")

now = call(a.base_url, key, "GET", f"/api/agents/{a.ceo_id}/delegations")
print("\nKiểm tra lại:")
print(json.dumps(now, ensure_ascii=False, indent=2)[:1200])
