"""
مُفصِّحُ اللِّسان - تطبيق ويب
Dialect → Modern Standard Arabic (MSA) Translator
"""
from __future__ import annotations
import json
import os
import random
import streamlit as st
from pathlib import Path

# ─── إعداد الصفحة ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="مُفصِّحُ اللِّسان",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── استيراد الخدمات ────────────────────────────────────────────────────────
from services_ai import OpenAIService
from services_converter import LocalConverter, LEVELS, simple_diff
import services_storage as store

DATA_DIR = Path(__file__).parent / "data"

# ─── CSS مخصص ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    .main-header {
        background: linear-gradient(135deg, #0b3d7a, #1a6b3c);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .main-header h1 { color: #6ee7b7; margin:0; font-size:2.2rem; }
    .main-header p  { color: #a7f3d0; margin:0.3rem 0 0; font-size:1rem; }

    .stat-card {
        background: #0f2540;
        border: 1px solid #1e4060;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.3rem;
    }
    .stat-card .num { font-size: 2rem; font-weight:900; color:#6ee7b7; }
    .stat-card .lbl { font-size: 0.85rem; color: #94a3b8; }

    .result-box {
        background: #0d2035;
        border-right: 4px solid #6ee7b7;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 1.1rem;
        line-height: 2;
    }
    .diff-added   { color: #6ee7b7; font-weight:700; }
    .diff-removed { color: #f87171; text-decoration: line-through; }

    .badge-pill {
        display:inline-block;
        background: linear-gradient(90deg,#1a6b3c,#0b3d7a);
        color:#6ee7b7;
        border-radius:20px;
        padding:4px 14px;
        margin:3px;
        font-size:0.85rem;
        font-weight:700;
    }
    .prize-card {
        background:#0f2540;
        border:1px solid #2a5070;
        border-radius:12px;
        padding:0.9rem;
        text-align:center;
        margin:0.4rem;
    }
    .stTextArea textarea { direction: rtl; font-size: 1.05rem; }
    .stSelectbox select  { direction: rtl; }
</style>
""", unsafe_allow_html=True)

# ─── رأس الصفحة ─────────────────────────────────────────────────────────────
profile = store.get_profile()
points  = store.get_points()
st.markdown(f"""
<div class="main-header">
    <h1>📖 مُفصِّحُ اللِّسان</h1>
    <p>يفصّح كلامك… ويُتمّم بيانك &nbsp;|&nbsp; {profile['avatar']} {profile['name']} &nbsp;⭐ {points} نقطة</p>
</div>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    DIALECTS = ["تلقائي","إماراتي/خليجي","سعودي","مصري","شامي","عراقي","جزائري","ليبي","تونسي","مغربي"]
    dialect = st.selectbox("اللهجة", DIALECTS, key="g_dialect")
    level   = st.selectbox("المستوى", LEVELS, key="g_level")

    st.divider()
    st.markdown("### 🔑 مفتاح OpenAI")
    api_key_input = st.text_input(
        "أدخل مفتاح OpenAI API",
        value=os.getenv("OPENAI_API_KEY",""),
        type="password",
        help="sk-proj-... احصل عليه من platform.openai.com"
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.divider()
    st.markdown(f"### 📊 ملخص سريع")
    st.markdown(f"⭐ **النقاط:** {store.get_points()}")
    badges = store.get_badges()
    if badges:
        st.markdown("🏅 **الألقاب:**")
        for b in badges[-5:]:
            st.markdown(f'<span class="badge-pill">{b}</span>', unsafe_allow_html=True)

# ─── التبويبات ───────────────────────────────────────────────────────────────
tabs = st.tabs(["🔄 التحويل","📝 الاختبارات","🎮 الألعاب","🏆 التحديات","📈 التقدم","😄 اضحك","📚 أدبنا","✍️ التعبير","🎁 الجوائز","👤 البروفايل"])

ai_svc    = OpenAIService(api_key=api_key_input or os.getenv("OPENAI_API_KEY",""))
local_svc = LocalConverter()

# ═══════════════════════════════════════════════════════════════════════
# تبويب 1: التحويل
# ═══════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("🔄 تحويل اللهجة إلى الفصحى")

    col_in, col_out = st.columns(2)
    with col_in:
        st.markdown("**✏️ النص باللهجة:**")
        user_text = st.text_area("", height=180, placeholder="اكتب باللهجة هنا… مثال: وش السالفة؟ أبغي أروح الحين", key="conv_in", label_visibility="collapsed")
        col_b1, col_b2 = st.columns(2)
        do_convert = col_b1.button("🚀 تحويل", type="primary", use_container_width=True)
        do_clear   = col_b2.button("🗑️ مسح", use_container_width=True)
        if do_clear:
            st.session_state["conv_in"] = ""
            st.rerun()

    with col_out:
        st.markdown("**📖 النص بالفصحى:**")
        result_placeholder = st.empty()
        explain_placeholder = st.empty()
        diff_placeholder    = st.empty()

    if do_convert and user_text.strip():
        with st.spinner("جارٍ التحويل..."):
            d = dialect if dialect != "تلقائي" else "إماراتي/خليجي"
            res_ai = ai_svc.convert_dialect_to_msa(text=user_text, dialect=dialect, level=level)

            if res_ai.get("ok"):
                msa  = res_ai["msa"]
                exps = res_ai.get("explanations", [])
                det  = res_ai.get("dialect_detected", "")
                store.add_points(2)
                store.add_history({"type":"تحويل-AI","dialect":dialect,"level":level,"input":user_text,"output":msa})
                mode_lbl = "✅ تحويل بالذكاء الاصطناعي"
            else:
                res_local = local_svc.convert(text=user_text, dialect=d, level=level)
                msa  = res_local.get("msa","")
                exps = res_local.get("explanations", [])
                det  = ""
                store.add_points(1)
                store.add_history({"type":"تحويل-محلي","dialect":dialect,"level":level,"input":user_text,"output":msa})
                mode_lbl = "⚡ تحويل محلي (بدون AI)"

        result_placeholder.markdown(f'<div class="result-box">{msa}</div>', unsafe_allow_html=True)
        if det:
            st.info(f"🔍 اللهجة المكتشفة: **{det}**")
        st.caption(mode_lbl)

        if exps:
            with explain_placeholder.expander("💡 شرح التحويل"):
                for e in exps[:10]:
                    st.markdown(f"- {e}")

        diffs = simple_diff(user_text, msa)
        with diff_placeholder.expander("✨ إبراز التغييرات"):
            for d_line in diffs:
                st.markdown(d_line)

        st.success(f"⭐ رصيدك الآن: {store.get_points()} نقطة")
        st.rerun()

    elif do_convert:
        st.warning("اكتب نصًا أولًا.")

    # آخر التحويلات
    history = store.get_history()
    if history:
        with st.expander("📜 آخر التحويلات"):
            for h in history[:5]:
                st.markdown(f"🕐 `{h.get('ts','')}` | {h.get('type','')} | **{h.get('input','')}** → {h.get('output','')}")

# ═══════════════════════════════════════════════════════════════════════
# تبويب 2: الاختبارات
# ═══════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("📝 اختبارات الفصاحة")

    QUESTIONS_FILE = DATA_DIR / "questions.json"
    def load_questions():
        if QUESTIONS_FILE.exists():
            return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
        return {}

    q_level = st.selectbox("اختر المستوى", ["مبتدئ", "متوسط", "متقدم"], key="q_level")

    if st.button("▶️ بدء اختبار جديد", type="primary"):
        qs = load_questions()
        lvl_qs = qs.get(q_level, [])
        if lvl_qs:
            st.session_state["test_data"] = lvl_qs
            st.session_state["test_idx"]   = 0
            st.session_state["test_score"] = 0
            st.session_state["test_answered"] = False
            st.session_state["test_level"] = q_level
            st.rerun()
        else:
            st.error("لا توجد أسئلة لهذا المستوى.")

    if "test_data" in st.session_state and st.session_state.test_data:
        td    = st.session_state.test_data
        idx   = st.session_state.test_idx
        total = len(td)

        st.progress((idx) / total, text=f"السؤال {idx+1} من {total}")

        if idx < total:
            q = td[idx]
            st.markdown(f"### ❓ {q['q']}")
            choices = q["choices"][1:]  # skip "..."
            choice_key = f"choice_{idx}"
            user_ans = st.radio("اختر إجابتك:", choices, key=choice_key, index=None)

            col1, col2 = st.columns([1,4])
            if col1.button("✅ تأكيد", disabled=(user_ans is None)):
                correct_text = q["choices"][q["answer"] + 1]
                if user_ans == correct_text:
                    st.session_state.test_score += 1
                    store.add_points(3)
                    st.success(f"✅ صحيح! {q['why']}")
                else:
                    st.error(f"❌ خطأ. الإجابة الصحيحة: **{correct_text}**\n\n{q['why']}")
                st.session_state.test_answered = True

            if st.session_state.get("test_answered") and col1.button("⏭️ التالي"):
                st.session_state.test_idx += 1
                st.session_state.test_answered = False
                st.rerun()
        else:
            score   = st.session_state.test_score
            percent = int((score / total) * 100)
            st.balloons()
            st.success(f"🎉 انتهى الاختبار! نتيجتك: **{score}/{total}** ({percent}%)")
            store.add_test_result(st.session_state.test_level, {"score":score,"total":total,"percent":percent})
            if percent >= 80:
                store.add_badge(f"نجاح {st.session_state.test_level}")
                st.success("🏅 حصلت على شارة!")
            if st.button("🔄 اختبار جديد"):
                del st.session_state["test_data"]
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# تبويب 3: الألعاب
# ═══════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("🎮 الألعاب التعليمية")

    game_tab1, game_tab2 = st.tabs(["🃏 مطابقة الكلمات", "🔀 ترتيب الجملة"])

    # ── لعبة 1: مطابقة الكلمات
    with game_tab1:
        st.markdown("**طابق الكلمة العامية بمقابلها الفصيح خلال 30 ثانية!**")

        PAIRS = [
            ("أبغي","أريد"), ("وش","ما"), ("عايز","أريد"),
            ("شو","ماذا"), ("كويس","جيد"), ("مرة","جدًا"),
            ("ماشي","حسنًا"), ("الحين","الآن"), ("مدري","لا أدري"),
            ("مش","ليس"), ("كتير","جدًا"), ("منيح","جيد"),
        ]

        if "wm_pairs" not in st.session_state or st.button("🎲 بدء لعبة جديدة", key="wm_start"):
            selected = random.sample(PAIRS, 5)
            st.session_state["wm_pairs"]   = selected
            st.session_state["wm_score"]   = 0
            st.session_state["wm_current"] = 0
            st.rerun()

        if "wm_pairs" in st.session_state:
            pairs   = st.session_state.wm_pairs
            current = st.session_state.wm_current
            if current < len(pairs):
                dialect_word, correct_fus = pairs[current]
                wrong_options = [p[1] for p in PAIRS if p[1] != correct_fus]
                options = random.sample(wrong_options, 3) + [correct_fus]
                random.shuffle(options)

                st.markdown(f"### الكلمة: **{dialect_word}**")
                chosen = st.radio("اختر المقابل الفصيح:", options, key=f"wm_{current}", index=None)
                if chosen:
                    if chosen == correct_fus:
                        st.session_state.wm_score += 1
                        store.add_points(1)
                        st.success("✅ صحيح!")
                    else:
                        st.error(f"❌ خطأ. الصواب: {correct_fus}")
                    st.session_state.wm_current += 1
                    st.rerun()
            else:
                score = st.session_state.wm_score
                store.set_game_best("word_match_best", score)
                st.success(f"🏆 انتهت اللعبة! نتيجتك: {score}/{len(pairs)} | أفضل نتيجة: {store.get_game_best('word_match_best')}")

    # ── لعبة 2: ترتيب الجملة
    with game_tab2:
        st.markdown("**رتّب كلمات الجملة الفصيحة بشكل صحيح!**")

        SENTENCES = [
            "أريد أن أذهب إلى المدرسة الآن",
            "ماذا تريد أن تفعل اليوم",
            "هل تعرف ما الخبر المهم",
            "أود أن أتعلم العربية الفصحى",
        ]

        if "ro_sentence" not in st.session_state or st.button("🎲 جملة جديدة", key="ro_start"):
            orig = random.choice(SENTENCES)
            words = orig.split()
            shuffled = words[:]
            random.shuffle(shuffled)
            st.session_state["ro_orig"]     = orig
            st.session_state["ro_shuffled"] = shuffled
            st.rerun()

        if "ro_orig" in st.session_state:
            orig     = st.session_state.ro_orig
            shuffled = st.session_state.ro_shuffled
            st.markdown(f"**الكلمات:** {' | '.join(shuffled)}")
            user_order = st.text_input("رتّب الكلمات (افصل بمسافة):", key="ro_input")
            if st.button("✅ تحقق", key="ro_check"):
                if user_order.strip() == orig:
                    store.add_points(2)
                    store.set_game_best("reorder_best", store.get_game_best("reorder_best")+1)
                    st.success("🎉 ممتاز! الترتيب صحيح!")
                else:
                    st.error(f"❌ الترتيب الصحيح: **{orig}**")

# ═══════════════════════════════════════════════════════════════════════
# تبويب 4: التحديات
# ═══════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("🏆 التحديات اليومية")

    challenges = [
        {"title":"تحدي المبتدئ 🌱","desc":"حوّل 3 جمل عامية إلى فصحى","points":10,"done":False},
        {"title":"تحدي المتوسط 📚","desc":"أجب على 5 أسئلة باختبار المستوى المتوسط","points":20,"done":False},
        {"title":"تحدي المتقدم 🎯","desc":"اجتز اختبار المستوى المتقدم بنسبة 80% فأكثر","points":30,"done":False},
        {"title":"تحدي اللاعب 🎮","desc":"العب لعبة مطابقة الكلمات مرتين","points":15,"done":False},
    ]

    cols = st.columns(2)
    for i, ch in enumerate(challenges):
        with cols[i%2]:
            st.markdown(f"""
            <div class="prize-card">
                <h3>{ch['title']}</h3>
                <p>{ch['desc']}</p>
                <p>🏅 <strong>{ch['points']} نقطة</strong></p>
            </div>
            """, unsafe_allow_html=True)

    st.info("💡 أكمل التحديات لتحصل على نقاط إضافية!")

# ═══════════════════════════════════════════════════════════════════════
# تبويب 5: التقدم
# ═══════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("📈 تقدمي")

    prog_level = st.selectbox("اختر المستوى", ["مبتدئ","متوسط","متقدم"], key="prog_level")
    results = store.get_tests(prog_level)

    if results:
        scores = [r.get("percent",0) for r in results[:10]]
        st.line_chart(scores, height=250)
        st.markdown(f"**📊 عدد الاختبارات:** {len(results)} | **🎯 أعلى نسبة:** {max(scores)}%")
        with st.expander("عرض كل النتائج"):
            for r in results[:20]:
                st.markdown(f"- {r.get('percent',0)}%  |  {r.get('score',0)}/{r.get('total',0)}")
    else:
        st.info("لم تجر اختبارات بعد في هذا المستوى.")

    st.divider()
    st.markdown("### 📜 سجل التحويلات")
    history = store.get_history()
    if history:
        for h in history[:10]:
            st.markdown(f"🕐 `{h.get('ts','')}` | {h.get('type','')} | **{h.get('input','')}** → {h.get('output','')}")
    else:
        st.info("لا يوجد سجل حتى الآن.")

# ═══════════════════════════════════════════════════════════════════════
# تبويب 6: اضحك مع الفصحى
# ═══════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("😄 اضحك مع الفصحى")

    JOKES_FILE = DATA_DIR / "jokes.json"
    if JOKES_FILE.exists():
        jokes_data = json.loads(JOKES_FILE.read_text(encoding="utf-8"))
        for cat, jokes in jokes_data.items():
            with st.expander(f"😂 {cat}"):
                for joke in jokes:
                    st.markdown(f"- {joke}")
    else:
        st.info("لا توجد نكت بعد.")

    st.divider()
    st.markdown("### 💬 ترجم نكتة!")
    joke_text = st.text_area("اكتب نكتتك باللهجة هنا:", height=100, key="joke_in")
    if st.button("🎭 فصّح النكتة", type="primary"):
        if joke_text.strip():
            with st.spinner("جارٍ التحويل..."):
                res = ai_svc.convert_dialect_to_msa(joke_text, dialect, level)
                if res.get("ok"):
                    store.add_points(1)
                    st.markdown(f'<div class="result-box">{res["msa"]}</div>', unsafe_allow_html=True)
                else:
                    local = local_svc.convert(joke_text, dialect if dialect != "تلقائي" else "سعودي", level)
                    st.markdown(f'<div class="result-box">{local["msa"]}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# تبويب 7: أدبنا الفصيح
# ═══════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader("📚 أدبنا الفصيح")

    STORIES_FILE = DATA_DIR / "stories.json"
    if STORIES_FILE.exists():
        stories_data = json.loads(STORIES_FILE.read_text(encoding="utf-8"))
        for cat, items in stories_data.items():
            with st.expander(f"📖 {cat}"):
                for item in items:
                    st.markdown(f"**{item['title']}**")
                    st.markdown(f"> {item['text']}")
                    st.divider()
    else:
        st.info("لا توجد قصص بعد.")

# ═══════════════════════════════════════════════════════════════════════
# تبويب 8: نافذة التعبير
# ═══════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.subheader("✍️ نافذة التعبير الحر")
    st.markdown("اكتب ما تريد باللهجة وسنحوّله إلى فصيح جميل!")

    expr_text = st.text_area("اكتب هنا:", height=150, key="expr_text")
    if st.button("✨ فصّح كلامي", type="primary", key="expr_btn"):
        if expr_text.strip():
            with st.spinner("جارٍ التعبير..."):
                res = ai_svc.convert_dialect_to_msa(expr_text, dialect, level)
                if res.get("ok"):
                    store.add_points(2)
                    st.markdown(f'<div class="result-box">{res["msa"]}</div>', unsafe_allow_html=True)
                    if res.get("explanations"):
                        with st.expander("💡 شرح"):
                            for e in res["explanations"]:
                                st.markdown(f"- {e}")
                else:
                    local = local_svc.convert(expr_text, dialect if dialect != "تلقائي" else "مصري", level)
                    st.markdown(f'<div class="result-box">{local["msa"]}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# تبويب 9: الجوائز والألقاب
# ═══════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.subheader("🎁 الجوائز والألقاب")

    PRIZES_FILE = DATA_DIR / "prizes.json"
    current_points = store.get_points()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏅 الألقاب")
        TITLES = [
            {"name":"فصيح ناشئ 🌱",    "need": 20},
            {"name":"سفير الفصحى 🌟",  "need": 80},
            {"name":"أديب صغير 📖",    "need": 150},
            {"name":"بلاغي محترف 🎓",  "need": 250},
        ]
        for t in TITLES:
            progress = min(1.0, current_points / t["need"])
            if current_points >= t["need"]:
                st.success(f"✅ {t['name']} - مفتوح!")
                store.add_badge(t["name"])
            else:
                st.markdown(f"🔒 {t['name']} — يحتاج {t['need']} نقطة")
                st.progress(progress)

    with col_b:
        st.markdown("### 🎁 مكافآت")
        if PRIZES_FILE.exists():
            prizes_data = json.loads(PRIZES_FILE.read_text(encoding="utf-8"))
            for cat, items in prizes_data.items():
                if cat == "جوائز تعليمية":
                    for prize in items:
                        cost = prize.get("cost", 0)
                        can_redeem = current_points >= cost
                        if can_redeem:
                            st.success(f"🎁 {prize['name']} — {cost} نقطة ✅")
                        else:
                            st.info(f"🎁 {prize['name']} — {cost} نقطة (تحتاج {cost - current_points} نقطة إضافية)")

    st.divider()
    st.markdown(f"### 💰 رصيدك الحالي: **{current_points} نقطة**")
    earned = store.get_badges()
    if earned:
        st.markdown("**🏅 ألقابك المكتسبة:**")
        badge_html = " ".join([f'<span class="badge-pill">{b}</span>' for b in earned])
        st.markdown(badge_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# تبويب 10: البروفايل
# ═══════════════════════════════════════════════════════════════════════
with tabs[9]:
    st.subheader("👤 البروفايل الشخصي")

    p = store.get_profile()
    col1, col2 = st.columns([2,1])
    with col1:
        new_name   = st.text_input("الاسم:", value=p.get("name",""), key="pf_name")
        new_school = st.text_input("المدرسة:", value=p.get("school",""), key="pf_school")
        new_grade  = st.text_input("الصف:", value=p.get("grade",""), key="pf_grade")
        new_avatar = st.text_input("الأيقونة (رمز تعبيري):", value=p.get("avatar","👤"), key="pf_avatar")

        if st.button("💾 حفظ البروفايل", type="primary"):
            store.set_profile(new_name, new_school, new_grade, new_avatar)
            st.success("✅ تم حفظ البروفايل!")
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="num">{store.get_points()}</div>
            <div class="lbl">⭐ نقطة</div>
        </div>
        """, unsafe_allow_html=True)

        tests_all = []
        for lvl in ["مبتدئ","متوسط","متقدم"]:
            tests_all.extend(store.get_tests(lvl))
        avg = int(sum(t.get("percent",0) for t in tests_all)/len(tests_all)) if tests_all else 0

        st.markdown(f"""
        <div class="stat-card">
            <div class="num">{len(tests_all)}</div>
            <div class="lbl">📝 اختبار</div>
        </div>
        <div class="stat-card">
            <div class="num">{avg}%</div>
            <div class="lbl">🎯 متوسط الدقة</div>
        </div>
        <div class="stat-card">
            <div class="num">{len(store.get_history())}</div>
            <div class="lbl">🔄 تحويل</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🏅 ألقابك")
    for b in store.get_badges():
        st.markdown(f'<span class="badge-pill">{b}</span>', unsafe_allow_html=True)
