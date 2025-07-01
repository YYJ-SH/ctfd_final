import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for

import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import WSGIRequestHandler

# SCRIPT_NAME 환경변수 처리를 위한 미들웨어
class ScriptNameMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        script_name = os.environ.get('SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        return self.app(environ, start_response)


app = Flask(__name__)
# 현재 앱의 base path 설정
import os
from urllib.parse import urljoin
from flask import request

def get_base_path():
    """현재 앱의 base path 반환"""
    return "/challenges/mobile_only"

def url_for_relative(endpoint):
    """상대 경로 URL 생성"""
    base = get_base_path()
    if endpoint == "index" or endpoint == "/":
        return base + "/"
    elif endpoint.startswith("/"):
        return base + endpoint
    else:
        return base + "/" + endpoint

# 템플릿에서 사용할 수 있도록 context processor 추가
@app.context_processor
def inject_base_path():
    return {
        'base_path': get_base_path(),
        'url_for_relative': url_for_relative
    }



# WSGI 미들웨어 적용
app.wsgi_app = ScriptNameMiddleware(app.wsgi_app)

# 프로덕션 환경에서 APPLICATION_ROOT 설정
if os.environ.get('FLASK_ENV') == 'production':
    app.config['APPLICATION_ROOT'] = '/challenges/mobile_only'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

# 기존 코드 유지하면서 static 경로 수정
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mobile Only</title>
    </head>
    <body>
        <h2>모바일 사용자 전용 사이트입니다.</h2>
        <!-- 관리자 페이지는 모바일에서만 접근 가능하다는 소문이 있습니다... -->
        <p><a href='admin'>관리자 페이지로 이동</a></p>
    </body>
    </html>
    """

@app.route('/admin')
def admin():
    ua = request.headers.get('User-Agent', '')
    print(f"[LOG] 접속 User-Agent: {ua}")

    if 'Mobile' not in ua:
        return """
        <h3>이 페이지는 모바일 브라우저에서만 접근할 수 있습니다.</h3>
        <p>F12 → Device Mode 또는 curl로 시도해 보세요.</p>
        """, 403

    try:
        with open('flag.txt') as f:
            flag = f.read().strip()
        return f"""
        <h3>관리자 페이지에 오신 것을 환영합니다!</h3>
        <p>FLAG: {flag}</p>
        """
    except FileNotFoundError:
        return "<h3>FLAG 파일이 없습니다.</h3>", 500

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /admin", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
