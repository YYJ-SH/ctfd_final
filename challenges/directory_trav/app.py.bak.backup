import os
import shutil
from flask import Flask, request, render_template, redirect

app = Flask(__name__)

UPLOAD_DIR = './uploads'
FLAG_PATH = './flag.txt'

@app.route('/')
def index():
    subdir = 'ybg_storage'
    target_dir = os.path.join(UPLOAD_DIR, subdir)
    if not os.path.exists(target_dir):
        files = []
    else:
        files = os.listdir(target_dir)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        filename = request.form.get('filename')
        content = request.form.get('content', '').encode('utf-8')

        if '..' in filename or '/' in filename:
            return render_template('upload_result.html', result='Invalid filename.')

        subdir = 'ybg_storage'
        target_dir = os.path.join(UPLOAD_DIR, subdir)
        os.makedirs(target_dir, exist_ok=True)

        full_path = os.path.join(target_dir, filename)
        with open(full_path, 'wb') as f:
            f.write(content)

        return redirect('/')
    return render_template('upload.html')

@app.route('/read')
def read_file():
    subdir = 'ybg_storage'
    filename = request.args.get('name', '')

    try:
        full_path = os.path.join(UPLOAD_DIR, subdir, filename)
        with open(full_path, 'rb') as f:
            content = f.read().decode('utf-8')
        error = False
    except Exception as e:
        content = str(e)
        error = True

    return render_template('read.html', filename=filename, content=content, error=error)

if __name__ == '__main__':
    # 업로드 폴더 초기화
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.mkdir(UPLOAD_DIR)

    # 플래그 존재 확인 (직접 파일로만 생성해야 함)
    if not os.path.exists(FLAG_PATH):
        print("[ERROR] flag.txt 파일이 존재하지 않습니다. 서버를 실행할 수 없습니다.")
        exit(1)

    app.run(host='0.0.0.0', port=8000)

