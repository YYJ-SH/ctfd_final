#!/bin/bash

echo "🎯 CTF 플랫폼 배포 시작!"

# CTFd 데이터 디렉토리 생성
mkdir -p ctfd/data/{CTFd/logs,CTFd/uploads,CTFd/themes,mysql,redis}

echo "🧹 기존 컨테이너 정리..."
docker-compose down --remove-orphans

echo "🔨 이미지 빌드..."
docker-compose build --parallel

echo "🚀 서비스 시작..."
docker-compose up -d

echo "⏳ 서비스 시작 대기..."
sleep 15

echo "🏥 헬스 체크..."
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ CTFd 시작 성공: http://ctf.localhost"
else
    echo "❌ CTFd 시작 확인 필요"
fi

echo ""
echo "🎉 배포 완료!"
echo "📊 Traefik 대시보드: http://localhost:8080"
echo ""
echo "🔗 URL 목록 보기:"
echo "./generate-urls.sh"