#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
장재수, 김정현 사주 신살 테스트 (포스텔러 비교)
"""
import json

# 원본 JSON에서 신살 읽기
def load_original_sinsal(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 두 사주 파일
files = [
    ('/Users/loyalee/Desktop/saju_장재수_20251227_105709.json', '장재수'),
    ('/Users/loyalee/Desktop/saju_김정현_20251227_105317.json', '김정현')
]

for filepath, name in files:
    data = load_original_sinsal(filepath)

    four_pillars = data.get('four_pillars', {})
    sinsal = data.get('sinsal', {})

    print("="*80)
    print(f"{name} 사주 - 원본 JSON 신살")
    print("="*80)

    for pillar_name in ['year', 'month', 'day', 'hour']:
        pillar_korean = {'year': '년주', 'month': '월주', 'day': '일주', 'hour': '시주'}[pillar_name]
        pillar = four_pillars.get(pillar_name, {})
        pillar_sinsal = sinsal.get(pillar_name, {})

        gan = pillar.get('gan', '')
        ji = pillar.get('ji', '')
        gan_sinsal = pillar_sinsal.get('gan', [])
        ji_sinsal = pillar_sinsal.get('ji', [])

        gan_str = ', '.join(gan_sinsal) if gan_sinsal else '없음'
        ji_str = ', '.join(ji_sinsal) if ji_sinsal else '없음'

        print(f"{pillar_korean:6} ({gan}{ji:6}): 천간=[{gan_str}] 지지=[{ji_str}]")

    print()
