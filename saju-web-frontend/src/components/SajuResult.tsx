"use client";

import { SajuResult } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";
import { motion } from "framer-motion";

interface SajuResultDisplayProps {
    result: SajuResult;
}

const elementColors: Record<string, string> = {
    "목": "text-green-400",
    "화": "text-red-400",
    "토": "text-yellow-600",
    "금": "text-gray-300",
    "수": "text-blue-400",
};

const elementBg: Record<string, string> = {
    "목": "bg-green-900/20 border-green-800",
    "화": "bg-red-900/20 border-red-800",
    "토": "bg-yellow-900/20 border-yellow-800",
    "금": "bg-gray-800 border-gray-600",
    "수": "bg-blue-900/20 border-blue-800",
};

// Map Cheongan/Jiji to Elements (Simplified mapping for display)
const getElement = (char: string) => {
    if ("갑을인묘".includes(char)) return "목";
    if ("병정사오".includes(char)) return "화";
    if ("무기진술축미".includes(char)) return "토";
    if ("경신신유".includes(char)) return "금";
    if ("임계해자".includes(char)) return "수";
    return "";
};

function PillarCard({ title, stem, branch }: { title: string; stem: string; branch: string }) {
    const stemElem = getElement(stem);
    const branchElem = getElement(branch);

    return (
        <div className="flex flex-col items-center">
            <span className="text-gray-500 text-sm mb-2">{title}</span>
            <div className="flex flex-col gap-2">
                <div className={`w-16 h-16 flex items-center justify-center rounded-xl border-2 text-3xl font-bold ${elementColors[stemElem]} ${elementBg[stemElem]}`}>
                    {stem}
                </div>
                <div className={`w-16 h-16 flex items-center justify-center rounded-xl border-2 text-3xl font-bold ${elementColors[branchElem]} ${elementBg[branchElem]}`}>
                    {branch}
                </div>
            </div>
        </div>
    );
}

