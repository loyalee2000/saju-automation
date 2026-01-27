import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
method_count = 0
method_sig = "def _calculate_pillar_sinsal(self, gan, ji, pillar_type):"

# Logic:
# 1. We want to keep the "Correct" code.
# The code I injected in Step 525 was correct (Amrok Im->In).
# That code was injected at the First Occurrence.
# So the First Occurrence is the one we "Want". 
# But we need to make sure we don't skip it.
# We want to SKIP the Second Occurrence.

# How to identify?
# Iterate lines. count occurrences of sig.
# If count == 1: Keep it.
# If count > 1: Skip until next def?

for i, line in enumerate(lines):
    if method_sig in line:
        method_count += 1
        if method_count > 1:
            skip = True
            # Don't append this line
        else:
            skip = False # Just to be sure
            new_lines.append(line)
    elif skip:
        # We are inside the second duplicate method.
        # Check if we hit the next method (end of block).
        # What is the next method?
        # In snippet it was `def get_gan_ji` or similar?
        # Checking snippet line 379: `def get_gan_ji(self):`
        if "def " in line and line.strip().startswith("def "):
            skip = False
            new_lines.append(line)
        else:
            # Continue skipping
            pass
    else:
        new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Cleaned up duplicates. Found {method_count} occurrences.")
