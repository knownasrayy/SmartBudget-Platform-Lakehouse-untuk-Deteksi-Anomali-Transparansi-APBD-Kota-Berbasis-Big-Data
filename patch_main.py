import re

with open('src/dashboard/assets/js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update onEachFeature inside renderHeatmapLayer
new_onEachFeature = """            onEachFeature: function(feature, layer) {
                const kecName = feature.properties.KECAMATAN;
                const k = filteredData.find(x => x.nama.toUpperCase() === kecName.toUpperCase());
                if (k) {
                    const isHigh = k.skor >= 0.75;
                    const isMed = k.skor >= 0.5;
                    const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
                    const label = isHigh ? 'KRITIS' : isMed ? 'WASPADA' : 'AMAN';
                    layer.bindTooltip(`<b>${k.nama}</b><br>Skor: ${(k.skor*100).toFixed(0)}%`);
                    layer.on('click', () => window.openDrillDown(k));
                }
            }"""
content = re.sub(
    r'onEachFeature: function\(feature, layer\) \{.*?\layer\.bindPopup\(.*?\).*?\}',
    new_onEachFeature,
    content,
    flags=re.DOTALL
)

# 2. Update L.marker in renderHeatmapLayer
content = re.sub(
    r'\}\)\.bindPopup\(.*?`\)\.addTo\(window\.heatmapMarkersLayer\);',
    r"}).on('click', () => window.openDrillDown(k)).addTo(window.heatmapMarkersLayer);",
    content,
    flags=re.DOTALL
)

# 3. Add window.generateSmartInsight into window.renderHeatmapLayer at the end
content = re.sub(
    r'(    if \(window\.renderHeatmapGrid\) \{\n        window\.renderHeatmapGrid\(filteredData\);\n    \})',
    r'\1\n    if (window.generateSmartInsight) window.generateSmartInsight(filteredData);',
    content
)

# 4. Append new functions at the end of the file
new_funcs = """

// --- ADVANCED HEATMAP FEATURES ---

window.exportHeatmapCSV = function() {
    let filteredData = KECAMATAN_ANOMALI.filter(k => {
        const level = k.skor >= 0.75 ? 'High' : k.skor >= 0.5 ? 'Medium' : 'Low';
        const levelMatch = window.heatmapLevelFilters.includes(level);
        const catMatch = k.kategori && k.kategori.some(cat => window.heatmapKategoriFilters.includes(cat));
        return levelMatch && catMatch;
    });
    
    let csvContent = "data:text/csv;charset=utf-8,Kecamatan,Skor Anomali,Status,Kategori Belanja\\n";
    filteredData.forEach(k => {
        const status = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
        const cats = k.kategori ? k.kategori.join(' & ') : '-';
        csvContent += `${k.nama},${(k.skor*100).toFixed(1)}%,${status},${cats}\\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "laporan_anomali_apbd_surabaya.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show toast
    const toast = document.getElementById('toast-notification');
    const msg = document.getElementById('toast-message');
    if(toast && msg) {
        msg.innerText = "Data CSV berhasil diunduh!";
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
    }
};

window.printDashboard = function() {
    window.print();
};

window.generateSmartInsight = function(filteredData) {
    const banner = document.getElementById('smart-insight-banner');
    const textEl = document.getElementById('smart-insight-text');
    if (!banner || !textEl) return;
    
    if (filteredData.length === 0) {
        textEl.innerText = "Tidak ada anomali yang terdeteksi pada filter saat ini.";
        return;
    }
    
    const kritisCount = filteredData.filter(k => k.skor >= 0.75).length;
    if (kritisCount > 0) {
        textEl.innerText = `⚠️ Terdapat ${kritisCount} kecamatan dengan anomali tingkat KRITIS. Area ini membutuhkan audit investigatif segera, khususnya pada pos belanja ${window.heatmapKategoriFilters.join(' dan ')}.`;
        banner.className = "bg-error/10 border-b border-error/20 px-6 py-3 flex items-start gap-3 transition-all";
        banner.querySelector('h4').className = "font-label-lg text-label-lg font-bold text-error mb-0.5";
        banner.querySelector('span').className = "material-symbols-outlined text-error mt-0.5";
    } else if (filteredData.length > 0) {
        textEl.innerText = `💡 Terdapat ${filteredData.length} kecamatan dalam pantauan. Terus monitor pos belanja ${window.heatmapKategoriFilters.join(' dan ')} untuk mencegah pembengkakan anggaran.`;
        banner.className = "bg-primary/10 border-b border-primary/20 px-6 py-3 flex items-start gap-3 transition-all";
        banner.querySelector('h4').className = "font-label-lg text-label-lg font-bold text-primary mb-0.5";
        banner.querySelector('span').className = "material-symbols-outlined text-primary mt-0.5";
    }
};

// Simulate time shift
window.originalKecamatanData = null;
window.updateTimeSimulation = function(month) {
    if (!window.originalKecamatanData) {
        window.originalKecamatanData = JSON.parse(JSON.stringify(KECAMATAN_ANOMALI));
    }
    
    document.getElementById('time-slider-label').innerText = `Bulan: ${month}`;
    
    const ratio = parseInt(month) / 12.0;
    
    KECAMATAN_ANOMALI.forEach((k, i) => {
        const orig = window.originalKecamatanData[i];
        // Simulate exponential growth of anomaly towards the end of the year
        const multiplier = ratio < 0.5 ? (ratio * 1.5) : (ratio * 1.5 + Math.pow(ratio, 3)*0.5);
        k.skor = Math.min(1.0, orig.skor * multiplier);
    });
    
    window.renderHeatmapLayer();
    if(window.renderTop5Anomali) window.renderTop5Anomali();
};

window.openDrillDown = function(k) {
    const panel = document.getElementById('drill-down-panel');
    if (!panel) return;
    
    document.getElementById('dd-kecamatan-name').innerText = k.nama;
    
    const isHigh = k.skor >= 0.75;
    const isMed = k.skor >= 0.5;
    const colorClass = isHigh ? 'text-error' : isMed ? 'text-amber-600' : 'text-green-600';
    const bgClass = isHigh ? 'bg-error' : isMed ? 'bg-amber-500' : 'bg-green-500';
    const status = isHigh ? 'KRITIS' : isMed ? 'WASPADA' : 'AMAN';
    
    const statusEl = document.getElementById('dd-kecamatan-status');
    statusEl.innerText = `Status: ${status}`;
    statusEl.className = `font-label-sm text-label-sm mt-1 font-bold ${colorClass}`;
    
    const valEl = document.getElementById('dd-skor-value');
    valEl.innerText = `${(k.skor*100).toFixed(1)}%`;
    valEl.className = `font-title-lg ${colorClass}`;
    
    document.getElementById('dd-skor-bar').style.width = `${k.skor*100}%`;
    document.getElementById('dd-skor-bar').className = `h-full rounded-full ${bgClass}`;
    
    const recEl = document.getElementById('dd-recommendation');
    if(isHigh) {
        recEl.innerText = `Lakukan audit investigatif segera pada pos belanja ${k.kategori.join(', ')}. Panggil PPK terkait untuk klarifikasi selisih anggaran sebesar Rp ${(Math.random()*500+200).toFixed(0)} Juta.`;
    } else if(isMed) {
        recEl.innerText = `Pantau ketat realisasi anggaran ${k.kategori.join(', ')} bulan depan. Mulai muncul deviasi harga satuan yang tidak wajar.`;
    } else {
        recEl.innerText = `Penggunaan anggaran normal. Lanjutkan pemantauan rutin.`;
    }
    
    // Vendor List Simulation
    const vendors = [
        ['CV. Karya Mandiri', 'Rp 450 Jt'],
        ['PT. Sinar Jaya Abadi', 'Rp 320 Jt'],
        ['CV. Makmur Sentosa', 'Rp 210 Jt'],
        ['PT. Global Solusi', 'Rp 150 Jt']
    ];
    let vHtml = '';
    for(let i=0; i < (isHigh ? 3 : isMed ? 2 : 1); i++) {
        vHtml += `
        <div class="flex items-center justify-between p-3 bg-surface border border-outline-variant rounded-lg">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant">
                    <span class="material-symbols-outlined text-[16px]">storefront</span>
                </div>
                <div>
                    <p class="font-label-md text-label-md text-on-surface">${vendors[i][0]}</p>
                    <p class="font-body-sm text-[11px] text-on-surface-variant">Indikasi Mark-up Harga</p>
                </div>
            </div>
            <span class="font-bold text-error">${vendors[i][1]}</span>
        </div>`;
    }
    document.getElementById('dd-vendor-list').innerHTML = vHtml;
    
    panel.classList.remove('translate-x-full');
};

window.closeDrillDown = function() {
    const panel = document.getElementById('drill-down-panel');
    if (panel) {
        panel.classList.add('translate-x-full');
    }
};

"""
content += new_funcs

with open('src/dashboard/assets/js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched main.js")
