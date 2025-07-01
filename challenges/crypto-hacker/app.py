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
    return "/challenges/crypto-hacker"

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
    app.config['APPLICATION_ROOT'] = '/challenges/crypto-hacker'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

# 기존 코드 유지하면서 static 경로 수정
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    return render_template('index.html', encoded_message=encoded_message, encoded_path=encoded_path)

@app.route('/agent-chatting')
def agent_chatting():
    # 쿠키에서 티켓 수 확인
    tickets = request.cookies.get('tickets', '0')
    try:
        ticket_count = int(tickets)
    except:
        ticket_count = 0
    
    # 세션에서 경고 횟수 확인
    warnings = session.get('warnings', 0)
    
    names = {
        "MICHAEL", "MICHAEL", "EMILY", "JESSICA", "MATTHEW", "LAUPA", "KAPIE", 
        "FHOMAS", "LISA", "BRIAN", "AMY", "ROBERT", "ERICA", "ANDREW", "HOLLY", 
        "DANIEL", "JULIE", "EIEPHEN", "RACHEL", "MELLIE", "ANGELA", "JESEPH", 
        "KNELY", "AMBER", "PETER", "THOMAS", "LISA", "ERIC", "HEATHER", "RYAN", 
        "ANGELA", "JOSEPH", "KELLY", "JOSEPH", "ANNA", "ANGELA", "JOSEPH", 
        "HERFEY", "KRISTEN", "PAUL", "ALIAM", "SCOTT", "ANNA", "TIMOTAY", 
        "MIARA", "SUSAN", "ANNA", "CHERYL", "CAROL"
    }
    
    # 기본 쿠키 설정 (tickets=0)
    resp = make_response(render_template('agent_chatting.html', names=names, ticket_count=ticket_count, warnings=warnings))
    if not request.cookies.get('tickets'):
        resp.set_cookie('tickets', '0')
    
    return resp

@app.route('/agent-chat/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    selected_name = data.get('name')
    message = data.get('message')
    
    # 쿠키에서 티켓 수 확인
    tickets = request.cookies.get('tickets', '0')
    try:
        ticket_count = int(tickets)
    except:
        ticket_count = 0
    
    # 세션에서 경고 횟수 확인
    warnings = session.get('warnings', 0)
    
    # 경고 3회 이상이면 차단
    if warnings >= 3:
        return jsonify({
            'success': False, 
            'message': '경고 3번이 초과되어 요청 전송이 차단되었습니다. 힌트 3번을 결제하시거나 주최측에 문의해 주세요.'
        })
    
    # 티켓이 3개 초과면 경고
    if ticket_count > 3:
        session['warnings'] = warnings + 1
        return jsonify({
            'success': False, 
            'message': f'수상한 활동이 감지되었습니다. 경고 {session["warnings"]}/3'
        })
    
    # 티켓이 없으면 메시지 전송 불가
    if ticket_count <= 0:
        return jsonify({
            'success': False, 
            'message': '접속 토큰이 부족합니다. 토큰이 있어야 메시지를 전송할 수 있습니다.'
        })
    
    # RACHEL을 선택하고 FLAG/플래그/flag 키워드가 포함된 메시지인지 확인
    if selected_name == 'RACHEL' and any(keyword in message.lower() for keyword in ['flag', '플래그']):
        resp = make_response(jsonify({
            'success': True, 
            'message': '접촉 성공. 요청된 정보: YBG{C3aser_and_bas3_sixty4}',
            'ticket_count': ticket_count - 1
        }))
        resp.set_cookie('tickets', str(ticket_count - 1))
        return resp
    else:
        resp = make_response(jsonify({
            'success': True, 
            'message': f'{selected_name}에게 메시지 전송 완료. 응답이 없습니다.',
            'ticket_count': ticket_count - 1
        }))
        resp.set_cookie('tickets', str(ticket_count - 1))
        return resp

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)