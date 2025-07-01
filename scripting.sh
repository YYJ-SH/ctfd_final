#!/bin/bash

echo "📁 Flask + HTML 경로 일괄 수정 스크립트 시작합니다..."

TARGET_DIR="./challenges"

# .py, .html 파일 전체 검색
find "$TARGET_DIR" -type f \( -name "*.py" -o -name "*.html" \) | while read -r file; do
    echo "🔍 처리 중: $file"

    # 백업 생성
    cp "$file" "$file.bak"
    echo "  ↪️ 백업 저장됨: $file.bak"

    # 경로 정규표현식 수정
    sed -i \
        -E 's|href="/([^"]+)"|href="\1"|g' \
        -E "s|href='/([^']+)'|href='\1'|g" \
        -E 's|action="/([^"]+)"|action="\1"|g' \
        -E "s|action='/([^']+)'|action='\1'|g" \
        -E 's|src="/static/([^"]+\.png)"|src="static/\1"|g' \
        -E "s|src='/static/([^']+\.png)'|src='static/\1'|g" \
        -E "s|url_for\('static', filename='([^']+\.png)'\)|'static/\1'|g" \
        "$file"

    echo "  ✅ 수정 완료!"
done

echo "🎉 모든 .py 및 .html 경로가 성공적으로 정리되었습니다!"
