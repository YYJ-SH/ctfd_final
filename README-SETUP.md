# CTF 플랫폼 올인원 설정

이 프로젝트는 CTFd와 다양한 웹 챌린지, MCP 서버 챌린지를 하나의 Docker Compose로 통합 운영하는 시스템입니다.

## 🚀 빠른 시작

### 1. 전체 설정 및 시작
```bash
# 스크립트 실행 권한 부여
chmod +x *.sh

# 전체 설정 및 시작 (한 번에)
./deploy.sh --setup --build --start
```

### 2. 단계별 실행
```bash
# 1단계: 초기 설정
./deploy.sh --setup

# 2단계: Docker 이미지 빌드
./deploy.sh --build

# 3단계: 서비스 시작
./deploy.sh --start
```

## 📋 주요 기능

### 웹 챌린지 (Flask 기반)
- **Ann Day**: `/ann-day`
- **Base64**: `/base64` 
- **Cookie Admin**: `/cookieadmin`
- **Cookie CTF**: `/cookie-ctf`
- **Directory Traversal**: `/directory-trav`
- **Hidden Images**: `/hidden-images`
- **Mobile Only**: `/mobile-only`
- **Path CTF**: `/path-ctf`
- **Regex CTF**: `/regex-ctf`
- **Why So Many Click**: `/why-so-many-click`

### PHP 챌린지
- **Calculating Game**: `/calculating-game`

### MCP 챌린지 (SSE 통신)
- **MCP 9001**: `/dmcp-9001` (기본 Echo)
- **MCP 9002**: `/dmcp-9002` (Base64 디코딩)
- **MCP 9006**: `/dmcp-9006` (JSON 파싱)
- **MCP 9007**: `/dmcp-9007` (시간 기반)

## 🌐 접속 URL

- **CTFd 메인**: http://localhost
- **Traefik 대시보드**: http://localhost:8080

## 📊 관리 명령어

### 서비스 상태 확인
```bash
./deploy.sh --status
```

### 로그 확인
```bash
# 모든 서비스 로그
./deploy.sh --logs

# 특정 서비스 로그
./deploy.sh --logs ctfd
./deploy.sh --logs traefik
```

### 서비스 제어
```bash
# 서비스 중지
./deploy.sh --stop

# 서비스 재시작
./deploy.sh --restart

# 전체 리소스 정리
./deploy.sh --clean
```

## 🔧 문제 해결

### 1. 포트 충돌
```bash
# 80, 8000, 8080 포트가 사용 중인지 확인
netstat -tulpn | grep :80
netstat -tulpn | grep :8000
netstat -tulpn | grep :8080

# 기존 서비스 중지 후 재시도
./deploy.sh --stop
./deploy.sh --start
```

### 2. Docker 권한 문제
```bash
# Docker 그룹에 사용자 추가 (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### 3. 경로 문제 복원
모든 Python 및 HTML 파일은 자동으로 백업됩니다:
```bash
# 백업 파일로 복원
find challenges/ -name "*.backup" | while read backup; do
    original="${backup%.backup}"
    cp "$backup" "$original"
done
```

### 4. MCP 서버 SSE 통신 테스트
```bash
# 브라우저에서 접속
curl http://localhost/dmcp-9001/health

# SSE 연결 테스트
curl -N -H "Accept: text/event-stream" http://localhost/dmcp-9001/sse
```

## 📁 프로젝트 구조

```
.
├── challenges/              # 웹 챌린지들
│   ├── ann_day/
│   ├── base64/
│   ├── calculating_game/    # PHP 기반
│   └── ...
├── damn-vulnerable-MCP-server/  # MCP 챌린지 서버
├── CTFd/                    # CTFd (자동 클론됨)
├── docker-compose-fixed.yml # 수정된 Docker Compose 설정
├── setup-ctf-platform.sh   # 초기 설정 스크립트
├── deploy.sh               # 배포 관리 스크립트
└── README.md              # 이 파일
```

## 🔍 개발자 정보

### 자동 생성되는 파일들
- 각 챌린지의 `Dockerfile`
- MCP 서버의 `supervisord.conf`
- 수정된 Flask 설정 (`app.run()`)
- 수정된 HTML 템플릿 (static 경로)

### 네트워크 구성
- `ctf-network`: Traefik와 챌린지 서비스들
- `internal`: CTFd, DB, Redis (내부 통신)
- `default`: 기본 네트워크

### 주요 변경사항
1. **중복 서비스 정의 제거**
2. **SSE 통신을 위한 MCP 서버 라우팅 개선**
3. **Flask 앱의 호스트/포트 설정 자동 수정**
4. **Static 파일 경로 url_for() 사용으로 변경**
5. **볼륨을 통한 데이터 영속성 보장**

## ⚠️ 주의사항

1. **포트 사용**: 80, 8000, 8080 포트가 필요합니다
2. **메모리**: 최소 4GB RAM 권장
3. **디스크**: 최소 10GB 여유 공간
4. **백업**: 중요한 데이터는 정기적으로 백업하세요

## 🆘 도움말

```bash
./deploy.sh --help
```

문제가 발생하면 GitHub Issues에 보고해주세요.
