# مُفصِّحُ اللِّسان - مترجم اللهجات إلى الفصحى

## مشكلة أمنية عاجلة ⚠️
**تحذير**: مفتاح OpenAI API كان مكشوفاً في الكود! يجب عليك:
1. الذهاب فوراً إلى [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. حذف المفتاح القديم
3. إنشاء مفتاح جديد
4. وضعه في متغيرات البيئة (انظر أدناه)

---

## 🌐 النشر على الإنترنت (Streamlit Cloud - مجاني)

### الخطوة 1: رفع على GitHub
```bash
git init
git add .
git commit -m "Initial commit - مُفصِّحُ اللِّسان"
git branch -M main
git remote add origin https://github.com/USERNAME/mofsih-app.git
git push -u origin main
```

### الخطوة 2: النشر على Streamlit Cloud
1. اذهب إلى [share.streamlit.io](https://share.streamlit.io)
2. سجّل بحساب GitHub
3. اضغط "New app"
4. اختر المستودع والملف `app.py`
5. في **Secrets** أضف:
```toml
OPENAI_API_KEY = "sk-proj-..."
```
6. اضغط "Deploy!"

---

## 🐳 النشر بـ Docker (للسيرفرات)
```bash
docker build -t mofsih-app .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-proj-... mofsih-app
```

---

## 🚀 بدائل النشر المجانية
- [Railway](https://railway.app) - مجاني ويدعم Python
- [Render](https://render.com) - مجاني مع نوم
- [Hugging Face Spaces](https://huggingface.co/spaces) - مجاني ويدعم Streamlit

---

## تشغيل محلي
```bash
pip install -r requirements.txt
streamlit run app.py
```
