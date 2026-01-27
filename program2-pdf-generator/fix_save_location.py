import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Logic to inject
# Find `with open("saju_analysis_result.json"`
# Replace with directory creation and path join.

old_save_logic = '            with open("saju_analysis_result.json", "w", encoding="utf-8") as f:'

new_save_logic = """            # Save to Desktop Folder
            save_dir = "/Users/loyalee/Desktop/명리심리연구소"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Use name in filename for better organization, or keep standard?
            # User wants "saju_analysis_result.json" usually for the next Program 2 to pick up.
            # But let's save as `saju_analysis_result.json` in that folder.
            save_path = os.path.join(save_dir, "saju_analysis_result.json")
            
            with open(save_path, "w", encoding="utf-8") as f:"""

if old_save_logic in content:
    content = content.replace(old_save_logic, new_save_logic)
    
    # Also need to ensure `import os` is present (it usually is)
    # But just in case, check existing imports.
    # `import os` is at the top of file usually. 
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated save location to Desktop/명리심리연구소.")
else:
    print("Could not find the save logic line.")
