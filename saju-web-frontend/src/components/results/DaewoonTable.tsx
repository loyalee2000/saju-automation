import { useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { ELEMENT_COLORS } from "@/lib/constants";

interface DaewoonPillar {
    age: number;
    end_age: number;
    ganji: string;
    seun?: any[];
    highlight?: string; // e.g. "현재"
}

interface DaewoonTableProps {
    data: {
        direction: string;
        pillars: DaewoonPillar[];
    };
}

export default function DaewoonTable({ data }: DaewoonTableProps) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const daewoonNum = Math.floor(data.pillars?.[0]?.age / 10) || 0;
    // Note: Daewoon number isn't always strictly age/10, but the logic in backend seems complex. 
    // Ideally, 'daewoon number' is the start age digit. 
    // Let's use the first pillar's start age modulo 10 or just the start age itself as the "Daewoon Number" indicator? 
    // Actually the prop data says "daewoon su" is usually calculated. Let's just use the first pillar's start age.

    const getChar = (text: string) => text?.split('(')[0] || '';
    const getColor = (char: string) => ELEMENT_COLORS[getChar(char)] || "text-gray-100";

    return (
        <div className="w-full p-6 bg-[#13131a] rounded-2xl border border-[#2A2A36]">
            <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="text-[var(--primary)]">◆</span> 대운 (10-Year Luck Cycle)
                </h3>
                <div className="text-sm text-gray-400">
                    방향: <span className="text-white font-semibold">{data.direction}</span> /
                    대운수: <span className="text-[var(--primary)] font-bold">{data.pillars?.[0]?.age % 10}</span>
                </div>
            </div>

            <div
                ref={scrollRef}
                className="flex gap-2 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent"
                style={{ scrollBehavior: 'smooth' }}
            >
                {data.pillars.map((pillar, idx) => {
                    const gan = pillar.ganji?.[0] || '';
                    const ji = pillar.ganji?.[1] || '';
                    const isCurrent = pillar.highlight === "현재";

                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: idx * 0.05 }}
                            className={cn(
                                "flex flex-col items-center justify-center min-w-[70px] md:min-w-[80px] py-3 rounded-lg border transition-all",
                                isCurrent
                                    ? "bg-[var(--primary)]/10 border-[var(--primary)] shadow-[0_0_10px_rgba(255,189,46,0.2)]"
                                    : "bg-[#1a1a24] border-[#2A2A36] opacity-70 hover:opacity-100"
                            )}
                        >
                            <span className={cn("text-xs mb-1", isCurrent ? "text-[var(--primary)] font-bold" : "text-gray-500")}>
                                {pillar.age}세
                            </span>

                            <div className="flex flex-col items-center gap-1 my-1">
                                <span className={cn("text-xl font-serif font-bold", getColor(gan))}>{gan}</span>
                                <span className={cn("text-xl font-serif font-bold", getColor(ji))}>{ji}</span>
                            </div>

                            {isCurrent && (
                                <span className="text-[10px] bg-[var(--primary)] text-black px-1.5 py-0.5 rounded-full font-bold mt-1">
                                    현재
                                </span>
                            )}
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
