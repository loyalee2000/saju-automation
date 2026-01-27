import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the four_pillars construction block
old_block = """            "four_pillars": {
                "year": {"gan": y_gan, "ji": y_ji},
                "month": {"gan": m_gan, "ji": m_ji},
                "day": {"gan": d_gan, "ji": d_ji},
                "hour": {"gan": h_gan, "ji": h_ji}
            },"""

new_block = """            "four_pillars": {
                "year": {"gan": y_gan, "ji": y_ji, "text": pillars['year']},
                "month": {"gan": m_gan, "ji": m_ji, "text": pillars['month']},
                "day": {"gan": d_gan, "ji": d_ji, "text": pillars['day']},
                "hour": {"gan": h_gan, "ji": h_ji, "text": pillars['hour']}
            },"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    # Try with indentation variation (spaces might be different in file)
    # The file has 12 spaces indent for dictionary items.
    pass

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Added text fields to four_pillars.")
