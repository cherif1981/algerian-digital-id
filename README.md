# Algerian Digital ID 🆔

نظام التعرف الضوئي (OCR) على البطاقة الوطنية الجزائرية
لاستخراج البيانات والتحقق منها تلقائياً.

## ✨ الميزات

- 🔍 استخراج النص من صور البطاقة (عربي/فرنسي)
- 🧹 تنظيف الصور ومعالجتها مسبقاً
- ✅ التحقق من صحة الحقول (NIN, تواريخ, أسماء)
- 🔗 المطابقة الضبابية مع قواعد بيانات مرجعية
- 🌐 REST API باستخدام FastAPI
- 🐳 Docker للتشغيل السريع

## 🚀 البدء السريع

### المتطلبات
- Python 3.10+
- Tesseract OCR (مع اللغات: ara, fra, eng)

### التثبيت
```bash
git clone https://github.com/YOUR_USERNAME/algerian-digital-id.git
cd algerian-digital-id
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# أو: .venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env