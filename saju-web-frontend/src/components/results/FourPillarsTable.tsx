import { ELEMENT_COLORS, ELEMENT_BG_COLORS, CHEONGAN_MAP, JIJI_MAP } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface FourPillarsTableProps {
    pillars: {
        year: { gan: string; ji: string };
        month: { gan: string; ji: string };
        day: { gan: string; ji: string };
        hour: { gan: string; ji: string };
    };
    sibseong: {
        year_gan: string; year_ji: string;
        month_gan: string; month_ji: string;
        day_gan: string; day_ji: string;
        hour_gan: string; hour_ji: string;
    };
    sinsal: {
        year: { gan: string[]; ji: string[] };
        month: { gan: string[]; ji: string[] };
        day: { gan: string[]; ji: string[] };
        hour: { gan: string[]; ji: string[] };
    };
}

export default function FourPillarsTable({ pillars, sibseong, sinsal }: FourPillarsTableProps) {

    // Helper to extract the character only (remove hanja if present in brackets)
    const getChar = (text: string) => text?.split('(')[0] || '';

    // Helper to get element color class
    const getColor = (char: string) => ELEMENT_COLORS[getChar(char)] || "text-gray-100";

    // Helper to get element background class (optional)
    const getBgColor = (char: string) => {
        const c = getChar(char);
        const element = CHEONGAN_MAP[c] || JIJI_MAP[c];
        return element ? ELEMENT_BG_COLORS[element] : "";
    };

    const renderPillarCell = (title: string, gan: string, ji: string, sibs: { gan: string, ji: string }, shin: { gan: string[], ji: string[] }) => {
        const ganChar = getChar(gan);
        const jiChar = getChar(ji);

        return (
            <div className="flex flex-col items-center gap-2 w-full">
                <div className="text-xs text-gray-500 mb-1">{title}</div>

                {/* Pillar Box */}
                <div className="w-full bg-[#1a1a24] border border-[#2A2A36] rounded-xl overflow-hidden shadow-lg">

                    {/* Heavenly Stem (Gan) */}
                    <div className={cn("flex flex-col items-center justify-center py-4 relative border-b border-[#2A2A36]", getBgColor(ganChar))}>
                        <span className="text-[10px] text-gray-400 absolute top-1">{sibs.gan}</span>
                        <span className={cn("text-4xl font-serif font-bold mt-2", getColor(ganChar))}>{ganChar}</span>
                        {/* Sinsal for Gan */}
                        <div className="flex flex-wrap justify-center gap-0.5 mt-1 px-1">
                            {shin.gan?.slice(0, 2).map((s, i) => (
                                <span key={i} className="text-[9px] bg-black/20 text-gray-400 px-1 rounded">{s}</span>
                            ))}
                        </div>
                    </div>

                    {/* Earthly Branch (Ji) */}
                    <div className={cn("flex flex-col items-center justify-center py-4 relative", getBgColor(jiChar))}>
                        <span className="text-[10px] text-gray-400 absolute top-1">{sibs.ji}</span>
                        <span className={cn("text-4xl font-serif font-bold mt-2", getColor(jiChar))}>{jiChar}</span>
                        {/* Sinsal for Ji */}
                        <div className="flex flex-wrap justify-center gap-0.5 mt-1 px-1">
                            {shin.ji?.slice(0, 3).map((s, i) => (
                                <span key={i} className="text-[9px] bg-black/20 text-gray-400 px-1 rounded">{s}</span>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
        );
    };

    return (
        <div className="w-full p-4 bg-[#13131a] rounded-2xl border border-[#2A2A36]">
            <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="text-[var(--primary)]">◆</span> 사주 원국 (Four Pillars)
                </h3>
                <div className="flex gap-2 text-[10px] text-gray-500">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-400"></span>목</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400"></span>화</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500"></span>토</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-gray-200"></span>금</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-400"></span>수</span>
                </div>
            </div>

            <div className="grid grid-cols-4 gap-2 md:gap-4">
                {/* Right to Left: Hour, Day, Month, Year */}
                {renderPillarCell("시주 (Hour)", pillars.hour?.gan, pillars.hour?.ji, { gan: sibseong.hour_gan, ji: sibseong.hour_ji }, sinsal.hour)}
                {renderPillarCell("일주 (Day)", pillars.day?.gan, pillars.day?.ji, { gan: "본인", ji: sibseong.day_ji }, sinsal.day)}
                {renderPillarCell("월주 (Month)", pillars.month?.gan, pillars.month?.ji, { gan: sibseong.month_gan, ji: sibseong.month_ji }, sinsal.month)}
                {renderPillarCell("년주 (Year)", pillars.year?.gan, pillars.year?.ji, { gan: sibseong.year_gan, ji: sibseong.year_ji }, sinsal.year)}
            </div>
        </div>
    );
}
