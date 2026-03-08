from __future__ import annotations
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MAP_FILE = DATA_DIR / "mappings.json"

LEVELS = ["مباشر", "محسّن", "رشيق"]

def simple_diff(a: str, b: str) -> list[str]:
    wa = re.findall(r"\w+|[^\w\s]", a, flags=re.UNICODE)
    wb = re.findall(r"\w+|[^\w\s]", b, flags=re.UNICODE)
    sa = set(wa)
    sb = set(wb)
    removed = [w for w in wa if w not in sb]
    added   = [w for w in wb if w not in sa]
    out = []
    if removed:
        out.append("حُذفت/تغيّرت: " + " ، ".join(removed[:20]))
    if added:
        out.append("أُضيفت/استُبدلت: " + " ، ".join(added[:20]))
    if not out:
        out.append("لا تغييرات واضحة على مستوى الكلمات.")
    return out

def default_mappings() -> dict:
    return {
        "إماراتي/خليجي": {
            "examples": ["وش السالفة؟ → ما الخبر؟", "أبغي أروح الحين → أريد أن أذهب الآن."],
            "map": {"أبغي":"أريد","بغيت":"أردت","وش":"ما","السالفة":"الخبر","الحين":"الآن","ماشي":"حسنًا"}
        },
        "سعودي": {
            "examples": ["ودي أذاكر → أود أن أذاكر.", "مرة حلو → جميل جدًا."],
            "map": {"ودي":"أود","مرة":"جدًا","يبغى":"يريد","مدري":"لا أدري"}
        },
        "مصري": {
            "examples": ["عايز أفهم → أريد أن أفهم.", "إزايك؟ → كيف حالك؟"],
            "map": {"عايز":"أريد","إزاي":"كيف","كويس":"جيد","مش":"ليس"}
        },
        "شامي": {
            "examples": ["شو بدك؟ → ماذا تريد؟", "كتير منيح → جيد جدًا."],
            "map": {"شو":"ماذا","بدك":"تريد","كتير":"جدًا","منيح":"جيد"}
        },
        "عراقي": {
            "examples": ["شكو ماكو؟ → ما الأخبار؟", "أريد أروح → أريد أن أذهب."],
            "map": {"شكو":"ما","ماكو":"لا يوجد","هسة":"الآن","أكو":"يوجد"}
        },
        "مغربي": {
            "examples": ["كيداير؟ → كيف حالك؟", "بغيت نمشي → أريد أن أذهب."],
            "map": {"كيداير":"كيف حالك","بغيت":"أريد","نمشي":"أذهب","زوين":"جيد"}
        },
        "ليبي": {
            "examples": ["أشحال؟ → كم؟", "نحب نمشي → أريد أن أذهب."],
            "map": {"أشحال":"كم","نحب":"أريد","نمشي":"أذهب","زين":"جيد"}
        },
        "تونسي": {
            "examples": ["شنو تحب؟ → ماذا تريد؟", "برشة → كثيرًا."],
            "map": {"شنو":"ماذا","تحب":"تريد","برشة":"كثيرًا","بهي":"جيد"}
        },
        "جزائري": {
            "examples": ["واش تبغي؟ → ماذا تريد؟", "زعما → إذن."],
            "map": {"واش":"ماذا","تبغي":"تريد","زعما":"إذن","مزيان":"جيد"}
        },
    }

class LocalConverter:
    def __init__(self):
        self.mappings = self._load()

    def _load(self) -> dict:
        if not MAP_FILE.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            MAP_FILE.write_text(json.dumps(default_mappings(), ensure_ascii=False, indent=2), encoding="utf-8")
        return json.loads(MAP_FILE.read_text(encoding="utf-8"))

    def convert(self, text: str, dialect: str, level: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {"ok": False, "msa": "", "explanations": ["المدخل فارغ."]}

        m = self.mappings.get(dialect, {})
        word_map = m.get("map", {})
        examples = m.get("examples", [])

        out = text
        explanations = []
        for k, v in word_map.items():
            if k in out:
                out = out.replace(k, v)
                explanations.append(f"استبدال «{k}» بـ «{v}» لأنها فصحى.")

        if level in ("محسّن", "رشيق"):
            out = out.replace("وش", "ما").replace("ليه", "لِمَ")

        if level == "رشيق":
            out = out.replace("يعني", "").replace("بس", "").strip()
            out = " ".join(out.split())

        diffs = simple_diff(text, out)
        if examples:
            explanations.append("أمثلة من هذه اللهجة:")
            explanations.extend([f"• {ex}" for ex in examples[:4]])

        return {"ok": True, "msa": out, "explanations": explanations[:12], "diffs": diffs}
