#!/usr/bin/env python3
"""Nối toàn bộ sơ đồ tổ chức: CEO -> 5 giám đốc -> 11 phòng ban.

Thay cho việc ghép tay 16 UUID. Script tra agent theo TÊN, nên tên trong hệ thống
phải khớp mảng ORG dưới đây. Sai tên thì script in ra tên thật để bạn sửa.

MẶC ĐỊNH LÀ DRY-RUN. Thêm --apply để thực thi.

Dùng:
  export ARCHESTRA_API_KEY=...
  python3 wire-org.py
  python3 wire-org.py --apply
  python3 wire-org.py --apply --ceo-prompt 06-ceo-prompt-v5.txt
"""
import argparse, json, os, sys, urllib.request, urllib.error

# Cấp trên -> danh sách cấp dưới trực tiếp.
ORG = {
    "CEO Agent Media": [
        "GD Noi dung", "GD San xuat", "GD Tang truong",
        "GD Tuan thu", "Giam doc Tai chinh",
    ],
    "GD Noi dung": [
        "Phong Nghien cuu & Y tuong", "Phong Packaging",
        "Phong Kich ban", "Phong Ban dia hoa & Giong doc",
    ],
    "GD San xuat": [
        "Phong Hau ky", "Phong Tai su dung & Phan phoi", "Phong Xuat ban & Toi uu",
    ],
    "GD Tang truong": ["Phong Phan tich", "Phong Cong dong"],
    "GD Tuan thu": ["Phong Ban quyen & Chinh sach", "Phong Tai san so"],
    "Giam doc Tai chinh": [],
}


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
    p.add_argument("--ceo-prompt", default=None,
                   help="Đường dẫn file prompt CEO v5. Bỏ qua thì chỉ nối delegation.")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()

    key = _check_key(os.environ.get("ARCHESTRA_API_KEY"))

    agents = call(a.base_url, key, "GET", "/api/agents")
    if not isinstance(agents, list):
        agents = agents.get("data", [])
    by_name = {ag["name"]: ag["id"] for ag in agents if ag.get("agentType") == "agent"}

    # Kiểm tra trùng tên — dấu hiệu đã lỡ import lại agent
    dupes = [n for n in by_name if n.endswith("(imported)")]
    if dupes:
        print("⚠️  CẢNH BÁO: có agent tên kết thúc bằng '(imported)' — dấu hiệu đã import trùng:")
        for d in dupes:
            print(f"    · {d}")
        print("    Hãy xoá bản thừa trước khi nối sơ đồ, nếu không bạn sẽ nối nhầm.\n")

    missing, plan = set(), []
    for boss, reports in ORG.items():
        if boss not in by_name:
            missing.add(boss)
            continue
        ids, names = [], []
        for r in reports:
            if r not in by_name:
                missing.add(r)
                continue
            ids.append(by_name[r]); names.append(r)
        plan.append((boss, by_name[boss], ids, names))

    if missing:
        print("KHÔNG TÌM THẤY các agent sau:")
        for m in sorted(missing):
            print(f"  - {m}")
        print("\n  Agent hiện có trong hệ thống:")
        for n in sorted(by_name):
            print(f"    · {n}")
        print("\n  Sửa mảng ORG trong script cho khớp, rồi chạy lại.\n")

    print(f"{'SẼ NỐI' if a.apply else 'XEM TRƯỚC (chưa thay đổi gì)'} — sơ đồ tổ chức:\n")
    for boss, _bid, ids, names in plan:
        print(f"  {boss}")
        if not names:
            print("      (không quản ai)")
        for n in names:
            print(f"      └─ {n}")
        if len(ids) != len(ORG[boss]):
            print(f"      ⚠️  thiếu {len(ORG[boss]) - len(ids)} cấp dưới so với thiết kế")
        print()

    if a.ceo_prompt:
        print(f"  + Cập nhật system prompt của CEO từ: {a.ceo_prompt}\n")

    if not a.apply:
        print("Chạy lại với --apply để thực thi.")
        return

    if missing:
        print("DỪNG: còn agent chưa tìm thấy. Sửa cho đủ rồi chạy lại,")
        print("      nếu không sơ đồ sẽ bị nối thiếu và việc sẽ rơi vào hư không.")
        sys.exit(1)

    if a.ceo_prompt:
        prompt = open(a.ceo_prompt, encoding="utf-8").read()
        call(a.base_url, key, "PUT", f"/api/agents/{by_name['CEO Agent Media']}",
             {"systemPrompt": prompt})
        print(f"✓ Đã cập nhật prompt CEO ({len(prompt)} ký tự)")

    for boss, bid, ids, _names in plan:
        call(a.base_url, key, "POST", f"/api/agents/{bid}/delegations", {"targetAgentIds": ids})
        print(f"✓ {boss} -> {len(ids)} cấp dưới")

    print("\nXong. Hãy tự kiểm chứng: hỏi CEO một việc thuộc Packaging và xác nhận nó đi qua")
    print("GĐ Nội dung chứ không gọi thẳng Phòng Packaging.")


if __name__ == "__main__":
    main()
