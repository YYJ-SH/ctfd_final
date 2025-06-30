#!/bin/bash

# Number Master - 융보공 웹 해킹 문제 배포 스크립트
# Created by: 예지 (융합보안공학과)

echo "🎯 Number Master 게임 배포 시작..."
echo "Created by: 예지 (융합보안공학과)"
echo "==============================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}📄 파일 구조 확인 중...${NC}"
if [ ! -d "deploy/src" ]; then
    echo -e "${RED}❌ deploy/src 디렉토리가 없습니다!${NC}"
    exit 1
fi

if [ ! -f "deploy/src/game.php" ]; then
    echo -e "${RED}❌ game.php 파일이 없습니다!${NC}"
    exit 1
fi

if [ ! -f "deploy/flag" ]; then
    echo -e "${RED}❌ flag 파일이 없습니다!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 파일 구조 확인 완료!${NC}"

# Docker 이미지 빌드
echo -e "${YELLOW}🐳 Docker 이미지 빌드 중...${NC}"
docker build -t ybg-number-master .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker 이미지 빌드 성공!${NC}"
else
    echo -e "${RED}❌ Docker 이미지 빌드 실패!${NC}"
    exit 1
fi

# 기존 컨테이너 정리
echo -e "${YELLOW}🧹 기존 컨테이너 정리 중...${NC}"
docker-compose down 2>/dev/null

# Docker Compose로 실행
echo -e "${YELLOW}🚀 서비스 시작 중...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 서비스 시작 성공!${NC}"
    echo
    echo -e "${PURPLE}🌐 게임 URL: http://localhost:10001${NC}"
    echo -e "${YELLOW}🎯 플래그: YBG{V4r14bl3_FuNc710n5_4r3_D4ng3r0u5_1n_PHP_by_YuJi_2024}${NC}"
    echo
    echo -e "${GREEN}🎉 Number Master 게임이 성공적으로 배포되었습니다!${NC}"
    echo -e "${BLUE}💡 풀이 힌트: 'phpinfo'(1) 을 입력해보세요${NC}"
    echo
    echo -e "${PURPLE}📊 컨테이너 상태 확인:${NC}"
    docker-compose ps
else
    echo -e "${RED}❌ 서비스 시작 실패!${NC}"
    exit 1
fi

echo
echo "==============================================="
echo -e "${PURPLE}Created by 예지 (융합보안공학과) with ❤️${NC}"
