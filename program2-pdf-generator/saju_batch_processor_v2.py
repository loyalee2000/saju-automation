import sys
import os
import json
import re
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import openai
from jinja2 import Environment, FileSystemLoader
import markdown
import base64
import shutil
try:
    import email_sender
except ImportError:
    # If using PyInstaller, it handles imports, but good to be safe if running raw
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import email_sender
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# SELEINIUM IMPORTS (New Chrome Engine)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Import prompts (assuming they are in the same dir)
try:
    import report_prompts
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import report_prompts

from static_data import EXPERT_COLUMNS, TOC_STRUCTURE, APPENDIX_TOC

# OpenAI API Key (Existing logic)
API_KEY = os.getenv("OPENAI_API_KEY")

def pad_zero(value):
    try:
        return f"{int(value):02d}"
    except:
        return str(value)

def get_color_class(char):
    # Map valid characters to Ohaeng colors
    # Extended list for robustness
    wood = ['갑', '을', '인', '묘']
    fire = ['병', '정', '사', '오']
    earth = ['무', '기', '진', '술', '축', '미']
    metal = ['경', '신', '신', '유'] 
    water = ['임', '계', '해', '자']
    
    if not char: return ''
    c = char[0]
    if c in wood: return 'wood'
    if c in fire: return 'fire'
    if c in earth: return 'earth'
    if c in metal: return 'metal'
    if c in water: return 'water'
    return ''

def get_element_eng(k):
    return {'목':'wood', '화':'fire', '토':'earth', '금':'metal', '수':'water'}.get(k, 'earth')

def build_request_message(prompts: dict, chapter_key: str) -> str:
    """
    Combines CORE_PROMPT_BLOCK + chapter_title + chapter_prompt into final request message.
    Called for each chapter when making an AI request.
    """
    core = prompts.get("CORE_PROMPT_BLOCK", "").strip()

    chapter = prompts["CHAPTER_BATCH_LIST"][chapter_key]
    title = chapter.get("chapter_title", "").strip()
    prompt = chapter.get("chapter_prompt", "").strip()

    return "\n\n".join([p for p in [core, title, prompt] if p]).strip()

