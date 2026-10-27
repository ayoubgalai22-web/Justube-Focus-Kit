#!/usr/bin/env python3
"""
خادم معاينة محلي للفيديو — يدعم Range (تقديم/تأخير الفيديو) وCORS.
الاستخدام:  python3 serve.py [port]
يخدم المجلد video/render (الفيديو) + assets (المصغّرة) على 0.0.0.0
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(HERE)
RENDER = os.path.join(VIDEO, "render")
ASSETS = os.path.join(VIDEO, "assets")

PAGE = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سر اختفاء العملات الورقية في المستقبل</title>
<style>
  :root { --navy:#0B1220; --mint:#00E5A0; --cream:#F2E8D5; --grey:#A7B0C0; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--navy); color:#fff;
         font-family: "Segoe UI", Tahoma, system-ui, sans-serif; }
  .wrap { max-width:1100px; margin:0 auto; padding:28px 18px 60px; }
  h1 { font-size:clamp(20px,3.4vw,34px); margin:0 0 6px; line-height:1.35; }
  .meta { color:var(--grey); font-size:14px; margin-bottom:18px; }
  .meta b { color:var(--cream); font-weight:600; }
  video { width:100%; border-radius:14px; background:#000; display:block;
          box-shadow:0 18px 50px rgba(0,0,0,.55); }
  .row { display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }
  a.btn { display:inline-block; text-decoration:none; padding:12px 18px; border-radius:10px;
          font-weight:700; font-size:15px; transition:.15s; }
  .dl { background:var(--mint); color:#062018; }
  .dl:hover { filter:brightness(1.1); }
  .alt { border:1px solid #2a3a52; color:var(--cream); }
  .alt:hover { border-color:var(--mint); color:var(--mint); }
  .hint { margin-top:22px; color:var(--grey); font-size:13px; line-height:2; }
  .hint code { background:#141d2e; padding:2px 7px; border-radius:5px; color:var(--mint); }
</style>
</head>
<body>
<div class="wrap">
  <h1>سر اختفاء العملات الورقية في المستقبل</h1>
  <div class="meta"><b>7:23</b> · 1920×1080 · 30fps · صوت ستيريو −14 LUFS</div>
  <video src="/cashless-future.mp4" poster="/thumbnail.jpg" controls preload="metadata" playsinline></video>
  <div class="row">
    <a class="btn dl" href="/cashless-future.mp4" download>⬇ تحميل الفيديو (62 MB)</a>
    <a class="btn alt" href="/thumbnail.jpg" download>المصغّرة</a>
  </div>
  <div class="hint">
    للتشغيل داخل مشغّل خارجي: <code>/cashless-future.mp4</code><br>
    لتضمينه في صفحة: <code>&lt;video src="…/cashless-future.mp4" controls&gt;&lt;/video&gt;</code>
  </div>
</div>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def _send_headers(self, code, ctype, length=None, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Accept-Ranges", "bytes")
        if length is not None:
            self.send_header("Content-Length", str(length))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        path = unquote(self.path.split("?")[0])

        if path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self._send_headers(200, "text/html; charset=utf-8", len(body))
            if not head:
                self.wfile.write(body)
            return

        if path == "/thumbnail.jpg":
            fp = os.path.join(ASSETS, "thumbnail_1280x720.jpg")
        else:
            fp = os.path.join(RENDER, os.path.basename(path))

        if not os.path.isfile(fp):
            body = b"not found"
            self._send_headers(404, "text/plain; charset=utf-8", len(body))
            if not head:
                self.wfile.write(body)
            return

        size = os.path.getsize(fp)
        ctype = "video/mp4" if fp.endswith(".mp4") else "image/jpeg"
        rng = self.headers.get("Range")

        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng.strip())
            start = int(m.group(1)) if m and m.group(1) else 0
            end = int(m.group(2)) if m and m.group(2) else size - 1
            end = min(end, size - 1)
            if start > end:
                self._send_headers(416, "text/plain", 0,
                                   {"Content-Range": f"bytes */{size}"})
                return
            length = end - start + 1
            self._send_headers(206, ctype, length,
                               {"Content-Range": f"bytes {start}-{end}/{size}"})
            if head:
                return
            with open(fp, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(262144, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            return

        # بث كامل (يسمح بالتشغيل التدريجي)
        self._send_headers(200, ctype, size)
        if head:
            return
        with open(fp, "rb") as f:
            while True:
                chunk = f.read(262144)
                if not chunk:
                    break
                self.wfile.write(chunk)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"serving {RENDER} on 0.0.0.0:{port}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
