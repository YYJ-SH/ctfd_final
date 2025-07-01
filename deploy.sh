#!/bin/bash

# production-deploy.sh
# 실제 호스팅 환경을 위한 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 서버 설정
SERVER_IP="49.50.135.55"
DOMAIN_NAME=""  # 도메인이 있다면 여기에 입력

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
    echo "  --setup     프로덕션 환경 초기 설정"
    echo "  --deploy    서비스 배포"
    echo "  --restart   서비스 재시작"
    echo "  --stop      서비스 중지"
    echo "  --status    서비스 상태 확인"
    echo "  --logs      로그 확인"
    echo "  --generate-urls   챌린지 URL 생성"
    echo "  --backup    데이터 백업"
    echo "  --restore   데이터 복원"
    echo "  --ssl       SSL 인증서 설정 (Let's Encrypt)"
    echo "  --monitor   실시간 모니터링"
    echo "  --help      도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0 --setup --deploy --generate-urls"
    echo "  $0 --restart"
    echo "  $0 --monitor"
}

# 프로덕션 환경 초기 설정
setup_production() {
    print_status "프로덕션 환경 초기 설정 시작..."
    
    # 시스템 업데이트
    print_status "시스템 업데이트 중..."
    sudo apt-get update && sudo apt-get upgrade -y
    
    # Docker 설치 확인
    if ! command -v docker &> /dev/null; then
        print_status "Docker 설치 중..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    # Docker Compose 설치 확인
    if ! command -v docker-compose &> /dev/null; then
        print_status "Docker Compose 설치 중..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    # 방화벽 설정
    print_status "방화벽 설정 중..."
    sudo ufw allow 22/tcp   # SSH
    sudo ufw allow 80/tcp   # HTTP
    sudo ufw allow 443/tcp  # HTTPS
    sudo ufw --force enable
    
    # 시스템 리소스 최적화
    print_status "시스템 리소스 최적화 중..."
    
    # 스왑 메모리 설정 (4GB)
    if [ ! -f /swapfile ]; then
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
    
    # Docker 데몬 최적화
    sudo mkdir -p /etc/docker
    cat > /tmp/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2"
}
EOF
    sudo mv /tmp/daemon.json /etc/docker/daemon.json
    sudo systemctl restart docker
    
    # 프로덕션용 디렉토리 생성
    mkdir -p ./backups
    mkdir -p ./logs
    mkdir -p ./ssl
    
    print_success "프로덕션 환경 설정 완료"
}

# 서비스 배포
deploy() {
    print_status "서비스 배포 시작..."
    
    # 프로덕션용 Docker Compose 파일 사용
    if [ -f "docker-compose-production.yml" ]; then
        cp docker-compose-production.yml docker-compose.yml
        print_status "프로덕션용 Docker Compose 파일 적용"
    else
        print_error "docker-compose-production.yml 파일을 찾을 수 없습니다."
        exit 1
    fi
    
    # 기존 서비스 중지
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # 이미지 빌드 및 시작
    print_status "Docker 이미지 빌드 중..."
    docker-compose build --no-cache --parallel
    
    print_status "서비스 시작 중..."
    docker-compose up -d
    
    # 서비스 헬스체크
    print_status "서비스 상태 확인 중..."
    sleep 30
    
    if docker-compose ps | grep -q "Up"; then
        print_success "서비스 배포 완료"
        show_service_urls
    else
        print_error "서비스 시작에 실패했습니다"
        docker-compose logs
        exit 1
    fi
}

# 서비스 재시작
restart() {
    print_status "서비스 재시작 중..."
    docker-compose restart
    sleep 10
    docker-compose ps
    print_success "서비스 재시작 완료"
}

# 서비스 중지
stop() {
    print_status "서비스 중지 중..."
    docker-compose down
    print_success "서비스 중지 완료"
}

# 서비스 상태 확인
status() {
    print_status "서비스 상태 확인 중..."
    
    echo ""
    echo "=== Docker Compose 서비스 ==="
    docker-compose ps
    
    echo ""
    echo "=== 시스템 리소스 ==="
    echo "CPU 사용률:"
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
    
    echo "메모리 사용률:"
    free -h
    
    echo "디스크 사용률:"
    df -h /
    
    echo ""
    echo "=== 네트워크 연결 테스트 ==="
    
    # 헬스체크
    if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_IP} | grep -q "200\|302"; then
        print_success "메인 서비스: 정상"
    else
        print_error "메인 서비스: 비정상"
    fi
    
    # 샘플 챌린지 테스트
    if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_IP}/challenges/base64 | grep -q "200"; then
        print_success "웹 챌린지: 정상"
    else
        print_warning "웹 챌린지: 확인 필요"
    fi
}

# 로그 확인
logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        print_status "전체 서비스 로그 확인..."
        docker-compose logs --tail=100 -f
    else
        print_status "$service 서비스 로그 확인..."
        docker-compose logs --tail=100 -f "$service"
    fi
}

