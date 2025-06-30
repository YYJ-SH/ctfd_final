# 동아리 모집 공고 웹 애플리케이션

이 프로젝트는 Flask를 사용하여 만든 동아리 회원 모집 공고 웹 애플리케이션입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 이미지 추가:
- `static/images/header.jpg` 파일을 추가하세요 (권장 크기: 1920x300 픽셀)

## 실행 방법

```bash
python app.py
```

서버가 시작되면 웹 브라우저에서 http://localhost:5000 으로 접속하세요.

## 설정 변경

`app.py` 파일의 `club_info` 딕셔너리를 수정하여 동아리 정보를 변경할 수 있습니다:
- name: 동아리 이름
- description: 동아리 소개
- requirements: 지원 자격 요건
- deadline: 지원 마감일
- contact: 문의 연락처 