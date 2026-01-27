import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

# We see a closing brace `        },` followed by `'month': { ...`.
# This indicates the `sinsal = { ... }` block wasn't cleanly replaced with `sinsal = { ... }`.
# Or duplicate blocks exist.

# The good block ends with:
#                 'hour': h_sinsal
#         },

# The bad block (residue) starts with:
#                 'month': {

# We should look for the line `        },` followed by lines that look like a continuation of a dictionary that shouldn't be there.
# OR, we just remove the residue lines.

# Strategy:
# 1. Keep the first `sinsal = { ... }` block (which is the new one using variables).
# 2. When we see the closing `        }` (or `        },` if inside something else?), we stop.
# 3. But here it seems we have `        },` then garbage.

for i, line in enumerate(lines):
    # Detect the residue
    if "'month': {" in line and i > 0 and "},".strip() in lines[i-1].strip():
        # This is likely the start of the residue
        skip = True
        
    if skip:
        # We skip until we see the end of the corrupted block.
        # It ends with `} ` or `}`.
        if line.strip() == "}":
            skip = False
            continue # and skip this closing brace logic
            
        # The residue seemingly ends at `                } ` then `            }`.
        continue

    new_lines.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed residue sinsal block.")
