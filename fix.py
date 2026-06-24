import re

file_path = 'src/dashboard/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update filter options
content = content.replace(
    '<option value="BPK RI Perwakilan Jabar">BPK Perwakilan</option>',
    '<option value="BPK RI Perwakilan Jatim">BPK Perwakilan Jatim</option>'
)

# 2. Add bpk-row class to the three rows
content = re.sub(
    r'<tr class="hover:bg-surface-container-low/30 transition-colors group" data-tahun="(2023|2022)" data-auditor="([^"]+)" data-title="([^"]+)">',
    r'<tr class="hover:bg-surface-container-low/30 transition-colors group bpk-row" data-tahun="\1" data-auditor="\2" data-title="\3">',
    content
)

# 3. Fix Row 1 text and auditor
content = content.replace(
    '<tr class="hover:bg-surface-container-low/30 transition-colors group bpk-row" data-tahun="2023" data-auditor="BPK RI Perwakilan Jabar" data-title="LHP BPK LKPD Prov. Jawa Barat TA 2023">',
    '<tr class="hover:bg-surface-container-low/30 transition-colors group bpk-row" data-tahun="2023" data-auditor="BPK RI Perwakilan Jatim" data-title="LHP BPK LKPD Kota Surabaya TA 2023">'
)
content = content.replace(
    '<h4 class="font-title-md text-on-surface mb-0.5">LHP BPK LKPD Prov. Jawa Barat TA 2023</h4>',
    '<h4 class="font-title-md text-on-surface mb-0.5">LHP BPK LKPD Kota Surabaya TA 2023</h4>'
)
content = content.replace(
    '<td class="p-5 text-on-surface-variant">BPK RI Perwakilan Jabar</td>',
    '<td class="p-5 text-on-surface-variant">BPK RI Perwakilan Jatim</td>'
)

# 4. Bump cache buster
content = re.sub(r'assets/js/main.js(\?v=\d+)?', 'assets/js/main.js?v=6', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
