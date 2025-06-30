import os

# CTFd 커스텀 설정
class Config(object):
    # 보안 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ctfd_secret_key_change_this_in_production'
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://ctfd:ctfd@db/ctfd'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis 설정
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://cache:6379'
    
    # 파일 업로드 설정
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/var/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # CTF 설정
    CTF_NAME = "우리 CTF 2025"
    CTF_DESCRIPTION = "해킹 실력을 겨뤄보세요!"
    
    # 로그 설정
    LOG_FOLDER = '/var/log/CTFd'
    
    # 리버스 프록시 설정 (Traefik 사용시 필요)
    REVERSE_PROXY = True
    
    # 이메일 설정 (선택사항)
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'your-email@gmail.com'
    # MAIL_PASSWORD = 'your-app-password'