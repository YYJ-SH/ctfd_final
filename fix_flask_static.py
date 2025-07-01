#!/usr/bin/env python3
"""
Flask 앱의 WSGI 환경 수정 스크립트
Static 파일 경로 문제를 해결하기 위해 각 Flask 앱에 미들웨어 추가
"""

import os
import re
import glob
from pathlib import Path

def fix_flask_app(app_file_path, challenge_name):
    """Flask 앱 파일을 수정하여 SCRIPT_NAME 환경변수 처리 추가"""
    
    with open(app_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = f"{app_file_path}.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # WSGI 미들웨어 코드 추가
    middleware_code = f'''
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

'''
    
    # Flask 앱 생성 부분 찾기
    app_pattern = r'(app\s*=\s*Flask\s*\([^)]*\))'
    
    if re.search(app_pattern, content):
        # Flask 앱 생성 후 미들웨어 적용
        content = re.sub(
            app_pattern,
            r'\1\n\n# WSGI 미들웨어 적용\napp.wsgi_app = ScriptNameMiddleware(app.wsgi_app)',
            content
        )
        
        # 미들웨어 코드를 import 섹션 후에 추가
        import_pattern = r'(from flask import[^\n]*\n)'
        content = re.sub(
            import_pattern,
            r'\1' + middleware_code,
            content
        )
    
    # app.run() 부분 수정
    content = re.sub(
        r'app\.run\([^)]*\)',
        'app.run(host="0.0.0.0", port=5000, debug=False)',
        content
    )
    
    # 수정된 내용 저장
    with open(app_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 수정 완료: {app_file_path}")

def fix_html_templates(template_dir, challenge_name):
    """HTML 템플릿의 static 경로 수정"""
    
    html_files = glob.glob(os.path.join(template_dir, "**/*.html"), recursive=True)
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 백업 생성
        backup_path = f"{html_file}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # url_for 사용하도록 수정
        # src="/static/" -> src="{{ url_for('static', filename='
        content = re.sub(
            r'src=["\']\/static\/([^"\']+)["\']',
            r'src="{{ url_for(\'static\', filename=\'\1\') }}"',
            content
        )
        
        # href="/static/" -> href="{{ url_for('static', filename='
        content = re.sub(
            r'href=["\']\/static\/([^"\']+)["\']',
            r'href="{{ url_for(\'static\', filename=\'\1\') }}"',
            content
        )
        
        # CSS의 url(/static/) -> url({{ url_for('static', filename=
        content = re.sub(
            r'url\(["\']?\/static\/([^"\')]+)["\']?\)',
            r'url({{ url_for(\'static\', filename=\'\1\') }})',
            content
        )
        
        # 수정된 내용 저장
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ HTML 수정 완료: {html_file}")

def update_dockerfile(dockerfile_path, challenge_name):
    """Dockerfile에 환경변수 추가"""
    
    if not os.path.exists(dockerfile_path):
        return
    
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = f"{dockerfile_path}.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 환경변수 추가 (이미 있으면 건너뛰기)
    if 'SCRIPT_NAME' not in content:
        env_section = f'''
# 프로덕션 환경에서 경로 설정
ENV SCRIPT_NAME=/challenges/{challenge_name}
ENV FLASK_ENV=production

'''
        
        # CMD 앞에 환경변수 추가
        content = re.sub(
            r'(CMD \[.*\])',
            env_section + r'\1',
            content
        )
        
        # 수정된 내용 저장
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Dockerfile 수정 완료: {dockerfile_path}")

def main():
    """메인 함수"""
    challenges_dir = "./challenges"
    
    if not os.path.exists(challenges_dir):
        print("❌ challenges 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🔧 Flask 앱 static 경로 문제 수정 시작...")
    
    for challenge_dir in os.listdir(challenges_dir):
        challenge_path = os.path.join(challenges_dir, challenge_dir)
        
        if not os.path.isdir(challenge_path):
            continue
        
        # calculating_game은 PHP이므로 건너뛰기
        if challenge_dir == "calculating_game":
            print(f"⏭️  PHP 챌린지 건너뛰기: {challenge_dir}")
            continue
        
        print(f"\n📂 처리 중: {challenge_dir}")
        
        # Flask 앱 파일 찾기 및 수정
        app_files = glob.glob(os.path.join(challenge_path, "app.py*"))
        for app_file in app_files:
            if not app_file.endswith('.backup'):
                fix_flask_app(app_file, challenge_dir)
        
        # HTML 템플릿 수정
        template_dir = os.path.join(challenge_path, "templates")
        if os.path.exists(template_dir):
            fix_html_templates(template_dir, challenge_dir)
        
        # Dockerfile 수정
        dockerfile_path = os.path.join(challenge_path, "Dockerfile")
        update_dockerfile(dockerfile_path, challenge_dir)
    
    print("\n🎉 모든 Flask 앱 수정 완료!")
    print("\n📋 다음 단계:")
    print("1. docker-compose-production-fixed.yml 사용")
    print("2. 서비스 재빌드 및 재시작")
    print("3. Static 파일 경로 테스트")

def restore_backups():
    """백업 파일로 복원"""
    challenges_dir = "./challenges"
    
    print("🔄 백업 파일로 복원 중...")
    
    backup_files = []
    for root, dirs, files in os.walk(challenges_dir):
        for file in files:
            if file.endswith('.backup'):
                backup_files.append(os.path.join(root, file))
    
    for backup_file in backup_files:
        original_file = backup_file[:-7]  # .backup 제거
        if os.path.exists(backup_file):
            os.rename(backup_file, original_file)
            print(f"✅ 복원: {original_file}")
    
    print(f"\n🎉 {len(backup_files)}개 파일 복원 완료!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_backups()
    else:
        main()
