import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the specific syntax error
# The bad line ends with:
# } 
#         }, 'month': {'gan': [], 'ji': []}, 'day': {'gan': [], 'ji': []}, 'hour': {'gan': [], 'ji': []}}

bad_string = "}, 'month': {'gan': [], 'ji': []}, 'day': {'gan': [], 'ji': []}, 'hour': {'gan': [], 'ji': []}}"

if bad_string in content:
    content = content.replace(bad_string, "}")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied final fix.")