# 챌린지 URL 생성
generate_urls() {
    print_status "챌린지 URL 생성 중..."
    
    if [ -f "challenge_url_generator.py" ]; then
        python3 challenge_url_generator.py
        print_success "챌린지 URL 생성 완료"
        
        echo ""
        print_status "생성된 파일:"
        echo "  📄 ctfd_challenges_import.json - CTFd 관리자 패널에서 임포트"
        echo "  📄 participant_guide.md - 참가자들에게 배포"
        
        if [ -f "participant_guide.md" ]; then
            echo ""
            print_status "참가자용 빠른 접속 URL:"
            echo "  🌐 메인: http://${SERVER_IP}"
            echo "  📋 챌린지 가이드: cat participant_guide.md"
        fi
    else
        print_error "challenge_url_generator.py 파일을 찾을 수 없습니다."
        exit 1
    fi
}

# 데이터 백업
backup() {
    print_status "데이터 백업 시작..."
    
    backup_dir="./backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Docker 볼륨 백업
    print_status "Docker 볼륨 백업 중..."
    docker run --rm -v ctfd_uploads:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/ctfd_uploads.tar.gz -C /data .
    docker run --rm -v mysql_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/mysql_data.tar.gz -C /data .
    docker run --rm -v redis_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    
    # 설정 파일 백업
    print_status "설정 파일 백업 중..."
    cp docker-compose.yml "$backup_dir/"
    cp -r challenges "$backup_dir/" 2>/dev/null || true
    cp -r damn-vulnerable-MCP-server "$backup_dir/" 2>/dev/null || true
    
    print_success "백업 완료: $backup_dir"
}

# 데이터 복원
restore() {
    print_warning "데이터 복원을 진행하시겠습니까? 기존 데이터가 삭제됩니다. (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "복원을 취소했습니다."
        return
    fi
    
    echo "백업 디렉토리를 입력하세요:"
    read -r backup_dir
    
    if [ ! -d "$backup_dir" ]; then
        print_error "백업 디렉토리를 찾을 수 없습니다: $backup_dir"
        return
    fi
    
    print_status "데이터 복원 시작..."
    
    # 서비스 중지
    docker-compose down
    
    # 볼륨 복원
    if [ -f "$backup_dir/ctfd_uploads.tar.gz" ]; then
        docker run --rm -v ctfd_uploads:/data -v $(pwd)/$backup_dir:/backup alpine tar xzf /backup/ctfd_uploads.tar.gz -C /data
    fi
    
    if [ -f "$backup_dir/mysql_data.tar.gz" ]; then
        docker run --rm -v mysql_data:/data -v $(pwd)/$backup_dir:/backup alpine tar xzf /backup/mysql_data.tar.gz -C /data
    fi
    
    if [ -f "$backup_dir/redis_data.tar.gz" ]; then
        docker run --rm -v redis_data:/data -v $(pwd)/$backup_dir:/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
    fi
    
    # 서비스 재시작
    docker-compose up -d
    
    print_success "데이터 복원 완료"
}

# SSL 인증서 설정
setup_ssl() {
    if [ -z "$DOMAIN_NAME" ]; then
        print_error "도메인 이름이 설정되지 않았습니다. 스크립트 상단의 DOMAIN_NAME을 설정하세요."
        return
    fi
    
    print_status "SSL 인증서 설정 시작..."
    
    # Certbot 설치
    sudo apt-get install -y certbot
    
    # SSL 인증서 발급
    sudo certbot certonly --standalone --email admin@${DOMAIN_NAME} --agree-tos --no-eff-email -d ${DOMAIN_NAME}
    
    # Traefik SSL 설정 업데이트
    print_status "Traefik SSL 설정 업데이트 중..."
    # SSL 설정은 추가 구현 필요
    
    print_success "SSL 인증서 설정 완료"
}

# 실시간 모니터링
monitor() {
    print_status "실시간 모니터링 시작 (Ctrl+C로 종료)"
    
    while true; do
        clear
        echo "=== CTF 플랫폼 실시간 모니터링 ==="
        echo "시간: $(date)"
        echo ""
        
        # 서비스 상태
        echo "📊 서비스 상태:"
        docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        
        # 시스템 리소스
        echo "💻 시스템 리소스:"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
        echo "메모리: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
        echo "디스크: $(df / | tail -1 | awk '{printf "%s", $5}')"
        
        echo ""
        
        # 네트워크 연결 테스트
        echo "🌐 서비스 상태:"
        if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_IP} | grep -q "200\|302"; then
            echo "✅ 메인 서비스: 정상"
        else
            echo "❌ 메인 서비스: 비정상"
        fi
        
        # 최근 로그
        echo ""
        echo "📋 최근 로그 (마지막 5줄):"
        docker-compose logs --tail=5 --no-color | tail -10
        
        sleep 5
    done
}

# 서비스 URL 표시
show_service_urls() {
    echo ""
    echo "🌐 === 서비스 접속 정보 ==="
    echo "메인 URL: http://${SERVER_IP}"
    echo "CTFd 관리자: http://${SERVER_IP}/admin"
    echo ""
    echo "📋 챌린지 URL 생성: $0 --generate-urls"
    echo "📊 상태 모니터링: $0 --monitor"
}

# 메인 로직
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            setup_production
            shift
            ;;
        --deploy)
            deploy
            shift
            ;;
        --restart)
            restart
            shift
            ;;
        --stop)
            stop
            shift
            ;;
        --status)
            status
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
        --generate-urls)
            generate_urls
            shift
            ;;
        --backup)
            backup
            shift
            ;;
        --restore)
            restore
            shift
            ;;
        --ssl)
            setup_ssl
            shift
            ;;
        --monitor)
            monitor
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