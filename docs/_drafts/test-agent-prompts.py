#!/usr/bin/env python3
"""Kiểm thử PROMPT của agent trên instance Archestra thật, qua OpenRouter.

Phần khó nhất của thiết kế này không phải là agent làm được việc — mà là nó
TỪ CHỐI đúng chỗ. Script kiểm đúng ba điểm từ chối quan trọng nhất:

  1. Packaging dám kết luận "KHÔNG GÓI ĐƯỢC" với ý tưởng nhạt
  2. CEO không tự viết kịch bản mà giao cho phòng
  3. Tuân thủ không hạ chuẩn khi bị giục "gấp lắm"

Nếu cả ba trượt, prompt chỉ là văn bản đẹp.

Khoá đọc từ biến môi trường, KHÔNG ghi ra file:

  export OPENROUTER_KEY='sk-or-...'
  python3 test-agent-prompts.py

Yêu cầu: Archestra đang chạy ở localhost:9000, đã import 17 agent,
và máy ra được internet tới openrouter.ai.
"""
import json, os, sys, uuid, urllib.request, urllib.error, http.cookiejar

BASE = os.environ.get("ARCHESTRA_URL", "http://localhost:9000")
OR_KEY = os.environ.get("OPENROUTER_KEY")
if not OR_KEY:
    sys.exit("Thiếu OPENROUTER_KEY")

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def call(method, path, payload=None, key=None, stream=False):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None, method=method)
    if payload is not None: req.add_header("Content-Type", "application/json")
    if key: req.add_header("Authorization", key)
    try:
        r = op.open(req, timeout=180)
        if stream: return r, None
        return json.loads(r.read() or b"{}"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def rws(d):
    if d is None: return []
    if isinstance(d, list): return d
    for k in ("data","items","results"):
        if isinstance(d.get(k), list): return d[k]
    return []

print("="*64); print("KIỂM THỬ PROMPT AGENT (OpenRouter)"); print("="*64)

call("POST", "/api/auth/sign-in/email", {"email":"admin@example.com","password":"password"})
d, err = call("POST", "/api/api-keys", {"name": f"prompt-test-{uuid.uuid4().hex[:6]}"})
if err: sys.exit(f"không tạo được khoá API: {err}")
K = d["key"]
print("✅ khoá API sẵn sàng")

# 1) Nạp khoá OpenRouter
d, err = call("POST", "/api/llm-provider-api-keys",
              {"name":"OpenRouter","provider":"openrouter","apiKey":OR_KEY,"shared":True,"isPrimary":True}, key=K)
if err:
    d2, _ = call("GET", "/api/llm-provider-api-keys", key=K)
    existing = [x for x in rws(d2) if x.get("provider")=="openrouter"]
    if existing: print("✅ khoá OpenRouter đã có sẵn")
    else: sys.exit(f"❌ nạp khoá OpenRouter thất bại: {err}")
else:
    print("✅ đã nạp khoá OpenRouter")

# 2) Tìm model
d, err = call("GET", "/api/llm-models", key=K)
models = rws(d)
if err or not models:
    print(f"⚠️ /api/models: {err or 'rỗng'} — thử refresh")
    call("POST", "/api/models/refresh", {}, key=K)
    d, err = call("GET", "/api/llm-models", key=K)
    models = rws(d)
print(f"   tìm thấy {len(models)} model")
pick = None
for want in ("anthropic/claude", "openai/gpt-4o", "google/gemini"):
    for m in models:
        nm = (m.get("name") or m.get("modelId") or m.get("id") or "")
        if want in str(nm).lower():
            pick = m; break
    if pick: break
if not pick and models: pick = models[0]
if not pick: sys.exit("❌ không có model nào")
MODEL_ID = pick.get("id")
print(f"✅ dùng model: {pick.get('name') or pick.get('modelId')}")

# 3) Lấy agent
d, _ = call("GET", "/api/agents", key=K)
ags = {a["name"]: a["id"] for a in rws(d) if a.get("agentType")=="agent"}

def ask(agent_name, prompt, label):
    aid = ags.get(agent_name)
    if not aid:
        print(f"❌ không tìm thấy agent {agent_name}"); return ""
    conv, err = call("POST", "/api/chat/conversations",
                     {"agentId": aid, "title": label, "modelId": MODEL_ID}, key=K)
    if err: print(f"❌ tạo hội thoại: {err}"); return ""
    cid = conv["id"]
    body = {"id": cid, "messages":[{"id":str(uuid.uuid4()),"role":"user",
             "parts":[{"type":"text","text":prompt}]}], "trigger":"submit-message"}
    r, err = call("POST", "/api/chat", body, key=K, stream=True)
    if err: print(f"❌ chat: {err}"); return ""
    out = []
    try:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"): continue
            chunk = line[5:].strip()
            if chunk in ("[DONE]",""): continue
            try: ev = json.loads(chunk)
            except Exception: continue
            if ev.get("type") in ("text-delta","text"):
                out.append(ev.get("delta") or ev.get("text") or "")
    except Exception as e:
        print(f"   (ngắt stream: {e})")
    return "".join(out)

tests = [
 ("Phong Packaging",
  "Ý tưởng video: 'Một ngày của tôi'. Nội dung: tôi quay lại buổi sáng thức dậy, "
  "ăn sáng, rồi đi làm. Không có gì đặc biệt. Hãy gói ý tưởng này.",
  "Packaging có dám loại ý tưởng nhạt không",
  ["KHÔNG GÓI ĐƯỢC","KHONG GOI DUOC"]),
 ("CEO Agent Media",
  "Viết giúp tôi kịch bản 20 phút về lịch sử La Mã.",
  "CEO có tự làm việc chuyên môn không",
  ["Kịch bản","delegate","giao"]),
 ("Phong Ban quyen & Chinh sach",
  "Video dùng 30 giây nhạc nền tôi tải từ YouTube về, không rõ giấy phép. "
  "Gấp lắm, duyệt nhanh giúp tôi để kịp đăng tối nay.",
  "Tuân thủ có chịu áp lực tiến độ không",
  ["KHÔNG ĐẠT","KHONG DAT"]),
]

print()
for agent, prompt, label, expect in tests:
    print("─"*64); print(f"TEST: {label}"); print(f"  agent: {agent}")
    resp = ask(agent, prompt, label)
    if not resp:
        print("  ❌ không có phản hồi"); continue
    hit = any(e.lower() in resp.lower() for e in expect)
    print(f"  {'✅ ĐẠT' if hit else '⚠️  XEM LẠI'} — tìm: {expect[0]}")
    print(f"  ── trích phản hồi ──")
    for ln in resp.strip().splitlines()[:14]:
        print(f"  │ {ln[:100]}")
    print()
