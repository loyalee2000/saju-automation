"use client";

import { useState } from "react";
import { Button } from "./ui/Button";
import { SajuInput } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card";
import { Moon, Sun } from "lucide-react";

interface SajuFormProps {
    onSubmit: (data: SajuInput) => void;
    isLoading: boolean;
}

export default function SajuForm({ onSubmit, isLoading }: SajuFormProps) {
    const [name, setName] = useState("");
    const [gender, setGender] = useState<"남" | "여">("남");
    const [isLunar, setIsLunar] = useState(false);

    // Date states
    const [year, setYear] = useState(2000);
    const [month, setMonth] = useState(1);
    const [day, setDay] = useState(1);
    const [hour, setHour] = useState(12);
    const [minute, setMinute] = useState(0);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            name,
            gender,
            year: Number(year),
            month: Number(month),
            day: Number(day),
            hour: Number(hour),
            minute: Number(minute),
            is_lunar: isLunar,
        });
    };

    return (
        <Card className="w-full max-w-lg mx-auto border-amber-900/50 bg-[#161b22]">
            <CardHeader>
                <CardTitle className="text-center text-2xl flex items-center justify-center gap-2">
                    <span className="text-amber-500">✷</span> 사주 정보 입력
                </CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Name */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-400">이름</label>
                        <input
                            type="text"
                            placeholder="이름을 입력하세요 (선택)"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-amber-500 transition-colors"
                        />
                    </div>

                    {/* Gender */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-400">성별</label>
                        <div className="grid grid-cols-2 gap-4">
                            <Button
                                type="button"
                                variant={gender === "남" ? "primary" : "secondary"}
                                onClick={() => setGender("남")}
                            >
                                남자
                            </Button>
                            <Button
                                type="button"
                                variant={gender === "여" ? "primary" : "secondary"}
                                onClick={() => setGender("여")}
                            >
                                여자
                            </Button>
                        </div>
                    </div>

                    {/* Date & Calendar Type */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="text-sm font-medium text-gray-400">생년월일시</label>
                            <button
                                type="button"
                                onClick={() => setIsLunar(!isLunar)}
                                className={`flex items-center gap-1 text-xs px-2 py-1 rounded ${isLunar ? "bg-indigo-900 text-indigo-200" : "bg-orange-900 text-orange-200"}`}
                            >
                                {isLunar ? <Moon size={12} /> : <Sun size={12} />}
                                {isLunar ? "음력" : "양력"}
                            </button>
                        </div>

                        <div className="grid grid-cols-4 gap-2">
                            <input
                                type="number"
                                placeholder="년"
                                value={year}
                                onChange={(e) => setYear(Number(e.target.value))}
                                className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-center text-white"
                            />
                            <input
                                type="number"
                                placeholder="월"
                                value={month}
                                onChange={(e) => setMonth(Number(e.target.value))}
                                className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-center text-white"
                            />
                            <input
                                type="number"
                                placeholder="일"
                                value={day}
                                onChange={(e) => setDay(Number(e.target.value))}
                                className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-center text-white"
                            />
                            <div className="flex gap-1">
                                <input
                                    type="number"
                                    placeholder="시"
                                    value={hour}
                                    onChange={(e) => setHour(Number(e.target.value))}
                                    className="w-1/2 bg-gray-900 border border-gray-700 rounded-lg p-3 text-center text-white"
                                />
                                <input
                                    type="number"
                                    placeholder="분"
                                    value={minute}
                                    onChange={(e) => setMinute(Number(e.target.value))}
                                    className="w-1/2 bg-gray-900 border border-gray-700 rounded-lg p-3 text-center text-white"
                                />
                            </div>
                        </div>
                    </div>

                    <Button type="submit" disabled={isLoading} className="w-full text-lg py-4">
                        {isLoading ? "분석 중..." : "✨ 사주 분석하기"}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
