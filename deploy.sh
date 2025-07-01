#!/bin/bash

# deploy.sh
# CTF 플랫폼 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 사용법 출력
usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --setup     초기 설정 실행"
    echo "  --build     Docker 이미지 빌드"
    echo "  --start     서비스 시작"
    echo "  --stop      서비스 중지"
    echo "  --restart   서비스 재시작"
    echo "  --logs      로그 확인"
    echo "  --status    서비스 상태 확인"
    echo "  --clean     모든 리소스 정리"
    echo "  --help      도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0 --setup --build --start    # 전체 설정 및 시작"
    echo "  $0 --restart                  # 서비스 재시작"
}

# 초기 설정
setup() {
    print_status "초기 설정 시작..."
    
    # setup-ctf-platform.sh 실행
    if [ -f "./setup-ctf-platform.sh" ]; then
        chmod +x ./setup-ctf-platform.sh
        ./setup-ctf-platform.sh
    else
        print_error "setup-ctf-platform.sh 파일을 찾을 수 없습니다."
        exit 1
    fi
    
    print_success "초기 설정 완료"
}

# Docker 이미지 빌드
build() {
    print_status "Docker 이미지 빌드 중..."
    
    # 수정된 Docker Compose 파일 사용
    if [ -f "docker-compose-fixed.yml" ]; then
        cp docker-compose-fixed.yml docker-compose.yml
        print_status "수정된 Docker Compose 파일을 적용했습니다."
    fi
    
    # 기존 컨테이너 정지
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # 이미지 빌드
    docker-compose build --no-cache
    
    print_success "Docker 이미지 빌드 완료"
}

# 서비스 시작
start() {
    print_status "서비스 시작 중..."
    
    # Docker Compose로 서비스 시작
    docker-compose up -d
    
    # 서비스 상태 확인
    sleep 10
    docker-compose ps
    
    print_success "서비스 시작 완료"
    print_urls
}

# 서비스 중지
stop() {
    print_status "서비스 중지 중..."
    
    docker-compose down
    
    print_success "서비스 중지 완료"
}

# 서비스 재시작
restart() {
    print_status "서비스 재시작 중..."
    
    stop
    sleep 5
    start
    
    print_success "서비스 재시작 완료"
}

# 로그 확인
logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        print_status "모든 서비스 로그 확인..."
        docker-compose logs -f
    else
        print_status "$service 서비스 로그 확인..."
        docker-compose logs -f "$service"
    fi
}

# 서비스 상태 확인
status() {
    print_status "서비스 상태 확인 중..."
    
    echo ""
    echo "=== Docker Compose 서비스 상태 ==="
    docker-compose ps
    
    echo ""
    echo "=== 실행 중인 컨테이너 ==="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "=== 디스크 사용량 ==="
    docker system df
    
    echo ""
    print_status "헬스체크 실행 중..."
    
    # CTFd 헬스체크
    if curl -s http://localhost:8000 > /dev/null; then
        print_success "CTFd: 정상"
    else
        print_error "CTFd: 비정상"
    fi
    
    # Traefik 헬스체크
    if curl -s http://localhost:8080 > /dev/null; then
        print_success "Traefik: 정상"
    else
        print_error "Traefik: 비정상"
    fi
    
    # MCP 서비스들 헬스체크
    for port in 9001 9002 9006 9007; do
        if curl -s "http://localhost/dmcp-${port}/health" > /dev/null; then
            print_success "MCP-${port}: 정상"
        else
            print_warning "MCP-${port}: 확인 필요"
        fi
    done
}

# 리소스 정리
clean() {
    print_warning "모든 Docker 리소스를 정리합니다. 계속하시겠습니까? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "리소스 정리 중..."
        
        # 컨테이너 중지 및 제거
        docker-compose down --volumes --remove-orphans
        
        # 이미지 제거
        docker-compose down --rmi all
        
        # 미사용 리소스 정리
        docker system prune -f
        
        print_success "리소스 정리 완료"
    else
        print_status "리소스 정리를 취소했습니다."
    fi
}

# URL 정보 출력
print_urls() {
    echo ""
    echo "=== 서비스 접속 URL ==="
    echo "🌐 CTFd 메인 페이지:      http://localhost"
    echo "🔧 Traefik 대시보드:     http://localhost:8080"
    echo ""
    echo "=== 웹 챌린지 URL ==="
    echo "📝 Ann Day:              http://localhost/ann-day"
    echo "🔐 Base64:               http://localhost/base64"
    echo "🧮 Calculating Game:     http://localhost/calculating-game"
    echo "🍪 Cookie Admin:         http://localhost/cookieadmin"
    echo "🍪 Cookie CTF:           http://localhost/cookie-ctf"
    echo "📁 Directory Traversal:  http://localhost/directory-trav"
    echo "🖼️  Hidden Images:        http://localhost/hidden-images"
    echo "📱 Mobile Only:          http://localhost/mobile-only"
    echo "🛤️  Path CTF:             http://localhost/path-ctf"
    echo "🔍 Regex CTF:            http://localhost/regex-ctf"
    echo "👆 Why So Many Click:    http://localhost/why-so-many-click"
    echo ""
    echo "=== MCP 챌린지 URL (SSE 통신) ==="
    echo "🔌 MCP 9001:             http://localhost/dmcp-9001"
    echo "🔌 MCP 9002:             http://localhost/dmcp-9002"
    echo "🔌 MCP 9006:             http://localhost/dmcp-9006"
    echo "🔌 MCP 9007:             http://localhost/dmcp-9007"
    echo ""
}

# 메인 로직
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            setup
            shift
            ;;
        --build)
            build
            shift
            ;;
        --start)
            start
            shift
            ;;
        --stop)
            stop
            shift
            ;;
        --restart)
            restart
            shift
            ;;
        --logs)
            if [ -n "$2" ] && [[ ! "$2" =~ ^-- ]]; then
                logs "$2"
                shift 2
            else
                logs
                shift
            fi
            ;;
        --status)
            status
            shift
            ;;
        --clean)
            clean
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "알 수 없는 옵션: $1"
            usage
            exit 1
            ;;
    esac
done

print_success "작업이 완료되었습니다!"