# -----------------------------------------------------------------------
# Prompt Manager (Logic from previous batch processor)
# -----------------------------------------------------------------------
class PromptManager:
    """Manages the retrieval and formatting of prompts for the 14-chapter detailed report."""
    
    PROMPTS = {}

    @classmethod
    def load_prompts(cls):
        """Load prompts from prompts.json if available, otherwise use defaults."""
        try:
            # Current directory
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            json_path = os.path.join(base_dir, 'prompts.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    cls.PROMPTS = json.load(f)
                print(f"✅ Loaded external prompts from {json_path}")
            else:
                print("ℹ️ prompts.json not found. Using internal defaults.")
        except Exception as e:
             print(f"⚠️ Error loading prompts.json: {e}")

    @classmethod
    def get_system_prompt(cls):
        """Constructs the System Prompt dynamically. Strictly V7 (CORE_PROMPT_BLOCK)."""
        if not cls.PROMPTS:
            return report_prompts.SYSTEM_PROMPT

        # V7 NEW: CORE_PROMPT_BLOCK (Single source of truth for all writing rules)
        core_block = cls.PROMPTS.get('CORE_PROMPT_BLOCK')
        if core_block:
            return f"[핵심 작성 규칙]\n{core_block}"
        
        # Fallback for completely empty or malformed prompts
        return (
            "You are a professional Saju Analysis Expert.\n"
            "Strictly follow the user's specific chapter instructions."
        )



    @classmethod
    def get_constructed_prompt(cls, key, user_info_str, specific_tone_key=None):
        """Builds the final User Prompt: User Info + Instruction + Tone"""
        # 1. Get Instruction
        instruction = ""
        # Check if new structure (CONTENT_MODULES)
        if 'CONTENT_MODULES' in cls.PROMPTS and key in cls.PROMPTS['CONTENT_MODULES']:
            instruction = cls.PROMPTS['CONTENT_MODULES'][key]
        elif key in cls.PROMPTS and isinstance(cls.PROMPTS[key], str):
             # Old flat structure compatibility
             # If exact match in root, use it (likely has {name} placeholders etc)
             # But if user_info_str is passed, we might need to handle it.
             # For now, if we find flat key, we assume it is the FULL template
             return cls.PROMPTS[key] 
        elif hasattr(report_prompts, key):
            # Fallback to internal
             return getattr(report_prompts, key)
        else:
            return f"No instruction found for {key}"

        # 2. Append Tone Adjustment if needed
        tone_adj = ""
        if specific_tone_key and specific_tone_key in cls.PROMPTS:
             tone_adj = f"\n\n[Specific Tone Adjustment]\n{json.dumps(cls.PROMPTS[specific_tone_key], ensure_ascii=False, indent=2)}"

        # 3. Assemble
        final_prompt = f"{user_info_str}\n\n[Analysis Request]\n{instruction}{tone_adj}"
        return final_prompt
    
    @staticmethod
    def _format_pillars(data):
        p = data.get('four_pillars', {})
        def get_p(key):
            val = p.get(key, {})
            return f"{val.get('gan','')}{val.get('ji','')}"
            
        return f"Year: {get_p('year')}, Month: {get_p('month')}, Day: {get_p('day')}, Hour: {get_p('hour')}"

    @staticmethod
    def _get_daewoon_info(data):
        # Extract Daewoon list and current daewoon
        dw_data = data.get('daewoon', {})
        dw_list = dw_data.get('pillars', [])
        formatted_dw_list = ", ".join([f"{d['age']}세({d['ganji']})" for d in dw_list])
        
        # Simple age calc
        try:
            birth_year = int(data.get('info', {}).get('input_date', '2000').split('-')[0])
            now_year = datetime.now().year
            age = now_year - birth_year + 1
        except:
            age = 0
            
        current_dw = "Unknown"
        for d in dw_list:
            if age >= d['age']:
                current_dw = f"{d['ganji']} 대운 (Age {d['age']}~)"
            else:
                break
        return formatted_dw_list, current_dw, age

    @staticmethod
    def get_01_essence(data):
        name = data.get('info', {}).get('name', 'Unknown')
        gender = data.get('info', {}).get('gender', 'Unknown')
        date = data.get('info', {}).get('input_date', '')
        time = data.get('info', {}).get('input_time', '')
        pillars = PromptManager._format_pillars(data)
        
        user_info = (f"**User Info**\nName: {name}\nGender: {gender}\n"
                     f"DOB: {date} {time}\nPillars: {pillars}")
                     
        # Use constructed prompt logic
        return PromptManager.get_constructed_prompt('PROMPT_01_ESSENCE', user_info)

    @staticmethod
    def get_02_daewoon(data):
        pillars = PromptManager._format_pillars(data)
        dw_list, curr_dw, _ = PromptManager._get_daewoon_info(data)
        
        user_info = (f"**User Info**\nPillars: {pillars}\n"
                     f"Daewoon List: {dw_list}\nCurrent Daewoon: {curr_dw}")
                     
        return PromptManager.get_constructed_prompt('PROMPT_02_DAEWOON', user_info, 'DAEWOON_TONE_ADJUSTMENT')

    @staticmethod
    def get_03_seun(data, year):
        pillars = PromptManager._format_pillars(data)
        _, curr_dw, _ = PromptManager._get_daewoon_info(data)
        
        # Calculate Ganji
        base_year = 2024
        cheongan = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        jiji = ['진', '사', '오', '미', '신', '유', '술', '해', '자', '축', '인', '묘']
        
        offset = year - base_year
        gan = cheongan[offset % 10]
        ji = jiji[offset % 12]
        seun_ganji = f"{gan}{ji}"
        
        try:
            birth_year = int(data.get('info', {}).get('input_date', '2000').split('-')[0])
            age_at_year = year - birth_year + 1
        except:
            age_at_year = 0

        user_info = (f"**User Info**\nPillars: {pillars}\nCurrent Daewoon: {curr_dw}\n"
                     f"Target Year: {year} ({seun_ganji})\nAge: {age_at_year}")

        # KEY MAPPING: User provided PROMPT_03_YEARLY, Code uses PROMPT_03_SEUN_YEARLY
        # But I wrote PROMPT_03_SEUN_YEARLY in prompts.json as per user's request (I mapped it internally in thought process, but let's check what I wrote).
        # I wrote PROMPT_03_SEUN_YEARLY in the json tool call.
        
        return PromptManager.get_constructed_prompt('PROMPT_03_SEUN_YEARLY', user_info, 'YEARLY_TONE_ADJUSTMENT')

    @staticmethod
    def get_04_monthly(data, year=None):
        pillars = PromptManager._format_pillars(data)
        if year is None:
            year = datetime.now().year
            
        # Calculate Ganji
        base_year = 2024
        cheongan = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        jiji = ['진', '사', '오', '미', '신', '유', '술', '해', '자', '축', '인', '묘']
        offset = year - base_year
        gan = cheongan[offset % 10]
        ji = jiji[offset % 12]
        seun_ganji = f"{gan}{ji}년"

        user_info = f"**User Info**\nPillars: {pillars}\nYear: {year} ({seun_ganji})"
        
        return PromptManager.get_constructed_prompt('PROMPT_04_MONTHLY', user_info, 'YEARLY_TONE_ADJUSTMENT')

    @staticmethod
    def get_common_prompt(data, prompt_key_or_text):
        pillars = PromptManager._format_pillars(data)
        name = data.get('info', {}).get('name', '내담자')
        
        user_info = f"**User Info**\nName: {name}\nPillars: {pillars}"
        
        # If prompt_key_or_text is NOT a key in prompts.json, it will be treated as text instruction
        return PromptManager.get_constructed_prompt(prompt_key_or_text, user_info)
        
    @staticmethod
    def get_with_gender(data, prompt_key_or_text):
        pillars = PromptManager._format_pillars(data)
        gender = data.get('info', {}).get('gender', 'Unknown')
        
        user_info = f"**User Info**\nPillars: {pillars}\nGender: {gender}"
        
        return PromptManager.get_constructed_prompt(prompt_key_or_text, user_info)
        
    @staticmethod
    def get_sinsal_prompt(data):
        pillars = PromptManager._format_pillars(data)
        sinsal_info = json.dumps(data.get('sinsal', {}), ensure_ascii=False)
        
        user_info = f"**User Info**\nPillars: {pillars}\nSinsal Data: {sinsal_info}"
        
        return PromptManager.get_constructed_prompt('PROMPT_06_SINSAL_MAIN', user_info)

    @staticmethod
    def get_sibseong_prompt(data):
        pillars = PromptManager._format_pillars(data)
        sibseong_info = json.dumps(data.get('sibseong', {}), ensure_ascii=False)
        
        user_info = f"**User Info**\nPillars: {pillars}\nSibseong Data: {sibseong_info}"
        
        return PromptManager.get_constructed_prompt('PROMPT_08_SIBSEONG', user_info)

    @staticmethod
    def get_02_daewoon(data):
        pillars = PromptManager._format_pillars(data)
        daewoon_data = data.get('daewoon', [])
        
        daewoon_list = []
        if isinstance(daewoon_data, dict):
            daewoon_list = daewoon_data.get('pillars', [])
        elif isinstance(daewoon_data, list):
            daewoon_list = daewoon_data
            
        current_daewoon = data.get('current_daewoon', '정보 없음')
        
        # Format daewoon list nicely
        formatted_items = []
        for d in daewoon_list:
            if isinstance(d, dict):
                ganji = d.get('ganji', '?')
                age = d.get('start_age', d.get('age', '?'))
                formatted_items.append(f"{ganji}({age}세)")
            else:
                formatted_items.append(str(d))
                
        daewoon_str = ", ".join(formatted_items)
        
    @staticmethod
    def _clean_text(text):
        """Removes English characters and parentheses like (Fire)."""
        import re
        if not isinstance(text, str): return str(text)
        # Remove (Text) where Text contains English
        text = re.sub(r'\([a-zA-Z\s]+\)', '', text)
        return text.strip()

    @staticmethod
    def _prepare_variables(data):
        """Prepares all variables defined in INPUT_VARIABLES."""
        # Basic Info
        info = data.get('info', {})
        name = info.get('name', '내담자')
        name_short = name[1:] if len(name) > 1 else name
        
        # Pillars
        pillars_str = PromptManager._format_pillars(data)
        
        # Ohaeng (Clean English)
        ohaeng = data.get('five_elements', {})
        cleaned_ohaeng = []
        for k, v in ohaeng.items():
            # k might be "목(Tree)" -> clean to "목"
            clean_k = PromptManager._clean_text(k)
            cleaned_ohaeng.append(f"{clean_k}: {v}")
        ohaeng_str = ", ".join(cleaned_ohaeng)
        
        # Sinsal & Sibseong & 12unseong (JSON dump for context)
        # Clean keys if possible (simple clean for now)
        sinsal_str = json.dumps(data.get('sinsal', {}), ensure_ascii=False)
        sibseong_str = json.dumps(data.get('sibseong', {}), ensure_ascii=False)
        twelve_unseong_str = json.dumps(data.get('twelve_unseong', {}), ensure_ascii=False) # Assuming key exists or is derived
        
        # Daewoon
        dw_list_str, curr_dw, _ = PromptManager._get_daewoon_info(data)
        
        # Calculated Future Data
        yearly_list_10y = PromptManager._get_yearly_list_10y(data)
        monthly_flow = PromptManager._get_monthly_flow(data, 2026) # Hardcoded for CH13 per user request
        
        return {
            "user_name_full": name,
            "user_name_short": name_short,
            "user_name_last": name_short, # V4 Support
            "birth_date": info.get('input_date', ''),
            "issue_date": datetime.now().strftime("%Y년 %m월 %d일"),
            "pillars": pillars_str,
            "oheng_distribution": ohaeng_str,
            "sinsal_data": sinsal_str,
            "sibseong_data": sibseong_str,
            "twelve_unseong_data": twelve_unseong_str,
            "daewoon_list": dw_list_str,
            "current_daewoon": curr_dw,
            "yearly_list_10y": yearly_list_10y,
            "target_year": "2026", # Contextual
            "seun_ganji": "병오년(예시)", # Placeholder or Calc
            "monthly_flow": monthly_flow
        }

    @staticmethod
    def _get_yearly_list_10y(data):
        # Calculate next 10 years seun
        current_year = datetime.now().year + 1
        output = []
        cheongan = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        jiji = ['진', '사', '오', '미', '신', '유', '술', '해', '자', '축', '인', '묘']
        base_year = 2024 # Gapjin
        
        for i in range(10):
            y = current_year + i
            offset = y - base_year
            gan = cheongan[offset % 10]
            ji = jiji[offset % 12]
            output.append(f"{y}년({gan}{ji})")
        return ", ".join(output)

    @staticmethod
    def _get_monthly_flow(data, target_year):
        # Calculate monthly ganji for target_year
        # This requires more complex perpetual calendar logic.
        # For simplification, we will list the months 1-12.
        # In a real engine, we'd use the saju library's calendar.
        return f"{target_year}년 1월 ~ 12월 월운 흐름 데이터 (상세 산출 필요)"

    @classmethod
    def get_chapter_prompt(cls, data, chap_info, chap_key=None, variable_overrides=None):
        """V7: CORE_PROMPT_BLOCK + chapter_title + chapter_prompt"""
        
        # Safety guard: chap_key is required
        if not chap_key:
            raise ValueError("chap_key is required for V7 prompt generation")
        
        print(f"🔧 Building prompt for chapter {chap_key}")
        
        variables = cls._prepare_variables(data)
        if variable_overrides:
            variables.update(variable_overrides)

        # build_request_message로 합친 프롬프트 + 분석 대상 정보
        combined_prompt = build_request_message(cls.PROMPTS, chap_key)
        
        # Safety guard: combined_prompt must not be empty
        if not combined_prompt:
            raise ValueError("Combined prompt is empty. Check CORE_PROMPT_BLOCK or chapter_prompt.")
        
        final_prompt = (
            f"{combined_prompt}\n\n"
            f"[분석 대상 정보]\n"
            f"이름: {variables['user_name_full']}\n"
            f"성별: {data.get('info', {}).get('gender', 'Unknown')}\n"
            f"사주(천간/지지 특성 포함): {variables['pillars']}\n"
            f"오행 분포: {variables['oheng_distribution']}\n"
            f"대운: {variables['current_daewoon']}\n"
            f"십성 상세(심리/성격): {variables['sibseong_data']}\n"
            f"신살 상세(의미/영향): {variables['sinsal_data']}\n"
            f"십이운성: {variables['twelve_unseong_data']}\n"
            f"대운 흐름: {variables['daewoon_list']}\n"
            f"향후 10년 연운: {variables['yearly_list_10y']}\n"
            f"월운 흐름: {variables['monthly_flow']}\n\n"
            f"[참고 - 십성 및 신살 상세 해석 (JSON 제공)]\n"
            f"{json.dumps(data.get('sibseong_details', {}), ensure_ascii=False, indent=2)}\n"
            f"{json.dumps(data.get('sinsal_details', {}), ensure_ascii=False, indent=2)}\n"
            f"{json.dumps(data.get('four_pillars', {}), ensure_ascii=False, indent=2)}"
        )
        return final_prompt


def generate_pdf_via_chrome(html_path, output_pdf_path, log_callback):
    """
    Generates a PDF using Headless Chrome.
    """
    if not SELENIUM_AVAILABLE:
        log_callback("❌ Selenium not available. Cannot use Chrome Engine.")
        return False
        
    try:
        html_abs_path = os.path.abspath(html_path)
        
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--hide-scrollbars')

        # Use webdriver_manager to get driver path automatically
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Load HTML
            driver.get(f"file://{html_abs_path}")
            
            # Print settings (CSS-Driven)
            print_options = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True # FULL TRUST IN CSS @page
            }
            
            pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
            
            with open(output_pdf_path, 'wb') as f:
                f.write(base64.b64decode(pdf_data['data']))
                
            log_callback(f"✅ PDF Generated via Chrome: {os.path.basename(output_pdf_path)}")
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        log_callback(f"❌ Chrome PDF Error: {e}")
        return False

