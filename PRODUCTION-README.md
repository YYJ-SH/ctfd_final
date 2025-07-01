# 🌐 실제 호스팅 CTF 플랫폼 가이드

서버 IP: **49.50.135.55**  
메인 URL: **http://49.50.135.55**

## 🚀 빠른 배포 가이드

### 1. 서버에서 실행
```bash
# 파일 다운로드 (또는 git clone)
cd /path/to/ctf-platform

# 권한 부여
chmod +x *.sh

# 프로덕션 환경 설정 및 배포
./production-deploy.sh --setup --deploy
```

### 2. 챌린지 URL 생성
```bash
# 참가자용 URL 목록 생성
./production-deploy.sh --generate-urls

# 생성된 파일 확인
cat participant_guide.md
```

## 📋 참가자들에게 제공할 정보

### CTF 접속 정보
- **메인 사이트**: http://49.50.135.55
- **등록**: http://49.50.135.55/register
- **로그인**: http://49.50.135.55/login

### 챌린지 URL 구조
```
# 웹 챌린지
http://49.50.135.55/challenges/[챌린지명]

# 예시
http://49.50.135.55/challenges/base64
http://49.50.135.55/challenges/cookie-ctf
http://49.50.135.55/challenges/calculating-game

# MCP 챌린지 (SSE 통신)
http://49.50.135.55/challenges/dmcp-9001
http://49.50.135.55/challenges/dmcp-9002
```

## 🎯 전체 챌린지 목록 (참가자용)

### 웹 취약점 (Web Exploitation)
1. **Ann Day** (Easy - 100점)
   - URL: http://49.50.135.55/challenges/ann-day
   - 설명: 날짜와 관련된 웹 취약점

2. **Base64 Challenge** (Easy - 150점)
   - URL: http://49.50.135.55/challenges/base64
   - 설명: Base64 인코딩/디코딩 문제

3. **Cookie Admin** (Medium - 200점)
   - URL: http://49.50.135.55/challenges/cookieadmin
   - 설명: 쿠키 조작으로 관리자 권한 획득

4. **Cookie CTF** (Medium - 250점)
   - URL: http://49.50.135.55/challenges/cookie-ctf
   - 설명: 쿠키 관련 취약점

5. **Directory Traversal** (Medium - 300점)
   - URL: http://49.50.135.55/challenges/directory-trav
   - 설명: 디렉토리 순회 공격

6. **Hidden Images** (Easy - 100점)
   - URL: http://49.50.135.55/challenges/hidden-images
   - 설명: 이미지 속 숨겨진 비밀

7. **Mobile Only** (Easy - 100점)
   - URL: http://49.50.135.55/challenges/mobile-only
   - 설명: 모바일 전용 페이지

8. **Path CTF** (Medium - 200점)
   - URL: http://49.50.135.55/challenges/path-ctf
   - 설명: 경로 관련 취약점

9. **Regex CTF** (Hard - 400점)
   - URL: http://49.50.135.55/challenges/regex-ctf
   - 설명: 정규식 우회

10. **Why So Many Click** (Medium - 250점)
    - URL: http://49.50.135.55/challenges/why-so-many-click
    - 설명: 수많은 클릭이 필요한 문제

### PHP 취약점 (PHP Exploitation)
11. **Calculating Game** (Hard - 400점)
    - URL: http://49.50.135.55/challenges/calculating-game
    - 설명: PHP 계산 게임 취약점

### MCP 프로토콜 (MCP Protocol)
12. **MCP Basic** (Easy - 150점)
    - URL: http://49.50.135.55/challenges/dmcp-9001
    - SSE: http://49.50.135.55/challenges/dmcp-9001/sse
    - 설명: 기본 MCP SSE 통신

13. **MCP Base64** (Medium - 250점)
    - URL: http://49.50.135.55/challenges/dmcp-9002
    - SSE: http://49.50.135.55/challenges/dmcp-9002/sse
    - 설명: Base64 디코딩 MCP

14. **MCP JSON** (Medium - 300점)
    - URL: http://49.50.135.55/challenges/dmcp-9006
    - SSE: http://49.50.135.55/challenges/dmcp-9006/sse
    - 설명: JSON 파싱 MCP

15. **MCP Time** (Hard - 400점)
    - URL: http://49.50.135.55/challenges/dmcp-9007
    - SSE: http://49.50.135.55/challenges/dmcp-9007/sse
    - 설명: 시간 기반 MCP

## 🔧 관리자용 명령어

### 서비스 관리
```bash
# 상태 확인
./production-deploy.sh --status

# 서비스 재시작
./production-deploy.sh --restart

# 로그 확인
./production-deploy.sh --logs

# 실시간 모니터링
./production-deploy.sh --monitor
```

### 백업 및 복원
```bash
# 백업 생성
./production-deploy.sh --backup

# 백업 복원
./production-deploy.sh --restore
```

## 🎯 CTFd 관리자 설정

### 1. 초기 설정
1. http://49.50.135.55/setup 접속
2. 관리자 계정 생성
3. CTF 기본 정보 설정

### 2. 챌린지 임포트
1. http://49.50.135.55/admin 접속
2. Config → Import 메뉴
3. `ctfd_challenges_import.json` 파일 업로드

### 3. 참가자 관리
- 팀 등록 허용/비허용
- 점수 공개/비공개
- 시간 제한 설정

## 📊 성능 및 보안

### 서버 사양 권장
- **CPU**: 최소 2코어 (4코어 권장)
- **메모리**: 최소 4GB (8GB 권장)
- **디스크**: 최소 20GB SSD
- **네트워크**: 1Gbps

### 보안 설정
- 방화벽: 22(SSH), 80(HTTP), 443(HTTPS)만 개방
- Traefik API 비활성화 (프로덕션)
- 정기 백업 (일일)
- SSL 인증서 설정 권장

### 모니터링 포인트
- Docker 컨테이너 상태
- 시스템 리소스 (CPU, 메모리, 디스크)
- 네트워크 연결성
- 서비스 응답 시간

## 🚨 문제 해결

### 일반적인 문제
1. **서비스가 시작되지 않을 때**
   ```bash
   docker-compose logs
   docker system prune -f
   ./production-deploy.sh --restart
   ```

2. **챌린지에 접속할 수 없을 때**
   ```bash
   curl -I http://49.50.135.55/challenges/base64
   docker-compose ps
   ```

3. **성능이 느릴 때**
   ```bash
   htop
   df -h
   docker stats
   ```

### 긴급 상황 대응
```bash
# 전체 서비스 중지
docker-compose down

# 긴급 백업
./production-deploy.sh --backup

# 로그 수집
docker-compose logs > emergency.log
```

## 📞 연락처

CTF 운영진: [연락처 정보]
서버 관리자: [연락처 정보]

---

**총 15개 챌린지 | 총 3,350점**  
**카테고리**: Web Exploitation (10), PHP Exploitation (1), MCP Protocol (4)
