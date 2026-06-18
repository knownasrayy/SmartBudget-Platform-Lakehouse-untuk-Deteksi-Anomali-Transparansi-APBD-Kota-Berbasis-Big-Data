import re
with open('src/dashboard/index.html', 'r', encoding='utf-8') as f:
    text = f.read()
print(re.findall(r'id=[\'"]([^\'"]*map[^\'"]*)[\'"]', text))
