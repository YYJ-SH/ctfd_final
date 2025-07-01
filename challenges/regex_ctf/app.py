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
    return "/challenges/regex_ctf"

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
    app.config['APPLICATION_ROOT'] = '/challenges/regex_ctf'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

# 기존 코드 유지하면서 static 경로 수정
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        user_input = request.form.get("flag", "")
        if re.fullmatch(pattern, user_input):
            if user_input == get_flag():
                result = "🎉 정답입니다! 플래그가 정확합니다."
            else:
                result = "❌ 형식은 맞지만 내용이 틀렸습니다."
        else:
            result = "🚫 플래그 형식이 올바르지 않습니다."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
