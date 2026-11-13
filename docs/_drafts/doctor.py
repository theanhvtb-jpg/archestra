#!/usr/bin/env python3
"""Kiểm tra hiện trạng Archestra trước khi import bộ agent.

Chỉ ĐỌC, không thay đổi gì. Chạy xong dán toàn bộ kết quả để biết phải làm gì tiếp.

Dùng:
  export ARCHESTRA_API_KEY='khoa-cua-ban'
  python3 doctor.py
  python3 doctor.py --base-url http://localhost:9000
"""
import argparse, json, os, sys, urllib.request, urllib.error

KB_CAN_CO = [
    "KB Nghien cuu Ngach", "KB Packaging", "KB Dieu hanh Media",
    "KB Tuan thu", "KB Kich ban", "KB Ban dia hoa", "KB Hau ky",
    "KB Tai su dung", "KB Xuat ban", "KB Phan tich", "KB Cong dong",
]

AGENT_CAN_CO = [
    "CEO Agent Media",
    "GD Noi dung", "GD San xuat", "GD Tang truong", "GD Tuan thu", "Giam doc Tai chinh",
    "Phong Nghien cuu & Y tuong", "Phong Packaging", "Phong Kich ban",
    "Phong Ban dia hoa & Giong doc", "Phong Hau ky", "Phong Tai su dung & Phan phoi",
    "Phong Chinh sach Noi dung", "Phong Tai san so",
    "Phong Xuat ban & Toi uu", "Phong Phan tich", "Phong Cong dong",
]

# Tool cần nối, theo nhóm từ khoá để dò trong danh sách tool thật
CAN_NOI = [
    ("Tìm kiếm web (Nghiên cứu)",      ["search", "brave", "exa", "tavily", "google"]),
    ("Sổ đăng ký tài sản (Tài sản số)", ["sheet", "spreadsheet", "postgres", "sql", "airtable", "notion"]),
    ("YouTube Data (Xuất bản, Cộng đồng)", ["youtube", "video"]),
    ("YouTube Analytics (Phân tích)",  ["analytic", "youtube"]),
]


