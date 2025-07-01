#!/bin/bash

# fix-flask-static-paths.sh
# Flask 앱의 static 경로 문제를 해결하는 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

CHALLENGES_DIR="./challenges"

# Flask 앱 코드 수정 함수
fix_flask_app() {
    local app_file="$1"
    local challenge_name="$2"
    
    print_status "Flask 앱 수정 중: $app_file"
    
    # 백업 생성
    cp "$app_file" "${app_file}.backup"
    
    # Python 파일 수정 - APPLICATION_ROOT 설정 추가
    cat > "${app_file}.tmp" << EOF
import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for

app = Flask(__name__)

# 프로덕션 환경에서 APPLICATION_ROOT 설정
if os.environ.get('FLASK_ENV') == 'production':
    app.config['APPLICATION_ROOT'] = '/challenges/${challenge_name}'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

# 기존 코드 유지하면서 static 경로 수정
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

EOF
    
    # 기존 파일에서 import와 app 설정 부분을 제외한 나머지 코드 추가
    sed -n '/^from flask import/,/^app = Flask/d; /^@app\.route/,$p' "$app_file" >> "${app_file}.tmp"
    
    # app.run() 부분 수정
    sed -i 's/app\.run.*/app.run(host="0.0.0.0", port=5000, debug=False)/' "${app_file}.tmp"
    
    # 원본 파일 교체
    mv "${app_file}.tmp" "$app_file"
    
    print_success "Flask 앱 수정 완료: $app_file"
}

# HTML 템플릿 수정 함수
fix_html_template() {
    local html_file="$1"
    local challenge_name="$2"
    
    print_status "HTML 템플릿 수정 중: $html_file"
    
    # 백업 생성
    cp "$html_file" "${html_file}.backup"
    
    # static 경로를 절대 경로로 변경
    sed -i.tmp \
        -e "s|src=\"/static/|src=\"/challenges/${challenge_name}/static/|g" \
        -e "s|href=\"/static/|href=\"/challenges/${challenge_name}/static/|g" \
        -e "s|url('/static/|url('/challenges/${challenge_name}/static/|g" \
        -e "s|url(\"/static/|url(\"/challenges/${challenge_name}/static/|g" \
        "$html_file"
    
    # 임시 파일 제거
    rm -f "${html_file}.tmp"
    
    print_success "HTML 템플릿 수정 완료: $html_file"
}

# Dockerfile 수정 함수 (환경변수 추가)
fix_dockerfile() {
    local dockerfile="$1"
    local challenge_name="$2"
    
    print_status "Dockerfile 수정 중: $dockerfile"
    
    # 백업 생성
    cp "$dockerfile" "${dockerfile}.backup"
    
    # 환경변수 추가
    cat >> "$dockerfile" << EOF

# 프로덕션 환경 설정
ENV FLASK_ENV=production
ENV APPLICATION_ROOT=/challenges/${challenge_name}

EOF
    
    print_success "Dockerfile 수정 완료: $dockerfile"
}

# 메인 수정 함수
fix_challenge() {
    local challenge_dir="$1"
    local challenge_name=$(basename "$challenge_dir")
    
    print_status "챌린지 수정 중: $challenge_name"
    
    # Python 파일들 수정
    find "$challenge_dir" -name "*.py" -type f | while read -r py_file; do
        if [[ ! "$py_file" =~ \.backup$ ]] && [[ "$py_file" =~ app\.py ]]; then
            fix_flask_app "$py_file" "$challenge_name"
        fi
    done
    
    # HTML 템플릿들 수정
    find "$challenge_dir" -name "*.html" -type f | while read -r html_file; do
        if [[ ! "$html_file" =~ \.backup$ ]]; then
            fix_html_template "$html_file" "$challenge_name"
        fi
    done
    
    # Dockerfile 수정
    if [ -f "$challenge_dir/Dockerfile" ]; then
        fix_dockerfile "$challenge_dir/Dockerfile" "$challenge_name"
    fi
    
    print_success "챌린지 수정 완료: $challenge_name"
}

# 모든 챌린지 수정
fix_all_challenges() {
    print_status "모든 챌린지의 static 경로 문제 수정 시작..."
    
    for challenge in "$CHALLENGES_DIR"/*; do
        if [ -d "$challenge" ]; then
            challenge_name=$(basename "$challenge")
            
            # calculating_game은 PHP이므로 제외
            if [ "$challenge_name" != "calculating_game" ]; then
                fix_challenge "$challenge"
            else
                print_warning "PHP 챌린지는 건너뜀: $challenge_name"
            fi
        fi
    done
    
    print_success "모든 챌린지 수정 완료!"
}

# 백업 복원 함수
restore_backups() {
    print_warning "모든 백업 파일로 복원하시겠습니까? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "백업 파일로 복원 중..."
        
        find "$CHALLENGES_DIR" -name "*.backup" | while read -r backup_file; do
            original_file="${backup_file%.backup}"
            cp "$backup_file" "$original_file"
            print_status "복원: $original_file"
        done
        
        print_success "모든 파일이 백업으로 복원되었습니다."
    else
        print_status "복원을 취소했습니다."
    fi
}

# 사용법
usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --fix       모든 챌린지의 static 경로 문제 수정"
    echo "  --restore   백업 파일로 복원"
    echo "  --help      도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0 --fix"
    echo "  $0 --restore"
}

# 메인 로직
case "${1:-}" in
    --fix)
        fix_all_challenges
        ;;
    --restore)
        restore_backups
        ;;
    --help)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac