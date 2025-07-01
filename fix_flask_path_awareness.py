#!/usr/bin/env python3
"""
Flask 앱 경로 인식 문제 해결 스크립트
앱이 자신의 base URL을 알고 올바른 경로를 생성하도록 수정
"""

import os
import re
import glob

def fix_flask_path_awareness():
    """Flask 앱이 자신의 base path를 인식하도록 수정"""
    
    challenges_dir = "./challenges"
    
    if not os.path.exists(challenges_dir):
        print("❌ challenges 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🔧 Flask 경로 인식 문제 해결 시작...")
    
    for challenge_dir in os.listdir(challenges_dir):
        challenge_path = os.path.join(challenges_dir, challenge_dir)
        
        if not os.path.isdir(challenge_path):
            continue
        
        if challenge_dir == "calculating_game":
            continue
        
        print(f"📂 처리 중: {challenge_dir}")
        
        # Python 파일 수정
        for app_file in glob.glob(os.path.join(challenge_path, "app.py*")):
            if app_file.endswith('.backup'):
                continue
                
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 백업 생성
            with open(f"{app_file}.path_backup", 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Flask 앱 생성 부분 찾기
            if 'app = Flask(__name__)' in content:
                # 경로 인식 함수 추가
                path_helper = f'''
# 현재 앱의 base path 설정
import os
from urllib.parse import urljoin
from flask import request

def get_base_path():
    """현재 앱의 base path 반환"""
    return "/challenges/{challenge_dir}"

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
    return {{
        'base_path': get_base_path(),
        'url_for_relative': url_for_relative
    }}

'''
                
                # app = Flask(__name__) 뒤에 추가
                content = content.replace(
                    'app = Flask(__name__)',
                    'app = Flask(__name__)' + path_helper
                )
                
                # HTML 템플릿 내의 절대 경로들을 템플릿 변수로 변경
                # href="/" → href="{{ base_path }}/"
                content = re.sub(
                    r'href="/"',
                    'href="{{ base_path }}/"',
                    content
                )
                
                # href="/hint" → href="{{ base_path }}/hint"
                content = re.sub(
                    r'href="/([^"]+)"',
                    r'href="{{ base_path }}/\1"',
                    content
                )
                
                # action="/submit" → action="{{ base_path }}/submit"  
                content = re.sub(
                    r'action="/([^"]+)"',
                    r'action="{{ base_path }}/\1"',
                    content
                )
                
                # JavaScript의 location.href 수정
                content = re.sub(
                    r'location\.href\s*=\s*"/([^"]*)"',
                    r'location.href = "{{ base_path }}/\1"',
                    content
                )
                
                # window.location 수정
                content = re.sub(
                    r'window\.location\s*=\s*"/([^"]*)"',
                    r'window.location = "{{ base_path }}/\1"',
                    content
                )
            
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 경로 인식 수정: {app_file}")
    
    print("\n🎉 Flask 경로 인식 문제 해결 완료!")
    print("\n📋 이제 모든 링크가 올바른 경로로 생성됩니다:")
    print("  - href='/' → href='/challenges/ann-day/'")
    print("  - href='/hint' → href='/challenges/ann-day/hint'") 
    print("  - action='/submit' → action='/challenges/ann-day/submit'")

def restore_path_backups():
    """백업 파일로 복원"""
    challenges_dir = "./challenges"
    
    print("🔄 경로 백업 파일로 복원 중...")
    
    backup_files = []
    for root, dirs, files in os.walk(challenges_dir):
        for file in files:
            if file.endswith('.path_backup'):
                backup_files.append(os.path.join(root, file))
    
    for backup_file in backup_files:
        original_file = backup_file[:-12]  # .path_backup 제거
        if os.path.exists(backup_file):
            os.rename(backup_file, original_file)
            print(f"✅ 복원: {original_file}")
    
    print(f"\n🎉 {len(backup_files)}개 파일 복원 완료!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_path_backups()
    else:
        fix_flask_path_awareness()
