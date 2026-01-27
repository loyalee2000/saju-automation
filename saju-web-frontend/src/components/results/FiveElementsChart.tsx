import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface FiveElementsChartProps {
    fiveElements: {
        "목(Tree)": number;
        "화(Fire)": number;
        "토(Earth)": number;
        "금(Metal)": number;
        "수(Water)": number;
    };
}

export default function FiveElementsChart({ fiveElements }: FiveElementsChartProps) {
    const data = [
        { label: "목", key: "목(Tree)", color: "bg-green-500", text: "text-green-400" },
        { label: "화", key: "화(Fire)", color: "bg-red-500", text: "text-red-400" },
        { label: "토", key: "토(Earth)", color: "bg-yellow-500", text: "text-yellow-500" },
        { label: "금", key: "금(Metal)", color: "bg-gray-300", text: "text-gray-200" },
        { label: "수", key: "수(Water)", color: "bg-blue-500", text: "text-blue-400" },
    ];

    const total = Object.values(fiveElements).reduce((a, b) => a + b, 0);

    return (
        <div className="w-full p-6 bg-[#13131a] rounded-2xl border border-[#2A2A36]">
            <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-[var(--primary)]">◆</span> 오행 분석 (Five Elements)
            </h3>

            <div className="space-y-4">
                {data.map((item) => {
                    const count = fiveElements[item.key as keyof typeof fiveElements] || 0;
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;

                    return (
                        <div key={item.key} className="relative">
                            <div className="flex justify-between text-sm mb-1.5 font-medium">
                                <span className={cn("flex items-center gap-2", item.text)}>
                                    <div className={`w-2 h-2 rounded-full ${item.color}`}></div>
                                    {item.label}
                                </span>
                                <span className="text-gray-400">
                                    {count}개 ({percentage}%)
                                </span>
                            </div>

                            <div className="h-3 bg-[#1a1a24] rounded-full overflow-hidden border border-[#2A2A36]">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${percentage}%` }}
                                    transition={{ duration: 0.8, ease: "easeOut" }}
                                    className={`h-full rounded-full ${item.color} opacity-80`}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
