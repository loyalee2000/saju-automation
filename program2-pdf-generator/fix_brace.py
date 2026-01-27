import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
# We just want to remove the specific duplicate } if it's causing syntax error.
# The previous script might have left the last '}' of the residue block?

# Let's inspect lines around 1265.
# If we have:
#         sinsal = { ... }
#         },   <-- Typo from previous patch
#         }    <-- residue?

for i, line in enumerate(lines):
    # Heuristic: if we see `        },` (8 spaces) and previous line was also `        },` or `        }` or `        sinsal = {...}` closing?
    # Actually, `sinsal = { ... }` (new block) ends with `        }` (8 spaces, no comma if it's the last statement? No, `sinsal` construction is followed by `pillars_list = ...`).
    
    # Let's just remove the line 1265 if it's just `            }` and doesn't match indentation context.
    
    # We will trust `sed` output from step 315.
    # It showed: `        },` (line 1264 approx) then residue.
    
    if i == 1264 and "}" in line: # line numbers might checking 0-indexed vs 1-indexed
         # Just simplistic check: if it looks like the orphan `}` from the error
         pass
         
    new_lines.append(line)

# Actually, doing it blindly by line number is risky if file changed.
# Let's re-read the file with python and look for `sinsal = { ... }` followed by `}`.

content = "".join(lines)
# Remove the double }} issue.
if "        }\n            }\n" in content:
   content = content.replace("        }\n            }\n", "        }\n")

if "        },\n            }\n" in content:
   content = content.replace("        },\n            }\n", "        }\n")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied brace fix.")
