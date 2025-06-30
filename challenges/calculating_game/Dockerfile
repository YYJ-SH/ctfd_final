FROM php:8.2.2-apache

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 웹 소스 파일 복사
COPY deploy/src/ /var/www/html/

# 플래그 파일 복사
COPY deploy/flag /flag

# 권한 설정
RUN chmod 644 /flag
RUN chown www-data:www-data /var/www/html -R

# Apache 설정
RUN a2enmod rewrite

# 포트 노출
EXPOSE 80

# 컨테이너 시작시 실행할 명령
CMD ["apache2-foreground"]
