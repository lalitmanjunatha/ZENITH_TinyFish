import os
os.chdir(r"C:\Users\Lalit Manjunatha\Desktop\ZENITH_V-")
for root, dirs, files in os.walk("autonomous_intelligence"):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            print(path)