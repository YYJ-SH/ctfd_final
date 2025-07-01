#!/usr/bin/env python3
"""
간단한 링크 수정 스크립트 - 절대 경로 "/" 를 "./" 로 변경
"""

import os
import re
import glob

def fix_absolute_paths():
    """모든 Flask 앱에서 절대 경로 "/" 를 상대 경로 "./" 로 수정"""
    
    challenges_dir = "./challenges"
    
    if not os.path.exists(challenges_dir):
        print("❌ challenges 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🔧 절대 경로 수정 시작...")
    
    for challenge_dir in os.listdir(challenges_dir):
        challenge_path = os.path.join(challenges_dir, challenge_dir)
        
        if not os.path.isdir(challenge_path):
            continue
        
        if challenge_dir == "calculating_game":
            continue
        
        print(f"📂 처리 중: {challenge_dir}")
        
        # Python 파일에서 href="/" 찾아서 수정
        for app_file in glob.glob(os.path.join(challenge_path, "app.py*")):
            if app_file.endswith('.backup'):
                continue
                
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 백업 생성
            with open(f"{app_file}.simple_backup", 'w', encoding='utf-8') as f:
                f.write(content)
            
            # href="/" → href="./" 수정
            content = re.sub(r'href="/"', 'href="./"', content)
            content = re.sub(r"href='/'", "href='./'", content)
            
            # action="/" → action="./" 수정  
            content = re.sub(r'action="/"', 'action="./"', content)
            content = re.sub(r"action='/'", "action='./'", content)
            
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 수정: {app_file}")
    
    print("\n🎉 절대 경로 수정 완료!")

if __name__ == "__main__":
    fix_absolute_paths()
