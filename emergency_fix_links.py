#!/usr/bin/env python3
"""
Flask 앱 내부 링크 긴급 수정 스크립트
절대 경로를 상대 경로로 변경하여 라우팅 문제 해결
"""

import os
import re
import glob
from pathlib import Path

def fix_flask_internal_links(app_file_path, challenge_name):
    """Flask 앱 파일의 내부 링크 수정"""
    
    with open(app_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = f"{app_file_path}.link_backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🔧 내부 링크 수정 중: {app_file_path}")
    
    # redirect('/hint') → redirect('./hint') 형태로 수정
    content = re.sub(
        r'redirect\s*\(\s*[\'\"]/([^\'\"]+)[\'\"]\s*\)',
        r'redirect("./" + "\1")',
        content
    )
    
    # url_for 없이 직접 href 생성하는 부분 수정
    content = re.sub(
        r'href\s*=\s*[\'\"]/([^\'\"]+)[\'\"',
        r'href="{{ url_for(".\1") if url_for else "./" + "\1" }}"',
        content
    )
    
    # 수정된 내용 저장
    with open(app_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 내부 링크 수정 완료: {app_file_path}")

def fix_html_internal_links(html_file_path, challenge_name):
    """HTML 템플릿의 내부 링크 수정"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = f"{html_file_path}.link_backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🔧 HTML 내부 링크 수정 중: {html_file_path}")
    
    # href="/hint" → href="./hint" 형태로 수정
    content = re.sub(
        r'href\s*=\s*[\'\"]/([^/\'\"][^\'\"]*)[\'\"',
        r'href="./\1"',
        content
    )
    
    # action="/submit" → action="./submit" 형태로 수정
    content = re.sub(
        r'action\s*=\s*[\'\"]/([^/\'\"][^\'\"]*)[\'\"',
        r'action="./\1"',
        content
    )
    
    # 자바스크립트의 location.href 수정
    content = re.sub(
        r'location\.href\s*=\s*[\'\"]/([^/\'\"][^\'\"]*)[\'\"',
        r'location.href = "./\1"',
        content
    )
    
    # window.location 수정
    content = re.sub(
        r'window\.location\s*=\s*[\'\"]/([^/\'\"][^\'\"]*)[\'\"',
        r'window.location = "./\1"',
        content
    )
    
    # 수정된 내용 저장
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ HTML 내부 링크 수정 완료: {html_file_path}")

def emergency_fix_all_links():
    """모든 Flask 앱의 내부 링크 긴급 수정"""
    challenges_dir = "./challenges"
    
    if not os.path.exists(challenges_dir):
        print("❌ challenges 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🚨 모든 Flask 앱 내부 링크 긴급 수정 시작...")
    
    for challenge_dir in os.listdir(challenges_dir):
        challenge_path = os.path.join(challenges_dir, challenge_dir)
        
        if not os.path.isdir(challenge_path):
            continue
        
        # calculating_game은 PHP이므로 건너뛰기
        if challenge_dir == "calculating_game":
            print(f"⏭️  PHP 챌린지 건너뛰기: {challenge_dir}")
            continue
        
        print(f"\n🚨 긴급 수정 중: {challenge_dir}")
        
        # Flask 앱 파일 수정
        for app_file in glob.glob(os.path.join(challenge_path, "app.py*")):
            if not app_file.endswith('.backup') and not app_file.endswith('.link_backup'):
                fix_flask_internal_links(app_file, challenge_dir)
        
        # HTML 템플릿 수정
        template_dir = os.path.join(challenge_path, "templates")
        if os.path.exists(template_dir):
            for html_file in glob.glob(os.path.join(template_dir, "**/*.html"), recursive=True):
                if not html_file.endswith('.backup') and not html_file.endswith('.link_backup'):
                    fix_html_internal_links(html_file, challenge_dir)
    
    print("\n🎉 모든 내부 링크 긴급 수정 완료!")
    print("\n📋 다음 단계:")
    print("1. docker-compose restart (재빌드 필요 없음)")
    print("2. 링크 테스트")

def restore_link_backups():
    """링크 백업 파일로 복원"""
    challenges_dir = "./challenges"
    
    print("🔄 링크 백업 파일로 복원 중...")
    
    backup_files = []
    for root, dirs, files in os.walk(challenges_dir):
        for file in files:
            if file.endswith('.link_backup'):
                backup_files.append(os.path.join(root, file))
    
    for backup_file in backup_files:
        original_file = backup_file[:-12]  # .link_backup 제거
        if os.path.exists(backup_file):
            os.rename(backup_file, original_file)
            print(f"✅ 복원: {original_file}")
    
    print(f"\n🎉 {len(backup_files)}개 파일 복원 완료!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_link_backups()
    else:
        emergency_fix_all_links()
