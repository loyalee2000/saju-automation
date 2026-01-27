#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for 신아름 sinsal
"""
import json
from saju_app import SajuAnalyzer

# Test case: 신아름 (2001-11-24, 16:17, female, solar)
analyzer = SajuAnalyzer(
    birth_date_str="2001-11-24",
    birth_time_str="16:17",
    gender="female",
    name="신아름",
    calendar_type="solar",
    is_leap_month=False
)

result = analyzer.get_result_json()

print("=" * 80)
print("신아름 사주 - 신살 분석")
print("=" * 80)
print(f"사주: {result['four_pillars']['year']['text']} {result['four_pillars']['month']['text']} "
      f"{result['four_pillars']['day']['text']} {result['four_pillars']['hour']['text']}")

print("\n" + "=" * 80)
print("신살 결과 (프로그램)")
print("=" * 80)
for pillar in ['year', 'month', 'day', 'hour']:
    pillar_text = result['four_pillars'][pillar]['text']
    gan_sinsal = ', '.join(result['sinsal'][pillar]['gan']) if result['sinsal'][pillar]['gan'] else '없음'
    ji_sinsal = ', '.join(result['sinsal'][pillar]['ji']) if result['sinsal'][pillar]['ji'] else '없음'
    print(f"{pillar:6s} ({pillar_text:10s}): 천간=[{gan_sinsal}] 지지=[{ji_sinsal}]")

print("\n" + "=" * 80)
print("신살 결과 (포스텔러)")
print("=" * 80)
print("year   (신사)      : 천간=[없음] 지지=[현침살, 역마살]")
print("month  (기해)      : 천간=[없음] 지지=[금여성, 태극귀인, 역마살, 천문성]")
print("day    (신묘)      : 천간=[없음] 지지=[도화살, 현침살, 귀문관살]")
print("hour   (병신)      : 천간=[없음] 지지=[역마살, 현침살, 귀문관살]")
