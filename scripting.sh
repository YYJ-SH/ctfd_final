#!/bin/bash

echo "🧼 경로 자동 수정 시작합니다..."

TARGET_DIR="./challenges"

find "$TARGET_DIR" -type f \( -name "*.py" -o -name "*.html" \) | while read -r file; do
    echo "📂 처리 중: $file"

    # 백업
    cp "$file" "$file.bak"

    # sed 명령을 하나로 작성 (큰 따옴표 내부)
    sed -i -E "
        s|href=\"/([^\"#]+)\"|href=\"\1\"|g;
        s|href='/([^'#]+)'|href='\1'|g;
        s|action=\"/([^\"#]+)\"|action=\"\1\"|g;
        s|action='/([^'#]+)'|action='\1'|g;
        s|src=\"/static/([^\"#]+\.png)\"|src=\"static/\1\"|g;
        s|src='/static/([^'#]+\.png)'|src='static/\1'|g;
        s|url_for\('static', filename='([^']+\.png)'\)|'static/\1'|g
    " "$file"

    echo "✅ 완료!"
done

echo "🎉 전체 파일 경로 상대화 완료!"
