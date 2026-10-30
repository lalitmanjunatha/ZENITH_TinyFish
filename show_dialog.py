with open('zenith_gui.py','r',encoding='utf-8') as f:
    c=f.read()
idx = c.find('class ProjectCompanionDialog')
if idx >= 0:
    print(c[idx:idx+3500])
else:
    print('NOT FOUND')
