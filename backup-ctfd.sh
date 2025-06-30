#!/bin/bash

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 CTFd 데이터 백업 중..."

# 데이터베이스 백업
docker-compose exec db mysqldump -u ctfd -pctfd ctfd > "$BACKUP_DIR/database.sql"

# 업로드 파일 백업
cp -r ./ctfd/data/CTFd/uploads "$BACKUP_DIR/"

# 설정 파일 백업
cp ./ctfd/data/CTFd/config.py "$BACKUP_DIR/"

echo "✅ 백업 완료: $BACKUP_DIR"