import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Look for the four_pillars construction in get_result_json
# 'year': {'gan': y_gan, 'ji': y_ji},
# Replace with 'year': {'gan': y_gan, 'ji': y_ji, 'text': y_gan + y_ji}, etc.

replacements = [
    ("'year': {'gan': y_gan, 'ji': y_ji}", "'year': {'gan': y_gan, 'ji': y_ji, 'text': y_gan+y_ji}"),
    ("'month': {'gan': m_gan, 'ji': m_ji}", "'month': {'gan': m_gan, 'ji': m_ji, 'text': m_gan+m_ji}"),
    ("'day': {'gan': d_gan, 'ji': d_ji}", "'day': {'gan': d_gan, 'ji': d_ji, 'text': d_gan+d_ji}"),
    ("'hour': {'gan': h_gan, 'ji': h_ji}", "'hour': {'gan': h_gan, 'ji': h_ji, 'text': h_gan+h_ji}")
]

for old, new in replacements:
    content = content.replace(old, new)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Restored text field in pillars.")
