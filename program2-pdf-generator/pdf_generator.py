#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사주 운세 PDF 생성 프로그램 (GUI Version - Batch Processor V3)
기능: OpenAI Assistants API 사용, 설정 자동 저장, 배치 처리 지원
"""

import json
import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# [핵심] 프록시 오류 방지
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)

load_dotenv()

CONFIG_FILE = "config.json"

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @staticmethod
    def save_config(api_key, assistant_id):
        config = {"OPENAI_API_KEY": api_key, "ASSISTANT_ID": assistant_id}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except:
            pass

class SajuPDFGenerator:
    """사주 운세 PDF 생성 클래스 (Assistants API + JSON 구조 수정)"""

    CHAPTERS = [
        {"number": 1, "title": "사주에 대한 이해", "prompt_key": "understanding"},
        {"number": 2, "title": "사주팔자 원국 분석", "prompt_key": "palja_analysis"},
        {"number": 3, "title": "일주 및 성격 분석", "prompt_key": "personality"},
        {"number": 4, "title": "십성 분석", "prompt_key": "sipseong"},
        {"number": 5, "title": "십이운성 분석", "prompt_key": "sibiunseong"},
        {"number": 6, "title": "십이신살 및 귀인 분석", "prompt_key": "sinsal"},
        {"number": 7, "title": "연애운 및 결혼운 분석", "prompt_key": "love"},
        {"number": 8, "title": "재물운 분석", "prompt_key": "wealth"},
        {"number": 9, "title": "직업운 분석", "prompt_key": "career"},
        {"number": 10, "title": "건강운 분석", "prompt_key": "health"},
        {"number": 11, "title": "대운 흐름 분석", "prompt_key": "daeun"},
        {"number": 12, "title": "10년 연운 흐름 분석", "prompt_key": "yeonun"},
        {"number": 13, "title": "2026년 월운 흐름 분석", "prompt_key": "wolun"}
    ]

    def __init__(self, json_file_path, api_key, assistant_id, log_func=print):
        self.json_file_path = json_file_path
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.log = log_func
        self.client = OpenAI(api_key=self.api_key)
        
        # JSON 로드 및 데이터 매핑 (KeyError 방지)
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        self.saju_data = raw_data
        # 데이터 호환성 보장
        self.user_info = raw_data.get('info', raw_data.get('basic_info', {}))
        self.pillars = raw_data.get('four_pillars', raw_data.get('saju_palja', {}))
        self.five_elements = raw_data.get('five_elements', raw_data.get('ohang_analysis', {}))

        if not self.user_info:
            raise ValueError("JSON 파일에서 사용자 정보를 찾을 수 없습니다. (Key: 'info' or 'basic_info')")

    def _create_prompt(self, chapter):
        """13개 장 전문 프롬프트 (V7 복구)"""
        p = self.pillars
        u = self.user_info
        e = self.five_elements
        
        # 기본 정보 요약
        info_str = f"""
[내담자 사주 정보]
이름: {u.get('name', '무명')}
성별: {u.get('gender', '남')}
생년월일: {u.get('birth_year')}-{u.get('birth_month')}-{u.get('birth_day')} ({u.get('calendar_type', '양력')})
사주 팔자:
  - 년주: {p.get('year', {}).get('text', '')}
  - 월주: {p.get('month', {}).get('text', '')}
  - 일주: {p.get('day', {}).get('text', '')}
  - 시주: {p.get('hour', {}).get('text', '시간 미상')}
