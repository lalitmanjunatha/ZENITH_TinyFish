import os
os.chdir(r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")

# Read director.py
with open("autonomous_intelligence/director.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Add import for search_web
# Find the import section - after "from .permissions"
import_section_end = content.find("from .permissions")
if import_section_end >= 0:
    # Add new import after the permissions import
    new_import = "\nfrom Tools.web_search import search_web\n"
    # Find the newline after "from .permissions"
    lines = content.split('\n')
    # Find the line with "from .permissions"
    for i, line in enumerate(lines):
        if 'from .permissions' in line:
            # Insert after this line
            lines.insert(i+1, new_import)
            break
    content = '\n'.join(lines)
    print("Added import for search_web")
else:
    print("Could not find import section")

# Replace the _execute_task method's web.search call
old_call = "results = self.web.search(query)"
new_call = "results = search_web(query)"

if old_call in content:
    content = content.replace(old_call, new_call)
    print("Replaced web.search call with search_web")
else:
    print(f"Could not find '{old_call}' in director.py - trying alternative")
    # Try alternative pattern
    if 'self.web.search' in content:
        print("Found self.web.search in director.py")

# Write the modified file
with open("autonomous_intelligence/director.py", "w", encoding="utf-8", errors="ignore") as f:
    f.write(content)

print("Modified director.py")