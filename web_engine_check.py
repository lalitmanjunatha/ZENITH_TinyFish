import os
os.chdir(r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")
with open("autonomous_intelligence/web_engine.py", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
for i in range(1, min(80, len(lines))):
    line = lines[i-1].encode('ascii', 'ignore').decode('ascii')
    print(f'{i:6d}: {line}', end='')