from flask import Flask, request, make_response
import os

app = Flask(__name__)

# flag.txt에서 플래그 읽기
def get_flag():
    try:
        with open("flag.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "FLAG_NOT_FOUND"

@app.route("/")
def index():
    resp = make_response("""
        <h1>쿠키 확인기(Cookie Checker)에 오신 것을 환영합니다!</h1>
        <p>오직 관리자만 플래그를 볼 수 있습니다. <a href='flag'>/flag</a>에 접근해 보세요.</p>
    """)
    if not request.cookies.get("is_admin"):
        resp.set_cookie("is_admin", "False")
    return resp

@app.route("/flag")
def flag():
    is_admin = request.cookies.get("is_admin", "False")
    if is_admin == "True":
        flag = get_flag()
        return f"<h1>플래그: {flag}</h1>"
    else:
        return "<h1>접근 거부됨. 당신은 관리자가 아닙니다.</h1>", 403

if __name__ == "__main__":
    app.run(debug=True)
 