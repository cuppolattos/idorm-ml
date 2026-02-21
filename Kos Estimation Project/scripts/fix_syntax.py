import glob

for file in glob.glob('notebooks/*.ipynb'):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = text.replace("',,", "',")
    text = text.replace(", ,", ",")
    text = text.replace(",,", ",")
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)

print('Fixed syntax.')
