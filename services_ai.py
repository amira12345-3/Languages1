from __future__ import annotations
import os
import json
import requests

OPENAI_HOST = "https://api.openai.com/v1/models"

def check_openai_reachable(timeout: int = 6) -> tuple[bool, str]:
    try:
        r = requests.get(OPENAI_HOST, timeout=timeout)
        if r.status_code in (200, 401, 403):
            return True, "OK"
        return True, f"وصلنا للسيرفر لكن رد: {r.status_code}"
    except Exception as e:
        return False, f"خطأ: {e}"

class OpenAIService:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def ready(self) -> tuple[bool, str]:
        ok, reason = check_openai_reachable()
        if not ok:
            return False, reason
        if not self.api_key:
            return False, "API Key غير موجود"
        return True, "OK"

    def convert_dialect_to_msa(self, text: str, dialect: str, level: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {"ok": False, "error": "المدخل فارغ.", "offline": False}

        ok, reason = self.ready()
        if not ok:
            return {"ok": False, "error": reason, "offline": True}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        prompt = f"""
حوّل النص من اللهجة إلى العربية الفصحى.
المعطيات:
- اللهجة المختارة: {dialect}
- المستوى: {level} (مباشر/محسّن/رشيق)
المخرجات (JSON فقط):
{{
  "msa":"...",
  "dialect_detected":"...",
  "explanations":["سبب 1","سبب 2","..."]
}}
اشرح باختصار سبب اختيار الكلمات (تعليمي).
النص:
{text}
""".strip()

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers, json=body, timeout=30
            )
            if r.status_code == 429:
                return {"ok": False, "error": "429: انتهى الرصيد.", "offline": False}
            if r.status_code >= 400:
                return {"ok": False, "error": f"API {r.status_code}: {r.text[:300]}", "offline": False}

            data = r.json()
            text_out = data["choices"][0]["message"]["content"].strip()

            # تنظيف ال JSON
            if "```" in text_out:
                text_out = text_out.split("```")[1]
                if text_out.startswith("json"):
                    text_out = text_out[4:]

            try:
                j = json.loads(text_out)
                return {
                    "ok": True,
                    "msa": (j.get("msa") or "").strip(),
                    "dialect_detected": (j.get("dialect_detected") or "").strip(),
                    "explanations": j.get("explanations") or []
                }
            except Exception:
                return {"ok": True, "msa": text_out.strip(), "dialect_detected": "", "explanations": []}

        except Exception as e:
            return {"ok": False, "error": f"فشل اتصال: {e}", "offline": True}
