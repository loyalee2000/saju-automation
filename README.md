# 사주 자동화 시스템

명리설리연구소 - 사주 팔자 계산 및 운세 풀이 자동화 프로그램

## 📋 프로젝트 개요

이 프로젝트는 2개의 독립적인 프로그램으로 구성되어 있습니다:

### 프로그램 1: 사주 계산 엔진
- **입력**: 생년월일시, 성별
- **처리**: 사주 팔자 계산 (천간지지, 오행, 십성, 대운 등)
- **출력**: JSON 파일

### 프로그램 2: PDF 생성기
- **입력**: JSON 파일 (프로그램 1의 출력)
- **처리**: OpenAI API를 통한 13장 운세 풀이 생성
- **출력**: PDF 파일

## 🗂️ 프로젝트 구조

```
saju-automation/
├── program1-calculator/      # 사주 계산 엔진
│   ├── saju_calculator.py
│   ├── requirements.txt
│   └── README.md
│
├── program2-pdf-generator/    # PDF 생성기
│   ├── pdf_generator.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── data/                      # 데이터 저장 폴더
│   ├── sample_output.json    # 샘플 JSON
│   ├── *.json                 # 생성된 사주 데이터
│   └── *.pdf                  # 생성된 PDF 파일
│
└── README.md                  # 이 파일
```

## 🚀 빠른 시작

### 1단계: 프로그램 1 실행 (사주 계산)

```bash
cd program1-calculator
pip install -r requirements.txt
python saju_calculator.py
```

입력 예시:
```
출생년도: 1990
출생월: 1
출생일: 15
출생시간: 10
출생분: 30
성별: 남
음력입니까? (y/n): n
```

출력: `../data/saju_19900115_1030.json`

### 2단계: 프로그램 2 실행 (PDF 생성)

```bash
cd program2-pdf-generator

# .env 파일 생성 (OpenAI API 키 설정)
cp .env.example .env
# .env 파일을 열어서 API 키 입력

pip install -r requirements.txt
python pdf_generator.py
```

입력 예시:
```
JSON 파일 경로: ../data/saju_19900115_1030.json
```

출력: `../data/saju_fortune_YYYYMMDD_HHMMSS.pdf`

## 📚 PDF 13장 구성

1. 사주에 대한 이해
2. 사주팔자 원국 분석
3. 일주 및 성격 분석
4. 십성 분석
5. 십이운성 분석
6. 십이신살 및 귀인 분석
7. 연애운 및 결혼운 분석
8. 재물운 분석
9. 직업운 분석
10. 건강운 분석
11. 대운 흐름 분석
12. 10년 연운 흐름 분석
13. 2026년 월운 흐름 분석

## 🔧 기술 스택

- **Python 3.8+**
- **korean-lunar-calendar**: 음력/양력 변환
- **OpenAI API (gpt-4o-mini)**: 운세 풀이 생성
- **ReportLab**: PDF 생성

## 💰 비용

- 프로그램 1: 무료
- 프로그램 2: OpenAI API 사용료 발생
  - gpt-4o-mini 모델 사용
  - PDF 1건당 약 $0.10-0.20

## ⚠️ 주의사항

### 프로그램 1
- 현재 버전은 기본적인 사주 계산 기능을 제공합니다
- 정확한 사주 계산을 위해서는 만세력 데이터 검증이 필요할 수 있습니다
- 음력 변환은 `korean-lunar-calendar` 라이브러리 사용

### 프로그램 2
- OpenAI API 키가 필요합니다
- 한 번의 PDF 생성에 13회의 API 호출 발생
- 한글 폰트는 macOS 시스템 폰트 사용 (다른 OS에서는 폰트 경로 수정 필요)

## 📝 개발 로드맵

### v1.0 (현재)
- [x] 기본 사주 계산 엔진
- [x] JSON 데이터 구조 설계
- [x] OpenAI 연동 PDF 생성
- [x] 13장 구성 템플릿

### v1.1 (예정)
- [ ] 사주 계산 정확도 향상 (만세력 데이터 검증)
- [ ] 십이신살 및 귀인 상세 계산
- [ ] PDF 디자인 개선
- [ ] Windows/Linux 폰트 지원

### v2.0 (예정)
- [ ] 웹 인터페이스 개발
- [ ] 데이터베이스 연동
- [ ] 사용자 관리 시스템
- [ ] 배치 처리 기능

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 개발되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 환영합니다!

---

**명리설리연구소** | 2025
