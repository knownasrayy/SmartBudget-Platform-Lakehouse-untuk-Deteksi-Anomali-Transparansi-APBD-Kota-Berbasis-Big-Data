import os
import re

html_file = 'src/dashboard/index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Create directories
os.makedirs('src/dashboard/assets/css', exist_ok=True)
os.makedirs('src/dashboard/assets/js', exist_ok=True)

# 1. Extract CSS
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    css_content = style_match.group(1).strip()
    with open('src/dashboard/assets/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    # Replace in HTML
    content = content.replace(style_match.group(0), '<link href="assets/css/style.css" rel="stylesheet"/>')

# 2. Extract Tailwind Config
tailwind_match = re.search(r'<script id="tailwind-config">(.*?)</script>', content, re.DOTALL)
if tailwind_match:
    tw_content = tailwind_match.group(1).strip()
    with open('src/dashboard/assets/js/tailwind-config.js', 'w', encoding='utf-8') as f:
        f.write(tw_content)
    # Replace in HTML
    content = content.replace(tailwind_match.group(0), '<script src="assets/js/tailwind-config.js"></script>')

# 3. Extract Main JS (the last script block before </body>)
script_match = re.search(r'<script>(.*?)</script>\n</body>', content, re.DOTALL)
if script_match:
    js_content = script_match.group(1).strip()
    with open('src/dashboard/assets/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    # Replace in HTML
    content = content.replace(script_match.group(0), '<script src="assets/js/main.js"></script>\n</body>')

# Save updated HTML
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactoring complete: CSS and JS extracted to assets/ folder.")
