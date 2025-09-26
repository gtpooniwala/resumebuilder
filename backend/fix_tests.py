#!/usr/bin/env python3
"""
Script to fix all tool invocations in test files
"""
import re

def fix_tool_invocations(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match ResumeEditingTools.method_name(args)
    patterns = [
        # get_resume_section calls
        (r'ResumeEditingTools\.get_resume_section\(([^,]+),\s*"([^"]+)"\)', 
         r'ResumeEditingTools.get_resume_section.invoke({"user_id": \1, "section_name": "\2"})'),
        
        # get_full_profile calls
        (r'ResumeEditingTools\.get_full_profile\(([^)]+)\)', 
         r'ResumeEditingTools.get_full_profile.invoke({"user_id": \1})'),
         
        # update_work_experience calls - these are more complex, need to handle manually
        # edit_professional_summary calls
        (r'ResumeEditingTools\.edit_professional_summary\(([^,]+),\s*([^)]+)\)',
         r'ResumeEditingTools.edit_professional_summary.invoke({"user_id": \1, "new_summary": \2})'),
         
        # manage_skills calls - also complex
        # search_resume_content calls
        (r'ResumeEditingTools\.search_resume_content\(([^,]+),\s*([^)]+)\)',
         r'ResumeEditingTools.search_resume_content.invoke({"user_id": \1, "query": \2})'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed tool invocations in {file_path}")

if __name__ == "__main__":
    fix_tool_invocations("tests/test_resume_tools.py")
