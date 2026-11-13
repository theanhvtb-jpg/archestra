#!/usr/bin/env python3
"""Tạo nhịp vận hành định kỳ bằng Archestra schedule triggers.

Mỗi nhịp là một cron gửi sẵn một câu lệnh tới một agent, giống như cuộc họp
định kỳ trong công ty thật.

MẶC ĐỊNH LÀ DRY-RUN. Thêm --apply để thực thi.

Dùng:
  export ARCHESTRA_API_KEY=...
  python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh
  python3 setup-rhythms.py --tz Asia/Ho_Chi_Minh --apply
"""
import argparse, json, os, sys, urllib.request, urllib.error

# (tên nhịp, tên agent phải khớp trong hệ thống, cron, câu lệnh)
RHYTHMS = [
    ("Giao ban hang ngay", "GD San xuat", "30 8 * * 1-5",
     "Giao ban: các video đang sản xuất hiện ở khâu nào? Việc nào đang tắc, tắc vì lý do gì, "
     "và cần ai gỡ? Chỉ nêu việc có thay đổi so với hôm qua."),

    ("Doc so lieu hang ngay", "GD Tang truong", "0 10 * * 1-5",
     "Các video đăng trong 48 giờ qua: CTR và thời lượng xem so với mức nền kênh ra sao? "
     "Nếu chưa đủ dữ liệu thì nói rõ, đừng kết luận sớm."),

    ("Bao cao KPI hang tuan", "CEO Agent Media", "0 9 * * 1",
     "Báo cáo tuần: tình hình từng bộ phận, các chỉ số chính, việc đang tắc, và ba đề xuất "
     "cần Ban giám đốc quyết."),

    ("Bao cao chi phi hang tuan", "Giam doc Tai chinh", "0 16 * * 5",
     "Báo cáo chi phí AI tuần này theo từng phòng, chi phí mỗi video, và mọi dấu hiệu bất thường. "
     "Nêu rõ nếu dữ liệu chưa đủ."),

    ("Soat tai san mo coi", "GD Tuan thu", "0 14 * * 3",
     "Liệt kê các tài sản đang thiếu hồ sơ giấy phép, ưu tiên những tài sản đã dùng trong video "
     "đã đăng. Có giấy phép nào sắp hết hạn không?"),

    ("Ra soat ngach hang tuan", "GD Noi dung", "0 11 * * 2",
     "Tuần qua trong ngách có video nào bứt phá bất thường không, và vì sao nó chạy? "
     "Đề xuất ý tưởng mới kèm chấm điểm."),

    ("Tong ket thang", "CEO Agent Media", "0 9 1 * *",
     "Tổng kết tháng: định dạng nào nên nhân rộng, định dạng nào nên dừng, chi phí mỗi video "
     "có xu hướng gì, và bộ phận nào cần điều chỉnh."),
]


def _schedule_needs_project(base, key):
    """v1.5+ bắt buộc projectId khi tạo schedule trigger; bản cũ thì không.
    Đọc OpenAPI thay vì đoán theo số phiên bản."""
    try:
        spec = call(base, key, "GET", "/openapi.json")
        schema = (spec["paths"]["/api/schedule-triggers"]["post"]["requestBody"]
                  ["content"]["application/json"]["schema"])
        if "$ref" in schema:
            schema = spec["components"]["schemas"][schema["$ref"].split("/")[-1]]
        return "projectId" in (schema.get("required") or [])
    except Exception:
        return False


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
    p.add_argument("--tz", default="Asia/Ho_Chi_Minh",
                   help="Múi giờ chạy lịch, ví dụ Asia/Ho_Chi_Minh hoặc America/New_York")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--project", default="Studio YouTube",
                   help="Tên project chứa các lịch (chỉ dùng với Archestra v1.5 trở lên)")
    a = p.parse_args()

    key = _check_key(os.environ.get("ARCHESTRA_API_KEY"))

    agents = call(a.base_url, key, "GET", "/api/agents")
    if not isinstance(agents, list):
        agents = agents.get("data", [])
    by_name = {ag["name"]: ag["id"] for ag in agents if ag.get("agentType") == "agent"}

    # Từ v1.5 trở đi, schedule trigger thuộc về một project. Phiên bản cũ thì không.
    need_project = _schedule_needs_project(a.base_url, key)
    project_id = None
    if need_project:
        projects = call(a.base_url, key, "GET", "/api/projects")
        rows_ = projects if isinstance(projects, list) else projects.get("data", [])
        match = [x for x in rows_ if x.get("name") == a.project]
        if match:
            project_id = match[0]["id"]
            print(f"Dùng project sẵn có: {a.project}\n")
        elif a.apply:
            created = call(a.base_url, key, "POST", "/api/projects", {"name": a.project})
            project_id = created.get("id")
            print(f"Đã tạo project: {a.project}\n")
        else:
            print(f"Phiên bản này gắn lịch vào project. Sẽ tạo project '{a.project}'.\n")

    planned, missing = [], []
    for name, agent_name, cron, msg in RHYTHMS:
        aid = by_name.get(agent_name)
        if not aid:
            missing.append((name, agent_name))
            continue
        item = {"name": name, "agentId": aid, "messageTemplate": msg,
                "cronExpression": cron, "timezone": a.tz, "enabled": True,
                "_agentName": agent_name}
        if need_project:
            item["projectId"] = project_id
        planned.append(item)

    if missing:
        print("KHÔNG TÌM THẤY AGENT — bỏ qua các nhịp sau:")
        for n, an in missing:
            print(f"  - {n}  (cần agent tên đúng: '{an}')")
        print("\n  Agent hiện có:")
        for n in sorted(by_name):
            print(f"    · {n}")
        print()

    if not planned:
        print("Không có nhịp nào tạo được. Hãy sửa tên agent trong mảng RHYTHMS cho khớp.")
        return

    print(f"{'SẼ TẠO' if a.apply else 'XEM TRƯỚC (chưa tạo gì)'} — {len(planned)} nhịp, múi giờ {a.tz}:\n")
    for it in planned:
        print(f"  {it['name']}")
        print(f"      agent : {it['_agentName']}")
        print(f"      cron  : {it['cronExpression']}\n")

    if not a.apply:
        print("Chạy lại với --apply để thực thi.")
        return

    for it in planned:
        body = {k: v for k, v in it.items() if not k.startswith("_")}
        call(a.base_url, key, "POST", "/api/schedule-triggers", body)
        print(f"✓ {it['name']}")

    print(f"\nĐã tạo {len(planned)} nhịp.")
    print("Bật/tắt từng nhịp qua /api/schedule-triggers/:id/enable và /disable.")
    print("Chạy thử ngay một nhịp bằng /api/schedule-triggers/:id/run-now trước khi tin nó chạy đúng.")


if __name__ == "__main__":
    main()
