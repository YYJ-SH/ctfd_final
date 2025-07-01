#!/usr/bin/env python3
"""
Flask 앱 라우팅 문제 해결 스크립트
/challenges/[name]과 / 경로 모두 처리하도록 수정
"""

import os
import re
import glob
from pathlib import Path

def fix_flask_routes(app_file_path, challenge_name):
    """Flask 앱의 라우팅을 수정하여 다중 경로 지원"""
    
    with open(app_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = f"{app_file_path}.backup2"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🔧 라우팅 수정 중: {app_file_path}")
    
    # 기존 @app.route('/') 찾아서 다중 경로로 변경
    # 단일 route 패턴
    single_route_pattern = r"@app\.route\s*\(\s*['\"]\/['\"]([^)]*)\)"
    
    # 다중 route로 변경
    def replace_route(match):
        params = match.group(1) if match.group(1) else ""
        if params:
            return f'@app.route("/"{params})\n@app.route("/challenges/{challenge_name}"{params})'
        else:
            return f'@app.route("/")\n@app.route("/challenges/{challenge_name}")'
    
    content = re.sub(single_route_pattern, replace_route, content)
    
    # 다른 경로들도 처리 (예: @app.route('/hint'), @app.route('/test') 등)
    other_route_pattern = r"@app\.route\s*\(\s*['\"]\/([^'\"\/]+)['\"]([^)]*)\)"
    
    def replace_other_route(match):
        path = match.group(1)
        params = match.group(2) if match.group(2) else ""
        return f'@app.route("/{path}"{params})\n@app.route("/challenges/{challenge_name}/{path}"{params})'
    
    content = re.sub(other_route_pattern, replace_other_route, content)
    
    # 수정된 내용 저장
    with open(app_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 라우팅 수정 완료: {app_file_path}")

def fix_all_flask_routes():
    """모든 Flask 앱의 라우팅 수정"""
    challenges_dir = "./challenges"
    
    if not os.path.exists(challenges_dir):
        print("❌ challenges 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🔧 모든 Flask 앱 라우팅 수정 시작...")
    
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
        for app_file in glob.glob(os.path.join(challenge_path, "app.py*")):
            if not app_file.endswith('.backup') and not app_file.endswith('.backup2'):
                fix_flask_routes(app_file, challenge_dir)
    
    print("\n🎉 모든 Flask 앱 라우팅 수정 완료!")

def restore_backups():
    """백업 파일로 복원"""
    challenges_dir = "./challenges"
    
    print("🔄 백업 파일로 복원 중...")
    
    backup_files = []
    for root, dirs, files in os.walk(challenges_dir):
        for file in files:
            if file.endswith('.backup2'):
                backup_files.append(os.path.join(root, file))
    
    for backup_file in backup_files:
        original_file = backup_file[:-8]  # .backup2 제거
        if os.path.exists(backup_file):
            os.rename(backup_file, original_file)
            print(f"✅ 복원: {original_file}")
    
    print(f"\n🎉 {len(backup_files)}개 파일 복원 완료!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_backups()
    else:
        fix_all_flask_routes()
