#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사주 팔자 계산 프로그램
입력: 생년월일시, 성별
출력: JSON 형식의 사주 데이터
"""

import json
from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar
from saju_desc_data import CHEONGAN_DESC, JIJI_DESC, SIBSEONG_DETAILS, TWELVE_UNSEONG_DESC_MAP
from saju_data import JIJANGGAN, get_napeum

class SajuCalculator:
    """사주 계산 클래스"""

    # 천간 (Heavenly Stems)
    HEAVENLY_STEMS = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']

    # 지지 (Earthly Branches)
    EARTHLY_BRANCHES = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

    # 십이지 동물
    ANIMALS = ['쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양', '원숭이', '닭', '개', '돼지']

    # 오행 매핑
    OHANG_MAP = {
        '갑': '목', '을': '목',
        '병': '화', '정': '화',
        '무': '토', '기': '토',
        '경': '금', '신': '금',
        '임': '수', '계': '수',
        '인': '목', '묘': '목',
        '사': '화', '오': '화',
        '진': '토', '술': '토', '축': '토', '미': '토',
        '신': '금', '유': '금',
        '자': '수', '해': '수'
    }

    # 십이운성
    SIBIUNSEONG = ['장생', '목욕', '관대', '건록', '제왕', '쇠', '병', '사', '묘', '절', '태', '양']

    def __init__(self, year, month, day, hour, minute=0, gender='남', is_lunar=False):
        """
        사주 계산기 초기화

        Args:
            year: 년
            month: 월
            day: 일
            hour: 시
            minute: 분
            gender: 성별 ('남' 또는 '여')
            is_lunar: 음력 여부
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.gender = gender
        self.is_lunar = is_lunar

        # 양력 날짜로 변환
        if is_lunar:
            self.solar_date = self._lunar_to_solar()
        else:
            self.solar_date = datetime(year, month, day, hour, minute)

    def _lunar_to_solar(self):
        """음력을 양력으로 변환"""
        calendar = KoreanLunarCalendar()
        calendar.setLunarDate(self.year, self.month, self.day, False)
        return datetime(
            calendar.solarYear,
            calendar.solarMonth,
            calendar.solarDay,
            self.hour,
            self.minute
        )

    def _get_stem_branch(self, year_num):
        """년도에서 천간지지 구하기"""
        # 갑자년 = 4년 (서기 4년이 갑자년)
        stem_idx = (year_num - 4) % 10
        branch_idx = (year_num - 4) % 12
        return self.HEAVENLY_STEMS[stem_idx], self.EARTHLY_BRANCHES[branch_idx]

    def _get_month_pillar(self, year_stem, month):
        """월주 계산"""
        # 월간 계산 (년간에 따라 달라짐)
        year_stem_idx = self.HEAVENLY_STEMS.index(year_stem)

        # 월건표
        month_stem_base = {
            0: 2,  # 갑, 기년
            1: 4,  # 을, 경년
            2: 6,  # 병, 신년
            3: 8,  # 정, 임년
            4: 0   # 무, 계년
        }

        base = month_stem_base[year_stem_idx % 5]
        month_stem_idx = (base + month - 1) % 10

        # 월지는 고정 (인월=1월부터 시작)
        month_branch_idx = (month + 1) % 12

        return self.HEAVENLY_STEMS[month_stem_idx], self.EARTHLY_BRANCHES[month_branch_idx]

    def _get_day_pillar(self, date):
        """일주 계산 (간략화된 버전)"""
        # 실제로는 만세력 기준일로부터 계산해야 하지만,
        # 여기서는 샘플로 간단히 구현
        days_from_epoch = (date - datetime(1984, 2, 4)).days
        stem_idx = days_from_epoch % 10
        branch_idx = days_from_epoch % 12

        return self.HEAVENLY_STEMS[stem_idx], self.EARTHLY_BRANCHES[branch_idx]

    def _get_hour_pillar(self, day_stem, hour):
        """시주 계산"""
        day_stem_idx = self.HEAVENLY_STEMS.index(day_stem)

        # 시간대별 지지
        hour_branch_idx = ((hour + 1) // 2) % 12

        # 시간 간지 계산
        hour_stem_base = {
            0: 0,  # 갑, 기일
            1: 2,  # 을, 경일
            2: 4,  # 병, 신일
            3: 6,  # 정, 임일
            4: 8   # 무, 계일
        }

        base = hour_stem_base[day_stem_idx % 5]
        hour_stem_idx = (base + hour_branch_idx) % 10

        return self.HEAVENLY_STEMS[hour_stem_idx], self.EARTHLY_BRANCHES[hour_branch_idx]

    def _calculate_ohang(self, year_stem, year_branch, month_stem, month_branch,
                        day_stem, day_branch, hour_stem, hour_branch):
        """오행 분석"""
        elements = [year_stem, year_branch, month_stem, month_branch,
                   day_stem, day_branch, hour_stem, hour_branch]

        ohang_count = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}

        for elem in elements:
            ohang = self.OHANG_MAP.get(elem, '')
            if ohang:
                ohang_count[ohang] += 1

        # 가장 강한 오행
        if ohang_count:
             max_ohang = max(ohang_count, key=ohang_count.get)
             min_ohang = min(ohang_count, key=ohang_count.get)
        else:
             max_ohang = 'Unknown'
             min_ohang = 'Unknown'

        return {
            'wood': ohang_count['목'],
            'fire': ohang_count['화'],
            'earth': ohang_count['토'],
            'metal': ohang_count['금'],
            'water': ohang_count['수'],
            'strength': f"{max_ohang} 왕",
            'weakness': f"{min_ohang} 약"
        }

    def _get_sipseong_type(self, day_stem, target_stem):
        """천간 대 천간 십성 계산"""
        if not target_stem: return None
        
        # 오행 및 음양 인덱스 (0:양, 1:음)
        day_idx = self.HEAVENLY_STEMS.index(day_stem)
        target_idx = self.HEAVENLY_STEMS.index(target_stem)
        
        day_elem = self.OHANG_MAP[day_stem]
        target_elem = self.OHANG_MAP[target_stem]
        
        # 오행 상생상극 관계
        # 목(0)->화(1)->토(2)->금(3)->수(4)->목(0)
        elem_order = ['목', '화', '토', '금', '수']
        day_elem_idx = elem_order.index(day_elem)
        target_elem_idx = elem_order.index(target_elem)
        
        diff = (target_elem_idx - day_elem_idx) % 5
        
        # 음양 같음/다름 (True: 같음, False: 다름)
        is_same_yinyang = (day_idx % 2) == (target_idx % 2)
        
        if diff == 0: # 비겁 (같은 오행)
            return '비견' if is_same_yinyang else '겁재'
        elif diff == 1: # 식상 (내가 생함)
            return '식신' if is_same_yinyang else '상관'
        elif diff == 2: # 재성 (내가 극함)
            return '편재' if is_same_yinyang else '정재'
        elif diff == 3: # 관성 (나를 극함)
            return '편관' if is_same_yinyang else '정관'
        elif diff == 4: # 인성 (나를 생함)
            return '편인' if is_same_yinyang else '정인'
        return '비견'

    def _calculate_sipseong(self, day_stem, year_stem, month_stem, hour_stem):
        """십성 분석 (실제 로직 적용)"""
        # 월지 기준 격국은 복잡하므로, 일단 천간 십성 위주로 계산
        year_sip = self._get_sipseong_type(day_stem, year_stem)
        month_sip = self._get_sipseong_type(day_stem, month_stem)
        hour_sip = self._get_sipseong_type(day_stem, hour_stem)

        # 메인 성향 (투출된 십성 중 월간 > 시간 > 년간 순으로 중요도 부여 - 간략화)
        main_sip = month_sip 

        return {
            'year_pillar': year_sip,
            'month_pillar': month_sip,
            'day_pillar': '비견', # 일간 자체
            'hour_pillar': hour_sip,
            'main_sipseong': main_sip
        }

    def _calculate_daeun(self, year_stem, month_stem, month_branch):
        """대운 계산 (간략화)"""
        daeun_list = []
        try:
            stem_idx = self.HEAVENLY_STEMS.index(month_stem)
            branch_idx = self.EARTHLY_BRANCHES.index(month_branch)
        except ValueError:
            return []

        for i in range(8):  # 80년치 대운
            age_start = i * 10 + 1
            age_end = (i + 1) * 10

            if self.gender == '남':
                stem_idx = (stem_idx + 1) % 10
                branch_idx = (branch_idx + 1) % 12
            else:
                stem_idx = (stem_idx - 1) % 10
                branch_idx = (branch_idx - 1) % 12

            daeun_list.append({
                'age_range': f"{age_start}-{age_end}",
                'heavenly_stem': self.HEAVENLY_STEMS[stem_idx],
                'earthly_branch': self.EARTHLY_BRANCHES[branch_idx],
                'description': f"{self.HEAVENLY_STEMS[stem_idx]}{self.EARTHLY_BRANCHES[branch_idx]} 대운"
            })

        return daeun_list

    def calculate(self):
        """사주 계산 및 JSON 생성"""
        # 년주
        year_stem, year_branch = self._get_stem_branch(self.solar_date.year)
        animal = self.ANIMALS[(self.solar_date.year - 4) % 12]

        # 월주
        month_stem, month_branch = self._get_month_pillar(year_stem, self.solar_date.month)

        # 일주
        day_stem, day_branch = self._get_day_pillar(self.solar_date)

        # 시주
        hour_stem, hour_branch = self._get_hour_pillar(day_stem, self.solar_date.hour)

        # 오행 분석
        ohang = self._calculate_ohang(
            year_stem, year_branch, month_stem, month_branch,
            day_stem, day_branch, hour_stem, hour_branch
        )

        # 십성 분석
        sipseong = self._calculate_sipseong(day_stem, year_stem, month_stem, hour_stem)

        # 대운
        daeun = self._calculate_daewoon(year_stem, month_stem, month_branch)

        # [NEW] 고급 분석 (지장간, 납음, 공망)
        jijangan = {
            'year': JIJANGGAN.get(year_branch, {}),
            'month': JIJANGGAN.get(month_branch, {}),
            'day': JIJANGGAN.get(day_branch, {}),
            'hour': JIJANGGAN.get(hour_branch, {})
        }

        gongmang_list = self._calculate_gongmang(day_stem, day_branch)
        
        napeum = {
            'year': get_napeum(year_stem, year_branch),
            'month': get_napeum(month_stem, month_branch),
            'day': get_napeum(day_stem, day_branch),
            'hour': get_napeum(hour_stem, hour_branch)
        }

        # 최종 JSON 데이터
        birth_date_info = {
            'solar': {
                'date': self.solar_date.strftime('%Y-%m-%d'),
                'year': self.solar_date.year,
                'month': self.solar_date.month,
                'day': self.solar_date.day
            },
            'time': self.solar_date.strftime('%H:%M'),
            'hour': self.solar_date.hour,
            'minute': self.solar_date.minute,
            'is_lunar_input': self.is_lunar
        }

        # 음력 입력인 경우 원래 음력 날짜도 포함
        if self.is_lunar:
            birth_date_info['lunar'] = {
                'date': f"{self.year}-{self.month:02d}-{self.day:02d}",
                'year': self.year,
                'month': self.month,
                'day': self.day
            }

        result = {
            'basic_info': {
                'birth_date': birth_date_info,
                'gender': self.gender,
                'timezone': 'Asia/Seoul'
            },
            'saju_palja': {
                'year': {
                    'heavenly_stem': year_stem,
                    'earthly_branch': year_branch,
                    'animal': animal
                },
                'month': {
                    'heavenly_stem': month_stem,
                    'earthly_branch': month_branch
                },
                'day': {
                    'heavenly_stem': day_stem,
                    'earthly_branch': day_branch
                },
                'hour': {
                    'heavenly_stem': hour_stem,
                    'earthly_branch': hour_branch
                }
            },
            'ilju': {
                'stem': day_stem,
                'branch': day_branch,
                'description': f"{day_stem}{day_branch}일주",
                'rich_desc': {
                    # 키가 "갑(甲)" 형태이므로 day_stem("갑")으로 시작하는 키를 찾음
                    'stem_trait': next((v for k, v in CHEONGAN_DESC.items() if k.startswith(day_stem)), {}),
                    'branch_trait': next((v for k, v in JIJI_DESC.items() if k.startswith(day_branch)), {}),
                }
            },
            'ohang_analysis': ohang,
            'sipseong_analysis': {
                k: {'name': v, 'detail': SIBSEONG_DETAILS.get(v, {}).get('desc', {})} 
                for k, v in sipseong.items() if v
            },
            'daeun': daeun,
            'advanced': {
                'jijangan': jijangan,
                'gongmang': gongmang_list,
                'napeum': napeum
            }
        }
        
        # 텍스트 리포트 생성 (API 결과에 포함)
        result['text_report'] = self._generate_text_report(result)

        return result

    def _calculate_gongmang(self, day_stem, day_branch):
        """공망 계산"""
        # 갑자순중 공망 찾기
        gan_idx = self.HEAVENLY_STEMS.index(day_stem)
        ji_idx = self.EARTHLY_BRANCHES.index(day_branch)
        
        diff = (ji_idx - gan_idx) % 12
        
        # diff 값에 따른 공망 (술해, 신유, 오미, 진사, 인묘, 자축)
        gongmang_map = {
            10: ['술', '해'],
            8: ['신', '유'],
            6: ['오', '미'],
            4: ['진', '사'],
            2: ['인', '묘'],
            0: ['자', '축']
        }
        return gongmang_map.get(diff, [])

    def _generate_text_report(self, res):
        """사용자가 요청한 형식의 상세 텍스트 리포트 생성"""
        info = res['basic_info']
        saju = res['saju_palja']
        sip = res['sipseong_analysis']
        adv = res['advanced']
        
        # 성별 문자열
        gender_str = "남자" if info['gender'] in ['남', 'male'] else "여자"
        
        # 나이 (만 나이 - 간략 계산)
        birth_year = info['birth_date']['solar']['year']
        current_year = datetime.now().year
        age = current_year - birth_year
        
        report = []
        report.append("━━━━━━━━━━━━━━━━━━━━━━")
        report.append("🌙 온율 만세력 - 사주분석 결과")
        report.append("━━━━━━━━━━━━━━━━━━━━━━")
        report.append("")
        report.append("【 기본 정보 】")
        report.append(f"양력: {info['birth_date']['solar']['date']} {info['birth_date']['time']}")
        if info['birth_date']['is_lunar_input']:
             report.append(f"음력: {info['birth_date'].get('lunar', {}).get('date', '')}")
        report.append(f"나이: {age}세")
        report.append(f"성별: {gender_str}")
        report.append("")
        report.append("【 사주 원국 (四柱原局) 】")
        report.append("┌────┬────┬────┬────┐")
        report.append("│ 시주 │ 일주 │ 월주 │ 년주 │")
        report.append("├────┼────┼────┼────┤")
        report.append(f"│  {saju['hour']['heavenly_stem']}  │  {saju['day']['heavenly_stem']}  │  {saju['month']['heavenly_stem']}  │  {saju['year']['heavenly_stem']}  │")
        report.append(f"│  {saju['hour']['earthly_branch']}  │  {saju['day']['earthly_branch']}  │  {saju['month']['earthly_branch']}  │  {saju['year']['earthly_branch']}  │")
        report.append("└────┴────┴────┴────┘")
        report.append(f"일간(日干): {saju['day']['heavenly_stem']}")
        report.append("")
        report.append("【 십성 (十星) 】")
        report.append(f"시주: {sip.get('hour_pillar', {}).get('name', '-')}")
        report.append(f"일주: {sip.get('day_pillar', {}).get('name', '본인')}")
        report.append(f"월주: {sip.get('month_pillar', {}).get('name', '-')}")
        report.append(f"년주: {sip.get('year_pillar', {}).get('name', '-')}")
        report.append("")
        report.append("【 지장간 (支藏干) 】")
        for pillar in ['hour', 'day', 'month', 'year']:
            jj = adv['jijangan'][pillar]
            vals = [v for v in [jj.get('chogi'), jj.get('junggi'), jj.get('bonggi')] if v]
            p_name = {'hour':'시지', 'day':'일지', 'month':'월지', 'year':'년지'}[pillar]
            report.append(f"{p_name}: {', '.join(vals)}")
        report.append("")
        report.append("【 납음 (納音) 】")
        report.append(f"시주: {adv['napeum']['hour']}")
        report.append(f"일주: {adv['napeum']['day']}")
        report.append(f"월주: {adv['napeum']['month']}")
        report.append(f"년주: {adv['napeum']['year']}")
        report.append("")
        report.append("【 공망 (空亡) 】")
        report.append(f"일공망: {', '.join(adv['gongmang'])}")
        report.append("")
        report.append("【 대운 (大運) 】")
        for d in res['daeun']:
            report.append(f"{d['age_range']}세: {d['heavenly_stem']}{d['earthly_branch']} 대운")
        
        report.append("")
        report.append("━━━━━━━━━━━━━━━━━━━━━━")
        report.append("온율 만세력으로 분석되었습니다.")
        
        return "\n".join(report)