오행 분포: 목({e.get('목(Tree)', e.get('wood', 0))}) 화({e.get('화(Fire)', e.get('fire', 0))}) 토({e.get('토(Earth)', e.get('earth', 0))}) 금({e.get('금(Metal)', e.get('metal', 0))}) 수({e.get('수(Water)', e.get('water', 0))})
"""
        # 상세 프롬프트 정의
        prompts = {
            "understanding": f"{info_str}\n'제1장: 사주에 대한 이해'를 전문적으로 작성해주세요. 사주가 개인의 운명에 미치는 영향과 이 사주의 전체적인 조화를 설명해주세요.",
            "palja_analysis": f"{info_str}\n'제2장: 사주팔자 원국 분석'을 진행해주세요. 네 기둥(년, 월, 일, 시)의 상호작용과 각 기둥이 상징하는 의미를 상세히 분석해주세요.",
            "personality": f"{info_str}\n'제3장: 일주 및 성격 분석'을 작성해주세요. 일간의 특성과 이로부터 파생되는 성격적 장단점, 사회적 기질을 심층적으로 다루어주세요.",
            "sipseong": f"{info_str}\n'제4장: 십성 분석'을 진행해주세요. 사주에 나타난 십성의 분포를 통해 타고난 재능과 인생의 우선순위를 분석해주세요.",
            "sibiunseong": f"{info_str}\n'제5장: 십이운성 분석'을 작성해주세요. 인생의 생로병사와 에너지의 강약을 통해 활동성과 근원적인 힘을 설명해주세요.",
            "sinsal": f"{info_str}\n'제6장: 십이신살 및 귀인 분석'을 진행해주세요. 천을귀인 등 주요 길성이나 신살이 주는 유의미한 영향과 혜택을 분석해주세요.",
            "love": f"{info_str}\n'제7장: 연애운 및 결혼운 분석'을 작성해주세요. 애정 성향과 어울리는 배우자 상, 결혼 적령기 등에 대한 조언을 포함해주세요.",
            "wealth": f"{info_str}\n'제8장: 재물운 분석'을 진행해주세요. 재물을 모으는 능력, 재테크 스타일, 인생 전체의 금전 흐름을 분석해주세요.",
            "career": f"{info_str}\n'제9장: 직업운 분석'을 작성해주세요. 타고난 적성에 근거한 추천 직업군과 직장운, 사업운의 균형을 설명해주세요.",
            "health": f"{info_str}\n'제10장: 건강운 분석'을 작성해주세요. 취약한 오행과 관련된 신체 부위 및 생활 속 건강 관리법을 제안해주세요.",
            "daeun": f"{info_str}\n'제11장: 대운 흐름 분석'을 진행해주세요. 10년 단위의 인생 주기 변화를 분석하고 현재 시점이 갖는 중요성을 강조해주세요.\n[대운 정보]: {self.saju_data.get('daeun', '')}",
            "yeonun": f"{info_str}\n'제12장: 10년 연운 흐름 분석'을 작성해주세요. 향후 10년간 오행의 변화에 따른 년도별 운의 고저와 주요 키워드를 제시해주세요.",
            "wolun": f"{info_str}\n'제13장: 2026년 월운 흐름 분석'을 작성해주세요. 2026년의 달별 흐름과 주의사항, 기회의 시기를 상세히 짚어주세요.\n[월운 데이터]: {self.saju_data.get('luck_cycle', {}).get('monthly', [])}"
        }
        return prompts.get(chapter['prompt_key'], prompts["understanding"])

    def _get_assistant_response(self, prompt, chapter_info):
        """OpenAI Assistants API 호출 (Run & Retrieve)"""
        self.log(f"  - {chapter_info['title']} 분석 중...")
        try:
            thread = self.client.beta.threads.create()
            self.client.beta.threads.messages.create(thread_id=thread.id, role="user", content=prompt)
            run = self.client.beta.threads.runs.create(thread_id=thread.id, assistant_id=self.assistant_id)

            while run.status != "completed":
                if run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"AI 호출 실패 (Status: {run.status})")
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value
        except Exception as e:
            self.log(f"    ❌ 오류: {str(e)}")
            return f"\n[제{chapter_info['number']}장 생성 중 오류가 발생했습니다.]\n{str(e)}"

    def generate_pdf(self, output_filename=None):
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            username = self.user_info.get('name', 'customer')
            output_filename = f"saju_report_{username}_{timestamp}.pdf"

        # [수정] 저장 위치를 바탕화면 SajuPro_Reports 폴더로 변경
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "SajuPro_Reports")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = os.path.join(output_dir, output_filename)

        self.log(f"\n🚀 [{username}] 님 PDF 생성 시작")
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # 폰트 설정
        font_name = 'Helvetica'
        font_paths = ['/System/Library/Fonts/Supplemental/AppleGothic.ttf', '/Library/Fonts/AppleGothic.ttf']
        for fp in font_paths:
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont('Korean', fp))
                font_name = 'Korean'
                break

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontName=font_name, fontSize=24, alignment=TA_CENTER, spaceAfter=50)
        chapter_style = ParagraphStyle('Chapter', parent=styles['Heading1'], fontName=font_name, fontSize=18, spaceBefore=20, spaceAfter=15)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName=font_name, fontSize=11, leading=18)

        # 표지
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("명리심리연구소", title_style))
        story.append(Paragraph(f"{name} 님 정밀 운세 보고서", title_style))
        story.append(PageBreak())

        # 각 장 생성
        for chapter in self.CHAPTERS:
            story.append(Paragraph(f"제 {chapter['number']}장. {chapter['title']}", chapter_style))
            content = self._get_assistant_response(self._create_prompt(chapter), chapter)
            
            for line in content.split('\n\n'):
                if line.strip():
                    story.append(Paragraph(line.replace('\n', '<br/>'), body_style))
                    story.append(Spacer(1, 10))
            story.append(PageBreak())

        doc.build(story)
        self.log(f"✅ PDF 저장 완료: {output_path}\n")
        return output_path

class SajuPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사주 운세 배치 프로세서 V3.0")
        self.root.geometry("620x800")
        self.root.configure(bg="#2c3e50")
        
        self.json_files = []
        config = ConfigManager.load_config()
        self.api_key_var = tk.StringVar(value=config.get("OPENAI_API_KEY", ""))
        self.asst_id_var = tk.StringVar(value=config.get("ASSISTANT_ID", "asst_iNDIeQB05RbsRV2r6tobSlPp"))
        
        self.setup_ui()

    def setup_ui(self):
        # 1. Header
        tk.Label(self.root, text="SAJU BATCH PROCESSOR V3", font=("Arial", 18, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

        # 2. Config Frame
        c_frame = tk.LabelFrame(self.root, text="시스템 설정", bg="#2c3e50", fg="#ecf0f1", padx=15, pady=10)
        c_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(c_frame, text="OpenAI API Key:", bg="#2c3e50", fg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(c_frame, textvariable=self.api_key_var, show="*", width=40).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(c_frame, text="Assistant ID:", bg="#2c3e50", fg="white").grid(row=1, column=0, sticky="w")
        tk.Entry(c_frame, textvariable=self.asst_id_var, width=40).grid(row=1, column=1, padx=10, pady=5)

        # 3. File List
        f_frame = tk.LabelFrame(self.root, text="처리 대상 목록 (JSON)", bg="#2c3e50", fg="#ecf0f1", padx=15, pady=10)
        f_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        btn_box = tk.Frame(f_frame, bg="#2c3e50")
        btn_box.pack(fill="x", pady=5)
        tk.Button(btn_box, text="파일 추가 (+)", command=self.add_files, width=15).pack(side="left", padx=2)
        tk.Button(btn_box, text="목록 초기화", command=self.clear_files, width=15).pack(side="left", padx=2)
        
        self.listbox = tk.Listbox(f_frame, height=8, bg="#34495e", fg="white", font=("Menlo", 11), borderwidth=0)
        self.listbox.pack(fill="both", expand=True, pady=5)

        # 4. Action
        self.btn_run = tk.Button(self.root, text="PDF 분석 및 생성 시작", command=self.start, bg="#27ae60", fg="black", font=("Arial", 14, "bold"), height=2)
        self.btn_run.pack(fill="x", padx=20, pady=10)

        # 5. Log Console
        l_frame = tk.LabelFrame(self.root, text="실시간 처리 로그", bg="#2c3e50", fg="#ecf0f1", padx=15, pady=10)
        l_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.log_area = scrolledtext.ScrolledText(l_frame, height=12, bg="black", fg="#2ecc71", font=("Menlo", 10))
        self.log_area.pack(fill="both", expand=True)

    def log(self, msg):
        self.root.after(0, lambda: self._update_log(msg))

    def _update_log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        for f in files:
            if f not in self.json_files:
                self.json_files.append(f)
                self.listbox.insert(tk.END, f" {os.path.basename(f)}")

    def clear_files(self):
        self.json_files = []
        self.listbox.delete(0, tk.END)

    def start(self):
        if not self.json_files:
            messagebox.showwarning("경고", "분석할 파일을 추가해주세요.")
            return
        
        api_key = self.api_key_var.get().strip()
        asst_id = self.asst_id_var.get().strip()
        
        if not api_key or not asst_id:
            messagebox.showwarning("경고", "설정값을 모두 입력해주세요.")
            return
            
        ConfigManager.save_config(api_key, asst_id)
        self.btn_run.config(state='disabled', text="작업 진행 중...")
        threading.Thread(target=self.work, args=(api_key, asst_id), daemon=True).start()

    def work(self, api_key, asst_id):
        success = 0
        total = len(self.json_files)
        for path in self.json_files:
            try:
                gen = SajuPDFGenerator(path, api_key, asst_id, self.log)
                gen.generate_pdf()
                success += 1
            except Exception as e:
                self.log(f"❌ 오류 발생: {str(e)}")
        
        self.log(f"\n✨ 배치 작업 완료 (성공: {success}/{total})")
        self.root.after(0, lambda: self.btn_run.config(state='normal', text="PDF 분석 및 생성 시작"))
        self.root.after(0, lambda: messagebox.showinfo("완료", "모든 사주 레포트 생성이 완료되었습니다."))

if __name__ == "__main__":
    root = tk.Tk()
    SajuPDFApp(root)
    root.mainloop()
