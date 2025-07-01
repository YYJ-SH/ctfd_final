#!/usr/bin/env python3
"""
CTFd 챌린지 URL 자동 생성 스크립트
실제 호스팅 환경에서 사용할 챌린지 URL들을 생성합니다.
"""

import json
import os
from datetime import datetime

# 서버 설정
SERVER_IP = "49.50.135.55"
SERVER_PORT = "80"  # Traefik을 통해 80포트로 통합
BASE_URL = f"http://{SERVER_IP}"

# 챌린지 정보 (카테고리별로 정리)
CHALLENGES = {
    "Web Exploitation": [
        {
            "name": "Ann Day",
            "path": "/challenges/ann-day",
            "description": "날짜와 관련된 웹 취약점을 찾아보세요.",
            "difficulty": "Easy",
            "points": 100
        },
        {
            "name": "Base64 Challenge",
            "path": "/challenges/base64",
            "description": "Base64 인코딩/디코딩 관련 문제입니다.",
            "difficulty": "Easy", 
            "points": 150
        },
        {
            "name": "Cookie Admin",
            "path": "/challenges/cookieadmin",
            "description": "쿠키 조작을 통해 관리자 권한을 획득하세요.",
            "difficulty": "Medium",
            "points": 200
        },
        {
            "name": "Cookie CTF",
            "path": "/challenges/cookie-ctf",
            "description": "또 다른 쿠키 관련 취약점 문제입니다.",
            "difficulty": "Medium",
            "points": 250
        },
        {
            "name": "Directory Traversal",
            "path": "/challenges/directory-trav",
            "description": "디렉토리 순회 공격을 이용해 숨겨진 파일을 찾으세요.",
            "difficulty": "Medium",
            "points": 300
        },
        {
            "name": "Hidden Images",
            "path": "/challenges/hidden-images",
            "description": "이미지 속에 숨겨진 비밀을 찾아보세요.",
            "difficulty": "Easy",
            "points": 100
        },
        {
            "name": "Mobile Only",
            "path": "/challenges/mobile-only",
            "description": "모바일에서만 접근 가능한 페이지입니다.",
            "difficulty": "Easy",
            "points": 100
        },
        {
            "name": "Path CTF",
            "path": "/challenges/path-ctf",
            "description": "경로 관련 취약점을 찾아보세요.",
            "difficulty": "Medium",
            "points": 200
        },
        {
            "name": "Regex CTF",
            "path": "/challenges/regex-ctf",
            "description": "정규식 우회 문제입니다.",
            "difficulty": "Hard",
            "points": 400
        },
        {
            "name": "Why So Many Click",
            "path": "/challenges/why-so-many-click",
            "description": "수많은 클릭이 필요한 문제... 정말 다 클릭해야 할까요?",
            "difficulty": "Medium",
            "points": 250
        }
    ],
    "PHP Exploitation": [
        {
            "name": "Calculating Game",
            "path": "/challenges/calculating-game",
            "description": "PHP로 만든 계산 게임에서 취약점을 찾아보세요.",
            "difficulty": "Hard",
            "points": 400
        }
    ],
    "MCP Protocol": [
        {
            "name": "MCP Basic",
            "path": "/challenges/dmcp-9001",
            "description": "기본적인 MCP SSE 통신 문제입니다. /sse 엔드포인트에 접속하세요.",
            "difficulty": "Easy",
            "points": 150
        },
        {
            "name": "MCP Base64",
            "path": "/challenges/dmcp-9002", 
            "description": "Base64 디코딩이 필요한 MCP 문제입니다.",
            "difficulty": "Medium",
            "points": 250
        },
        {
            "name": "MCP JSON",
            "path": "/challenges/dmcp-9006",
            "description": "JSON 파싱이 필요한 MCP 문제입니다.",
            "difficulty": "Medium", 
            "points": 300
        },
        {
            "name": "MCP Time",
            "path": "/challenges/dmcp-9007",
            "description": "시간 기반 MCP 문제입니다.",
            "difficulty": "Hard",
            "points": 400
        }
    ]
}

