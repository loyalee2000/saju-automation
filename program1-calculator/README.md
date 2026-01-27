# 프로그램 1: 사주 팔자 계산 엔진

## 개요
생년월일시와 성별을 입력받아 사주 팔자를 계산하고 JSON 형식으로 출력하는 프로그램입니다.

## 설치

```bash
cd program1-calculator
pip install -r requirements.txt
```

## 사용법

```bash
python saju_calculator.py
```

### 입력 항목
- 출생년도 (예: 1990)
- 출생월 (예: 1)
- 출생일 (예: 15)
- 출생시간 (0-23시)
- 출생분 (0-59분)
- 성별 (남/여)
- 음력 여부 (y/n)

### 출력
- JSON 파일이 `../data/` 폴더에 저장됩니다
- 파일명 형식: `saju_YYYYMMDD_HHMM.json`

## 출력 JSON 구조

```json
{
  "basic_info": {
    "birth_date": {...},
    "gender": "남",
    "timezone": "Asia/Seoul"
  },
  "saju_palja": {
    "year": {"heavenly_stem": "경", "earthly_branch": "오", "animal": "말"},
    "month": {...},
    "day": {...},
    "hour": {...}
  },
  "ilju": {...},
  "ohang_analysis": {...},
  "sipseong_analysis": {...},
  "daeun": [...]
}
```

## 주의사항
- 현재 버전은 기본적인 사주 계산 기능을 제공합니다
- 정확한 사주 계산을 위해서는 만세력 데이터가 필요할 수 있습니다
- 음력 변환은 `korean-lunar-calendar` 라이브러리를 사용합니다
