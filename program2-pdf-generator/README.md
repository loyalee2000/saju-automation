# 프로그램 2: 사주 운세 PDF 생성기

## 개요
JSON 파일을 입력받아 OpenAI API를 통해 13장의 운세 풀이를 생성하고 PDF 파일로 출력하는 프로그램입니다.

## 설치

```bash
cd program2-pdf-generator
pip install -r requirements.txt
```

## OpenAI API 키 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
OPENAI_API_KEY=your-api-key-here
```

또는 실행 시 직접 입력할 수 있습니다.

## 사용법

```bash
python pdf_generator.py
```

### 입력
- JSON 파일 경로 (프로그램 1에서 생성된 파일)

### 출력
- PDF 파일이 `../data/` 폴더에 저장됩니다
- 파일명 형식: `saju_fortune_YYYYMMDD_HHMMSS.pdf`

## PDF 구성 (13장)

1. 제 1장: 사주에 대한 이해
2. 제 2장: 사주팔자 원국 분석
3. 제 3장: 일주 및 성격 분석
4. 제 4장: 십성 분석
5. 제 5장: 십이운성 분석
6. 제 6장: 십이신살 및 귀인 분석
7. 제 7장: 연애운 및 결혼운 분석
8. 제 8장: 재물운 분석
9. 제 9장: 직업운 분석
10. 제 10장: 건강운 분석
11. 제 11장: 대운 흐름 분석
12. 제 12장: 10년 연운 흐름 분석
13. 제 13장: 2026년 월운 흐름 분석

## 주의사항
- OpenAI API 사용 시 비용이 발생합니다
- 한 번의 PDF 생성에 약 13회의 API 호출이 발생합니다
- gpt-4o-mini 모델을 사용하여 비용을 절감했습니다
- 한글 폰트는 macOS 시스템 폰트를 사용합니다

## 비용 예상
- gpt-4o-mini 기준: 약 $0.10-0.20 / PDF
