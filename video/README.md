# video/ — الفيديو النهائي وحزمة البناء

| المسار | الوصف |
|---|---|
| `render/cashless-future.mp4` | **الفيديو النهائي** — 1920×1080، 30fps، 7:23، صوت AAC ستيريو −14 LUFS (~62 MB، غير مرفوع إلى Git) |
| `assets/` | 9 صور B-roll مولّدة + المصغّرة `thumbnail_1280x720.jpg` |
| `audio/` | 6 مقاطع تعليق صوتي (mp3) |
| `build/make_video.py` | سكربت المونتاج الكامل (Ken Burns + ASS RTL + موسيقى مولّدة + تطبيع جهارة) |
| `build/fonts/` | خطوط Tajawal وNoto Naskh Arabic (OFL) |

## إعادة البناء

```bash
pip install --break-system-packages imageio-ffmpeg
cd video/build && python3 make_video.py
```

يعيد بناء الفيديو كاملًا من الصفر (≈ 7 دقائق معالجة على CPU عادي).

## تعديل سريع

كل شيء في `build/make_video.py`:
- `SEGMENTS`: المخطط الزمني — صورة، مدة، حركة الكاميرا، والنصوص على الشاشة `(بداية، نهاية، نمط، نص)`.
- `ASS_HEADER`: الخطوط والألوان.
- الأنماط: `Big` (رقم/عبارة كبيرة)، `Title`، `Cap` (ترجمة سفلية)، `Badge` (شريط الفصل).

## ملاحظة على المصادر

الصور الصورية (B-roll) **مولّدة** لهذا الفيديو — لا حقوق طرف ثالث، ولا لقطات إخبارية.
الأرقام المعروضة على الشاشة مطابقة لجدول المصادر في
[`content/youtube/cashless-future.md`](../content/youtube/cashless-future.md) (Riksbank، ECB، World Bank، RBI، Xinhua، Allium/DefiLlama — حتى أكتوبر 2026).
