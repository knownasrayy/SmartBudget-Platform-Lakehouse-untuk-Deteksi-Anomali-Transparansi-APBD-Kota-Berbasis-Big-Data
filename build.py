import os
import re

base_dir = 'stitch_smartapbd_transparency_dashboard'
output_file = 'src/dashboard/index.html'

tabs = [
    {"id": "dashboard_utama", "icon": "dashboard", "title": "Dashboard Utama", "folder": "smartapbd_dashboard_utama"},
    {"id": "heatmap_anomali", "icon": "bubble_chart", "title": "Heatmap Anomali", "folder": "smartapbd_heatmap_anomali"},
    {"id": "analisis_sentimen", "icon": "psychology", "title": "Analisis Sentimen", "folder": "smartapbd_analisis_sentimen"},
    {"id": "laporan_bpk", "icon": "assessment", "title": "Laporan BPK", "folder": "smartapbd_laporan_bpk"},
    {"id": "detail_anomali", "icon": "search", "title": "Detail Anomali", "folder": "smartapbd_dashboard_detail_anomali"},
    {"id": "peta_spasial", "icon": "map", "title": "Peta Spasial", "folder": "smartapbd_peta_spasial_anomali"},
    {"id": "jejaring_entitas", "icon": "hub", "title": "Jejaring Entitas", "folder": "smartapbd_jejaring_entitas_audit"},
    {"id": "framework", "icon": "account_balance", "title": "Framework", "folder": "institutional_transparency_framework"},
]

def extract_main_content(html):
    # Find <main ...> and extract everything inside it until </main>
    match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if match:
        content = match.group(1)
        # remove any FAB buttons if they exist outside or inside
        return content
    return ""

def extract_head(html):
    match = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
    if match:
        return match.group(1)
    return ""

# Read base HTML from dashboard_utama
with open(os.path.join(base_dir, 'smartapbd_dashboard_utama', 'code.html'), 'r', encoding='utf-8') as f:
    base_html = f.read()

# Build the new sidebar NAV
nav_html = '<nav class="flex flex-col gap-1">\n'
for i, tab in enumerate(tabs):
    active_class = "bg-secondary-container dark:bg-secondary text-on-secondary-container dark:text-on-secondary rounded-lg transition-all translate-x-1"
    inactive_class = "text-on-surface-variant dark:text-on-tertiary-container hover:bg-surface-container-high dark:hover:bg-surface-variant transition-all rounded-lg"
    
    cls = active_class if i == 0 else inactive_class
    icon_cls = "sidebar-active" if i == 0 else ""
    icon_style = "style=\"font-variation-settings: 'FILL' 1;\"" if i == 0 else ""
    
    nav_html += f'''
    <a href="#" onclick="switchTab('{tab['id']}', this)" class="nav-item flex items-center gap-3 px-3 py-2.5 {cls}" data-id="{tab['id']}">
        <span class="material-symbols-outlined {icon_cls} icon-elem" {icon_style}>{tab['icon']}</span>
        <span class="font-label-lg text-label-lg">{tab['title']}</span>
    </a>
    '''
nav_html += '</nav>'

# Replace the existing nav in base_html
base_html = re.sub(r'<nav class="flex flex-col gap-1">.*?</nav>', nav_html, base_html, flags=re.DOTALL)

# Build the main content area
main_content_html = ""
scripts_html = ""

for i, tab in enumerate(tabs):
    file_path = os.path.join(base_dir, tab['folder'], 'code.html')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            inner_main = extract_main_content(content)
            
            # Extract any scripts that might be needed
            script_match = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            for s in script_match:
                if 'tailwind.config' not in s and 'switchTab' not in s:
                    scripts_html += f"/* From {tab['title']} */\n" + s + "\n"

            display = "block" if i == 0 else "none"
            main_content_html += f'<div id="tab-content-{tab["id"]}" class="tab-pane" style="display: {display}; width: 100%; height: 100%;">\n'
            main_content_html += inner_main
            main_content_html += '</div>\n'

# Replace the existing main content in base_html
base_html = re.sub(r'<main([^>]*)>.*?</main>', f'<main\\1>\n{main_content_html}\n</main>', base_html, flags=re.DOTALL)

# Inject our JS
js_code = """
<script>
function switchTab(tabId, element) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(el => {
        el.style.display = 'none';
    });
    // Show selected tab pane
    document.getElementById('tab-content-' + tabId).style.display = 'block';

    // Reset all nav items
    document.querySelectorAll('.nav-item').forEach(el => {
        el.className = "nav-item flex items-center gap-3 px-3 py-2.5 text-on-surface-variant dark:text-on-tertiary-container hover:bg-surface-container-high dark:hover:bg-surface-variant transition-all rounded-lg";
        const icon = el.querySelector('.icon-elem');
        icon.classList.remove('sidebar-active');
        icon.style = "";
    });

    // Set active class to clicked nav item
    element.className = "nav-item flex items-center gap-3 px-3 py-2.5 bg-secondary-container dark:bg-secondary text-on-secondary-container dark:text-on-secondary rounded-lg transition-all translate-x-1";
    const icon = element.querySelector('.icon-elem');
    icon.classList.add('sidebar-active');
    icon.style = "font-variation-settings: 'FILL' 1;";
}

// Any embedded scripts from pages
""" + scripts_html + """
</script>
</body>
"""

base_html = re.sub(r'<script>.*?</script>\n</body>', js_code, base_html, flags=re.DOTALL)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(base_html)

print("Build successful: " + output_file)
