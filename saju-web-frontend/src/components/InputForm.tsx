"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Sparkles, Clipboard, Check } from "lucide-react";
import SajuResultView from "./results/SajuResultView";
import { SajuFormData, SajuResult } from "@/lib/types";



// Helper for safer access
const getStr = (val: string | undefined | null) => val || "";

function formatResultToText(data: SajuResult): string {
    const info = data.info;
    const pillars = data.four_pillars;

    let text = `
━━━━━━━━━━━━━━━━━━━━━━
🌙 온율 만세력 - 사주분석 결과
━━━━━━━━━━━━━━━━━━━━━━

【 기본 정보 】
이름: ${info.name}
양력: ${info.solar_date?.year}년 ${info.solar_date?.month}월 ${info.solar_date?.day}일 ${info.solar_date?.hour}:${info.solar_date?.minute ? String(info.solar_date.minute).padStart(2, '0') : '00'}
`;

    if (info.lunar_date && info.lunar_date.year > 0) {
        text += `음력: ${info.lunar_date.year}년 ${info.lunar_date.month}월 ${info.lunar_date.day}일\n`;
    }

    text += `띠: ${info.ddi}띠
나이: 만 ${info.age ? info.age - 1 : 0}세 (${info.age}세)
성별: ${info.gender === 'male' ? '남자' : '여자'}

【 사주 원국 (四柱原局) 】
┌────┬────┬────┬────┐
│ 시주 │ 일주 │ 월주 │ 년주 │
├────┼────┼────┼────┤
│  ${pillars.hour.gan?.charAt(0) || ' '}  │  ${pillars.day.gan?.charAt(0) || ' '}  │  ${pillars.month.gan?.charAt(0) || ' '}  │  ${pillars.year.gan?.charAt(0) || ' '}  │
│  ${pillars.hour.ji?.charAt(0) || ' '}  │  ${pillars.day.ji?.charAt(0) || ' '}  │  ${pillars.month.ji?.charAt(0) || ' '}  │  ${pillars.year.ji?.charAt(0) || ' '}  │
└────┴────┴────┴────┘
일간(日干): ${pillars.day.gan?.charAt(0)}

【 십성 (十星) 】
시주 천간: ${pillars.hour.gan} / 지지: ${pillars.hour.ji}
일주 천간: ${pillars.day.gan} (본인) / 지지: ${pillars.day.ji}
월주 천간: ${pillars.month.gan} / 지지: ${pillars.month.ji}
년주 천간: ${pillars.year.gan} / 지지: ${pillars.year.ji}
(참고: 상세 십성은 별도 표기)

【 지장간 (支藏干) 】
시지: ${Array.isArray(data.jijanggan?.hour) ? data.jijanggan.hour.join(', ') : data.jijanggan?.hour || '-'}
일지: ${Array.isArray(data.jijanggan?.day) ? data.jijanggan.day.join(', ') : data.jijanggan?.day || '-'}
월지: ${Array.isArray(data.jijanggan?.month) ? data.jijanggan.month.join(', ') : data.jijanggan?.month || '-'}
년지: ${Array.isArray(data.jijanggan?.year) ? data.jijanggan.year.join(', ') : data.jijanggan?.year || '-'}

【 십이운성 (十二運星) 】
시지: ${data.twelve_unseong?.hour?.stage || '-'}
일지: ${data.twelve_unseong?.day?.stage || '-'}
월지: ${data.twelve_unseong?.month?.stage || '-'}
년지: ${data.twelve_unseong?.year?.stage || '-'}

【 납음 (納音) 】
시주: ${data.nabeum?.hour || '-'}
일주: ${data.nabeum?.day || '-'}
월주: ${data.nabeum?.month || '-'}
년주: ${data.nabeum?.year || '-'}

【 공망 (空亡) 】
${Array.isArray(data.gongmang) ? data.gongmang.join(', ') : data.gongmang}

【 오행 분석 】
`;
    for (const [key, value] of Object.entries(data.five_elements)) {
        // approximate percentage
        const total = Object.values(data.five_elements).reduce((a, b) => a + b, 0) || 1;
        const pct = Math.round((value / total) * 100);
        text += `${key.charAt(0)}: ${value}개 (${pct}%)\n`;
    }

    text += `
【 신살 (神煞) 】
`;
    const allSinsal = new Set<string>();
    ['year', 'month', 'day', 'hour'].forEach(p => {
        // @ts-ignore
        const s = data.sinsal?.[p];
        if (s) {
            s.gan?.forEach((i: string) => allSinsal.add(i));
            s.ji?.forEach((i: string) => allSinsal.add(i));
        }
    });
    text += Array.from(allSinsal).join(', ') || "없음";

    text += `

【 대운 (大運) 】
대운방향: ${data.daewoon.direction}
────────────────────
`;

    data.daewoon.pillars.forEach((p) => {
        text += `\n▶ ${p.age}~${p.end_age}세 대운: ${p.ganji}\n`;
        if (p.seun && p.seun.length > 0) {
            text += `  [세운]\n`;
            p.seun.forEach((s) => {
                text += `    ${s.year}년(${s.age}세): ${s.ganji}\n`;
                text += `      월운: ${s.monthly_luck || '-'}\n`;
            });
        }
    });

    // 8. Detailed Analysis (Restored from previous request)
    if (data.gyeokguk || data.strength || data.yongsin_structure) {
        text += `\n【 심층 분석 (Deep Analysis) 】\n`;
        if (data.gyeokguk) {
            text += `- 격국: ${data.gyeokguk.name || "미정"} (${data.gyeokguk.basis || "판단 불가"})\n`;
        }
        if (data.strength) {
            text += `- 신강약: ${data.strength.verdict || "-"} (점수: ${data.strength.score || 0})\n`;
        }
        if (data.yongsin_structure) {
            text += `- 용신: ${data.yongsin_structure.yongsin || "-"}\n`;
            if (data.yongsin_structure.lucky_color) {
                text += `- 행운의 색 (Lucky Color): ${data.yongsin_structure.lucky_color}\n`;
            }
        }
    }

    // 9. Health Analysis
    if (data.health_analysis && data.health_analysis.risks && data.health_analysis.risks.length > 0) {
        text += `\n【 건강 분석 (Health) 】\n`;
        data.health_analysis.risks.forEach((risk: any) => {
            text += `[${risk.type} 주의] ${risk.advice}\n`;
        });
    }

    text += `
━━━━━━━━━━━━━━━━━━━━━━
온율 만세력으로 분석되었습니다.
`;

    return text;
}

