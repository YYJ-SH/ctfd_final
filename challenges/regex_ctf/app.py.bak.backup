from flask import Flask, request, render_template
import re

app = Flask(__name__)

pattern = r"^YBG\{[A-Z]_[0-9]{4}_[a-f0-9]{6}\}$"

def get_flag():
    try:
        with open("flag.txt", "r") as f:
            return f.read().strip()
    except:
        return "FLAG_NOT_FOUND"

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
    app.run(debug=True)
