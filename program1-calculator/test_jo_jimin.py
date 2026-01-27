#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조지민 사주 신살 테스트 (포스텔러 만세력과 비교)
"""
from saju_app import SajuAnalyzer
import json

print("="*80)
print("조지민 사주 - 신살 분석 (포스텔러 비교)")
print("="*80)

# 양력 1972-12-12 (음력 1972-11-07)
test_dates = [
    '1972-12-12',
]

for date_str in test_dates:
    analyzer = SajuAnalyzer(
        birth_date_str=date_str,
        birth_time_str='21:00',
        gender='male',
        name='조지민',
        calendar_type='solar'
    )

    result = analyzer.get_result_json()

    # 사주 확인
    year_pillar = f"{result['four_pillars']['year']['gan']}{result['four_pillars']['year']['ji']}"
    month_pillar = f"{result['four_pillars']['month']['gan']}{result['four_pillars']['month']['ji']}"
    day_pillar = f"{result['four_pillars']['day']['gan']}{result['four_pillars']['day']['ji']}"
    hour_pillar = f"{result['four_pillars']['hour']['gan']}{result['four_pillars']['hour']['ji']}"

    # 임자/임자/정축/경술 확인
    if (year_pillar == "임(壬)자(子)" and
        month_pillar == "임(壬)자(子)" and
        day_pillar == "정(丁)축(丑)" and
        hour_pillar == "경(庚)술(戌)"):

        print(f"\n✓ 정확한 사주 발견: {date_str}")
        print(f"사주: {year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
        print()

        print("="*80)
        print("신살 결과 (현재 코드)")
        print("="*80)
        for pillar_name in ['year', 'month', 'day', 'hour']:
            pillar_korean = {'year': '년주', 'month': '월주', 'day': '일주', 'hour': '시주'}[pillar_name]
            pillar_ganji = {'year': year_pillar, 'month': month_pillar, 'day': day_pillar, 'hour': hour_pillar}[pillar_name]

            gan_sinsal = result['sinsal'][pillar_name]['gan']
            ji_sinsal = result['sinsal'][pillar_name]['ji']

            gan_str = ', '.join(gan_sinsal) if gan_sinsal else '없음'
            ji_str = ', '.join(ji_sinsal) if ji_sinsal else '없음'

            print(f"{pillar_korean:6} ({pillar_ganji:14}): 천간=[{gan_str}] 지지=[{ji_str}]")

        print()
        print("="*80)
        print("신살 결과 (포스텔러 만세력)")
        print("="*80)
        print("년주   (임(壬)자(子)    ): 천간=[없음] 지지=[도화살] + 길성: 월덕귀인")
        print("월주   (임(壬)자(子)    ): 천간=[없음] 지지=[도화살]")
        print("일주   (정(丁)축(丑)    ): 천간=[백호대살] 지지=[화개살, 백호대살]")
        print("시주   (경(庚)술(戌)    ): 천간=[괴강살] 지지=[화개살, 천문성, 괴강살]")

        print()
        print("="*80)
        print("차이점 분석")
        print("="*80)

        # 년주 비교
        expected_year_gan = []
        expected_year_ji = ['도화살']
        actual_year_gan = result['sinsal']['year']['gan']
        actual_year_ji = result['sinsal']['year']['ji']

        if set(expected_year_ji) != set(actual_year_ji):
            print(f"❌ 년주 지지: 기대={expected_year_ji}, 실제={actual_year_ji}")
        else:
            print(f"✓ 년주 지지: {actual_year_ji}")

        # 월주 비교
        expected_month_ji = ['도화살']
        actual_month_ji = result['sinsal']['month']['ji']

        if set(expected_month_ji) != set(actual_month_ji):
            print(f"❌ 월주 지지: 기대={expected_month_ji}, 실제={actual_month_ji}")
        else:
            print(f"✓ 월주 지지: {actual_month_ji}")

        # 일주 비교
        expected_day_gan = ['백호대살']
        expected_day_ji = ['화개살', '백호대살']
        actual_day_gan = result['sinsal']['day']['gan']
        actual_day_ji = result['sinsal']['day']['ji']

        if set(expected_day_gan) != set(actual_day_gan):
            print(f"❌ 일주 천간: 기대={expected_day_gan}, 실제={actual_day_gan}")
        else:
            print(f"✓ 일주 천간: {actual_day_gan}")

        if set(expected_day_ji) != set(actual_day_ji):
            print(f"❌ 일주 지지: 기대={expected_day_ji}, 실제={actual_day_ji}")
        else:
            print(f"✓ 일주 지지: {actual_day_ji}")

        # 시주 비교
        expected_hour_gan = ['괴강살']
        expected_hour_ji = ['화개살', '천문성', '괴강살']
        actual_hour_gan = result['sinsal']['hour']['gan']
        actual_hour_ji = result['sinsal']['hour']['ji']

        if set(expected_hour_gan) != set(actual_hour_gan):
            print(f"❌ 시주 천간: 기대={expected_hour_gan}, 실제={actual_hour_gan}")
        else:
            print(f"✓ 시주 천간: {actual_hour_gan}")

        if set(expected_hour_ji) != set(actual_hour_ji):
            print(f"❌ 시주 지지: 기대={expected_hour_ji}, 실제={actual_hour_ji}")
        else:
            print(f"✓ 시주 지지: {actual_hour_ji}")

        break
else:
    print("정확한 사주를 찾지 못했습니다.")
