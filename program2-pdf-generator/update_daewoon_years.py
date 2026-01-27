import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Current get_daewoon implementation pattern to match
old_method_start = "    def get_daewoon(self, year_gan_idx, month_gan_idx, month_ji_idx):"
# We'll replace the whole method.

# New method with Year Calculation
# We need access to birth year. `self.adjusted_dt.year` is reliable.
# In `__init__`, `self.adjusted_dt` is created.

new_method = """    def get_daewoon(self, year_gan_idx, month_gan_idx, month_ji_idx):
        is_year_yang = (year_gan_idx % 2 == 0)
        is_male = (self.gender == 'male')
        is_forward = (is_year_yang == is_male)
        
        start_age = self._calculate_daewoon_num(is_forward)
        
        daewoon_list = []
        curr_gan = month_gan_idx
        curr_ji = month_ji_idx
        
        # Base Year for calculation
        # Assuming daewoon_num is Korean Age (Standard Saju).
        # Korean Age 1 = Birth Year.
        # Start Year = Birth Year + (Start Age - 1)
        base_year = self.adjusted_dt.year
        
        for i in range(10): 
            if is_forward:
                curr_gan = (curr_gan + 1) % 10
                curr_ji = (curr_ji + 1) % 12
            else:
                curr_gan = (curr_gan - 1 + 10) % 10
                curr_ji = (curr_ji - 1 + 12) % 12
            pillar = CHEONGAN[curr_gan] + JIJI[curr_ji]
            
            age = start_age + (i * 10)
            
            # Calculate Gregorian Year
            # If age is Korean Age:
            current_start_year = base_year + (age - 1)
            current_end_year = current_start_year + 9
            
            daewoon_list.append({
                "age": age,
                "ganji": pillar,
                "year": current_start_year,      # Start Year
                "end_year": current_end_year     # End Year
            })
            
        return {"direction": "순행" if is_forward else "역행", "pillars": daewoon_list}
"""

# Replace the method
# Find start index
idx = content.find(old_method_start)
if idx != -1:
    # Find end of method? simpler to regex replace or manual finding next method.
    # Next method usually `analyze_ohaeng`.
    next_method = "    def analyze_ohaeng(self, pillars):"
    end_idx = content.find(next_method)
    
    if end_idx != -1:
        new_content = content[:idx] + new_method + "\n" + content[end_idx:]
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Updated get_daewoon with year calculation.")
    else:
        print("Could not find end of get_daewoon.")
else:
    print("Could not find get_daewoon.")
