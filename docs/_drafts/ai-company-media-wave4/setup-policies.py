#!/usr/bin/env python3
"""Cài tool invocation policy cho các tool có thể gây hậu quả không hoàn tác.

Đây là lớp bảo vệ KỸ THUẬT, thay cho quy ước trong prompt. Từ Đợt 4 trở đi hệ thống
lần đầu có tool đăng được nội dung ra ngoài, nên bước này là BẮT BUỘC.

MẶC ĐỊNH LÀ DRY-RUN: script chỉ in ra những gì nó định làm. Thêm --apply để thực thi.

Dùng:
  export ARCHESTRA_API_KEY=...
  python3 setup-policies.py                 # xem trước
  python3 setup-policies.py --apply         # thực thi
"""
import argparse, json, os, sys, urllib.request, urllib.error

# Mỗi quy tắc: tool nào (khớp chuỗi con, không phân biệt hoa thường) -> hành động gì.
# SỬA DANH SÁCH NÀY cho khớp tên tool thật trong MCP catalog của bạn.
RULES = [
    {
        "match": ["dang_video", "publish", "upload"],
        "action": "require_approval",
        "conditions": [],
        "reason": "Dang video la hanh dong khong the hoan tac - phai co nguoi duyet",
    },
    {
        "match": ["cap_nhat_metadata", "update_video", "edit_video"],
        "action": "require_approval",
        "conditions": [],
        "reason": "Sua tieu de/thumbnail video dang chay anh huong truc tiep toi hieu qua",
    },
    {
        "match": ["tra_loi_binh_luan", "comment_reply", "post_comment"],
        "action": "require_approval",
        "conditions": [],
        "reason": "Tra loi cong khai thay mat kenh - phai co nguoi duyet",
    },
    {
        "match": ["gui_mail", "send_email", "send_message"],
        "action": "require_approval",
        "conditions": [],
        "reason": "Gui tin ra ngoai khong the thu hoi",
    },
    {
        "match": ["xoa", "delete", "remove"],
        "action": "require_approval",
        "conditions": [],
        "reason": "Hanh dong xoa khong the hoan tac",
    },
    # Chan hoan toan khi ngu canh khong dang tin (binh luan, web, email khach).
    # Ap cho moi tool ghi ra ben ngoai.
    {
        "match": ["dang_video", "publish", "upload", "tra_loi_binh_luan",
                  "comment_reply", "gui_mail", "send_email"],
        "action": "block_when_context_is_untrusted",
        "conditions": [],
        "reason": "Chan ro ri du lieu khi ngu canh co the chua prompt injection",
    },
]


def call(base, key, method, path, payload=None):
    req = urllib.request.Request(base.rstrip("/") + path,
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 method=method)
    req.add_header("Authorization", key)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"LỖI {method} {path} -> HTTP {e.code}: {e.read().decode()[:400]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:9000")
    p.add_argument("--apply", action="store_true",
                   help="Thực sự tạo policy. Không có cờ này thì chỉ in ra xem trước.")
    a = p.parse_args()

    key = os.environ.get("ARCHESTRA_API_KEY")
    if not key:
        sys.exit("Thiếu biến môi trường ARCHESTRA_API_KEY")

    # Kiểm tra phiên bản API TRƯỚC khi làm gì khác.
    # Từ v1.5, policy theo từng tool bị thay bằng một tài liệu guardrails duy nhất.
    spec = call(a.base_url, key, "GET", "/openapi.json")
    paths = (spec or {}).get("paths", {})
    if "/api/autonomy-policies/tool-invocation" not in paths:
        ver = (spec or {}).get("info", {}).get("version", "không rõ")
        print(f"\n⛔ DỪNG — phiên bản Archestra này ({ver}) KHÔNG có API policy theo từng tool.\n")
        print("   Script này viết cho mô hình cũ: mỗi tool một policy trong")
        print("   /api/autonomy-policies/tool-invocation. Endpoint đó không còn tồn tại.\n")
        if "/api/guardrails-policy" in paths:
            print("   Phiên bản này dùng MỘT tài liệu guardrails (định dạng TOML) cho cả tổ chức:")
            print("     GET  /api/guardrails-policy   — xem policy hiện tại")
            print("     PUT  /api/guardrails-policy   — thay thế, cần {content, expectedRevision}")
            print("   Nó gom quy tắc theo 'battery' thay vì theo từng tool, nên không")
            print("   chuyển đổi tự động được từ danh sách RULES bên dưới.\n")
        print("   ⚠️  KHÔNG CÓ POLICY NÀO ĐƯỢC CÀI. Đừng gán tool đăng cho agent")
        print("       cho tới khi bạn tự dựng guardrails tương đương.\n")
        print("   Các quy tắc cần có, để bạn chuyển thủ công:")
        for r in RULES:
            print(f"     · {r['action']:<34} {', '.join(r['match'][:3])}")
        sys.exit(2)

    tools = call(a.base_url, key, "GET", "/api/tools")
    if not isinstance(tools, list):
        tools = tools.get("data", [])
    print(f"Tìm thấy {len(tools)} tool trong hệ thống.\n")

    existing = call(a.base_url, key, "GET", "/api/autonomy-policies/tool-invocation")
    if not isinstance(existing, list):
        existing = existing.get("data", [])
    have = {(p["toolId"], p["action"]) for p in existing}
    print(f"Đã có sẵn {len(existing)} policy.\n")

    planned, skipped = [], []
    for rule in RULES:
        for tool in tools:
            name = (tool.get("name") or "").lower()
            if not any(m.lower() in name for m in rule["match"]):
                continue
            kkey = (tool["id"], rule["action"])
            if kkey in have:
                skipped.append((tool["name"], rule["action"]))
                continue
            have.add(kkey)
            planned.append({
                "toolId": tool["id"],
                "conditions": rule["conditions"],
                "action": rule["action"],
                "reason": rule["reason"],
                "_toolName": tool["name"],
            })

    if skipped:
        print("Bỏ qua (đã có policy cùng hành động):")
        for n, act in skipped:
            print(f"  - {n} :: {act}")
        print()

    if not planned:
        print("Không có policy nào cần tạo.")
        print("\nNếu bạn nghĩ phải có, hãy kiểm tra: tên tool thật có khớp mục 'match' trong RULES không?")
        print("Danh sách tên tool hiện có:")
        for t in tools[:40]:
            print(f"  - {t.get('name')}")
        return

    print(f"{'SẼ TẠO' if a.apply else 'XEM TRƯỚC (chưa tạo gì)'} — {len(planned)} policy:\n")
    for item in planned:
        print(f"  {item['_toolName']}")
        print(f"      hành động : {item['action']}")
        print(f"      lý do     : {item['reason']}\n")

    if not a.apply:
        print("Chạy lại với --apply để thực thi.")
        return

    for item in planned:
        body = {k: v for k, v in item.items() if not k.startswith("_")}
        call(a.base_url, key, "POST", "/api/autonomy-policies/tool-invocation", body)
        print(f"✓ {item['_toolName']} :: {item['action']}")

    print(f"\nĐã tạo {len(planned)} policy.")
    print("Hãy tự kiểm chứng: bảo agent thực hiện một hành động bị chặn và xác nhận nó dừng lại chờ duyệt.")


if __name__ == "__main__":
    main()
