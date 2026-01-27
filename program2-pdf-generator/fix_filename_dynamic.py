import os

target_file = "../program1-calculator/saju_app.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Current Logic:
# save_path = os.path.join(save_dir, "saju_analysis_result.json")

# New Logic:
new_save_logic = """            # Save to Desktop Folder
            save_dir = "/Users/loyalee/Desktop/명리심리연구소"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Dynamic Filename: saju_result_이름.json
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
            if not safe_name: safe_name = "Unknown"
            filename = f"saju_result_{safe_name}.json"
            
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, "w", encoding="utf-8") as f:"""

# We need to replace the PREVIOUS fix block or whatever is there now.
# The previous fix was:
# save_path = os.path.join(save_dir, "saju_analysis_result.json")
# with open(save_path, "w", encoding="utf-8") as f:

# Let's search for "saju_analysis_result.json" related lines
# And replace the whole block.

# Find the block identifier
block_id = 'save_path = os.path.join(save_dir, "saju_analysis_result.json")'

if block_id in content:
    # We replace from `save_dir = ...` (if present) or just `save_path = ...`
    # Let's replace the chunk we inserted in Step 841.
    
    old_chunk_start = 'save_dir = "/Users/loyalee/Desktop/명리심리연구소"'
    # We'll just find where `save_path` is defined and replace it + the save_dir lines before it if needed.
    
    # Actually, simpler: finding the `save_path = ...` line is enough if we insert `safe_name` logic before it.
    
    start_marker = '            save_dir = "/Users/loyalee/Desktop/명리심리연구소"'
    end_marker = '            with open(save_path, "w", encoding="utf-8") as f:'
    
    # Locate indices
    idx_start = content.find(start_marker)
    idx_end = content.find(end_marker)
    
    if idx_start != -1 and idx_end != -1:
        # Include end line length
        end_len = len(end_marker)
        
        # New block needs to reproduce the `save_dir` lines + new logic
        replacement = new_save_logic
        
        # Replacement
        new_content = content[:idx_start] + replacement + content[idx_end + end_len:]
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Updated filename logic to saju_result_{name}.json.")
    else:
        # Fallback: maybe exact strings don't match due to spaces?
        # Let's replace `save_path = os.path.join(save_dir, "saju_analysis_result.json")`
        old_line = 'save_path = os.path.join(save_dir, "saju_analysis_result.json")'
        if old_line in content:
            new_lines = """            # Dynamic Filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
            if not safe_name: safe_name = "Unknown"
            save_path = os.path.join(save_dir, f"saju_result_{safe_name}.json")"""
            
            content = content.replace(old_line, new_lines)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            print("Updated filename via regex fallback.")
        else:
            print("Could not find save logic.")
else:
    # Try finding the string directly
    print("Could not find block identifier.")

