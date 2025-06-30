#!/bin/bash

echo "🔧 Docker Compose 설치 중..."

# 운영체제 확인
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux 환경 감지"
    
    # Docker Compose 최신 버전 다운로드
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 실행 권한 부여
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 심볼릭 링크 생성 (선택사항)
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS 환경 감지"
    
    # Homebrew가 있는지 확인
    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew로 설치 중..."
        brew install docker-compose
    else
        echo "❌ Homebrew가 설치되지 않았습니다. Docker Desktop을 설치하세요."
        echo "   https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Windows 환경 감지"
    echo "Windows에서는 Docker Desktop을 설치하는 것을 권장합니다."
    echo "https://www.docker.com/products/docker-desktop"
    
    # Windows용 Docker Compose 다운로드 (PowerShell 필요)
    echo "또는 아래 명령어를 PowerShell에서 실행하세요:"
    echo 'Invoke-WebRequest "https://github.com/docker/compose/releases/latest/download/docker-compose-Windows-x86_64.exe" -UseBasicParsing -OutFile $Env:ProgramFiles\Docker\Docker\resources\bin\docker-compose.exe'
    
else
    echo "❌ 알 수 없는 운영체제입니다."
    exit 1
fi

echo "✅ Docker Compose 설치 완료!"

# 설치 확인
if command -v docker-compose &> /dev/null; then
    echo "🎉 설치 성공! 버전: $(docker-compose --version)"
else
    echo "❌ 설치 실패. 수동으로 설치해주세요."
    echo "https://docs.docker.com/compose/install/"
fi