import json

path = 'notebooks/jakarta_utara2.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# remove 'is_internet' from wherever it is in binary_cols
text = text.replace("'is_internet', ", "")
text = text.replace(", 'is_internet'", "")
text = text.replace("'is_internet'", "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Fixed jakarta_utara2.ipynb")
