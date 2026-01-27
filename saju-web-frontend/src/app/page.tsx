"use client";

import InputForm from "@/components/InputForm";
import { Moon } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-[var(--background)] text-[var(--foreground)]">

      {/* Header Section */}
      <div className="flex flex-col items-center mb-8 space-y-2">
        <div className="flex items-center gap-3">
          <Moon className="w-8 h-8 text-[var(--primary)] fill-[var(--primary)]" />
          <h1 className="text-3xl font-light tracking-wide text-[var(--primary)]">온율 만세력</h1>
        </div>
        <p className="text-xs text-gray-500 tracking-wider">한국천문연구원 데이터 기반 · 정확한 절기시간 적용</p>
      </div>

      <div className="w-full max-w-[550px]">
        <InputForm />
      </div>

      {/* Footer Section */}
      <footer className="mt-16 text-center space-y-4">
        <div className="flex justify-center items-center gap-2">
          <Moon className="w-5 h-5 text-[var(--primary)] fill-[var(--primary)]" />
          <span className="text-lg text-[var(--primary)] font-medium">사주팔자를 확인해보세요</span>
        </div>
        <p className="text-sm text-gray-500">생년월일과 시간을 입력하고 분석 버튼을 눌러주세요</p>
      </footer>
    </main>
  );
}
