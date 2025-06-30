#!/bin/bash

BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ 사용법: $0 <backup_directory>"
    exit 1
fi

echo "🔄 CTFd 데이터 복원 중..."

# 데이터베이스 복원
docker-compose exec -T db mysql -u ctfd -pctfd ctfd < "$BACKUP_DIR/database.sql"

# 업로드 파일 복원
cp -r "$BACKUP_DIR/uploads" ./ctfd/data/CTFd/

# 설정 파일 복원
cp "$BACKUP_DIR/config.py" ./ctfd/data/CTFd/

echo "✅ 복원 완료!"
docker-compose restart ctfd