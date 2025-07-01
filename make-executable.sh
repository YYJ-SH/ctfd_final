#!/bin/bash

echo "CTF 플랫폼 설정 스크립트 권한 부여 중..."

# Windows에서도 실행 가능하도록 스크립트 권한 설정
chmod +x setup-ctf-platform.sh
chmod +x deploy.sh

echo "권한 부여 완료!"
echo ""
echo "이제 다음 명령어로 시작할 수 있습니다:"
echo "./deploy.sh --setup --build --start"
