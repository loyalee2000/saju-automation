"use client";

import { useState, useEffect } from "react";
import { Moon } from "lucide-react";

interface PasswordGateProps {
    children: React.ReactNode;
}

export default function PasswordGate({ children }: PasswordGateProps) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check session storage on mount
        const storedAuth = sessionStorage.getItem("saju_auth");
        if (storedAuth === "true") {
            setIsAuthenticated(true);
        }
        setIsLoading(false);
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const correctPassword = process.env.NEXT_PUBLIC_SITE_PASSWORD || "onyul1234";

        if (password === correctPassword) {
            sessionStorage.setItem("saju_auth", "true");
            setIsAuthenticated(true);
            setError("");
        } else {
            setError("비밀번호가 올바르지 않습니다.");
        }
    };

    if (isLoading) {
        return null; // Prevent flash of content
    }

    if (isAuthenticated) {
        return <>{children}</>;
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-[#0d1117] text-[#c9d1d9]">
            <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-8 w-full max-w-sm shadow-2xl">
                <div className="flex flex-col items-center mb-8 space-y-3">
                    <Moon className="w-10 h-10 text-amber-500 fill-amber-500" />
                    <h1 className="text-2xl font-semibold text-amber-500 tracking-wide">온율 만세력</h1>
                    <p className="text-xs text-gray-500 tracking-wider">접근이 제한된 서비스입니다</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-1">
                        <input
                            type="password"
                            placeholder="비밀번호 입력"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-white focus:outline-none focus:border-amber-500 transition-colors text-center placeholder-gray-600"
                        />
                        {error && <p className="text-red-400 text-xs text-center">{error}</p>}
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-amber-600 hover:bg-amber-700 text-white font-medium py-3 rounded-lg transition-colors duration-200"
                    >
                        입장하기
                    </button>
                </form>
            </div>
        </div>
    );
}
