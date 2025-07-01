#!/bin/bash

echo "🔧 모든 문제의 절대 경로를 상대 경로로 수정 중..."

# 백업 폴더 생성
BACKUP_DIR="./backup_paths_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 백업 폴더: $BACKUP_DIR"

# 모든 Python 파일에서 절대 경로 찾기
for app_file in ./challenges/*/app.py; do
    if [ -f "$app_file" ]; then
        challenge_name=$(dirname "$app_file" | xargs basename)
        echo ""
        echo "🔧 수정 중: $challenge_name"
        
        # 백업
        cp "$app_file" "$BACKUP_DIR/${challenge_name}_app.py"
        
        # 절대 경로를 상대 경로로 변경
        # href="/path" → href="path"
        sed -i 's|href="/\([^"]*\)"|href="\1"|g' "$app_file"
        sed -i "s|href='/\([^']*\)'|href='\1'|g" "$app_file"
        
        # action="/path" → action="path"  
        sed -i 's|action="/\([^"]*\)"|action="\1"|g' "$app_file"
        sed -i "s|action='/\([^']*\)'|action='\1'|g" "$app_file"
        
        # src="/path" → src="path"
        sed -i 's|src="/\([^"]*\)"|src="\1"|g' "$app_file"
        sed -i "s|src='/\([^']*\)'|src='\1'|g" "$app_file"
        
        # 루트 경로는 현재 디렉토리로
        sed -i 's|href=""|href="."|g' "$app_file"
        sed -i "s|href=''|href='.'|g" "$app_file"
        
        echo "   ✅ 완료"
    fi
done

echo ""
echo "🎉 모든 문제 수정 완료!"
echo ""
echo "🚀 이제 다시 빌드하세요:"
echo "   docker-compose build"
echo "   docker-compose up -d"