#!/bin/bash

echo "🔧 누락된 Dockerfile 일괄 생성 중..."

# app.py.py 파일들을 app.py로 이름 변경
find ./challenges -name "app.py.py" -exec sh -c 'mv "$1" "${1%.py}"' _ {} \;

# 모든 문제 폴더 체크
for dir in ./challenges/*/; do
    if [ -d "$dir" ]; then
        challenge_name=$(basename "$dir")
        echo ""
        echo "🔍 체크 중: $challenge_name"
        
        if [ ! -f "$dir/Dockerfile" ]; then
            echo "❌ Dockerfile 없음, 생성 중..."
            ./auto-dockerfile.sh "$dir"
        else
            echo "✅ Dockerfile 존재"
        fi
    fi
done

# DMCP Dockerfile 체크
echo ""
echo "🔍 DMCP 체크 중..."
if [ ! -f "./damn-vulnerable-MCP-server/Dockerfile" ]; then
    echo "❌ DMCP Dockerfile 없음, 생성 중..."
    cat > "./damn-vulnerable-MCP-server/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# 애플리케이션 파일들 복사
COPY . .

# 실행 권한 설정
RUN chmod +x *.sh 2>/dev/null || true

# 포트들 노출
EXPOSE 9001 9002 9006 9007

# 기본 실행 명령 (실제 DMCP 구조에 맞게 수정 필요)
CMD ["python", "-c", "print('DMCP Server Ready'); import time; time.sleep(3600)"]
EOF
    echo "✅ DMCP Dockerfile 생성 완료"
else
    echo "✅ DMCP Dockerfile 존재"
fi

echo ""
echo "🎉 모든 Dockerfile 생성/확인 완료!"
echo ""
echo "📋 생성된 Dockerfile 목록:"
find . -name "Dockerfile" | sort