#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사주 팔자 계산 프로그램 (Main Entry Point)
입력: 생년월일시, 성별
출력: JSON 형식의 상세 사주 데이터
"""

import json
import sys
import os
from datetime import datetime
from saju_app import SajuAnalyzer


def main():
    """메인 함수"""
    print("=" * 60)
    print("사주 팔자 계산 프로그램 v2.0 (상세 분석)")
    print("=" * 60)
    print()

    # 사용자 입력
    try:
        name = input("이름: ")

        # 음력/양력 선택
        calendar_input = input("음력입니까? (y/n): ").lower()
        calendar_type = 'lunar' if calendar_input == 'y' else 'solar'

        # 윤달 여부 (음력인 경우만)
        is_leap_month = False
        if calendar_type == 'lunar':
            leap_input = input("윤달입니까? (y/n): ").lower()
            is_leap_month = leap_input == 'y'

        # 날짜 입력
        year = int(input("출생년도 (예: 1990): "))
        month = int(input("출생월 (예: 1): "))
        day = int(input("출생일 (예: 15): "))

        # 시간 입력
        time_unknown = input("출생시간을 모르십니까? (y/n): ").lower()

        if time_unknown == 'y':
            birth_date_str = f"{year:04d}{month:02d}{day:02d}"
            birth_time_str = None
        else:
            hour = int(input("출생시간 (0-23시): "))
            minute = int(input("출생분 (0-59분): "))
            birth_date_str = f"{year:04d}{month:02d}{day:02d}"
            birth_time_str = f"{hour:02d}{minute:02d}"

        # 성별
        gender_input = input("성별 (남/여): ")
        gender = 'male' if gender_input == '남' else 'female'

        print("\n" + "=" * 60)
        print("사주 계산 중...")
        print("=" * 60)

        # 사주 분석 객체 생성
        analyzer = SajuAnalyzer(
            birth_date_str=birth_date_str,
            birth_time_str=birth_time_str,
            gender=gender,
            name=name,
            calendar_type=calendar_type,
            is_leap_month=is_leap_month
        )

        # 결과 가져오기
        result = analyzer.get_verbose_result()

        # JSON 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"saju_{name}_{timestamp}.json"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop_path, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"\n✅ 사주 계산 완료!")
        print(f"📄 저장 위치: {output_path}")
        print()

        # 기본 정보 출력
        print("=" * 60)
        print("사주 팔자 (Four Pillars)")
        print("=" * 60)
        fp = result['four_pillars']
        print(f"년주(Year):  {fp['year']['text']}")
        print(f"월주(Month): {fp['month']['text']}")
        print(f"일주(Day):   {fp['day']['text']}")
        if 'hour' in fp:
            print(f"시주(Hour):  {fp['hour']['text']}")
        else:
            print(f"시주(Hour):  (시간 미상)")
        print()

        # 오행 분석
        print("=" * 60)
        print("오행 분석 (Five Elements)")
        print("=" * 60)
        fe = result['five_elements']
        print(f"목(Wood):  {fe.get('목(Tree)', 0)}")
        print(f"화(Fire):  {fe.get('화(Fire)', 0)}")
        print(f"토(Earth): {fe.get('토(Earth)', 0)}")
        print(f"금(Metal): {fe.get('금(Metal)', 0)}")
        print(f"수(Water): {fe.get('수(Water)', 0)}")
        print()

        # 격국
        if 'gyeokguk' in result:
            print("=" * 60)
            print("격국 (Pattern)")
            print("=" * 60)
            print(f"격국: {result['gyeokguk']['name']}")
            print(f"설명: {result['gyeokguk'].get('desc', {}).get('desc', '')}")
            print()

        # 일간 강약
        if 'strength' in result:
            print("=" * 60)
            print("일간 강약 (Day Master Strength)")
            print("=" * 60)
            print(f"판정: {result['strength']['verdict']}")
            print(f"점수: {result['strength']['score']}")
            print()

        print("=" * 60)
        print(f"전체 결과는 {output_path} 파일을 확인하세요.")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