def main():
    """메인 함수"""
    print("=" * 50)
    print("사주 팔자 계산 프로그램")
    print("=" * 50)

    # 사용자 입력
    try:
        year = int(input("출생년도 (예: 1990): "))
        month = int(input("출생월 (예: 1): "))
        day = int(input("출생일 (예: 15): "))
        hour = int(input("출생시간 (0-23시): "))
        minute = int(input("출생분 (0-59분): "))
        gender = input("성별 (남/여): ")
        is_lunar_input = input("음력입니까? (y/n): ")
        is_lunar = is_lunar_input.lower() == 'y'

        # 사주 계산
        calculator = SajuCalculator(year, month, day, hour, minute, gender, is_lunar)
        result = calculator.calculate()

        # JSON 파일로 저장
        output_filename = f"saju_{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}.json"
        
        # NOTE: In the ported version, we might output to stdout or a different dir.
        # output_path = f"../data/{output_filename}" 
        # For safety in new env, just use current dir
        output_path = output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 사주 계산 완료!")
        print(f"📄 저장 위치: {output_path}")
        print(f"\n사주 팔자:")
        print(f"년주: {result['saju_palja']['year']['heavenly_stem']}{result['saju_palja']['year']['earthly_branch']} ({result['saju_palja']['year']['animal']})")
        print(f"월주: {result['saju_palja']['month']['heavenly_stem']}{result['saju_palja']['month']['earthly_branch']}")
        print(f"일주: {result['saju_palja']['day']['heavenly_stem']}{result['saju_palja']['day']['earthly_branch']}")
        print(f"시주: {result['saju_palja']['hour']['heavenly_stem']}{result['saju_palja']['hour']['earthly_branch']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
