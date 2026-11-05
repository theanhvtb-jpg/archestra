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
    p.add_argument("--tz", default="Asia/Ho_Chi_Minh",
                   help="Múi giờ chạy lịch, ví dụ Asia/Ho_Chi_Minh hoặc America/New_York")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()

    key = os.environ.get("ARCHESTRA_API_KEY")
    if not key:
        sys.exit("Thiếu biến môi trường ARCHESTRA_API_KEY")

    agents = call(a.base_url, key, "GET", "/api/agents")
    if not isinstance(agents, list):
        agents = agents.get("data", [])
    by_name = {ag["name"]: ag["id"] for ag in agents if ag.get("agentType") == "agent"}

    planned, missing = [], []
    for name, agent_name, cron, msg in RHYTHMS:
        aid = by_name.get(agent_name)
        if not aid:
            missing.append((name, agent_name))
            continue
        planned.append({"name": name, "agentId": aid, "messageTemplate": msg,
                        "cronExpression": cron, "timezone": a.tz, "enabled": True,
                        "_agentName": agent_name})

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
