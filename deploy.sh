#!/bin/bash

echo "🎯 CTF 플랫폼 배포 시작!"

# Docker와 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다!"
    echo "Docker 설치: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다!"
    echo "🔧 자동 설치를 시도합니다..."
    chmod +x install-docker-compose.sh
    ./install-docker-compose.sh
    
    # 다시 확인
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ 자동 설치 실패. 수동으로 설치해주세요."
        echo "https://docs.docker.com/compose/install/"
        exit 1
    fi
fi

echo "✅ Docker: $(docker --version)"
echo "✅ Docker Compose: $(docker-compose --version)"

# CTFd 데이터 디렉토리 생성
echo "📁 CTFd 데이터 디렉토리 생성 중..."
mkdir -p ctfd/data/{CTFd/logs,CTFd/uploads,CTFd/themes,mysql,redis}

echo "🧹 기존 컨테이너 정리..."
docker-compose down --remove-orphans 2>/dev/null || true

echo "🔨 이미지 빌드..."
docker-compose build --parallel

echo "🚀 서비스 시작..."
docker-compose up -d

echo "⏳ 서비스 시작 대기..."
sleep 20

echo "🏥 헬스 체크..."
# 여러 번 시도
for i in {1..5}; do
    if curl -f http://localhost > /dev/null 2>&1; then
        echo "✅ CTFd 시작 성공: http://ctf.localhost"
        break
    else
        echo "⏳ 시도 $i/5 - CTFd 시작 대기 중..."
        sleep 10
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ CTFd 시작 확인 필요"
        echo "🔍 컨테이너 상태 확인:"
        docker-compose ps
        echo ""
        echo "📋 CTFd 로그 확인:"
        docker-compose logs ctfd | tail -20
    fi
done

echo ""
echo "🎉 배포 완료!"
echo "📊 Traefik 대시보드: http://localhost:8080"
echo "🌐 CTFd 플랫폼: http://ctf.localhost"
echo ""
echo "🔗 URL 목록 보기:"
echo "./generate-urls.sh"
echo ""
echo "📋 서비스 상태 확인:"
docker-compose ps