export default function InputForm() {
    const [formData, setFormData] = useState<SajuFormData>({
        name: "",
        gender: "female",
        year: "",
        month: "",
        day: "",
        hour: "",
        minute: "",
        timeUnknown: false,
        calendarType: "solar",
        isLeapMonth: false,
        location: "서울",
    });

    const [result, setResult] = useState<SajuResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        if (!result) return;

        const text = formatResultToText(result);
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy:", err);
            setError("클립보드 복사에 실패했습니다.");
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        if (type === "checkbox") {
            setFormData(prev => ({ ...prev, [name]: (e.target as HTMLInputElement).checked }));
        } else if (["year", "month", "day", "hour", "minute"].includes(name)) {
            const maxLength = name === "year" ? 4 : 2;
            if ((value === "" || /^\d+$/.test(value)) && value.length <= maxLength) {
                setFormData(prev => ({ ...prev, [name]: value }));
            }
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleGenderSelect = (gender: "male" | "female") => {
        setFormData(prev => ({ ...prev, gender }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setResult(null);

        try {
            // Basic validation
            if (!formData.year || !formData.month || !formData.day) {
                throw new Error("생년월일을 입력해주세요.");
            }

            const payload = {
                name: formData.name || "Unknown",
                gender: formData.gender,
                year: parseInt(formData.year),
                month: parseInt(formData.month),
                day: parseInt(formData.day),
                hour: formData.timeUnknown ? 0 : (parseInt(formData.hour) || 0),
                minute: formData.timeUnknown ? 0 : (parseInt(formData.minute) || 0),
                calendarType: formData.calendarType,
                isLeapMonth: formData.isLeapMonth,
                location: formData.location
            };

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const response = await axios.post(`${apiUrl}/api/analyze`, payload);
            setResult(response.data);

        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || err.message || "분석 중 오류가 발생했습니다.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            {/* Form Container */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
            >
                <form onSubmit={handleSubmit} className="space-y-5">

                    {/* Name Input */}
                    <div className="space-y-2">
                        <label className="text-sm text-[var(--primary)] font-medium">이름</label>
                        <input
                            type="text"
                            name="name"
                            placeholder="이름을 입력하세요 (선택)"
                            value={formData.name}
                            onChange={handleChange}
                            className="w-full bg-[var(--surface-highlight)]"
                        />
                    </div>

                    {/* Gender Selection */}
                    <div className="space-y-2">
                        <label className="text-sm text-[var(--primary)] font-medium">성별</label>
                        <div className="flex rounded-md overflow-hidden border border-[var(--border)]">
                            <button
                                type="button"
                                onClick={() => handleGenderSelect("female")}
                                className={`flex-1 py-3 text-sm font-medium transition-colors ${formData.gender === "female"
                                    ? "bg-[var(--primary)] text-black font-bold"
                                    : "bg-[var(--surface-highlight)] text-gray-400 hover:text-white"
                                    } `}
                            >
                                여자
                            </button>
                            <div className="w-[1px] bg-[var(--border)]"></div>
                            <button
                                type="button"
                                onClick={() => handleGenderSelect("male")}
                                className={`flex-1 py-3 text-sm font-medium transition-colors ${formData.gender === "male"
                                    ? "bg-[var(--primary)] text-black font-bold"
                                    : "bg-[var(--surface-highlight)] text-gray-400 hover:text-white"
                                    } `}
                            >
                                남자
                            </button>
                        </div>
                    </div>

                    {/* Birth Date Section */}
                    {/* Birth Date Section */}
                    <div className="space-y-3">
                        <label className="text-sm text-[var(--primary)] font-medium">생년월일시</label>

                        {/* Date/Time Row Container */}
                        <div className="flex gap-2 h-[50px] w-full">
                            {/* Calendar Type */}
                            <select
                                name="calendarType"
                                value={formData.calendarType}
                                onChange={handleChange}
                                className="w-[70px] bg-[#1a1a24] text-[var(--foreground)] text-center px-0 text-[15px] h-full cursor-pointer appearance-none border border-[#2A2A36] rounded-md focus:border-[var(--primary)] outline-none transition-colors"
                                style={{ textAlignLast: 'center' }}
                            >
                                <option value="solar">양력</option>
                                <option value="lunar">음력</option>
                            </select>

                            {/* Year - Flex 1 */}
                            <input
                                type="text"
                                name="year"
                                placeholder="YYYY"
                                maxLength={4}
                                value={formData.year}
                                onChange={handleChange}
                                className="flex-1 min-w-0 bg-[#1a1a24] text-[var(--foreground)] text-center placeholder:text-gray-600 h-full border border-[#2A2A36] rounded-md focus:border-[var(--primary)] outline-none transition-colors text-[15px] relative z-10"
                            />
                            {/* Month - Flex 1 */}
                            <input
                                type="text"
                                name="month"
                                placeholder="MM"
                                maxLength={2}
                                value={formData.month}
                                onChange={handleChange}
                                className="flex-1 min-w-0 bg-[#1a1a24] text-[var(--foreground)] text-center placeholder:text-gray-600 h-full border border-[#2A2A36] rounded-md focus:border-[var(--primary)] outline-none transition-colors text-[15px] relative z-10"
                            />
                            {/* Day - Flex 1 */}
                            <input
                                type="text"
                                name="day"
                                placeholder="DD"
                                maxLength={2}
                                value={formData.day}
                                onChange={handleChange}
                                className="flex-1 min-w-0 bg-[#1a1a24] text-[var(--foreground)] text-center placeholder:text-gray-600 h-full border border-[#2A2A36] rounded-md focus:border-[var(--primary)] outline-none transition-colors text-[15px] relative z-10"
                            />

                            {/* Time Box - Fixed 100px */}
                            <div className={`w - [100px] flex items - center justify - center bg - [#1a1a24] rounded - md border border - [#2A2A36] h - full ${formData.timeUnknown ? 'opacity-30' : 'focus-within:border-[var(--primary)]'} transition - colors gap - 0.5 px - 0 relative`}>
                                <input
                                    type="text"
                                    name="hour"
                                    placeholder="시"
                                    maxLength={2}
                                    value={formData.hour}
                                    onChange={handleChange}
                                    disabled={formData.timeUnknown}
                                    className="bg-transparent border-none text-[var(--foreground)] text-center w-[32px] text-[15px] focus:ring-0 placeholder:text-gray-600 outline-none relative z-10 !p-0 !m-0"
                                />
                                <span className="text-gray-500 pb-1">:</span>
                                <input
                                    type="text"
                                    name="minute"
                                    placeholder="분"
                                    maxLength={2}
                                    value={formData.minute}
                                    onChange={handleChange}
                                    disabled={formData.timeUnknown}
                                    className="bg-transparent border-none text-[var(--foreground)] text-center w-[32px] text-[15px] focus:ring-0 placeholder:text-gray-600 outline-none relative z-10 !p-0 !m-0"
                                />
                            </div>
                        </div>

                        {/* Checkboxes */}
                        <div className="flex gap-6 mt-3 px-1">
                            <label className="flex items-center gap-2 text-sm text-[var(--foreground)] cursor-pointer hover:text-white transition-colors group">
                                <div className={`w - 5 h - 5 border rounded flex items - center justify - center transition - colors ${formData.timeUnknown ? 'bg-[var(--foreground)] border-[var(--foreground)]' : 'border-gray-500 bg-transparent group-hover:border-gray-400'} `}>
                                    {formData.timeUnknown && <Check className="w-3.5 h-3.5 text-black" strokeWidth={4} />}
                                    <input
                                        type="checkbox"
                                        name="timeUnknown"
                                        checked={formData.timeUnknown}
                                        onChange={handleChange}
                                        className="hidden"
                                    />
                                </div>
                                <span className="text-gray-400 group-hover:text-gray-300">시간 모름</span>
                            </label>

                            <label className="flex items-center gap-2 text-sm text-[var(--foreground)] cursor-pointer hover:text-white transition-colors group">
                                <div className="w-5 h-5 border border-gray-500 rounded flex items-center justify-center transition-colors bg-transparent group-hover:border-gray-400">
                                    {/* Placeholder for functionality later */}
                                    <input
                                        type="checkbox"
                                        name="yajasi"
                                        className="hidden"
                                    />
                                </div>
                                <span className="text-gray-400 group-hover:text-gray-300">야자시/조자시</span>
                            </label>

                            {formData.calendarType === "lunar" && (
                                <label className="flex items-center gap-2 text-sm text-[var(--foreground)] cursor-pointer hover:text-white transition-colors group">
                                    <div className={`w - 5 h - 5 border rounded flex items - center justify - center transition - colors ${formData.isLeapMonth ? 'bg-[var(--foreground)] border-[var(--foreground)]' : 'border-gray-500 bg-transparent group-hover:border-gray-400'} `}>
                                        {formData.isLeapMonth && <Check className="w-3.5 h-3.5 text-black" strokeWidth={4} />}
                                        <input
                                            type="checkbox"
                                            name="isLeapMonth"
                                            checked={formData.isLeapMonth}
                                            onChange={handleChange}
                                            className="hidden"
                                        />
                                    </div>
                                    <span className="text-gray-400 group-hover:text-gray-300">윤달</span>
                                </label>
                            )}
                        </div>
                    </div>

                    {/* Location */}
                    <div className="space-y-2">
                        <label className="text-sm text-[var(--primary)] font-medium">출생 도시</label>
                        <select
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            className="w-full bg-[var(--surface-highlight)] py-3 px-4 appearance-none"
                        >
                            <optgroup label="한국 주요도시">
                                <option value="서울">KR 서울</option>
                                <option value="부산">KR 부산</option>
                                <option value="대구">KR 대구</option>
                                <option value="인천">KR 인천</option>
                                <option value="광주">KR 광주</option>
                                <option value="대전">KR 대전</option>
                                <option value="울산">KR 울산</option>
                                <option value="세종">KR 세종</option>
                                <option value="수원">KR 수원</option>
                                <option value="창원">KR 창원</option>
                                <option value="청주">KR 청주</option>
                                <option value="전주">KR 전주</option>
                                <option value="제주">KR 제주</option>
                            </optgroup>
                            <optgroup label="북한">
                                <option value="평양">KP 평양</option>
                                <option value="함흥">KP 함흥</option>
                                <option value="원산">KP 원산</option>
                                <option value="신의주">KP 신의주</option>
                            </optgroup>
                            <optgroup label="해외">
                                <option value="도쿄">JP 도쿄</option>
                                <option value="오사카">JP 오사카</option>
                                <option value="베이징">CN 베이징</option>
                                <option value="상하이">CN 상하이</option>
                                <option value="홍콩">HK 홍콩</option>
                                <option value="타이베이">TW 타이베이</option>
                                <option value="뉴욕">US 뉴욕</option>
                                <option value="LA">US LA</option>
                                <option value="런던">UK 런던</option>
                                <option value="파리">FR 파리</option>
                                <option value="시드니">AU 시드니</option>
                            </optgroup>
                        </select>
                    </div>

                    {/* Action Buttons */}
                    <div className="grid grid-cols-[1.5fr_1fr] gap-3 pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center justify-center gap-2 bg-[var(--primary)] text-black font-bold py-3.5 rounded-lg hover:bg-[var(--primary-hover)] transition-all disabled:opacity-50 shadow-lg shadow-amber-900/20"
                        >
                            <Sparkles className="w-5 h-5" />
                            {loading ? "분석중..." : "사주 분석하기"}
                        </button>
                        <button
                            type="button"
                            onClick={handleCopy}
                            className="flex items-center justify-center gap-2 bg-[var(--surface-highlight)] text-gray-400 font-medium py-3.5 rounded-lg border border-[var(--border)] hover:text-white hover:border-gray-500 transition-all active:scale-95"
                        >
                            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Clipboard className="w-4 h-4" />}
                            {copied ? "복사됨" : "전체복사"}
                        </button>
                    </div>

                </form>

                {error && (
                    <div className="p-3 bg-red-900/30 border border-red-800 text-red-200 text-sm rounded-lg text-center">
                        {error}
                    </div>
                )}
            </motion.div>

            {/* NEW Results Section - SajuResultView */}
            {result && (
                <div className="mt-12 mb-20">
                    <SajuResultView result={result} />
                </div>
            )}
        </div>
    );
}