def merge_pdf_background(content_pdf_path, background_pdf_path, output_pdf_path, log_callback):
    """
    Overlays content_pdf ON TOP OF background_pdf page by page.
    Assumes background_pdf has 1 page (stationery) which is repeated.
    """
    if not PYPDF2_AVAILABLE:
        log_callback("❌ PyPDF2 not installed. Cannot merge background.")
        return False

    try:
        # Open Files
        content_file = open(content_pdf_path, 'rb')
        background_file = open(background_pdf_path, 'rb')
        
        content_reader = PyPDF2.PdfReader(content_file)
        background_reader = PyPDF2.PdfReader(background_file)
        background_page = background_reader.pages[0] 
        
        writer = PyPDF2.PdfWriter()
        
        for i, page in enumerate(content_reader.pages):
            # Create a NEW page object from the background (copy)
            # We merge content INTO the background (or vice versa)
            # Standard approach: Take background, merge content on top
            
            # Note: PyPDF2 merge_page overlays the argument ONTO the invoking page
            # So: new_page.merge_page(content_page)
            
            # We need a fresh copy of the background for each page
            writer.add_page(background_page)
            
            # Now get the page we just added (last one) and merge content
            # BUT: PyPDF2 add_page might add a reference. Modifications might ripple.
            
            # Correct Logic:
            # 1. Take Background Page
            # 2. Merge Content Page (as overlay) onto Background
            # 3. Add to Writer.
            
            # So:
            # final_page = PageObject.create_blank_page(...)
            # final_page.merge_page(background_page)
            # final_page.merge_page(content_page)
            # writer.add_page(final_page)
            
            # Let's try this standard composition.
            
            merged_page = PyPDF2.PageObject.create_blank_page(
                width=page.mediabox.width, 
                height=page.mediabox.height
            )
            merged_page.merge_page(background_page) # Background First
            merged_page.merge_page(page)            # Content Second
            
            writer.add_page(merged_page)
            
        with open(output_pdf_path, 'wb') as f_out:
            writer.write(f_out)
            
        content_file.close()
        background_file.close()
        
        # Cleanup Content PDF (temp)
        if os.path.exists(content_pdf_path):
            # For Debugging: Keep the file
            # os.remove(content_pdf_path)
            pass
            
        log_callback(f"✅ Merged Background + Content: {os.path.basename(output_pdf_path)}")
        return True
        
    except Exception as e:
        log_callback(f"❌ Merge Error: {e}")
        return False