def generate_challenge_urls():
    """챌린지 URL 목록 생성"""
    print("=" * 60)
    print("CTF 챌린지 URL 목록")
    print("=" * 60)
    print(f"서버: {BASE_URL}")
    print(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total_challenges = 0
    total_points = 0
    
    for category, challenges in CHALLENGES.items():
        print(f"\n📂 {category}")
        print("-" * 40)
        
        for challenge in challenges:
            url = f"{BASE_URL}{challenge['path']}"
            total_challenges += 1
            total_points += challenge['points']
            
            print(f"🎯 {challenge['name']}")
            print(f"   URL: {url}")
            print(f"   난이도: {challenge['difficulty']} | 점수: {challenge['points']}")
            print(f"   설명: {challenge['description']}")
            print()
    
    print("=" * 60)
    print(f"총 챌린지 수: {total_challenges}")
    print(f"총 점수: {total_points}")
    print("=" * 60)

def generate_ctfd_import_json():
    """CTFd 임포트용 JSON 파일 생성"""
    ctfd_data = {
        "db_version": "3.6.0",
        "results": []
    }
    
    challenge_id = 1
    
    for category, challenges in CHALLENGES.items():
        for challenge in challenges:
            url = f"{BASE_URL}{challenge['path']}"
            
            # MCP 챌린지의 경우 SSE 정보 추가
            description = challenge['description']
            if 'dmcp-' in challenge['path']:
                description += f"\n\n🔗 연결 URL: {url}\n📡 SSE 엔드포인트: {url}/sse"
            else:
                description += f"\n\n🔗 연결 URL: {url}"
            
            challenge_data = {
                "model": "Challenges",
                "pk": challenge_id,
                "fields": {
                    "name": challenge['name'],
                    "description": description,
                    "value": challenge['points'],
                    "category": category,
                    "type": "standard",
                    "state": "visible",
                    "max_attempts": 0,
                    "requirements": None
                }
            }
            
            ctfd_data["results"].append(challenge_data)
            challenge_id += 1
    
    # JSON 파일 저장
    with open('ctfd_challenges_import.json', 'w', encoding='utf-8') as f:
        json.dump(ctfd_data, f, ensure_ascii=False, indent=2)
    
    print("CTFd 임포트용 JSON 파일이 생성되었습니다: ctfd_challenges_import.json")

def generate_participant_guide():
    """참가자용 가이드 생성"""
    guide = f"""# CTF 참가자 가이드

## 🌐 서버 정보
- **메인 URL**: {BASE_URL}
- **CTFd 대시보드**: {BASE_URL}

## 📋 챌린지 접속 방법

### 1. 일반 웹 챌린지
각 챌린지는 다음과 같은 URL 구조를 가집니다:
```
{BASE_URL}/challenges/[챌린지명]
```

### 2. MCP 프로토콜 챌린지
MCP 챌린지는 SSE(Server-Sent Events) 통신을 사용합니다:
```
{BASE_URL}/challenges/dmcp-[포트번호]     # 웹 인터페이스
{BASE_URL}/challenges/dmcp-[포트번호]/sse # SSE 엔드포인트
```

## 🎯 전체 챌린지 목록

"""
    
    for category, challenges in CHALLENGES.items():
        guide += f"### {category}\n\n"
        
        for challenge in challenges:
            url = f"{BASE_URL}{challenge['path']}"
            guide += f"**{challenge['name']}** ({challenge['difficulty']} - {challenge['points']}점)\n"
            guide += f"- URL: {url}\n"
            guide += f"- 설명: {challenge['description']}\n\n"
    
    guide += """## 🔧 기술적 참고사항

### MCP 챌린지 접속 방법
1. 웹 브라우저로 MCP 챌린지 URL에 접속
2. SSE 연결이 자동으로 설정됩니다
3. 메시지 입력창에서 서버와 통신 가능

### 문제 해결
- 모든 챌린지는 80포트를 통해 접근 가능합니다
- 만약 특정 챌린지에 접속할 수 없다면 관리자에게 문의하세요
- 서버 상태는 실시간으로 모니터링됩니다

## 📞 지원
문제가 발생하면 CTF 운영진에게 연락하세요.
"""
    
    with open('participant_guide.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("참가자용 가이드가 생성되었습니다: participant_guide.md")

def main():
    """메인 함수"""
    print("CTF 플랫폼 URL 생성기")
    print("=" * 30)
    
    # 1. 콘솔에 URL 목록 출력
    generate_challenge_urls()
    
    # 2. CTFd 임포트용 JSON 생성
    generate_ctfd_import_json()
    
    # 3. 참가자용 가이드 생성
    generate_participant_guide()
    
    print("\n모든 파일이 생성되었습니다!")
    print("📁 생성된 파일:")
    print("  - ctfd_challenges_import.json (CTFd 관리자용)")
    print("  - participant_guide.md (참가자용)")

if __name__ == "__main__":
    main()
