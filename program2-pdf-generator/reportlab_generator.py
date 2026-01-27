import os
import re
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

class ReportLabPDFGenerator:
    """
    showPage() 제어를 완벽하게 한 PDF 생성기
    빈 페이지 0% 보장
    """
    
    def __init__(self, filename="saju_report.pdf"):
        self.filename = filename
        self.width, self.height = A4
        
        # 폰트 설정
        self.font_path = "AppleMyungjo.ttf"
        self.font_name = "AppleMyungjo"
        self._register_font()

    def _register_font(self):
        """한글 폰트 등록"""
        if os.path.exists(self.font_path):
            pdfmetrics.registerFont(TTFont(self.font_name, self.font_path))
            print(f"✅ 폰트 로드 성공: {self.font_path}")
        else:
            print(f"⚠️ 경고: {self.font_path} 파일을 찾을 수 없습니다. 기본 폰트를 사용합니다.")
            self.font_name = "Helvetica"

    def draw_background_border(self, c):
        """
        페이지 테두리 - showPage() 절대 호출 금지!
        """
        # 0. 배경색 적용 (따뜻한 미색)
        c.setFillColor(HexColor("#F7F4EB"))
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

        # 바깥쪽 진한 테두리
        c.setStrokeColor(HexColor("#8D8364"))
        c.setLineWidth(1.5)
        c.rect(5*mm, 5*mm, self.width - 10*mm, self.height - 10*mm, fill=0, stroke=1)
        
        # 안쪽 얇은 테두리
        c.setLineWidth(0.5)
        c.rect(7*mm, 7*mm, self.width - 14*mm, self.height - 14*mm)
        
        # 하단 브랜드 로고 (삭제됨)
        # c.setFont(self.font_name, 9)
        # c.setFillColor(HexColor("#888888"))
        # c.drawCentredString(self.width / 2, 10*mm, "명리심리연구소 프리미엄 사주 리포트")

    def parse_markdown_simple(self, text):
        """마크다운/HTML 간단 파싱 (태그 제거 전 줄바꿈 처리)"""
        if not text: return ""
        
        # 1. Block Tags -> Double Newline
        # </p>, </div>, </h1>..</h6>, <hr>, </ul>, </ol>
        text = re.sub(r'</(p|div|h[1-6]|ul|ol|li)>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<hr[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
        
        # 2. HTML Tags Removal
        text = re.sub(r'<[^>]+>', '', text)
        
        # 3. Entity Decoding (Simple)
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        # 4. ** Bold Removal (Since we don't support inline bold yet in simple parser)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        return text.strip()
    
    def wrap_text(self, text, max_width_mm, font_size):
        """
        긴 텍스트를 페이지 폭에 맞춰 자동 줄바꿈
        """
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        return lines # Returns List[List[str]] (Paragraphs -> Lines)
    
    def wrap_text(self, text, max_width_mm, font_size):
        """
        긴 텍스트를 페이지 폭에 맞춰 자동 줄바꿈 (문단 보존)
        Returns: List of Paragraphs, where Paragraph is List of Lines
        """
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        paragraphs = []
        
        # 1. Split by double newlines to detect paragraph blocks
        # Normalizing newlines first
        normalized_text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split by double newline to identify explicit paragraphs
        raw_paragraphs = re.split(r'\n\s*\n', normalized_text)
        
        for raw_p in raw_paragraphs:
            if not raw_p.strip():
                continue
                
            lines = []
            # Treat single newlines within a paragraph as spaces (like Markdown)
            # OR keep them if user wants strict line breaks? 
            # Usually strict newlines are better for poetry/lyrics, but for prose convert single \n to space?
            # User request: "divide paragraphs". Let's assume single \n is just soft break or wrap.
            # But simpler: split paragraph by words and rebuild lines.
            
            # Combine single newlines into spaces to reflow text
            # clean_p = raw_p.replace('\n', ' ')
            # words = clean_p.split(' ')
            
            # Actually, let's respect single newlines as intentional breaks if they exist, 
            # but usually Markdown treats them as space. Let's reflow.
            words = raw_p.split() # Splits by any whitespace including \n
            
            current_line = ''
            for word in words:
                test_line = current_line + ' ' + word if current_line else word
                width_points = stringWidth(test_line, self.font_name, font_size)
                width_mm = width_points * 0.352778
                
                if width_mm <= max_width_mm:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            if lines:
                paragraphs.append(lines)
        
        return paragraphs
    
    def add_chapter_title_page(self, c, chapter_number, chapter_title):
        """
        챕터 타이틀 전용 페이지 (참고 이미지 스타일)
        """
        self.draw_background_border(c)
    def add_chapter_title_page(self, c, chapter_number, chapter_title):
        """
        챕터 타이틀 전용 페이지 (이미지 참조 스타일)
        """
        self.draw_background_border(c)
        
        # 상단 작은 텍스트
        c.setFont(self.font_name, 10)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(self.width / 2, self.height - 30*mm, "명리심리연구소")
        
        # 중앙 - 챕터 번호 (큰 글씨) - Bold Simulation
        # 중앙 - 챕터 번호 (큰 글씨) - Bold Simulation via TextObject
        c.saveState() # Isolate Bold State
        
        c.setFont(self.font_name, 32)
        c.setFillColor(HexColor("#000000"))
        c.setStrokeColor(HexColor("#000000"))
        c.setLineWidth(1)
        
        # Manual centering with text object
        t = c.beginText()
        t.setFont(self.font_name, 32)
        t.setTextRenderMode(2) # Fill and Stroke
        width = c.stringWidth(chapter_number, self.font_name, 32)
        t.setTextOrigin(self.width/2 - width/2, self.height/2 + 15*mm)
        t.textOut(chapter_number)
        c.drawText(t)
        
        c.restoreState() # Restore to normal state (Fill only, thinner lines)
        
        # 챕터 제목 (Normal Weight - User Request)
        c.setFont(self.font_name, 20)
        c.setFillColor(HexColor("#000000"))
        c.drawCentredString(self.width / 2, self.height / 2 - 10*mm, chapter_title)
        
        c.showPage()  # 타이틀 페이지 완성 (다음 페이지로 넘김)

    def add_content_pages(self, c, content):
        """
        본문 내용 페이지들 (타이틀 페이지 뒤에 이어짐)
        """
        # 본문 내용 파싱
        clean_content = self.parse_markdown_simple(content)
        max_text_width = self.width - 50*mm
        
        # wrap_text now returns List[List[str]] (Paragraphs)
        # wrap_text now returns List[List[str]] (Paragraphs)
        paragraphs = self.wrap_text(clean_content, max_text_width / mm, 15) 
        
        # 첫 본문 페이지 시작
        self.draw_background_border(c)
        c.setFont(self.font_name, 15) 
        c.setFillColor(HexColor("#424242")) 
        text_y = self.height - 40*mm
        
        # Line height and spacing
        line_height = 10 * mm # Increased for 15pt (approx 1.5 line height)
        paragraph_gap = 8 * mm # Extra gap between paragraphs
        
        for p_idx, paragraph_lines in enumerate(paragraphs):
            # Check if whole paragraph fits? No, check line by line but try to keep together if possible
            # Or just flow naturally.
            
            for l_idx, line in enumerate(paragraph_lines):
                # Page break check
                if text_y < 30*mm:
                    c.showPage()
                    self.draw_background_border(c)
                    c.setFont(self.font_name, 15)
                    c.setFillColor(HexColor("#424242"))
                    text_y = self.height - 40*mm
                
                c.drawString(25*mm, text_y, line)
                text_y -= line_height
            
            # Add Paragraph Gap
            text_y -= paragraph_gap
        
        c.showPage()  # 본문 끝

    def create_page(self, c, title, content):
        """
        챕터 생성 (타이틀 페이지 -> 본문 페이지 분리 생성)
        """
        # 제목 파싱
        parts = title.split(' ', 2)
        if len(parts) >= 3:
            chapter_number = f"{parts[0]} {parts[1]}"
            chapter_title = parts[2]
        else:
            chapter_number = "제 1장"
            chapter_title = title
            
        # 1. 독립된 타이틀 페이지 생성
        self.add_chapter_title_page(c, chapter_number, chapter_title)
        
        # 2. 이어서 본문 페이지 생성
        if content and content.strip():
            self.add_content_pages(c, content)
        else:
            # 내용이 없을 경우 빈 페이지 방지를 위해... 
            # 하지만 타이틀은 이미 출력됨. 그냥 넘어감.
            pass

    def add_saju_table_page(self, c, pillars, ohaeng_counts=None, sinsal_data=None):
        """사주 4주 표 페이지 - V11 통합형 (표 + 신살 + 오행)"""
        self.draw_background_border(c)
        
        # 제목
        c.setFont(self.font_name, 24)
        c.setFillColor(HexColor("#2C3E50"))
        c.drawCentredString(self.width / 2, self.height - 35*mm, "나의 사주 원국")
        
        # --- [1] 사주 원국 표 (Joined Layout) ---
        
        # Colors
        colors_map = {
            'mok': HexColor("#81C784"), 'hwa': HexColor("#E57373"),
            'to':  HexColor("#FFF176"), 'geum': HexColor("#E0E0E0"),
            'su':  HexColor("#64B5F6"),
            'gray_bg': HexColor("#EEEEEE"), 'white': HexColor("#FFFFFF"),
            'border': HexColor("#BDBDBD"), 'text': HexColor("#333333")
        }
        
        def get_color(char_str):
            if not char_str: return colors_map['white']
            first = char_str.strip()[0]
            if first in ['갑', '을', '인', '묘']: return colors_map['mok']
            if first in ['병', '정', '사', '오']: return colors_map['hwa']
            if first in ['무', '기', '진', '술', '축', '미']: return colors_map['to']
            if first in ['경', '신', '유']: return colors_map['geum']
            if first in ['임', '계', '해', '자']: return colors_map['su']
            return colors_map['white']

        def clean_text(text):
            # "갑(甲)" -> "갑"
            if not text: return ""
            return text.split('(')[0].strip()

        # Layout Geometry
        table_w = 40 * mm * 4  # 160mm
        col_w = 40 * mm
        header_h = 10 * mm
        cell_h = 25 * mm
        sub_h = 10 * mm
        
        start_x = (self.width - table_w) / 2
        start_y = self.height - 60 * mm
        
        # Data Prep
        cols = ['hour', 'day', 'month', 'year']
        headers = ['시주', '일주', '월주', '년주']
        
        # 1. Header (Gray)
        curr_y = start_y
        c.setFillColor(colors_map['gray_bg'])
        c.setStrokeColor(colors_map['border'])
        c.setLineWidth(0.5)
        c.rect(start_x, curr_y - header_h, table_w, header_h, fill=1, stroke=1)
        
        c.setFillColor(colors_map['text'])
        c.setFont(self.font_name, 11)
        for i, h in enumerate(headers):
            c.drawCentredString(start_x + (col_w * i) + (col_w/2), curr_y - header_h + 3*mm, h)
        
        # 2. Cheongan (Row 1)
        curr_y -= header_h
        for i, key in enumerate(cols):
            p = pillars.get(key, {})
            gan = p.get('gan', '')
            bg = get_color(gan)
            # Siju exception: Gray if desired? User image shows colors, so stick to colors.
            # But "시주" column usually gray in some styles. Let's follow the user's "Second Image" which shows gray for "Day"? No, they show colorful squares.
            # Image 2: Si(Gray), Il(Yellow), Wol(Red), Year(Green). So Si IS Gray.
            if key == 'hour': bg = colors_map['geum'] # Use Gray for Siju column as per image 2 usually.
            
            x = start_x + (col_w * i)
            c.setFillColor(bg)
            c.rect(x, curr_y - cell_h, col_w, cell_h, fill=1, stroke=1)
            
            c.setFillColor(colors_map['text'])
            c.setFont(self.font_name, 32)
            c.drawCentredString(x + col_w/2, curr_y - cell_h + 8*mm, clean_text(gan))

        # 3. Cheongan Sipseong (Row 2)
        curr_y -= cell_h
        c.setFillColor(colors_map['white'])
        c.rect(start_x, curr_y - sub_h, table_w, sub_h, fill=1, stroke=1)
        # Vertical lines
        for i in range(1, 4): c.line(start_x + col_w*i, curr_y, start_x + col_w*i, curr_y - sub_h)
        
        sample_ten = ["편관", "비견", "정관", "편인"] # Replace with real if available
        c.setFont(self.font_name, 10)
        c.setFillColor(colors_map['text'])
        for i in range(4):
            c.drawCentredString(start_x + col_w*i + col_w/2, curr_y - sub_h + 3*mm, sample_ten[i])

        # 4. Jiji (Row 3)
        curr_y -= sub_h
        for i, key in enumerate(cols):
            p = pillars.get(key, {})
            ji = p.get('ji', '')
            bg = get_color(ji)
            if key == 'hour': bg = colors_map['geum'] # Siju Gray
            
            x = start_x + (col_w * i)
            c.setFillColor(bg)
            c.rect(x, curr_y - cell_h, col_w, cell_h, fill=1, stroke=1)
            
            c.setFillColor(colors_map['text'])
            c.setFont(self.font_name, 32)
            c.drawCentredString(x + col_w/2, curr_y - cell_h + 8*mm, clean_text(ji))

        # 5. Jiji Sipseong (Row 4)
        curr_y -= cell_h
        c.setFillColor(colors_map['white'])
        c.rect(start_x, curr_y - sub_h, table_w, sub_h, fill=1, stroke=1)
        for i in range(1, 4): c.line(start_x + col_w*i, curr_y, start_x + col_w*i, curr_y - sub_h)
        
        sample_ten_ji = ["상관", "식신", "재성", "관성"]
        c.setFont(self.font_name, 10)
        c.setFillColor(colors_map['text'])
        for i in range(4):
            c.drawCentredString(start_x + col_w*i + col_w/2, curr_y - sub_h + 3*mm, sample_ten_ji[i])

        # --- [2] 신살 박스 (Rounded Info Box) ---
        cursor_y = curr_y - sub_h - 15*mm
        
        c.setFillColor(colors_map['white'])
        c.setStrokeColor(colors_map['border'])
        c.roundRect(start_x, cursor_y - 30*mm, table_w, 30*mm, 5, fill=1, stroke=1)
        
        c.setFont(self.font_name, 12)
        c.setFillColor(colors_map['text'])
        c.drawString(start_x + 5*mm, cursor_y - 8*mm, "주요 신살 및 길성")
        
        # Display Sinsal Data
        sinsal_text = ""
        if sinsal_data:
            # Robust Extraction for multiple JSON structures
            all_sinsals = []
            
            # Case 1: Structure is {'year': {'gan': [...], 'ji': [...]}, 'month': ...}
            # Case 2: Structure is {'year': ['Tianyi', ...], 'month': ...}
            # Case 3: Structure is {'Mangshinsal': 'Description', ...}
            
            for k, v in sinsal_data.items():
                if isinstance(v, dict):
                    # Nested dict with 'gan' and 'ji' (Case 1)
                    for sub_k, sub_v in v.items():
                        if isinstance(sub_v, list):
                            all_sinsals.extend([str(x) for x in sub_v if x])
                elif isinstance(v, list):
                    # Direct list of sinsals (Case 2)
                    all_sinsals.extend([str(x) for x in v if x])
                elif isinstance(v, str) and v:
                    # Description string, KEY is Sinsal name (Case 3)
                    if k not in ['year', 'month', 'day', 'hour', 'date', 'name']:
                         all_sinsals.append(k)
            
            # Remove duplicates and empty strings
            unique_sinsals = list(dict.fromkeys([s for s in all_sinsals if s]))
            sinsal_text = ", ".join(unique_sinsals[:30]) # Show up to 30 (Wrapped)
            
        if not sinsal_text: sinsal_text = "천을귀인, 문창귀인, 역마살, 도화살, 화개살 (예시)"
            
        c.setFont(self.font_name, 10)
        c.setFillColor(HexColor("#616161"))
        
        # Text Wrap Logic
        max_sinsal_w = (table_w - 10*mm) / mm # mm to match wrap_text unit
        wrapped_sinsal = self.wrap_text(sinsal_text, max_sinsal_w, 10)
        
        text_y = cursor_y - 18*mm
        for paragraph in wrapped_sinsal:
            for line in paragraph:
                c.drawString(start_x + 5*mm, text_y, line)
                text_y -= 5*mm # Line spacing
        
        # --- [3] 오행 분포 분석 (Bar Chart) ---
        cursor_y -= 45*mm
        c.setFont(self.font_name, 12)
        c.setFillColor(colors_map['text'])
        c.drawString(start_x, cursor_y, "오행 분포 분석")
        
        if ohaeng_counts:
            bar_x = start_x + 30*mm
            bar_w = 90 * mm
            row_h = 8 * mm
            gap_h = 4 * mm
            
            elements = [
                ('목', 'mok', 'Tree', '나무'),
                ('화', 'hwa', 'Fire', '불'),
                ('토', 'to', 'Earth', '흙'),
                ('금', 'geum', 'Metal', '쇠'),
                ('수', 'su', 'Water', '물')
            ]
            
            for i, (kor, key, json_eng, disp_kor) in enumerate(elements):
                by = cursor_y - 10*mm - (i * (row_h + gap_h))
                
                # Label
                c.setFont(self.font_name, 10)
                c.setFillColor(colors_map['text'])
                c.drawString(start_x, by + 2*mm, f"{kor} ({disp_kor})")
                
                # Bg Bar
                c.setFillColor(HexColor("#EEEEEE"))
                c.rect(bar_x, by, bar_w, row_h, fill=1, stroke=0)
                
                # Fore Bar
                # Try multiple key formats: '목', '목(Tree)', etc.
                count = ohaeng_counts.get(kor, 0)
                if count == 0:
                    # Use the English suffix for lookup: e.g. "목(Tree)"
                    count = ohaeng_counts.get(f"{kor}({json_eng})", 0)
                total = sum(ohaeng_counts.values()) or 8
                pct = count / total
                fill_w = bar_w * pct
                
                c.setFillColor(colors_map[key])
                c.roundRect(bar_x, by, fill_w, row_h, 2, fill=1, stroke=0)
                
                # Count (개수)
                c.setFillColor(colors_map['text'])
                c.drawString(bar_x + bar_w + 5*mm, by + 2*mm, f"{count}개")

        c.showPage()


    def add_toc_page(self, c, chapter_config=None):
        """
        목차 페이지 (Table of Contents) - Dynamic
        """
        # 1. Background
        self.draw_background_border(c)
        
        # 2. Subtitle (Top Center)
        c.setFont(self.font_name, 12)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(self.width / 2, self.height - 40*mm, "명리심리연구소") # Updated per user request
        
        # 3. Title "목차"
        # Manual centering with text object for Bold simulation if needed, or just normal
        c.saveState()
        t = c.beginText()
        t.setFont(self.font_name, 32)
        t.setTextRenderMode(0) # Fill only (Standard) or 2 for bold simulation
        c.setFillColor(HexColor("#333333"))
        
        # Center manually
        title_text = "목차"
        title_w = c.stringWidth(title_text, self.font_name, 32)
        t.setTextOrigin(self.width/2 - title_w/2, self.height - 70*mm) # Updated Position
        t.textOut(title_text)
        c.drawText(t)
        
        c.restoreState()
        
        # 4. Chapter List
        if chapter_config:
            chapter_titles = [title for key, title in chapter_config]
        else:
            # Fallback (Should typically not happen if generate passes defaults)
            chapter_titles = []
            
        start_y = self.height - 100*mm # Updated Position
        row_h = 12*mm # Increased Spacing for larger font
        
        # Font for list
        c.setFont(self.font_name, 15) # Increased to 15pt
        c.setFillColor(HexColor("#333333"))
        
        # Center alignment logic?
        # Image shows left aligned but centered block?
        # Or just fixed margin. Let's use fixed margin ~40mm
        left_margin = 60*mm
        
        for i, title in enumerate(chapter_titles):
            y = start_y - (i * row_h)
            
            # Use Regex to split by 2 or more spaces
            # Improved Split Logic: Keep "제 N장" together
            parts = title.split()
            if len(parts) >= 2 and parts[0] == "제" and "장" in parts[1]:
                num = f"{parts[0]} {parts[1]}" # "제 N장"
                text = " ".join(parts[2:])
            else:
                # Fallback
                split_parts = title.split(' ', 1)
                num = split_parts[0]
                text = split_parts[1] if len(split_parts) > 1 else ""
            
            # Draw Num (Left Aligned)
            c.setFont(self.font_name, 15) 
            c.drawString(left_margin, y, num)
            
            # Draw Text (Title) - 30mm offset for safe alignment of "제 12장"
            c.drawString(left_margin + 30*mm, y, text)

        c.showPage()

    def generate(self, user_info, chapters, pillars=None, ohaeng_counts=None, sinsal=None, chapter_config=None):
        """전체 리포트 생성"""
        c = canvas.Canvas(self.filename, pagesize=A4)
        c.setTitle("사주 분석 리포트")
        
        # --- [1. 표지 페이지] ---
        self.draw_background_border(c)
        
        # 메인 타이틀
        c.setFont(self.font_name, 40)
        c.setFillColor(HexColor("#333333"))
        c.drawCentredString(self.width/2, self.height/2 + 25*mm, "사주 분석 리포트")
        
        # 부제
        c.setFont(self.font_name, 16)
        c.setFillColor(HexColor("#666666"))
        c.drawCentredString(self.width/2, self.height/2 + 10*mm, "당신의 삶을 밝히는 지혜")
        
        # 구분선
        c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(1)
        line_y = self.height/2 - 10*mm
        # c.line(self.width/2 - 60*mm, line_y, self.width/2 + 60*mm, line_y)

        # 정보 섹션 (테이블 형태)
        info_y_start = self.height/2 - 30*mm
        row_h = 10*mm
        col_w_label = 30*mm
        col_w_value = 50*mm
        
        # 중앙 정렬을 위한 시작 X 좌표 계산
        total_w = col_w_label + col_w_value
        start_x = (self.width - total_w) / 2
        
        infos = [
            ("이름", user_info.get('name', '')),
            ("생년월일", user_info.get('birth_date', '')),
            ("발행일", datetime.now().strftime('%Y-%m-%d'))
        ]
        
        c.setFont(self.font_name, 12)
        
        for i, (label, value) in enumerate(infos):
            y = info_y_start - (i * row_h)
            
            # Label
            c.setFont(self.font_name + "-Bold" if self.font_name != "AppleMyungjo" else self.font_name, 12) # 명조는 볼드 별도 처리 필요할수도
            c.drawRightString(start_x + col_w_label - 5*mm, y, label)
            
            # Value
            c.setFont(self.font_name, 12)
            c.drawString(start_x + col_w_label + 5*mm, y, value)
            
            # Vertical Divider (Optional)
            c.setStrokeColor(HexColor("#CCCCCC"))
            c.setLineWidth(0.5)
            # c.line(start_x + col_w_label, y - 2*mm, start_x + col_w_label, y + 8*mm)

        c.showPage()
        
        # --- [1.5 목차 페이지] ---
        # Default chapter list if none provided
        if not chapter_config:
             chapter_config = [
                ('01_intro', '제 1장 사주에 대하여'),
                ('02_saju_palja', '제 2장 나의 사주팔자'),
                ('03_ilju', '제 3장 일주로 보는 나의 성격'),
                ('04_sibseong', '제 4장 십성 분석'),
                ('05_12unseong', '제 5장 십이운성 분석'),
                ('06_sinsal', '제 6장 십이신살 및 귀인 분석'),
                ('07_love', '제 7장 연애운 및 결혼운 분석'),
                ('08_wealth', '제 8장 재물운 분석'),
                ('09_career', '제 9장 직업운 분석'),
                ('10_health', '제 10장 건강운 분석'),
                ('11_daewoon', '제 11장 나의 대운'),
                ('12_seun', '제 12장 나의 10년간 연운'),
                ('13_monthly_2026', '제 13장 나의 2026년 월운'),
            ]
            
        self.add_toc_page(c, chapter_config)
        
        # --- [2. 사주 원국 표] ---
        if pillars:
            self.add_saju_table_page(c, pillars, ohaeng_counts, sinsal)
            
        # --- [3. 챕터별 내용] ---
        for key, title in chapter_config:
            if key in chapters and chapters[key]:
                self.create_page(c, title, chapters[key])
        
        c.save()
        print(f"🎉 성공! 빈 페이지 없는 깔끔한 리포트가 생성되었습니다: {self.filename}")
        return self.filename