# -----------------------------------------------------------------------
# PDF / HTML Generator Logic
# -----------------------------------------------------------------------
class SajuBatchProcessor:
    def __init__(self, api_key, assistant_id=None, model="gpt-4o"):
        print(f"DEBUG: SajuBatchProcessor initialized with Key: {api_key[:15]}... (Check if this matches new key 'sk-proj-iz5Q')")
        self.client = openai.OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        if not self.assistant_id:
            # Helper: Use default if not provided (though user should provide it)
            pass
            
        self.model = model
        self.pm = PromptManager()
        # Ensure prompts are loaded!
        if not self.pm.PROMPTS:
            self.pm.load_prompts()
        
        # Setup Jinja2
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.template_dir = os.path.join(base_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Register Filters
        self.env.filters['pad_zero'] = pad_zero
    
    def _call_ai(self, user_prompt, system_prompt):
        # Override system_prompt if we have dynamic one available from PromptManager
        dynamic_system_prompt = self.pm.get_system_prompt()
        final_system_prompt = dynamic_system_prompt if dynamic_system_prompt else system_prompt

        # Clean Response Logic
        import re
        def clean_ai_response(text):
            # 1. Strip OpenAI Citations
            text = re.sub(r"【\d+:\d+†source】", "", text)
            text = re.sub(r"\[\d+:\d+†source\]", "", text)
            
            # 2. Strict Header Removal (Top level chapters)
            text = re.sub(r'^\s*\[\s*제\s*\d+\s*장.*?\]', '', text, flags=re.MULTILINE)
            text = re.sub(r'^\s*제\s*\d+\s*장.*?$', '', text, flags=re.MULTILINE)

            # 3. Strip Bracketed Sub-headers [Title] -> Title (Bold? Just pure text for now)
            text = re.sub(r'\[(.*?)\]', r'\1', text) 

            # 4. Strip Hanja (Range: \u4e00-\u9fff)
            text = re.sub(r'[\u4e00-\u9fff]', '', text)
            text = re.sub(r'\(\s*\)', '', text)

            # 5. Safety Net: Hallucination "길동" removal
            text = text.replace("길동님", "다은님") 
            text = text.replace("길동", "") 

            # 6. Remove List Numbering "1. ", "2. " to force flow
            # e.g. "1. 역마의 힘" -> "역마의 힘"
            text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)

            # 7. Remove "Greet/Closing" Artifacts (New!)
            # Remove "안녕하세요...", "감사합니다..." if they start/end the block
            # This is risky if it's part of a sentence, but usually AI writes them as separate paragraphs.
            
            # Remove start lines like "안녕하세요, OO님."
            lines = text.split('\n')
            if lines:
                first_line = lines[0].strip()
                if first_line.startswith("안녕하세요") or first_line.startswith("반갑습니다"):
                    lines = lines[1:]
                
                if lines: # Check last line
                    last_line = lines[-1].strip()
                    if last_line.startswith("감사합니다") or "도움이 되셨기를" in last_line:
                        lines = lines[:-1]
            
            text = "\n".join(lines).strip()

            # 8. Remove Bullet points "-" to force essay flow
            # Replace "- " with "" (empty) or better, join to previous line?
            # User wants "Essay". Bullets are "List".
            # Let's just strip the bullet marker.
            text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)

            # Cleanup extra whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()

        # 1. Try Assistants API if ID is provided
        if self.assistant_id:
            try:
                # Create a Thread (per request for simplicity and isolation)
                thread = self.client.beta.threads.create()
                
                # Add User Message
                self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_prompt
                )
                
                # Run WITHOUT overriding instructions - let GPT's dashboard instructions take control
                run = self.client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=self.assistant_id
                    # instructions parameter REMOVED - GPT's native System Instructions will be used
                )
                
                # Poll
                run = self._wait_for_run(thread.id, run.id)
                
                if run.status == 'completed':
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    # Get the latest message from assistant
                    for msg in messages.data:
                        if msg.role == "assistant":
                             if hasattr(msg.content[0], 'text'):
                                 raw_text = msg.content[0].text.value
                                 return clean_ai_response(raw_text)
                    return "Error: No assistant message found."
                else:
                    raise Exception(f"Run status: {run.status}")

            except Exception as e:
                print(f"⚠️ Assistant API Critical Error (ID: {self.assistant_id}): {e}")
                raise e

        # 2. Standard Chat Completions (Only used if no assistant_id provided)
        # Note: If assistant_id IS provided, we returned or raised above.
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        return clean_ai_response(response.choices[0].message.content)

    def _wait_for_run(self, thread_id, run_id):
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status in ['queued', 'in_progress', 'cancelling']:
                time.sleep(1) # Wait 1s
                continue
            elif run.status == 'failed':
                error_msg = f"Run status: {run.status}"
                if hasattr(run, 'last_error') and run.last_error:
                    error_msg += f" | Code: {run.last_error.code} | Message: {run.last_error.message}"
                raise Exception(error_msg)
            else:
                return run

    def process_file(self, json_path, output_dir, log_callback, stop_event=None, email_config=None, override_email=None, preview_mode=False):
        try:
            # 1. Load Data
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            name = data.get('info', {}).get('name', 'Unknown')
            # 1. Look for Override, 2. Look in JSON
            # Check for Global Recipient Override first
            if email_config and email_config.get('global_recipient'):
                 client_email = email_config['global_recipient']
                 log_callback(f"ℹ️ Email Override: Sending to {client_email} (Global Setting)")
            else:
                 client_email = override_email if override_email else data.get('info', {}).get('email', '')
            
            log_callback(f"\n▶ Processing: {name} ({client_email if client_email else 'No Email'})")
            if preview_mode:
                log_callback("⚠️ Preview Mode Active: Skipping AI Generation (No Cost)")

            # 2. Define Tasks (Chapters)
            # 2. Define Tasks (Chapters) matches new TOC
            # Note: prompts need to align. For "About Saju", we use static text or a generic prompt?
            # Let's generate it to be safe and personal.
            
            # 2. Define Tasks (Chapters) 
            tasks = []
            
            # V7 Strict: CHAPTER_BATCH_LIST
            chapter_map = self.pm.PROMPTS.get('CHAPTER_BATCH_LIST', {})

            if not chapter_map:
                log_callback("❌ Error: CHAPTER_BATCH_LIST not found in prompts.json")
                return False

            # Sort by key (CH01, CH02, ...)
            sorted_chapters = sorted(chapter_map.items(), key=lambda x: x[0])
            
            for chap_id, chap_info in sorted_chapters:
                # V7: Title is explicit
                title = chap_info.get('chapter_title', f"Chapter {chap_id}")
                
                # Check for skipped chapters (optional feature)
                if chap_info.get('skip', False):
                    continue
                
                # Read execution type if available
                exec_type = chap_info.get('execution_type', 'standard')
                
                # Generate Prompt (V7: pass chap_id for build_request_message)
                try:
                    prompt = self.pm.get_chapter_prompt(data, chap_info, chap_key=chap_id)
                except Exception as e:
                    log_callback(f"⚠️ Error building prompt for {chap_id}: {e}")
                    prompt = f"Error: {e}"

                tasks.append({
                    'key': chap_id, 
                    'name': title,
                    'prompt': prompt,
                    'type': exec_type,
                    'chap_info': chap_info
                })

            current_date = datetime.now().strftime("%Y-%m-%d")
            # 3. Execute AI Tasks
            ai_analysis = {}
            total_tasks = len(tasks)
            
            # Start Year for Seun
            current_year = datetime.now().year
            start_forecast_year = current_year + 1 # Next Year
            
            for idx, task in enumerate(tasks):
                if stop_event and stop_event.is_set():
                    log_callback("🛑 Processing Stopped by User.")
                    return False
                    
                key = task['key']
                
                if preview_mode:
                     # (Preview Mode logic omitted for brevity, keeping existing)
                     ai_analysis[key] = f"<h3>[Preview] {task['name']}</h3><p>미리보기... (생략)</p>"
                     continue

                log_callback(f"  Generating: {task['name']}...")
                
                try:
                    if task.get('type') == 'monthly_loop':
                        # Monthly Loop Logic (12 calls)
                        combined_res = f"<h3>{task['name']}</h3>\n"
                        # Intro from template (Executed ONCE locally)
                        intro_text = task['chap_info'].get('intro_template','').format(**self.pm._prepare_variables(data))
                        combined_res += f"<p>{intro_text}</p><hr>\n"

                        for m in range(1, 13):
                            if stop_event and stop_event.is_set(): return False
                            log_callback(f"    - Month {m}...")
                            
                            # Construct Single Month Prompt
                            overrides = {
                                'target_period': f"{m}월",
                                'current_month': m
                            }
                            # Re-generate prompt with specific month focus, using get_chapter_prompt
                            p = self.pm.get_chapter_prompt(data, task['chap_info'], chap_key=task['key'], variable_overrides=overrides)
                            
                            # Add instruction to focus ONLY on this month
                            p += f"\n\n[특별 지침]\n이번 출력은 오직 '{m}월'에 대한 분석만 작성하십시오. 다른 달은 언급하지 마십시오."
                            
                            res = self._call_ai(p, report_prompts.SYSTEM_PROMPT)
                            if res:
                                html_res = markdown.markdown(res)
                                combined_res += f"<h4>{m}월 운세</h4>\n{html_res}\n<br>\n"
                        
                        ai_analysis[key] = combined_res

                    elif task.get('type') == 'loop_10_years':
                        # Special handling for Seun (aggrgating 10 years)
                        combined_res = ""
                        for i in range(10):
                            if stop_event and stop_event.is_set(): return False
                            target_year = start_forecast_year + i
                            log_callback(f"    - Year {target_year}...")
                            p = self.pm.get_03_seun(data, target_year)
                            res = self._call_ai(p, report_prompts.SYSTEM_PROMPT)
                            if res:
                                # Convert 10-year loop content to HTML immediately
                                html_res = markdown.markdown(res)
                                combined_res += f"<h4>{target_year}년 운세</h4>\n{html_res}\n<hr style='border:0; border-top:1px dashed #ccc; margin:20px 0;'>\n"
                        ai_analysis[key] = combined_res
                    else:
                        res = self._call_ai(task['prompt'], report_prompts.SYSTEM_PROMPT)
                        if res:
                            # Sanitize: Remove excessive newlines that might cause blank pages
                            cleaned_res = re.sub(r'\n{3,}', '\n\n', res.strip())
                            
                            # [V7 Fix] Normalize Name Spacing (OO 님 -> OO님)
                            # Ensure consistency regardless of AI output
                            if name: 
                                # Replace "Unknown 님" or "Hong 님" etc.
                                # Matches Name + whitespace + 님 -> Name님
                                # Also handles cases with multiple spaces
                                cleaned_res = re.sub(f'{name}\s+님', f'{name}님', cleaned_res)
                            
                            # [V8 Feature] User-Configurable Post-Processing (post_process_rules.json)
                            try:
                                rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'post_process_rules.json')
                                if os.path.exists(rules_path):
                                    with open(rules_path, 'r', encoding='utf-8') as rf:
                                        rules_data = json.load(rf)
                                        
                                        # Support new list-based regex format
                                        if isinstance(rules_data, list):
                                            for rule in rules_data:
                                                find_pat = rule.get('find_pattern')
                                                replace_with = rule.get('replace_with')
                                                
                                                if not find_pat or find_pat == "IGNORE_THIS_LINE_JUST_SECTION_HEADER":
                                                    continue
                                                    
                                                # Handle dynamic variables like {user_name}
                                                if replace_with and "{user_name}" in replace_with and name:
                                                    replace_with = replace_with.replace("{user_name}", name)
                                                
                                                # Apply Regex
                                                try:
                                                    cleaned_res = re.sub(find_pat, replace_with, cleaned_res)
                                                except Exception as re_err:
                                                    log_callback(f"⚠️ Regex Error for pattern '{find_pat}': {re_err}")

                                        # Support old dict format (Backward Compatibility)
                                        elif isinstance(rules_data, dict):
                                            replacements = rules_data.get('replacements', {})
                                            for target, replacement in replacements.items():
                                                if target in cleaned_res:
                                                    cleaned_res = cleaned_res.replace(target, replacement)

                            except Exception as e:
                                log_callback(f"⚠️ Post-processing Rule Error: {e}")

                            ai_analysis[key] = markdown.markdown(cleaned_res)
                        else:
                            ai_analysis[key] = "내용을 생성하지 못했습니다."
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    log_callback(f"❌ AI Error ({task['name']}): {e}")
                    ai_analysis[key] = f"내용을 생성하지 못했습니다. (AI 오류: {e})"
            
            # 4. Prepare Data
            # Ohaeng Counts
            ohaeng_map = {'목':0, '화':0, '토':0, '금':0, '수':0}
            four_pillars = data.get('four_pillars', {})
            
            log_callback(f"    🔍 Debug: Pillars Data -> {four_pillars}")
            
            # If JSON has specific counts, use them
            if 'five_elements' in data and isinstance(data['five_elements'], dict):
                 ohaeng_map = data['five_elements']
                 log_callback(f"    🔍 Debug: Loaded five_elements from JSON -> {ohaeng_map}")
            
            # Format pillars for easier template access
            pillars_ctx = {
                'year': four_pillars.get('year',{}),
                'month': four_pillars.get('month',{}),
                'day': four_pillars.get('day',{}),
                'hour': four_pillars.get('hour',{})
            }
            
            # Recalculate Ohaeng if empty (Robust Fallback)
            if sum(ohaeng_map.values()) == 0:
                log_callback("    ⚠️ Ohaeng map is empty. Recalculating from pillars...")
                # Simple mapping (Keys must match ohaeng_map Korean keys)
                o_map = {
                    '목': ['갑', '을', '인', '묘'],
                    '화': ['병', '정', '사', '오'],
                    '토':  ['무', '기', '진', '술', '축', '미'],
                    '금': ['경', '신', '유'],
                    '수':  ['임', '계', '해', '자']
                }
                for p_key, p_val in pillars_ctx.items():
                    chars = [p_val.get('gan', ''), p_val.get('ji', '')]
                    for c in chars:
                        if not c: continue
                        target = c.strip()[0] # First char
                        for o_key, o_chars in o_map.items():
                            if target in o_chars:
                                ohaeng_map[o_key] += 1
                                break
                log_callback(f"    ℹ️ Calculated Ohaeng: {ohaeng_map}")
            
            # Sinsal Debug
            sinsal_data = data.get('sinsal', {})
            log_callback(f"    🔍 Debug: Sinsal Data -> {sinsal_data}")

            # 🎯 ReportLab PDF Generation (Direct, No HTML/Blank Pages)
            log_callback("  Generating PDF with ReportLab...")
            pdf_generated_path = None
            
            try:
                from reportlab_generator import ReportLabPDFGenerator
                
                pdf_filename = f"{name}_Premium_Final.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                
                # User info
                user_info = {
                    'name': name,
                    'birth_date': data.get('info', {}).get('input_date', ''),
                }
                
                # Generate PDF directly
                pdf_gen = ReportLabPDFGenerator(pdf_path)
                
                # prepare chapter config for TOC and Order
                chapter_config = [(t['key'], t['name']) for t in tasks]
                
                pdf_gen.generate(
                    user_info=user_info,
                    chapters=ai_analysis,
                    pillars=pillars_ctx,
                    ohaeng_counts=ohaeng_map,
                    sinsal=data.get('sinsal', {}),
                    chapter_config=chapter_config
                )
                
                log_callback(f"✅ PDF Generated: {pdf_filename}")
                pdf_generated_path = pdf_path
                
            except Exception as e:
                import traceback
                log_callback(f"❌ ReportLab Error: {e}")
                traceback.print_exc()
                log_callback("  Falling back to HTML/Chrome method...")
            
            # Fallback to HTML if ReportLab failed
            if not pdf_generated_path:
                # Load Watermark (Local > Remote Fallback)
                watermark_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Mankai_Kamon.svg/600px-Mankai_Kamon.svg.png"

                # Check for local watermark.png in various locations
                possible_paths = [
                    os.path.join(os.path.dirname(json_path), 'watermark.png'), # Next to JSON
                    os.path.join(os.getcwd(), 'watermark.png'), # CWD
                    os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), 'watermark.png') # App dir
                ]

                for p in possible_paths:
                    if os.path.exists(p):
                        try:
                            with open(p, "rb") as img_file:
                                 b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                                 watermark_src = f"data:image/png;base64,{b64_string}"
                                 log_callback("  Found local watermark.png!")
                                 break
                        except Exception as e:
                            log_callback(f"  Failed to load local watermark: {e}")

                context = {
                'watermark_src': watermark_src,
                'user_info': {
                    'name': name,
                    'birth_date': data.get('info', {}).get('input_date'),
                    'birth_time': data.get('info', {}).get('input_time'),
                },
                'current_date': current_date,
                'pillars': pillars_ctx,
                'ohaeng_counts': ohaeng_map,
                'toc_structure': TOC_STRUCTURE,
                'expert_columns': EXPERT_COLUMNS,
                'ai_analysis': ai_analysis,
                'chapter_keys': [t['key'] for t in tasks],
                'zip': zip,
                'get_color_class': get_color_class,
                'get_element_eng': get_element_eng
                }

                # 5. Render HTML
                log_callback("  Rendering Premium HTML...")
                template = self.env.get_template('premium_report.html')
                html_content = template.render(context)
                
                # Save HTML for Chrome conversion
                html_filename = f"{name}_PremiumReport.html"
                html_path = os.path.join(output_dir, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f_html:
                    f_html.write(html_content)
            
                if generate_pdf_via_chrome(html_path, temp_pdf_path, log_callback):
                    # 2. Merge with Background
                    # Locate background file (assume in same dir as script or bundled)
                    if getattr(sys, 'frozen', False):
                        bg_path = os.path.join(sys._MEIPASS, 'stationery_background.pdf')
                    else:
                        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stationery_background.pdf')
                    
                    if os.path.exists(bg_path):
                         log_callback("  🎨 Merging with Stationery Background...")
                         if merge_pdf_background(temp_pdf_path, bg_path, final_pdf_path, log_callback):
                             pdf_generated_path = final_pdf_path
                         else:
                             log_callback("  ⚠️ Merge failed. Using content-only PDF.")
                             pdf_generated_path = temp_pdf_path
                    else:
                        log_callback("  ⚠️ Background PDF not found. Using content-only PDF.")
                        pdf_generated_path = temp_pdf_path
                
                elif PDFKIT_AVAILABLE:
                    # Fallback to wkhtmltopdf if Selenium is missing
                    wkhtmltopdf_path = shutil.which('wkhtmltopdf')
                    
                    if wkhtmltopdf_path:
                        log_callback("  Converting to PDF (Legacy wkhtmltopdf)...")
                        pdf_filename = f"{name}_PremiumReport.pdf"
                        pdf_path = os.path.join(output_dir, pdf_filename)
                        
                        options = {
                            'page-size': 'A4',
                            'margin-top': '0mm',
                            'margin-right': '0mm',
                            'margin-bottom': '0mm',
                            'margin-left': '0mm',
                            'encoding': "UTF-8",
                            'no-outline': None,
                            'print-media-type': None,
                            'enable-local-file-access': None
                        }
                        
                        try:
                            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                            pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
                            log_callback(f"✅ PDF Saved: {pdf_filename}")
                            pdf_generated_path = pdf_path
                        except Exception as e:
                            log_callback(f"❌ PDF Error: {e}")
                    else:
                        log_callback("⚠️ wkhtmltopdf/Selenium not found. Skipping PDF generation.")
                else:
                     log_callback("⚠️ No PDF engine (Selenium/PDFKit) installed. Only HTML saved.")

            # 7. Email Dispatch
            if email_config and email_config.get('enabled') and pdf_generated_path:
                if client_email:
                    log_callback(f"  Sending Email to {client_email}...")
                    subject = f"[{name}님] 프리미엄 사주 분석 보고서 도착"
                    body = f"""
                    <h2>안녕하세요, {name}님.</h2>
                    <p>요청하신 프리미엄 사주 분석 보고서가 완료되어 첨부파일로 보내드립니다.</p>
                    <p>당신의 삶에 작은 등불이 되기를 바랍니다.</p>
                    <br>
                    <p>감사합니다.</p>
                    """
                    
                    success = email_sender.send_email(
                        email_config['sender'],
                        email_config['password'],
                        client_email,
                        subject,
                        body,
                        pdf_generated_path
                    )
                    
                    if success:
                        log_callback("✅ Email Sent Successfully!")
                    else:
                        log_callback("❌ Email Sending Failed.")
                else:
                    log_callback("⚠️ Client Email not found in JSON. Skipping Email.")

            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            log_callback(f"❌ Critical Error: {e}")
            return False

# -----------------------------------------------------------------------
# GUI (Simplified wrapper)
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# GUI (Advanced)
# -----------------------------------------------------------------------
class SajuBatchProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Saju Analysis Batch Processor v2.0")
        self.root.geometry("1000x800")
        
        # Load Prompts (External Config)
        PromptManager.load_prompts()
        
        # Data
        self.json_files = []
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.api_key_var = tk.StringVar()
        self.assistant_id_var = tk.StringVar()  # [NEW] Assistant ID for 명리심리연구소 GPT
        self.output_path_var = tk.StringVar()
        
        # Set Default Path (User Request: ~/Desktop/SajuPro_Reports)
        default_out_path = os.path.join(os.path.expanduser("~"), "Desktop", "SajuPro_Reports")
        try:
            os.makedirs(default_out_path, exist_ok=True)
            self.output_path_var.set(default_out_path)
        except Exception as e:
            print(f"Failed to create default directory: {e}")
        
        # Email Vars
        self.email_sender_var = tk.StringVar(value="loyalee2000@gmail.com") # Default per user request
        self.email_password_var = tk.StringVar()
        self.email_recipient_var = tk.StringVar() # NEW: Global recipient override
        self.email_enabled_var = tk.BooleanVar(value=False)
        
        self.json_files = []
        self.file_emails = {} # Map path -> email override
        self.stop_event = threading.Event()
        
        self._load_api_key() # Load API key on startup
        
        self._create_layout()
        self._add_mac_shortcuts()
        
        # [Auto-Load] Automatically load saju_analysis_result.json from default path if exists
        try:
            auto_file = os.path.join(default_out_path, "saju_analysis_result.json")
            if os.path.exists(auto_file):
                self.json_files.append(auto_file)
                self.file_listbox.insert(tk.END, os.path.basename(auto_file))
        except Exception as e:
            print(f"Auto-load failed: {e}")

    # --- Config Persistence ---
    def _get_config_path(self):
        return os.path.expanduser("~/.saju_config.json")

    def _load_api_key(self):
        try:
            config_path = self._get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    key = config.get('api_key', '')
                    if key:
                        self.api_key_var.set(key)
                    self.email_sender_var.set(config.get('email_sender', ''))
                    self.email_password_var.set(config.get('email_password', ''))
                    self.email_recipient_var.set(config.get('email_recipient', '')) # Load recipient
                    self.email_enabled_var.set(config.get('email_enabled', False))
            
            # [NEW] Also load from config.json (for Assistant ID)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_json_path = os.path.join(script_dir, 'config.json')
            if os.path.exists(config_json_path):
                with open(config_json_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    self.assistant_id_var.set(cfg.get('ASSISTANT_ID', ''))
                    # Also use API key from config.json if not already set
                    if not self.api_key_var.get():
                        self.api_key_var.set(cfg.get('OPENAI_API_KEY', ''))
                    print(f"✅ Loaded Assistant ID: {self.assistant_id_var.get()}")
        except Exception as e:
            print(f"Failed to load config: {e}")

    def _save_api_key(self):
        try:
            config_path = self._get_config_path()
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try: config = json.load(f)
                    except: pass
            
            config['api_key'] = self.api_key_var.get()
            config['email_sender'] = self.email_sender_var.get()
            config['email_password'] = self.email_password_var.get()
            config['email_recipient'] = self.email_recipient_var.get() # Save recipient
            config['email_enabled'] = self.email_enabled_var.get()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    # --- UI Layout ---
    def _create_layout(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_pane, width=400)
        main_pane.add(left_frame, weight=1)
        right_frame = ttk.Frame(main_pane, width=700)
        main_pane.add(right_frame, weight=2)
        
        # --- Left: Settings ---
        settings_frame = ttk.LabelFrame(left_frame, text="설정 (Configurations)")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # API Key
        ttk.Label(settings_frame, text="OpenAI API 키 (API Key):").pack(anchor="w", padx=5)
        # Using a normal Entry but without show="*" initially so user can see it if they want, 
        # or show="*" for security. User asked for convenience, usually visible or saved is fine.
        # Let's keep it masked but pre-filled.
        ttk.Entry(settings_frame, textvariable=self.api_key_var, show="*").pack(fill=tk.X, padx=5, pady=2)
        
        # Output Path
        ttk.Label(settings_frame, text="저장 경로 (Output Directory):").pack(anchor="w", padx=5, pady=(10,0))
        out_frame = ttk.Frame(settings_frame)
        out_frame.pack(fill=tk.X, padx=5)
        ttk.Entry(out_frame, textvariable=self.output_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(out_frame, text="찾아보기", command=self._select_output).pack(side=tk.RIGHT)
        
        # Info
        info_frame = ttk.LabelFrame(left_frame, text="작업 정보 (Job Info)")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        lbl_info = ttk.Label(info_frame, text="14개 챕터의 상세 보고서를 생성합니다.\n(HTML 및 PDF 자동 생성)\n디자인: Classic Premium (Hanji Style)", justify=tk.LEFT)
        lbl_info.pack(padx=10, pady=10)
        
        # Controls
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Preview Mode Checkbox
        self.preview_var = tk.BooleanVar(value=False)
        self.chk_preview = ttk.Checkbutton(btn_frame, text="Preview Mode (No AI Cost)", variable=self.preview_var)
        self.chk_preview.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_start = ttk.Button(btn_frame, text="분석 시작 (START)", command=self._start_process)
        self.btn_start.pack(fill=tk.X, ipady=10)
        
        ttk.Button(btn_frame, text="중지 (STOP)", command=self._stop_process).pack(fill=tk.X, pady=5)

        # Email Settings Section
        email_frame = ttk.LabelFrame(left_frame, text="이메일 자동 전송 (Email Automation)")
        email_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(email_frame, text="변환 후 자동 전송 사용", variable=self.email_enabled_var).pack(anchor="w", padx=5)
        
        ttk.Label(email_frame, text="보내는 이메일 (Sender Email):").pack(anchor="w", padx=5)
        ttk.Entry(email_frame, textvariable=self.email_sender_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(email_frame, text="앱 비밀번호 (App Password):").pack(anchor="w", padx=5)
        ttk.Entry(email_frame, textvariable=self.email_password_var, show="*").pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(email_frame, text="받는 이메일 (Recipient Email - Optional):").pack(anchor="w", padx=5, pady=(5,0))
        ttk.Entry(email_frame, textvariable=self.email_recipient_var).pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(email_frame, text="※ 비워두면 파일 내 이메일 주소로 전송합니다.", font=("", 9), foreground="gray").pack(anchor="w", padx=5)
        
        ttk.Label(email_frame, text="※ Gmail/Naver 등에서 '앱 비밀번호'를 발급받아 입력하세요.", font=("", 9), foreground="gray").pack(anchor="w", padx=5, pady=2)

        # --- Right: Files & Logs ---
        file_frame = ttk.LabelFrame(right_frame, text="입력 파일 (JSON Files)")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        f_btn_frame = ttk.Frame(file_frame)
        f_btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(f_btn_frame, text="파일 추가...", command=self._add_files).pack(side=tk.LEFT)
        ttk.Button(f_btn_frame, text="목록 초기화", command=self._clear_files).pack(side=tk.LEFT, padx=5)
        ttk.Label(f_btn_frame, text="(목록 더블클릭하여 이메일 지정 가능)", font=("", 9), foreground="blue").pack(side=tk.LEFT, padx=5)
        
        self.file_listbox = tk.Listbox(file_frame, height=10)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_listbox.bind("<Double-Button-1>", self._edit_file_email)
        
        log_frame = ttk.LabelFrame(right_frame, text="진행 로그 (Processing Log)")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, state="disabled", height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _add_mac_shortcuts(self):
        try:
            if sys.platform != 'darwin': return
        except: return

        def copy(event):
            try: event.widget.event_generate("<<Copy>>")
            except: pass
        def paste(event):
            try: event.widget.event_generate("<<Paste>>")
            except: pass
        def cut(event):
            try: event.widget.event_generate("<<Cut>>")
            except: pass
        def select_all(event):
            try:
                event.widget.select_range(0, 'end')
                event.widget.icursor('end')
            except: pass

        self.root.bind_all("<Command-c>", copy)
        self.root.bind_all("<Command-v>", paste)
        self.root.bind_all("<Command-x>", cut)
        self.root.bind_all("<Command-a>", select_all)

    def _select_output(self):
        d = filedialog.askdirectory()
        if d: self.output_path_var.set(d)

    def _add_files(self):
        fs = filedialog.askopenfilenames(filetypes=[("JSON Files", "*.json")])
        for f in fs:
            if f not in self.json_files:
                self.json_files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))

    def _clear_files(self):
        self.json_files = []
        self.file_emails = {}
        self.file_listbox.delete(0, tk.END)

    def _edit_file_email(self, event):
        sel = self.file_listbox.curselection()
        if not sel: return
        idx = sel[0]
        f_path = self.json_files[idx]
        
        # Ask for email
        from tkinter import simpledialog
        existing = self.file_emails.get(f_path, "")
        new_email = simpledialog.askstring("이메일 설정", f"'{os.path.basename(f_path)}'의 수신 이메일:", initialvalue=existing, parent=self.root)
        
        if new_email is not None: # None if cancelled
            self.file_emails[f_path] = new_email.strip()
            # Update listbox text
            display_text = os.path.basename(f_path)
            if self.file_emails[f_path]:
                display_text += f"  [To: {self.file_emails[f_path]}]"
            
            self.file_listbox.delete(idx)
            self.file_listbox.insert(idx, display_text)

    def _log(self, msg):
        print(msg) # Print to stdout for debugging
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _log_thread(self, msg):
        self.root.after(0, self._log, msg)

    def _start_process(self):
        if not self.json_files:
            messagebox.showwarning("파일 없음", "JSON 파일을 먼저 추가해주세요.")
            return
            
        is_preview = self.preview_var.get()
        
        # API Key check only if NOT in preview mode
        if not is_preview and not self.api_key_var.get():
            messagebox.showerror("API 키 없음", "OpenAI API 키를 입력해주세요.\n(Preview Mode를 체크하면 키 없이 테스트 가능합니다.)")
            return
            
        if not self.output_path_var.get():
            messagebox.showwarning("경로 없음", "저장할 경로를 선택해주세요.")
            return

        self.stop_event.clear()
        self.btn_start.config(state="disabled")
        
        api_key = self.api_key_var.get()
        out_dir = self.output_path_var.get()
        
        # Email Config
        email_config = {
            'enabled': self.email_enabled_var.get(),
            'sender': self.email_sender_var.get(),
            'password': self.email_password_var.get(),
            'global_recipient': self.email_recipient_var.get().strip() 
        }
        
        # Save key for next time
        self._save_api_key()
        
        threading.Thread(target=self._run_batch, args=(api_key, out_dir, email_config, is_preview)).start()

    def _run_batch(self, api_key, out_dir, email_config, is_preview=False):
        # Use SajuBatchProcessor (The updated class with PDF/Preview support)
        # HTMLBatchProcessor was the legacy class.
        # [NEW] Pass assistant_id to use 명리심리연구소 GPT
        assistant_id = self.assistant_id_var.get()
        if assistant_id:
            self._log_thread(f"✅ Using Assistant: {assistant_id[:20]}...")
        processor = SajuBatchProcessor(api_key, assistant_id=assistant_id, model="gpt-4o")
        
        self._log_thread("=== 배치 분석을 시작합니다 (Premium V2) ===")
        if is_preview:
             self._log_thread("⚠️ [Preview Mode] API 호출 없이 디자인/데이터만 확인합니다.")
        
        for f_path in self.json_files:
            if self.stop_event.is_set(): break
            
            override = self.file_emails.get(f_path, None)
            
            # Pass preview_mode to process_file
            success = processor.process_file(f_path, out_dir, self._log_thread, self.stop_event, email_config=email_config, override_email=override, preview_mode=is_preview)
            if not success and self.stop_event.is_set():
                break

        self._log_thread("=== 모든 작업이 완료되었습니다 ===")
        self.root.after(0, lambda: self.btn_start.config(state="normal"))

    def _stop_process(self):
        self.stop_event.set()
        self._log("중지 요청됨... (현재 진행 중인 작업까지만 완료하고 멈춥니다)")

def main():
    root = tk.Tk()
    app = SajuBatchProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
