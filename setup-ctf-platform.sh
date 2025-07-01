#!/bin/bash

# setup-ctf-platform.sh
# CTF 플랫폼 전체 설정을 자동화하는 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "=== CTF 플랫폼 설정 시작 ==="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
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

# 1. 환경 확인
print_status "환경 확인 중..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    print_error "Docker가 설치되어 있지 않습니다!"
    exit 1
fi

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose가 설치되어 있지 않습니다!"
    exit 1
fi

print_success "Docker 및 Docker Compose 확인 완료"

# 2. 디렉토리 구조 확인
print_status "디렉토리 구조 확인 중..."

required_dirs=("challenges" "damn-vulnerable-MCP-server")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        print_error "필수 디렉토리가 없습니다: $dir"
        exit 1
    fi
done

print_success "디렉토리 구조 확인 완료"

# 3. CTFd 클론 (없는 경우에만)
if [ ! -d "CTFd" ]; then
    print_status "CTFd 클론 중..."
    git clone https://github.com/CTFd/CTFd.git
    print_success "CTFd 클론 완료"
else
    print_warning "CTFd 디렉토리가 이미 존재합니다. 스킵..."
fi

# 4. Dockerfile 자동 생성
print_status "Dockerfile 자동 생성 중..."

# Flask 기반 챌린지용 Dockerfile 생성 함수
create_flask_dockerfile() {
    local challenge_dir="$1"
    local dockerfile_path="$challenge_dir/Dockerfile"
    
    cat > "$dockerfile_path" << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 권한 설정
RUN chmod -R 755 /app

# 포트 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 애플리케이션 실행
CMD ["python", "app.py"]
EOF
}

# PHP 기반 챌린지용 Dockerfile 생성 함수
create_php_dockerfile() {
    local challenge_dir="$1"
    local dockerfile_path="$challenge_dir/Dockerfile"
    
    cat > "$dockerfile_path" << 'EOF'
FROM php:8.1-apache

# 필요한 PHP 확장 설치
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Apache 설정
RUN a2enmod rewrite

# 소스 코드 복사
COPY deploy/src/ /var/www/html/
COPY deploy/flag /flag

# 권한 설정
RUN chown -R www-data:www-data /var/www/html
RUN chmod 644 /flag

# Apache 설정 파일 생성
RUN echo '<Directory /var/www/html>\n\
    Options Indexes FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' > /etc/apache2/conf-available/docker-php.conf

RUN a2enconf docker-php

# 포트 노출
EXPOSE 80

# Apache 시작
CMD ["apache2-foreground"]
EOF
}

# 각 챌린지 디렉토리에 Dockerfile 생성
for challenge in challenges/*; do
    if [ -d "$challenge" ]; then
        challenge_name=$(basename "$challenge")
        
        if [ ! -f "$challenge/Dockerfile" ]; then
            print_status "  $challenge_name: Dockerfile 생성 중..."
            
            if [ "$challenge_name" = "calculating_game" ]; then
                create_php_dockerfile "$challenge"
            else
                create_flask_dockerfile "$challenge"
            fi
            
            print_success "  $challenge_name: Dockerfile 생성 완료"
        else
            print_warning "  $challenge_name: Dockerfile이 이미 존재합니다"
        fi
    fi
done

# 5. 경로 문제 수정
print_status "경로 문제 수정 중..."

# Python 파일에서 Flask 설정 수정
fix_python_file() {
    local file_path="$1"
    
    # 백업 생성
    cp "$file_path" "$file_path.backup" 2>/dev/null || true
    
    # app.run() 설정 수정
    sed -i.tmp \
        -e 's/app\.run()/app.run(host="0.0.0.0", port=5000, debug=False)/g' \
        -e 's/app\.run(debug=True)/app.run(host="0.0.0.0", port=5000, debug=False)/g' \
        -e 's/app\.run(host=[^,]*,/app.run(host="0.0.0.0",/g' \
        "$file_path"
    
    rm -f "$file_path.tmp"
}

# HTML 파일에서 static 경로 수정
fix_html_file() {
    local file_path="$1"
    
    # 백업 생성
    cp "$file_path" "$file_path.backup" 2>/dev/null || true
    
    # static 파일 경로를 url_for로 변경
    sed -i.tmp \
        -e 's|src="/static/\([^"]*\)"|src="{{ url_for('\''static'\'', filename='\''\1'\'') }}"|g' \
        -e 's|href="/static/\([^"]*\)"|href="{{ url_for('\''static'\'', filename='\''\1'\'') }}"|g' \
        "$file_path"
    
    rm -f "$file_path.tmp"
}

# 각 챌린지의 파일들 수정
for challenge in challenges/*; do
    if [ -d "$challenge" ]; then
        challenge_name=$(basename "$challenge")
        print_status "  $challenge_name: 경로 수정 중..."
        
        # Python 파일들 수정
        find "$challenge" -name "*.py" -type f | while read -r py_file; do
            if [[ ! "$py_file" =~ \.backup$ ]]; then
                fix_python_file "$py_file"
            fi
        done
        
        # HTML 파일들 수정
        find "$challenge" -name "*.html" -type f | while read -r html_file; do
            if [[ ! "$html_file" =~ \.backup$ ]]; then
                fix_html_file "$html_file"
            fi
        done
        
        print_success "  $challenge_name: 경로 수정 완료"
    fi
done

# 6. 설정 완료 메시지
print_success "모든 설정이 완료되었습니다!"
echo ""
echo "=== 다음 단계 ==="
echo "1. 수정된 Docker Compose 파일 사용:"
echo "   cp docker-compose-fixed.yml docker-compose.yml"
echo ""
echo "2. Docker Compose 빌드 및 실행:"
echo "   docker-compose up --build -d"
echo ""
echo "3. 서비스 접속 URL:"
echo "   - CTFd 메인: http://localhost"
echo "   - Traefik 대시보드: http://localhost:8080"
echo "   - 웹 챌린지들: http://localhost/[challenge-name]"
echo "   - MCP 챌린지들: http://localhost/dmcp-[port]"
echo ""
print_warning "문제가 발생하면 .backup 파일로 복원할 수 있습니다."
