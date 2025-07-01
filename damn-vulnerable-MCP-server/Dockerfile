FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements_updated.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 권한 설정
RUN chmod +x *.sh 2>/dev/null || true

# supervisord 설정
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 포트 노출 (9001-9007)
EXPOSE 9001 9002 9006 9007

# supervisor로 모든 서비스 시작
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
