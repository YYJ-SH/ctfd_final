#!/bin/bash

# 전체 문제 Dockerfile 일괄 생성기
# 사용법: ./setup-all-challenges.sh

echo "🚀 CTF 문제 자동 설정 시작!"
echo "================================"

CHALLENGES_DIR="./challenges"
DMCP_DIR="./damn-vulnerable-MCP-server"

# 웹 문제들 처리
if [ -d "$CHALLENGES_DIR" ]; then
    echo "📁 웹 문제들 처리 중..."
    
    for challenge_dir in "$CHALLENGES_DIR"/*; do
        if [ -d "$challenge_dir" ]; then
            challenge_name=$(basename "$challenge_dir")
            echo ""
            echo "🔨 처리 중: $challenge_name"
            
            # app.py.py를 app.py로 이름 변경
            if [ -f "$challenge_dir/app.py.py" ]; then
                echo "   📝 app.py.py → app.py"
                mv "$challenge_dir/app.py.py" "$challenge_dir/app.py"
            fi
            
            # Dockerfile이 없으면 생성
            if [ ! -f "$challenge_dir/Dockerfile" ]; then
                ./auto-dockerfile.sh "$challenge_dir"
            else
                echo "   ⚠️  Dockerfile이 이미 존재함 (건너뜀)"
            fi
        fi
    done
fi

# DMCP 처리
if [ -d "$DMCP_DIR" ]; then
    echo ""
    echo "📁 DMCP 서비스 처리 중..."
    
    # DMCP Dockerfile이 없으면 생성
    if [ ! -f "$DMCP_DIR/Dockerfile" ]; then
        echo "🐍 DMCP Python 서비스로 감지됨"
        
        cat > "$DMCP_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일들 복사
COPY . .

# 실행 권한 설정
RUN chmod +x *.sh

# 포트들 노출 (9001, 9002, 9006, 9007)
EXPOSE 9001 9002 9006 9007

# Supervisor로 멀티 서비스 실행
CMD ["supervisord", "-c", "/app/supervisord.conf", "-n"]
EOF
        echo "✅ DMCP Dockerfile 생성 완료"
    else
        echo "⚠️  DMCP Dockerfile이 이미 존재함"
    fi
fi

echo ""
echo "================================"
echo "🎉 모든 설정 완료!"
echo "================================"
echo ""
echo "🚀 다음 단계:"
echo "   1. ./generate-docker-compose.sh 실행"
echo "   2. ./deploy.sh 실행"
echo ""
echo "📂 생성된 파일들:"
echo "   - 각 문제별 Dockerfile"
echo "   - DMCP Dockerfile"