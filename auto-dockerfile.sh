#!/bin/bash

# 자동 Dockerfile 생성기
# 사용법: ./auto-dockerfile.sh <challenge_directory>

set -e

CHALLENGE_DIR="$1"
CHALLENGE_NAME=$(basename "$CHALLENGE_DIR")

if [ -z "$CHALLENGE_DIR" ]; then
    echo "❌ 사용법: $0 <challenge_directory>"
    echo "예시: $0 ./challenges/ann_day"
    exit 1
fi

if [ ! -d "$CHALLENGE_DIR" ]; then
    echo "❌ 디렉토리가 존재하지 않습니다: $CHALLENGE_DIR"
    exit 1
fi

echo "🔍 $CHALLENGE_NAME 문제 분석 중..."

# 파일 존재 여부 확인
HAS_FLASK=$(find "$CHALLENGE_DIR" -name "*.py" -exec grep -l "flask\|Flask" {} \; 2>/dev/null | wc -l)
HAS_PHP=$(find "$CHALLENGE_DIR" -name "*.php" 2>/dev/null | wc -l)
HAS_NODE=$(find "$CHALLENGE_DIR" -name "package.json" 2>/dev/null | wc -l)
HAS_HTML=$(find "$CHALLENGE_DIR" -name "*.html" 2>/dev/null | wc -l)
HAS_REQUIREMENTS=$([ -f "$CHALLENGE_DIR/requirements.txt" ] && echo 1 || echo 0)
HAS_APP_PY=$(find "$CHALLENGE_DIR" -name "app.py*" 2>/dev/null | wc -l)
HAS_INDEX_PHP=$([ -f "$CHALLENGE_DIR/index.php" ] && echo 1 || echo 0)

echo "📊 분석 결과:"
echo "   Flask 파일: $HAS_FLASK"
echo "   PHP 파일: $HAS_PHP"
echo "   Node.js: $HAS_NODE"
echo "   HTML 파일: $HAS_HTML"
echo "   requirements.txt: $HAS_REQUIREMENTS"
echo "   app.py 파일: $HAS_APP_PY"

# Dockerfile 생성
DOCKERFILE_PATH="$CHALLENGE_DIR/Dockerfile"

if [ "$HAS_FLASK" -gt 0 ] || [ "$HAS_APP_PY" -gt 0 ]; then
    echo "🐍 Flask 애플리케이션으로 감지됨"
    
    # requirements.txt가 없으면 생성
    if [ "$HAS_REQUIREMENTS" -eq 0 ]; then
        echo "📝 requirements.txt 생성 중..."
        cat > "$CHALLENGE_DIR/requirements.txt" << EOF
Flask==2.3.3
werkzeug==2.3.7
EOF
    fi
    
    # app.py.py 파일이 있으면 app.py로 이름 변경
    if [ -f "$CHALLENGE_DIR/app.py.py" ]; then
        echo "📝 app.py.py를 app.py로 이름 변경..."
        mv "$CHALLENGE_DIR/app.py.py" "$CHALLENGE_DIR/app.py"
    fi
    
    # Flask Dockerfile 생성
    cat > "$DOCKERFILE_PATH" << EOF
FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \\
    curl \\
    sqlite3 \\
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일들 복사
COPY . .

# 플래그 파일이 있다면 권한 설정
RUN find . -name "flag*.txt" -exec chmod 644 {} \; 2>/dev/null || true

# 데이터베이스 초기화 (init_db.py가 있다면)
RUN if [ -f "init_db.py" ]; then python init_db.py; fi

# 비특권 사용자 생성 및 전환
RUN useradd -m -u 1000 ctfuser && \\
    chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

# Flask 앱 실행 (포트 5000에서 모든 인터페이스에 바인드)
CMD ["python", "-c", "import app; app.app.run(host='0.0.0.0', port=5000, debug=False)"]
EOF

elif [ "$HAS_PHP" -gt 0 ]; then
    echo "🐘 PHP 애플리케이션으로 감지됨"
    
    # PHP Dockerfile 생성
    cat > "$DOCKERFILE_PATH" << EOF
FROM php:8.2.2-apache

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \\
    curl \\
    sqlite3 \\
    && rm -rf /var/lib/apt/lists/*

# 웹 소스 파일 복사
COPY . /var/www/html/

# deploy/src 폴더가 있다면 그 내용을 웹 루트로 복사
RUN if [ -d "/var/www/html/deploy/src" ]; then \\
        cp -r /var/www/html/deploy/src/* /var/www/html/ && \\
        rm -rf /var/www/html/deploy; \\
    fi

# 플래그 파일 복사 및 권한 설정 (deploy/flag가 있다면)
RUN find /var/www/html -name "flag" -not -path "*/.*" -exec cp {} /flag \; 2>/dev/null || true
RUN find /var/www/html -name "flag*.txt" -exec cp {} / \; 2>/dev/null || true
RUN find / -name "flag*" -maxdepth 1 -exec chmod 644 {} \; 2>/dev/null || true

# 권한 설정
RUN chown www-data:www-data /var/www/html -R

# Apache 설정
RUN a2enmod rewrite

# 포트 노출
EXPOSE 80

# 컨테이너 시작시 실행할 명령
CMD ["apache2-foreground"]
EOF

elif [ "$HAS_NODE" -gt 0 ]; then
    echo "📦 Node.js 애플리케이션으로 감지됨"
    
    # Node.js Dockerfile 생성
    cat > "$DOCKERFILE_PATH" << EOF
FROM node:18-alpine

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 애플리케이션 소스 복사
COPY . .

# 플래그 파일 권한 설정 (있다면)
RUN find . -name "flag*" -exec chmod 644 {} \; 2>/dev/null || true

# 비특권 사용자 생성
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nextjs -u 1001
USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
EOF

elif [ "$HAS_HTML" -gt 0 ]; then
    echo "🌐 정적 웹사이트로 감지됨"
    
    # Nginx 정적 파일 Dockerfile 생성
    cat > "$DOCKERFILE_PATH" << EOF
FROM nginx:alpine

# 웹 파일들 복사
COPY . /usr/share/nginx/html/

# 플래그 파일 복사 및 권한 설정 (있다면)
RUN find /usr/share/nginx/html -name "flag*" -exec cp {} / \; 2>/dev/null || true
RUN find / -name "flag*" -maxdepth 1 -exec chmod 644 {} \; 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

else
    echo "❌ 알 수 없는 애플리케이션 타입입니다."
    echo "수동으로 Dockerfile을 작성해주세요."
    exit 1
fi

echo "✅ Dockerfile 생성 완료: $DOCKERFILE_PATH"
echo ""
echo "🔧 생성된 Dockerfile 내용:"
echo "================================"
cat "$DOCKERFILE_PATH"
echo "================================"
echo ""
echo "💡 다음 단계:"
echo "   docker build -t $CHALLENGE_NAME $CHALLENGE_DIR"
echo "   docker run -p 5000:5000 $CHALLENGE_NAME"