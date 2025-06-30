from flask import Flask, request, render_template_string
import sqlite3, random

app = Flask(__name__)

# 플래그를 파일에서 읽어오기
def read_flag_file(path, default="[**FLAG**]"):
    try:
        return open(path, 'r').read().strip()
    except:
        return default

FLAG1 = read_flag_file('./flag.txt')
FLAG2 = read_flag_file('./fake_flag_1.txt')
FLAG3 = read_flag_file('./fake_flag_2.txt')

CHARACTER_FLAGS = {
    "엘싸": FLAG1,
    "올랄프": FLAG2,
    "쿠리수토푸": FLAG3,
}

CHARACTER_RESPONSES = {
    "엘싸": [
        "마법을 어떻게 쓰냐고? 그걸 알려주면 마법이 아니지~",
        "마법은 마음으로 느끼는 거야.",
        "차가운 얼음보다 차가운 진실을 원해?"
    ],
    "올랄프": [
        "사랑? 눈사람도 사랑받고 싶어~",
        "사랑은 따뜻한 핫초코 같은 거야!",
        "사랑이 뭔지는 모르지만 눈이 좋아!"
    ],
    "쿠리수토푸": [
        "트롤은 오늘도 트롤링 중~",
        "트롤은 계획이 다 있지!",
        "누구보다 장난을 잘 치는 게 바로 트롤!"
    ]
}