export default function SajuResultDisplay({ result }: SajuResultDisplayProps) {
    const { saju_palja, basic_info, daeun, ohang_analysis, ilju, sipseong_analysis } = result;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-2xl mx-auto space-y-8 mt-10"
        >
            {/* 1. Header Information */}
            <div className="text-center space-y-2">
                <div className="inline-block bg-amber-900/30 text-amber-500 px-4 py-1 rounded-full text-sm border border-amber-800">
                    {basic_info.name ? `${basic_info.name}님을 위한 분석` : "사주 분석 결과"}
                </div>
                <h2 className="text-3xl font-bold text-white">온율 AI Saju</h2>
                <p className="text-gray-400 text-sm">
                    {basic_info.birth_date.solar.year}년 {basic_info.birth_date.solar.month}월 {basic_info.birth_date.solar.day}일 {basic_info.birth_date.time} 출생
                    ({basic_info.gender})
                </p>
            </div>

            {/* 2. Four Pillars (Won-Guk) */}
            <Card className="bg-[#0d1117] border-gray-800">
                <CardContent className="pt-6">
                    <div className="flex justify-between px-2 md:px-8">
                        <PillarCard title="시주" stem={saju_palja.hour.heavenly_stem} branch={saju_palja.hour.earthly_branch} />
                        <PillarCard title="일주" stem={saju_palja.day.heavenly_stem} branch={saju_palja.day.earthly_branch} />
                        <PillarCard title="월주" stem={saju_palja.month.heavenly_stem} branch={saju_palja.month.earthly_branch} />
                        <PillarCard title="년주" stem={saju_palja.year.heavenly_stem} branch={saju_palja.year.earthly_branch} />
                    </div>
                    <div className="mt-8 text-center pt-6 border-t border-gray-800">
                        <p className="text-lg text-gray-300">
                            당신은 <span className={`font-bold ${elementColors[getElement(saju_palja.day.heavenly_stem)]}`}>
                                {ilju.description}
                            </span> 입니다.
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* 2.5 Ilju Detail */}
            {ilju.rich_desc && (
                <Card className="bg-[#1f2937] border-gray-700">
                    <CardHeader>
                        <CardTitle className="text-xl text-amber-500 flex items-center gap-2">
                            ✨ <span className="text-white">{ilju.rich_desc.stem_trait.nature}</span> 같은 성향
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <h4 className="font-bold text-gray-300 mb-1">성격과 특징</h4>
                            <p className="text-gray-400 leading-relaxed">
                                {ilju.rich_desc.stem_trait.personality}
                            </p>
                        </div>
                        {ilju.rich_desc.branch_trait && ilju.rich_desc.branch_trait.animal && (
                            <div>
                                <h4 className="font-bold text-gray-300 mb-1">잠재력 ({ilju.rich_desc.branch_trait.animal})</h4>
                                <p className="text-gray-400 leading-relaxed">
                                    {ilju.rich_desc.branch_trait.personality}
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* 3. Sipseong Analysis */}
            {sipseong_analysis && (
                <Card className="bg-[#0d1117] border-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-bold text-gray-200">십성 분석 (사회적 관계)</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {Object.entries(sipseong_analysis)
                            .filter(([key]) => ['year_pillar', 'month_pillar', 'hour_pillar'].includes(key))
                            .map(([key, value]) => {
                                if (!value || !value.detail) return null;
                                const titles: Record<string, string> = {
                                    year_pillar: "년주 (초년/조상)",
                                    month_pillar: "월주 (청년/부모)",
                                    hour_pillar: "시주 (말년/자식)"
                                };

                                return (
                                    <div key={key} className="border-b border-gray-800 pb-4 last:border-0 last:pb-0">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm text-gray-500">{titles[key] || key}</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-amber-500 font-bold">{value.name}</span>
                                                <span className="text-xs text-gray-600 bg-gray-900 px-2 py-1 rounded">{value.detail.meaning}</span>
                                            </div>
                                        </div>
                                        <p className="text-gray-300 text-sm leading-relaxed">{value.detail.traits}</p>
                                        <div className="mt-2 bg-gray-800/50 p-3 rounded-lg">
                                            <p className="text-xs text-gray-400">💡 {value.detail.advice}</p>
                                        </div>
                                    </div>
                                )
                            })}
                    </CardContent>
                </Card>
            )}

            {/* 4. Ohang Chart (Simple Bar) */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg font-bold text-gray-200">오행 분포</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-5 gap-2 text-center">
                        {['목', '화', '토', '금', '수'].map((elem) => {
                            const key = { '목': 'wood', '화': 'fire', '토': 'earth', '금': 'metal', '수': 'water' }[elem] as keyof typeof ohang_analysis;
                            const count = Number(ohang_analysis[key]);
                            return (
                                <div key={elem} className="flex flex-col gap-2">
                                    <div className="h-24 bg-gray-900 rounded-full relative overflow-hidden">
                                        <div
                                            className={`absolute bottom-0 w-full rounded-full transition-all duration-1000 ${elementColors[elem].replace('text', 'bg')}`}
                                            style={{ height: `${(count / 8) * 100}%` }}
                                        />
                                    </div>
                                    <span className={`font-bold ${elementColors[elem]}`}>{elem}</span>
                                    <span className="text-xs text-gray-500">{count}개</span>
                                </div>
                            )
                        })}
                    </div>
                </CardContent>
            </Card>

            {/* 4.5 Total Text Report */}
            {result.text_report && (
                <Card className="bg-[#0d1117] border-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-bold text-gray-200">📄 종합 분석 결과 (상세)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono bg-gray-900 p-4 rounded-lg overflow-x-auto leading-relaxed border border-gray-700">
                            {result.text_report}
                        </pre>
                    </CardContent>
                </Card>
            )}

            {/* 4. Daewoon (Scrollable) */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold text-white px-2">대운 (10년 운) 흐름</h3>
                <div className="flex gap-4 overflow-x-auto pb-4 px-2 scrollbar-hide">
                    {daeun.map((d, i) => {
                        const stemElem = getElement(d.heavenly_stem);
                        const branchElem = getElement(d.earthly_branch);
                        return (
                            <div key={i} className="flex-shrink-0 w-24 bg-gray-800 rounded-xl p-4 flex flex-col items-center gap-2 border border-gray-700">
                                <span className="text-sm text-gray-400">{d.age_range}세</span>
                                <div className="flex flex-col gap-1 my-2">
                                    <span className={`text-xl font-bold ${elementColors[stemElem]}`}>{d.heavenly_stem}</span>
                                    <span className={`text-xl font-bold ${elementColors[branchElem]}`}>{d.earthly_branch}</span>
                                </div>
                                <span className="text-xs text-amber-600/80">{d.description.replace(/ .*/, '')}</span>
                            </div>
                        )
                    })}
                </div>
            </div>

        </motion.div>
    );
}
