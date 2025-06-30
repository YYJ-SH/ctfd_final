# CTF 플랫폼 설정 가이드

## 🚀 빠른 시작

1. **모든 Dockerfile 자동 생성**:
   ```bash
   chmod +x auto-dockerfile.sh setup-all-challenges.sh
   ./setup-all-challenges.sh
   ```

2. **CTFd 설정 폴더 생성**:
   ```bash
   mkdir -p ctfd/data/CTFd
   cp ctfd-config.py ctfd/data/CTFd/config.py
   ```

3. **배포**:
   ```bash
   chmod +x deploy.sh generate-urls.sh backup-ctfd.sh restore-ctfd.sh
   ./deploy.sh
   ```

4. **URL 목록 확인**:
   ```bash
   ./generate-urls.sh
   ```

## 📁 현재 폴더 구조

```
D:\Yeji\
├── challenges/           # 웹 문제들
├── damn-vulnerable-MCP-server/  # MCP 서비스
├── auto-dockerfile.sh    # Dockerfile 자동 생성기
├── setup-all-challenges.sh  # 전체 설정 스크립트
├── docker-compose.yml    # Docker Compose 설정
├── deploy.sh            # 배포 스크립트
├── generate-urls.sh     # URL 목록 생성기
├── ctfd-config.py       # CTFd 설정 파일
├── backup-ctfd.sh       # 백업 스크립트
├── restore-ctfd.sh      # 복원 스크립트
└── README.md           # 이 파일
```

## 🌐 접속 URL

### 로컬 개발용
- **CTFd 메인**: http://ctf.localhost
- **Traefik 대시보드**: http://localhost:8080
- **문제들**: http://문제이름.ctf.localhost

### /etc/hosts 설정 (Windows의 경우 C:\Windows\System32\drivers\etc\hosts)
```
127.0.0.1 ctf.localhost ann-day.ctf.localhost base64.ctf.localhost calculating-game.ctf.localhost cookieadmin.ctf.localhost cookie-ctf.ctf.localhost crypto-hacker.ctf.localhost directory-trav.ctf.localhost hidden-images.ctf.localhost mobile-only.ctf.localhost path-ctf.ctf.localhost regex-ctf.ctf.localhost why-so-many-click.ctf.localhost dmcp-9001.ctf.localhost dmcp-9002.ctf.localhost dmcp-9006.ctf.localhost dmcp-9007.ctf.localhost
```

## 🔧 관리 명령어

### 서비스 관리
```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f ctfd
```

### 백업/복원
```bash
# 백업
./backup-ctfd.sh

# 복원
./restore-ctfd.sh ./backups/20250101_120000
```

## 🎯 CTFd에서 문제 설정

1. http://ctf.localhost/admin 접속
2. Challenges > Create 클릭
3. 각 문제별로:
   - **Connection Info**에 `./generate-urls.sh`로 생성된 URL 입력
   - **Description**: 문제 설명
   - **Category**: "Web" 또는 "MCP"
   - **Value**: 점수

## 🐳 Git 저장소 준비

클라우드에서 사용할 때는:

1. **Git 저장소 생성**:
   ```bash
   git init
   git add .
   git commit -m "Initial CTF platform setup"
   git remote add origin <your-git-repo>
   git push -u origin main
   ```

2. **클라우드에서 클론**:
   ```bash
   git clone <your-git-repo>
   cd <repo-name>
   ./deploy.sh
   ```

## ⚠️ 주의사항

- **프로덕션 환경**에서는 `ctfd-config.py`의 SECRET_KEY를 변경하세요
- **도메인**을 실제 도메인으로 변경하려면 `docker-compose.yml`의 Host 부분을 수정하세요
- **SSL**이 필요하면 Traefik에 Let's Encrypt 설정을 추가하세요