# SQLite 쿼리 실행
def run_query(query):
    print(f"[DEBUG] Executing query: {query}")
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        print(f"[DEBUG] Query result: {rows}")
        return rows
    except Exception as e:
        print(f"[DEBUG] Query error: {e}")
        return []

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⛄ 안놔의 일상 ⛄</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Jua', cursive;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        /* 눈송이 애니메이션 */
        .snowflake {
            position: absolute;
            top: -10px;
            color: white;
            user-select: none;
            pointer-events: none;
            z-index: 1;
        }
        
        @keyframes snowfall {
            from {
                transform: translateY(-100vh) rotate(0deg);
            }
            to {
                transform: translateY(100vh) rotate(360deg);
            }
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            position: relative;
            z-index: 2;
        }
        
        h1 {
            color: #1976d2;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        h3 {
            color: #1565c0;
            text-align: center;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        h5 {
            color: #0d47a1;
            text-align: center;
            margin-bottom: 30px;
            font-style: italic;
        }
        
        .form-container {
            background: linear-gradient(45deg, #e1f5fe, #f3e5f5);
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            color: #0d47a1;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 3px solid #42a5f5;
            border-radius: 25px;
            font-size: 1.1em;
            font-family: 'Jua', cursive;
            background: rgba(255, 255, 255, 0.9);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #1976d2;
            box-shadow: 0 0 20px rgba(25, 118, 210, 0.3);
            transform: scale(1.02);
        }
        
        button {
            background: linear-gradient(45deg, #42a5f5, #1976d2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            font-family: 'Jua', cursive;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(25, 118, 210, 0.3);
            display: block;
            margin: 0 auto;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(25, 118, 210, 0.4);
            background: linear-gradient(45deg, #1976d2, #0d47a1);
        }
        
        .hint-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #1976d2;
            text-decoration: none;
            font-size: 1.2em;
            padding: 10px 20px;
            border: 2px solid #42a5f5;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.5);
            transition: all 0.3s ease;
        }
        
        .hint-link:hover {
            background: #42a5f5;
            color: white;
            transform: scale(1.05);
        }
        
        /* 캐릭터 아이콘들 */
        .characters {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        
        .character {
            text-align: center;
            padding: 10px;
        }
        
        .character-icon {
            font-size: 3em;
            margin-bottom: 5px;
        }
        
        .character-name {
            color: #1565c0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <script>
        // 눈송이 생성
        function createSnowflake() {
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.innerHTML = '❄';
            snowflake.style.left = Math.random() * 100 + '%';
            snowflake.style.fontSize = Math.random() * 20 + 10 + 'px';
            snowflake.style.animationDuration = Math.random() * 3 + 2 + 's';
            snowflake.style.animation = `snowfall ${snowflake.style.animationDuration} linear infinite`;
            document.body.appendChild(snowflake);
            
            setTimeout(() => {
                snowflake.remove();
            }, 5000);
        }
        
        setInterval(createSnowflake, 300);
    </script>
    
    <div class="container">
        <h1>⛄ 안놔의 일상 ⛄</h1>
        
        <div class="characters">
            <div class="character">
                <div class="character-icon">❄️</div>
                <div class="character-name">엘싸</div>
            </div>
            <div class="character">
                <div class="character-icon">⛄</div>
                <div class="character-name">올랄프</div>
            </div>
            <div class="character">
                <div class="character-icon">🗿</div>
                <div class="character-name">쿠리수토푸</div>
            </div>
        </div>
        
        <h3>엘싸, 올랄프, 쿠리수토푸에게 말을 걸어보세요.<br>
        과연 어떻게 해야 플래그를 얻을 수 있을까요?</h3>
        <h5>이름을 부르지 않으면 누구에게 말을 거는지 친구들이 모를 수도 있습니다!</h5>
        
        <div class="form-container">
            <form method="POST" action="/submit">
                <label for="message">하고싶은 말:</label>
                <input type="text" id="message" name="message" placeholder="여기에 메시지를 입력하세요...">
                <button type="submit">✨ 전송 ✨</button>
            </form>
        </div>
        
        <a href="/hint" class="hint-link">💡 힌트 보기</a>
    </div>
</body>
</html>
    ''')

@app.route('/hint')
def hint():
    return render_template_string('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💡 힌트 - 안놔의 일상</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Jua', cursive;
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 50%, #a5d6a7 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
            color: #2e7d32;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        ul {
            list-style: none;
            padding: 0;
        }
        
        li {
            background: linear-gradient(45deg, #f1f8e9, #e8f5e8);
            margin: 15px 0;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #4caf50;
            font-size: 1.1em;
            line-height: 1.6;
            color: #1b5e20;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        li:hover {
            transform: translateX(10px);
        }
        
        li::before {
            content: "🔍 ";
            font-size: 1.2em;
            margin-right: 10px;
        }
        
        .back-button {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #2e7d32;
            text-decoration: none;
            font-size: 1.3em;
            padding: 15px 30px;
            border: 3px solid #4caf50;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.8);
            transition: all 0.3s ease;
            max-width: 200px;
            margin: 30px auto 0;
        }
        
        .back-button:hover {
            background: #4caf50;
            color: white;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>💡 힌트</h2>
        
        <ul>
            <li>친구들은 당신이 한 말을 그들의 기억 속에서 찾으려고 해요.</li>
            <li>그 기억은 단순한 회상이 아니라, 무언가를 조회하는 구조에 가깝죠.</li>
            <li>친구들은 아주 특정한 기억을 떠올릴 때에만, 진짜 말을 해줍니다.</li>
            <li>그 말 속에는… 음, 어떤 상징적인 '단어'가 들어 있어야 하는 걸지도요.</li>
            <li>기억을 조작해서 특정 '단어'가 결과에 포함되게 만들 수 있다면…?</li>
        </ul>

        <a href="/" class="back-button">🏠 돌아가기</a>
    </div>
</body>
</html>
    ''')

@app.route('/submit', methods=["POST"])
def submit():
    message = request.form.get('message', '')

    query = f"SELECT * FROM users WHERE message = '{message}'"
    query_result = run_query(query)

    # 캐릭터 선택
    if '마법' in message or '엘싸' in message:
        speaker = '엘싸'
        character_icon = '❄️'
        character_color = '#1976d2'
    elif '사랑' in message or '올랄프' in message:
        speaker = '올랄프'
        character_icon = '⛄'
        character_color = '#ff9800'
    elif '트롤' in message or '쿠리수토푸' in message:
        speaker = '쿠리수토푸'
        character_icon = '🗿'
        character_color = '#795548'
    else:
        return render_template_string('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>응답 - 안놔의 일상</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        body {
            font-family: 'Jua', cursive;
            background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        p {
            font-size: 1.5em;
            color: #c2185b;
            margin-bottom: 30px;
        }
        button {
            background: linear-gradient(45deg, #e91e63, #c2185b);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            font-family: 'Jua', cursive;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <p>😕 누구에게 말을 거는지 모르겠네?</p>
        <form method="GET" action="/">
            <button type="submit">🏠 다시 말 걸기</button>
        </form>
    </div>
</body>
</html>
        ''')

    if query_result and any(row for row in query_result if any(row)):
        result_html = repr(query_result)
    else:
        result_html = "쿼리 결과 없음"

    # 반응 조건
    if query_result:
        if speaker == '엘싸' and any("flag" in str(r).lower() for r in query_result):
            response = f"{CHARACTER_FLAGS[speaker]}"
            is_flag = True
        elif speaker == '올랄프' and any("flag" in str(r).lower() for r in query_result):
            response = f"{CHARACTER_FLAGS[speaker]}"
            is_flag = True
        elif speaker == '쿠리수토푸' and any("flag" in str(r).lower() for r in query_result):
            response = f"{CHARACTER_FLAGS[speaker]}"
            is_flag = True
        else:
            response = "어...? 이 말은 어딘가에서 본 것 같은데...!"
            is_flag = False
    else:
        response = random.choice(CHARACTER_RESPONSES[speaker])
        is_flag = False

    return render_template_string(f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>응답 - 안놔의 일상</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Jua', cursive;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }}
        
        .snowflake {{
            position: absolute;
            top: -10px;
            color: white;
            user-select: none;
            pointer-events: none;
            z-index: 1;
        }}
        
        @keyframes snowfall {{
            from {{
                transform: translateY(-100vh) rotate(0deg);
            }}
            to {{
                transform: translateY(100vh) rotate(360deg);
            }}
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 2;
        }}
        
        h1 {{
            color: {character_color};
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .character-response {{
            background: linear-gradient(45deg, rgba(255, 255, 255, 0.9), rgba(240, 248, 255, 0.9));
            border: 3px solid {character_color};
            border-radius: 20px;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .character-icon {{
            font-size: 4em;
            margin-bottom: 15px;
        }}
        
        .character-name {{
            color: {character_color};
            font-size: 1.5em;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        
        .response-text {{
            font-size: 1.3em;
            color: #333;
            line-height: 1.6;
            {'background: linear-gradient(45deg, #ffd700, #ffed4e); padding: 20px; border-radius: 15px; font-weight: bold; border: 3px solid #ffc107;' if is_flag else ''}
        }}
        
        .query-result {{
            background: #f5f5f5;
            border: 2px solid #ddd;
            border-radius: 15px;
            padding: 20px;
            margin: 30px 0;
            font-family: 'Courier New', monospace;
        }}
        
        .query-result h3 {{
            color: #666;
            margin-bottom: 15px;
            font-family: 'Jua', cursive;
        }}
        
        .query-result p {{
            background: #fff;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #ccc;
            word-break: break-all;
        }}
        
        button {{
            background: linear-gradient(45deg, {character_color}, {character_color}dd);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            font-family: 'Jua', cursive;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            display: block;
            margin: 30px auto 0;
        }}
        
        button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }}
        
        {'@keyframes celebration { 0%, 100% { transform: scale(1) rotate(0deg); } 25% { transform: scale(1.1) rotate(-5deg); } 75% { transform: scale(1.1) rotate(5deg); } } .celebration { animation: celebration 0.6s ease-in-out infinite; }' if is_flag else ''}
    </style>
</head>
<body>
    <script>
        function createSnowflake() {{
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.innerHTML = '❄';
            snowflake.style.left = Math.random() * 100 + '%';
            snowflake.style.fontSize = Math.random() * 20 + 10 + 'px';
            snowflake.style.animationDuration = Math.random() * 3 + 2 + 's';
            snowflake.style.animation = `snowfall ${{snowflake.style.animationDuration}} linear infinite`;
            document.body.appendChild(snowflake);
            
            setTimeout(() => {{
                snowflake.remove();
            }}, 5000);
        }}
        
        setInterval(createSnowflake, 300);
    </script>
    
    <div class="container">
        <h1>응답</h1>
        
        <div class="character-response {'celebration' if is_flag else ''}">
            <div class="character-icon">{character_icon}</div>
            <div class="character-name">{speaker}</div>
            <div class="response-text">{response}</div>
        </div>
        
        <div class="query-result">
            <h3>🔍 쿼리 결과:</h3>
            <p>{result_html}</p>
        </div>
        
        <form method="GET" action="/">
            <button type="submit">🏠 다시 말 걸기</button>
        </form>
    </div>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)