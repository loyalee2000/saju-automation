import { motion } from "framer-motion";
import FourPillarsTable from "./FourPillarsTable";
import FiveElementsChart from "./FiveElementsChart";
import DaewoonTable from "./DaewoonTable";
import { SajuResult } from "@/lib/types";

interface SajuResultViewProps {
    result: SajuResult;
}

export default function SajuResultView({ result }: SajuResultViewProps) {
    const { info, four_pillars, five_elements, daewoon, derived, sibseong, sinsal } = result;

    // Note: The structure of 'result' coming from backend vs what we defined in types might vary slightly
    // 'sibseong' and 'sinsal' in Props of FourPillarsTable expect flattened structure, 
    // but SajuResult type has 'derived.sinsal' and 'tibseong' (legacy). 
    // We need to map correctly.

    // Backend seems to return flat sibseong or derived sibseong?
    // Let's use the 'sibseong' field if available (it was populated in get_result_json)
    // Actually the 'InputForm' old code accessed 'sibseong?.year_gan' etc. 
    // The Type definition has 'sibseong?: { [key: string]: string }'. 
    // We might need to cast or fallback.

    // Helper to get sibseong safely
    const getSib = (key: string) => {
        if (!sibseong) return "";
        return (sibseong as any)[key] || "";
    };

    const mappedSibseong = {
        year_gan: getSib('year_gan'), year_ji: getSib('year_ji'),
        month_gan: getSib('month_gan'), month_ji: getSib('month_ji'),
        day_gan: "본인", day_ji: getSib('day_ji'),
        hour_gan: getSib('hour_gan'), hour_ji: getSib('hour_ji'),
    };

    // Helper for sinsal
    // InputForm used 'sinsal.year.gan' etc.
    // Type has 'derived.sinsal'. Let's check which one is populated. 
    // Based on previous code, 'sinsal' was at top level. 
    const effectiveSinsal = sinsal || derived?.sinsal || { year: {}, month: {}, day: {}, hour: {} };

    // Format dates safely
    const sDate = info?.solar_date;
    const solarDateStr = sDate ? `${sDate.year}년 ${sDate.month}월 ${sDate.day}일 ${sDate.hour}:${String(sDate.minute).padStart(2, '0')}` : "";
    const lDate = info?.lunar_date;
    const lunarDateStr = (lDate && lDate.year > 0) ? `${lDate.year}년 ${lDate.month}월 ${lDate.day}일` : "";

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-4xl mx-auto space-y-6"
        >
            {/* 1. Header & Basic Information */}
            <div className="bg-[#1a1a24] p-6 rounded-2xl border border-[#2A2A36] shadow-lg">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#2A2A36] pb-4 mb-4">
                    <div>
                        <h2 className="text-2xl font-bold text-white">
                            {info.name}<span className="text-lg font-normal text-gray-400">님의 사주 분석</span>
                        </h2>
                        <div className="text-sm text-[var(--primary)] mt-1">{info.gender === "male" ? "건명 (乾命)" : "곤명 (坤命)"}</div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-[var(--primary)]">{info.age}세</div>
                        <div className="text-sm text-gray-400">만 {info.age ? info.age - 1 : 0}세</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between p-3 bg-[#13131a] rounded-lg">
                        <span className="text-gray-400">양력</span>
                        <span className="text-white font-medium">{solarDateStr}</span>
                    </div>
                    <div className="flex justify-between p-3 bg-[#13131a] rounded-lg">
                        <span className="text-gray-400">음력</span>
                        <span className="text-white font-medium">{lunarDateStr}</span>
                    </div>
                    <div className="flex justify-between p-3 bg-[#13131a] rounded-lg">
                        <span className="text-gray-400">띠</span>
                        <span className="text-white font-medium">{info.ddi}띠</span>
                    </div>
                    <div className="flex justify-between p-3 bg-[#13131a] rounded-lg">
                        <span className="text-gray-400">일주</span>
                        <span className="text-[var(--primary)] font-bold">{four_pillars?.day?.gan}{four_pillars?.day?.ji} ({result.nabeum?.day || result.derived?.nabeum?.day || ""})</span>
                    </div>
                </div>
            </div>

            {/* 2. Four Pillars Table */}
            <FourPillarsTable
                pillars={four_pillars}
                sibseong={mappedSibseong}
                sinsal={effectiveSinsal}
            />

            {/* 3. Five Elements & Daewoon Split/Stack */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <FiveElementsChart fiveElements={five_elements} />
                <DaewoonTable data={daewoon} />
            </div>

            {/* 4. Detailed Sections (Collapsible or Cards) */}

            {/* Gyeokguk & Strength */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-6 bg-[#1a1a24] rounded-2xl border border-[#2A2A36]">
                    <h3 className="text-lg font-bold text-white mb-3">격국 (Pattern)</h3>
                    <div className="text-[var(--primary)] text-xl font-bold mb-2">{result.gyeokguk?.name || "미정"}</div>
                    <p className="text-sm text-gray-400 leading-relaxed">{result.gyeokguk?.basis}</p>
                </div>
                <div className="p-6 bg-[#1a1a24] rounded-2xl border border-[#2A2A36]">
                    <h3 className="text-lg font-bold text-white mb-3">신강약 / 용신</h3>
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-400">신강약</span>
                        <span className="text-white font-bold">{result.strength?.verdict} ({result.strength?.score}점)</span>
                    </div>
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-400">용신</span>
                        <span className="text-[var(--primary)] font-bold">{result.yongsin_structure?.yongsin}</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-gray-400">행운의 색</span>
                        <span className="text-white font-bold">{result.yongsin_structure?.yongsin_structure?.lucky_color}</span>
                    </div>
                </div>
            </div>

            {/* Detailed Analysis (Using existing data structure) */}
            {result.health_analysis && (
                <div className="p-6 bg-[#1a1a24] rounded-2xl border border-[#2A2A36]">
                    <h3 className="text-lg font-bold text-white mb-4">건강 분석</h3>
                    <div className="space-y-3">
                        {result.health_analysis.risks?.map((risk: any, i: number) => (
                            <div key={i} className="p-3 bg-red-900/10 border border-red-900/30 rounded-lg">
                                <div className="font-bold text-red-200 mb-1">{risk.type} 주의</div>
                                <div className="text-sm text-gray-400">{risk.advice}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </motion.div>
    );
}