def get(base, key, path):
    req = urllib.request.Request(base.rstrip("/") + path, method="GET")
    req.add_header("Authorization", key)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"{}"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def rows(data):
    if data is None:
        return []
    if isinstance(data, list):
        return data
    for k in ("data", "items", "results"):
        if isinstance(data.get(k), list):
            return data[k]
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
    a = p.parse_args()

    key = os.environ.get("ARCHESTRA_API_KEY")
    key = _check_key(key) if key else _auto_key(a.base_url)

    print("=" * 62)
    print(f"KIỂM TRA ARCHESTRA — {a.base_url}")
    print("=" * 62)

    # --- 1. Kết nối ---
    data, err = get(a.base_url, key, "/api/agents")
    if err:
        print(f"\n❌ KHÔNG KẾT NỐI ĐƯỢC: {err}\n")
        if "401" in err or "403" in err:
            print("  Khoá API sai hoặc thiếu quyền.")
            print("  Lưu ý: header là 'Authorization: <khoá>' — KHÔNG có chữ Bearer.")
        else:
            print("  Kiểm tra Archestra đã chạy chưa, và cổng có đúng 9000 không:")
            print("    docker ps | grep archestra")
        sys.exit(1)
    print("\n✅ Kết nối và xác thực OK")

    agents = rows(data)
    noi_bo = [x for x in agents if x.get("agentType") == "agent"]
    ten_agent = {x.get("name") for x in noi_bo}

    # --- 2. Agent ---
    print(f"\n{'─'*62}\nAGENT — có {len(noi_bo)} agent nội bộ\n{'─'*62}")
    da_co = [n for n in AGENT_CAN_CO if n in ten_agent]
    thieu = [n for n in AGENT_CAN_CO if n not in ten_agent]
    print(f"  Thuộc bộ thiết kế : {len(da_co)}/17")
    if da_co:
        for n in da_co:
            print(f"    ✓ {n}")
    if thieu:
        print(f"  Chưa import ({len(thieu)}):")
        for n in thieu:
            print(f"    · {n}")
    la = sorted(ten_agent - set(AGENT_CAN_CO))
    if la:
        print(f"  Agent khác đang có ({len(la)}):")
        for n in la:
            canh = "  ⚠️ dấu hiệu import trùng!" if n.endswith("(imported)") else ""
            print(f"    · {n}{canh}")

    # --- 3. Knowledge Base ---
    data, err = get(a.base_url, key, "/api/knowledge-bases?limit=100&offset=0")
    print(f"\n{'─'*62}\nKNOWLEDGE BASE\n{'─'*62}")
    if err:
        print(f"  ⚠️ không đọc được: {err}")
    else:
        kbs = rows(data)
        ten_kb = {x.get("name") for x in kbs}
        co = [n for n in KB_CAN_CO if n in ten_kb]
        print(f"  Thuộc bộ thiết kế : {len(co)}/{len(KB_CAN_CO)}")
        for n in KB_CAN_CO:
            print(f"    {'✓' if n in ten_kb else '·'} {n}")
        khac = sorted(ten_kb - set(KB_CAN_CO))
        if khac:
            print(f"  KB khác: {', '.join(khac)}")

    # --- 4. Tool ---
    data, err = get(a.base_url, key, "/api/tools")
    print(f"\n{'─'*62}\nTOOL — phần quan trọng nhất\n{'─'*62}")
    if err:
        print(f"  ⚠️ không đọc được: {err}")
    else:
        tools = rows(data)
        noi_bo_tool = [t for t in tools if (t.get("name") or "").startswith("archestra__")]
        ngoai = [t for t in tools if not (t.get("name") or "").startswith("archestra__")]
        print(f"  Tổng: {len(tools)}  |  có sẵn của Archestra: {len(noi_bo_tool)}  |  từ MCP ngoài: {len(ngoai)}")

        if ngoai:
            print(f"\n  TOOL TỪ MCP SERVER NGOÀI — dán phần này để thay placeholder:")
            for t in sorted(ngoai, key=lambda x: x.get("name") or ""):
                print(f"    · {t.get('name')}")
        else:
            print("\n  Chưa có MCP server ngoài nào. Cài tại: giao diện -> MCP Registry")

        print(f"\n  ĐỐI CHIẾU VỚI 4 TÍCH HỢP CẦN CÓ:")
        for nhan, tu_khoa in CAN_NOI:
            khop = [t.get("name") for t in ngoai
                    if any(k in (t.get("name") or "").lower() for k in tu_khoa)]
            if khop:
                print(f"    ✓ {nhan}")
                for k in khop[:4]:
                    print(f"        -> {k}")
            else:
                print(f"    ⬜ {nhan}  — chưa có")

    # --- 5. Policy ---
    data, err = get(a.base_url, key, "/api/autonomy-policies/tool-invocation")
    print(f"\n{'─'*62}\nPOLICY CHẶN\n{'─'*62}")
    chua_co_policy = False
    if err and "404" in err:
        spec, _ = get(a.base_url, key, "/openapi.json")
        ver = ((spec or {}).get("info") or {}).get("version", "không rõ")
        co_guardrails = "/api/guardrails-policy" in ((spec or {}).get("paths") or {})
        print(f"  ⚠️ Phiên bản này ({ver}) không có policy theo từng tool.")
        if co_guardrails:
            print("     Nó dùng MỘT tài liệu guardrails cho cả tổ chức:")
            print("       GET/PUT /api/guardrails-policy  (định dạng TOML, theo 'battery')")
            print("     setup-policies.py KHÔNG dùng được ở đây — nó sẽ dừng và báo rõ.")
        print("     ⚠️ Chưa có gì chặn hành động đăng. Đừng gán tool đăng cho agent")
        print("        cho tới khi bạn dựng guardrails tương đương.")
    elif err:
        print(f"  ⚠️ không đọc được: {err}")
    else:
        pol = rows(data)
        chua_co_policy = not pol
        print(f"  Đang có: {len(pol)} policy")
        if not pol:
            print("  ⬜ Chưa có policy nào.")
            print("     BẮT BUỘC chạy setup-policies.py TRƯỚC khi gán tool đăng cho agent.")
        else:
            dem = {}
            for x in pol:
                dem[x.get("action")] = dem.get(x.get("action"), 0) + 1
            for k, v in sorted(dem.items()):
                print(f"    · {k}: {v}")

    # --- 6. Lịch ---
    data, err = get(a.base_url, key, "/api/schedule-triggers")
    print(f"\n{'─'*62}\nNHỊP VẬN HÀNH\n{'─'*62}")
    if err:
        print(f"  ⚠️ không đọc được: {err}")
    else:
        tr = rows(data)
        bat = [x for x in tr if x.get("enabled")]
        print(f"  Đang có: {len(tr)} lịch ({len(bat)} đang bật)")
        for x in tr:
            print(f"    {'▶' if x.get('enabled') else '⏸'} {x.get('name')} — {x.get('cronExpression')}")

    # --- Kết luận ---
    print(f"\n{'='*62}\nVIỆC TIẾP THEO\n{'='*62}")
    buoc = []
    if thieu:
        buoc.append(f"Import {len(thieu)} agent còn thiếu (theo thứ tự các Đợt)")
    if chua_co_policy:
        buoc.append("Chạy setup-policies.py --apply trước khi gán tool đăng")
    buoc.append("Nạp dữ liệu vào KB — việc này không ai làm thay được")
    for i, b in enumerate(buoc, 1):
        print(f"  {i}. {b}")
    print(f"\n{'='*62}\nDán TOÀN BỘ kết quả trên để được hướng dẫn bước tiếp theo.\n{'='*62}")


if __name__ == "__main__":
    main()
