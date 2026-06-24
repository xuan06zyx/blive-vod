# -*- coding: utf-8 -*-
"""
二维码展示页面 - 使用本地HTTP服务器展示B站登录二维码
启动后自动在浏览器中打开二维码页面
"""
import os
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

_server = None
_qr_url = ""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>B站扫码登录</title>
    <script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 420px;
            width: 90%;
        }
        .title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 14px;
            color: #666;
            margin-bottom: 24px;
        }
        .qr-container {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            display: inline-block;
            margin-bottom: 20px;
        }
        #qrcode img {
            display: block;
        }
        .status {
            font-size: 14px;
            color: #fb7299;
            margin-top: 16px;
            font-weight: 500;
        }
        .tip {
            font-size: 12px;
            color: #999;
            margin-top: 12px;
        }
        .bili-logo {
            font-size: 36px;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="bili-logo">📺</div>
        <div class="title">B站扫码登录</div>
        <div class="subtitle">请使用哔哩哔哩手机APP扫描二维码</div>
        <div class="qr-container">
            <div id="qrcode"></div>
        </div>
        <div class="status">等待扫码中...</div>
        <div class="tip">扫码后请在手机上确认登录<br>登录成功后此页面会自动关闭</div>
    </div>
    <script>
        var qr = qrcode(0, 'M');
        qr.addData('{qr_url_escaped}');
        qr.make();
        document.getElementById('qrcode').innerHTML = qr.createImgTag(5, 10);
    </script>
</body>
</html>"""


class QRHandler(BaseHTTPRequestHandler):
    """处理二维码页面请求"""

    def do_GET(self):
        if self.path == "/" or self.path == "/qr":
            # 对URL进行JavaScript字符串转义
            escaped_url = _qr_url.replace("\\", "\\\\").replace("'", "\\'").replace("&", "\\x26")
            html = HTML_TEMPLATE.replace("{qr_url_escaped}", escaped_url)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/close":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            # 关闭服务器
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """静默日志，不在终端输出HTTP请求"""
        pass


def show_qr_page(qr_url: str, port: int = 19820):
    """
    启动本地HTTP服务器并在浏览器中打开二维码页面
    :param qr_url: B站登录二维码URL
    :param port: 本地服务器端口
    """
    global _server, _qr_url
    _qr_url = qr_url

    _server = HTTPServer(("127.0.0.1", port), QRHandler)
    # 在后台线程运行服务器
    server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
    server_thread.start()

    # 自动打开浏览器
    webbrowser.open(f"http://127.0.0.1:{port}/qr")
    print(f"[登录] 二维码页面已在浏览器中打开: http://127.0.0.1:{port}/qr")


def close_qr_page():
    """关闭二维码页面服务器"""
    global _server
    if _server:
        try:
            _server.shutdown()
        except Exception:
            pass
        _server = None
