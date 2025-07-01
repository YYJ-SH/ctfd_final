from flask import Flask, request, redirect, make_response, render_template
import os

app = Flask(__name__)
SESSIONS = {}
FLAG = "YBG{y0u_fixed_your_0wn_session}"

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session_id = request.cookies.get('auth')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'adminpass':
            if not session_id:
                session_id = 'sess_' + username

            SESSIONS[session_id] = username
            resp = make_response(redirect('/flag'))
            resp.set_cookie('auth', session_id)
            return resp
        return "잘못된 자격 증명입니다."

    return render_template("login.html")

@app.route('/flag')
def flag():
    session_id = request.cookies.get('auth')
    if session_id in SESSIONS and SESSIONS[session_id] == 'admin':
        return f"<h2>플래그: {FLAG}</h2>"
    return "관리자로 로그인해야 합니다."

@app.route('/logout')
def logout():
    session_id = request.cookies.get('auth')
    if session_id in SESSIONS:
        del SESSIONS[session_id]
    resp = make_response("로그아웃되었습니다.")
    resp.set_cookie('auth', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
