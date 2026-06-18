// ---- SURABAYA KECAMATAN HEATMAP DATA (real coordinates) ----
// [lat, lng, intensity] — intensity based on anomaly score weighting
const SURABAYA_CENTER = [-7.2575, 112.7521];
const KECAMATAN_ANOMALI = [
    // Nama, lat, lng, skor (0-1 = rendah, 1+ = tinggi)
    { nama: 'Wonokromo',    lat: -7.3102, lng: 112.7350, skor: 0.95 },
    { nama: 'Tegalsari',    lat: -7.2720, lng: 112.7338, skor: 0.88 },
    { nama: 'Genteng',      lat: -7.2600, lng: 112.7450, skor: 0.62 },
    { nama: 'Bubutan',      lat: -7.2438, lng: 112.7306, skor: 0.55 },
    { nama: 'Simokerto',    lat: -7.2352, lng: 112.7456, skor: 0.70 },
    { nama: 'Pabean Cantian',lat:-7.2232, lng: 112.7374, skor: 0.45 },
    { nama: 'Semampir',     lat: -7.2222, lng: 112.7550, skor: 0.60 },
    { nama: 'Krembangan',   lat: -7.2300, lng: 112.7250, skor: 0.40 },
    { nama: 'Gubeng',       lat: -7.2653, lng: 112.7590, skor: 0.78 },
    { nama: 'Sukolilo',     lat: -7.2900, lng: 112.7970, skor: 0.50 },
    { nama: 'Tambaksari',   lat: -7.2511, lng: 112.7650, skor: 0.65 },
    { nama: 'Mulyorejo',    lat: -7.2639, lng: 112.7935, skor: 0.35 },
    { nama: 'Sawahan',      lat: -7.2853, lng: 112.7278, skor: 0.82 },
    { nama: 'Lakarsantri',  lat: -7.3239, lng: 112.6720, skor: 0.30 },
    { nama: 'Benowo',       lat: -7.2617, lng: 112.6620, skor: 0.28 },
    { nama: 'Pakal',        lat: -7.2330, lng: 112.6735, skor: 0.22 },
    { nama: 'Asemrowo',     lat: -7.2269, lng: 112.6974, skor: 0.42 },
    { nama: 'Sukomanunggal',lat: -7.2750, lng: 112.7058, skor: 0.55 },
    { nama: 'Tandes',       lat: -7.2500, lng: 112.6970, skor: 0.48 },
    { nama: 'Sambikerep',   lat: -7.2717, lng: 112.6825, skor: 0.32 },
    { nama: 'Dukuh Pakis',  lat: -7.3003, lng: 112.7150, skor: 0.67 },
    { nama: 'Gayungan',     lat: -7.3369, lng: 112.7350, skor: 0.72 },
    { nama: 'Wonocolo',     lat: -7.3361, lng: 112.7553, skor: 0.58 },
    { nama: 'Rungkut',      lat: -7.3300, lng: 112.7956, skor: 0.75 },
    { nama: 'Tenggilis Mejoyo', lat: -7.3189, lng: 112.7742, skor: 0.53 },
    { nama: 'Gunung Anyar', lat: -7.3531, lng: 112.7964, skor: 0.38 },
    { nama: 'Sukolilo',     lat: -7.2950, lng: 112.8050, skor: 0.44 },
    { nama: 'Karang Pilang',lat: -7.3467, lng: 112.7122, skor: 0.68 },
    { nama: 'Jambangan',    lat: -7.3614, lng: 112.7208, skor: 0.50 },
    { nama: 'Wiyung',       lat: -7.3267, lng: 112.6972, skor: 0.43 },
    { nama: 'Bulak',        lat: -7.2150, lng: 112.7736, skor: 0.36 },
];

// Leaflet map instances
let leafletMaps = {};

function initLeafletMaps() {
    // Guard: Leaflet must be loaded
    if (typeof L === 'undefined') return;

    // ---- 1. MINI MAP (Dashboard Utama) ----
    if (!leafletMaps['mini'] && document.getElementById('mini-map')) {
        const miniMap = L.map('mini-map', { zoomControl: false, attributionControl: false, dragging: false, scrollWheelZoom: false })
            .setView(SURABAYA_CENTER, 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(miniMap);
        
        const heatData = KECAMATAN_ANOMALI.map(k => [k.lat, k.lng, k.skor]);
        L.heatLayer(heatData, { radius: 30, blur: 22, maxZoom: 14, gradient: {0.3:'#3b82f6', 0.6:'#f59e0b', 1.0:'#ef4444'} }).addTo(miniMap);
        
        KECAMATAN_ANOMALI.filter(k => k.skor >= 0.75).forEach(k => {
            L.marker([k.lat, k.lng], {
                icon: L.divIcon({ className: '', html: `<div style="background:#ef4444;color:white;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;white-space:nowrap;box-shadow:0 2px 4px rgba(0,0,0,0.3)">${k.nama}</div>`, iconAnchor: [30, 10] })
            }).addTo(miniMap);
        });
        leafletMaps['mini'] = miniMap;
        setTimeout(() => miniMap.invalidateSize(), 100);
    }

    // ---- 2. HEATMAP ANOMALI (Full tab) ----
    if (!leafletMaps['heatmap'] && document.getElementById('heatmap-main-map')) {
        const hmMap = L.map('heatmap-main-map', { zoomControl: true, attributionControl: true })
            .setView(SURABAYA_CENTER, 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(hmMap);
        
        const heatData = KECAMATAN_ANOMALI.map(k => [k.lat, k.lng, k.skor]);
        L.heatLayer(heatData, { radius: 40, blur: 30, maxZoom: 16, gradient: {0.2:'#22c55e', 0.5:'#f59e0b', 0.75:'#ef4444', 1.0:'#7f1d1d'} }).addTo(hmMap);
        
        KECAMATAN_ANOMALI.forEach(k => {
            const color = k.skor >= 0.75 ? '#ef4444' : k.skor >= 0.5 ? '#f59e0b' : '#22c55e';
            const label = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
            L.marker([k.lat, k.lng], {
                icon: L.divIcon({ className: '', html: `<div style="background:${color};color:white;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.4)">${k.nama}</div>`, iconAnchor: [40, 10] })
            }).bindPopup(`<b>${k.nama}</b><br>Skor Anomali: ${(k.skor*100).toFixed(0)}%<br>Status: <b style="color:${color}">${label}</b>`).addTo(hmMap);
        });
        leafletMaps['heatmap'] = hmMap;
        setTimeout(() => hmMap.invalidateSize(), 100);
    }

    // ---- 3. PETA SPASIAL ----
    if (!leafletMaps['peta'] && document.getElementById('peta-spasial-map')) {
        const petaMap = L.map('peta-spasial-map', { zoomControl: true, attributionControl: true })
            .setView(SURABAYA_CENTER, 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(petaMap);
        
        KECAMATAN_ANOMALI.forEach(k => {
            const color = k.skor >= 0.75 ? '#ef4444' : k.skor >= 0.5 ? '#f59e0b' : '#22c55e';
            const fillOpacity = 0.2 + k.skor * 0.5;
            L.circle([k.lat, k.lng], {
                color: color, fillColor: color, fillOpacity: fillOpacity,
                radius: 800 + k.skor * 1200,
                weight: k.skor >= 0.75 ? 2.5 : 1
            }).bindPopup(`
                <div style="min-width:180px">
                <b style="font-size:14px">${k.nama}</b><br>
                <hr style="margin:6px 0">
                <b>Skor Risiko:</b> ${(k.skor*100).toFixed(0)}%<br>
                <b>Status:</b> <span style="color:${color};font-weight:bold">${k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN'}</span>
                </div>
            `).addTo(petaMap);
        });
        leafletMaps['peta'] = petaMap;
        setTimeout(() => petaMap.invalidateSize(), 100);
    }
}

function switchTab(tabId, element) {
    if(typeof event !== 'undefined' && event) event.preventDefault();
    document.querySelectorAll('.tab-pane').forEach(el => {
        el.style.display = 'none';
    });
    const targetTab = document.getElementById('tab-content-' + tabId);
    if(targetTab) {
        targetTab.style.display = 'block';
    }
    document.querySelectorAll('.nav-item').forEach(el => {
        el.className = "nav-item flex items-center gap-3 px-3 py-2.5 text-on-surface-variant dark:text-on-tertiary-container hover:bg-surface-container-high dark:hover:bg-surface-variant transition-all rounded-lg";
        const icon = el.querySelector('.icon-elem');
        icon.classList.remove('sidebar-active');
        icon.style = "";
    });
    element.className = "nav-item flex items-center gap-3 px-3 py-2.5 bg-secondary-container dark:bg-secondary text-on-secondary-container dark:text-on-secondary rounded-lg transition-all translate-x-1";
    const icon = element.querySelector('.icon-elem');
    icon.classList.add('sidebar-active');
    icon.style = "font-variation-settings: 'FILL' 1;";

    // Lazy-init Leaflet maps on tab switch (maps need visible container to render)
    setTimeout(initLeafletMaps, 150);
}


// Hover effects
document.querySelectorAll('.group').forEach(item => {
    item.addEventListener('mouseenter', () => item.classList.add('elevation-2'));
    item.addEventListener('mouseleave', () => item.classList.remove('elevation-2'));
});

console.log("SmartAPBD Dashboard Initialized");

// --- SMARTAPBD DYNAMIC DATA INTEGRATION ---
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    // Init maps after a short delay to ensure DOM is rendered
    setTimeout(initLeafletMaps, 300);
    // Populate Grid View
    populateHeatmapGrid();
});

function toggleHeatmapView(view) {
    const mapDiv = document.getElementById('heatmap-main-map');
    const gridDiv = document.getElementById('heatmap-grid-view');
    const btnMap = document.getElementById('btn-hm-map');
    const btnGrid = document.getElementById('btn-hm-grid');
    const legendCard = document.getElementById('heatmap-legend-card');
    
    if (!mapDiv || !gridDiv) return;
    
    if (view === 'map') {
        mapDiv.style.display = 'block';
        gridDiv.style.display = 'none';
        if (legendCard) legendCard.style.display = 'block';
        
        btnMap.className = "px-4 py-1.5 bg-white shadow-sm rounded-md font-label-lg text-label-lg text-primary flex items-center gap-2";
        btnGrid.className = "px-4 py-1.5 font-label-lg text-label-lg text-on-surface-variant flex items-center gap-2 hover:text-primary transition-colors";
        
        if (leafletMaps['heatmap']) {
            leafletMaps['heatmap'].invalidateSize();
        }
    } else {
        mapDiv.style.display = 'none';
        gridDiv.style.display = 'block';
        if (legendCard) legendCard.style.display = 'none';
        
        btnGrid.className = "px-4 py-1.5 bg-white shadow-sm rounded-md font-label-lg text-label-lg text-primary flex items-center gap-2";
        btnMap.className = "px-4 py-1.5 font-label-lg text-label-lg text-on-surface-variant flex items-center gap-2 hover:text-primary transition-colors";
    }
}

function populateHeatmapGrid() {
    const tbody = document.getElementById('heatmap-grid-tbody');
    if (!tbody) return;
    
    // Sort descending by score
    const sorted = [...KECAMATAN_ANOMALI].sort((a, b) => b.skor - a.skor);
    
    tbody.innerHTML = sorted.map(k => {
        const colorClass = k.skor >= 0.75 ? 'text-error bg-error/10' : k.skor >= 0.5 ? 'text-amber-600 bg-amber-500/10' : 'text-green-600 bg-green-500/10';
        const label = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
        
        return `
            <tr class="hover:bg-surface-container-lowest transition-colors">
                <td class="p-4 font-bold">${k.nama}</td>
                <td class="p-4">
                    <span class="px-2 py-1 rounded text-xs font-bold ${colorClass}">${label}</span>
                </td>
                <td class="p-4 text-right font-mono">${(k.skor*100).toFixed(1)}%</td>
            </tr>
        `;
    }).join('');
}

function formatRupiah(number) {
    if (!number || isNaN(number)) return '-';
    if (number >= 1000000000000) {
        return 'Rp ' + (number / 1000000000000).toFixed(1) + ' Triliun';
    } else if (number >= 1000000000) {
        return 'Rp ' + (number / 1000000000).toFixed(1) + ' Miliar';
    } else if (number >= 1000000) {
        return 'Rp ' + (number / 1000000).toFixed(1) + ' Juta';
    }
    return 'Rp ' + number.toLocaleString('id-ID');
}

// --- PAGINATION & SORTING LOGIC ---
window.renderAnomalyTable = function() {
    const tbodyUtama = document.getElementById('tabel-anomali-body');
    if(!tbodyUtama || !window.tableAnomalies) return;
    
    tbodyUtama.innerHTML = '';
    const ITEMS_PER_PAGE = 5;
    const startIndex = (window.currentAnomalyPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const paginated = window.tableAnomalies.slice(startIndex, endIndex);
    
    if (paginated.length === 0) {
        tbodyUtama.innerHTML = '<tr><td colspan="6" class="text-center py-4">Tidak ada anomali terdeteksi</td></tr>';
    } else {
        paginated.forEach(row => {
            tbodyUtama.appendChild(createAnomalyRow(row));
        });
    }
    
    const infoSpan = document.getElementById('anomaly-pagination-info');
    if(infoSpan) {
        infoSpan.innerText = `Menampilkan ${Math.min(startIndex + 1, window.tableAnomalies.length)}-${Math.min(endIndex, window.tableAnomalies.length)} dari ${window.tableAnomalies.length} anomali`;
    }
};

window.nextAnomalyPage = function() {
    const ITEMS_PER_PAGE = 5;
    if (window.currentAnomalyPage * ITEMS_PER_PAGE < window.tableAnomalies.length) {
        window.currentAnomalyPage++;
        window.renderAnomalyTable();
    }
};

window.prevAnomalyPage = function() {
    if (window.currentAnomalyPage > 1) {
        window.currentAnomalyPage--;
        window.renderAnomalyTable();
    }
};

window.sortAnomalyTable = function(col) {
    if(!window.tableAnomalies) return;
    window.tableAnomalies.sort((a,b) => {
        let valA = a[col] || '';
        let valB = b[col] || '';
        if(!isNaN(parseFloat(valA)) && !isNaN(parseFloat(valB))) {
            return parseFloat(valB) - parseFloat(valA); // Descending
        }
        return String(valA).localeCompare(String(valB)); // Ascending string
    });
    window.currentAnomalyPage = 1;
    window.renderAnomalyTable();
};

function initDashboard() {
    // 1. Fetch gold_skpd_summary.csv for KPI 1 (Total Anggaran)
    Papa.parse('/data/gold/gold_skpd_summary.csv', {
        download: true,
        header: true,
        complete: function(results) {
            let data = results.data;
            let totalAnggaran = 0;
            data.forEach(row => {
                if(row.total_pagu) {
                    totalAnggaran += parseFloat(row.total_pagu);
                }
            });
            const el = document.getElementById('kpi-total-anggaran');
            if(el && totalAnggaran > 0) el.innerText = formatRupiah(totalAnggaran);
        }
    });

    // 2. Fetch apbd_scored.csv for KPI 2 & Tables & Heatmap
    Papa.parse('/data/gold/apbd_scored.csv', {
        download: true,
        header: true,
        complete: function(results) {
            let data = results.data.filter(r => r.id_transaksi); // filter empty rows
            let anomalies = [];
            let wilayahAnomalies = {};

            let qData = { Q1: {a:0, r:0}, Q2: {a:0, r:0}, Q3: {a:0, r:0}, Q4: {a:0, r:0} };

            data.forEach(row => {
                let isFlagged = String(row.is_flagged || '').trim().toLowerCase();
                if(isFlagged === 'true' || isFlagged === '1' || row.anomaly_label === 'Anomaly' || row.anomaly_label === 'Anomali') {
                    anomalies.push(row);
                    let kec = row.nama_skpd || 'Tidak Diketahui';
                    if (!wilayahAnomalies[kec]) wilayahAnomalies[kec] = 0;
                    wilayahAnomalies[kec] += parseFloat(row.realisasi || 0);
                }

                // Time Series Aggregation - use bulan_kontrak if available
                let m = parseInt(row.bulan_kontrak) || 1;
                if(!row.bulan_kontrak && row.tanggal_kontrak) {
                    m = parseInt(row.tanggal_kontrak.split('-')[1]) || 1;
                }
                let q = m <= 3 ? 'Q1' : (m <= 6 ? 'Q2' : (m <= 9 ? 'Q3' : 'Q4'));
                qData[q].a += parseFloat(row.pagu_anggaran || row.anggaran || 0);
                qData[q].r += parseFloat(row.realisasi || 0);
            });
            
            const elCount = document.getElementById('kpi-anomali-count');
            if(elCount) elCount.innerText = anomalies.length + ' Item';

            // Also update Heatmap sidebar
            const elHeatmapTotal = document.getElementById('heatmap-anomali-total');
            if(elHeatmapTotal) elHeatmapTotal.innerText = data.length;

            // --- TIME-SERIES REALISASI ANGGARAN ---
            const tsContainer = document.getElementById('time-series-container');
            if(tsContainer) {
                tsContainer.innerHTML = '';
                let maxVal = 0;
                ['Q1','Q2','Q3','Q4'].forEach(q => {
                    if (qData[q].a > maxVal) maxVal = qData[q].a;
                    if (qData[q].r > maxVal) maxVal = qData[q].r;
                });
                maxVal = maxVal || 1;

                ['Q1','Q2','Q3','Q4'].forEach(q => {
                    let aPct = Math.max(Math.min((qData[q].a / maxVal) * 100, 100), 5);
                    let rPct = Math.max(Math.min((qData[q].r / maxVal) * 100, 100), 5);
                    
                    let div = document.createElement('div');
                    div.className = "h-full flex-1 flex flex-col items-center gap-2 group cursor-pointer";
                    div.title = `Alokasi: ${formatRupiah(qData[q].a)}\nRealisasi: ${formatRupiah(qData[q].r)}`;
                    div.innerHTML = `
                        <div class="w-full h-full flex justify-center items-end gap-1">
                            <div class="w-8 bg-primary rounded-t-sm transition-all group-hover:opacity-80" style="height: ${aPct}%"></div>
                            <div class="w-8 bg-secondary-container rounded-t-sm transition-all group-hover:opacity-80" style="height: ${rPct}%"></div>
                        </div>
                        <span class="font-label-md text-label-md mt-2">${q}</span>
                    `;
                    tsContainer.appendChild(div);
                });

                // Update footer totals
                let totalRealisasi = Object.values(qData).reduce((s,q) => s + q.r, 0);
                let totalAlokasi = Object.values(qData).reduce((s,q) => s + q.a, 0);
                let sisaPagu = totalAlokasi - totalRealisasi;
                const elTR = document.getElementById('ts-total-realisasi');
                const elSP = document.getElementById('ts-sisa-pagu');
                if(elTR) elTR.innerText = formatRupiah(totalRealisasi);
                if(elSP) elSP.innerText = formatRupiah(Math.abs(sisaPagu));
            }

            // --- TABEL DASHBOARD UTAMA ---
            window.tableAnomalies = anomalies;
            window.tableAnomalies.sort((a, b) => parseFloat(b.ensemble_score || b.anomaly_score || 0) - parseFloat(a.ensemble_score || a.anomaly_score || 0));
            window.currentAnomalyPage = 1;
            window.renderAnomalyTable();

            // --- TABEL DETAIL ANOMALI (SEMUA) ---
            const tbodyDetail = document.getElementById('tabel-detail-anomali-body');
            if(tbodyDetail) {
                tbodyDetail.innerHTML = '';
                if (anomalies.length === 0) {
                    tbodyDetail.innerHTML = '<tr><td colspan="6" class="text-center py-4">Tidak ada anomali terdeteksi</td></tr>';
                } else {
                    anomalies.forEach(row => {
                        tbodyDetail.appendChild(createAnomalyRow(row));
                    });
                }
            }

            // --- TOP 5 WILAYAH KRITIS (HEATMAP) ---
            // If we only have 1-2 SKPDs (e.g. CKAN data), group by uraian_belanja (sektor pajak) instead
            const wilayahKritisContainer = document.getElementById('top-5-wilayah-kritis');
            if(wilayahKritisContainer) {
                wilayahKritisContainer.innerHTML = '';
                
                // Build grouping: prefer multiple SKPDs, else use uraian_belanja
                let groupData = {};
                let useSektor = Object.keys(wilayahAnomalies).length <= 2;
                
                if (useSektor) {
                    // Group anomalies by uraian_belanja (sektor pajak)
                    anomalies.forEach(row => {
                        let key = row.uraian_belanja || row.nama_skpd || 'Tidak Diketahui';
                        if (!groupData[key]) groupData[key] = 0;
                        groupData[key] += parseFloat(row.realisasi || 0);
                    });
                } else {
                    groupData = wilayahAnomalies;
                }
                
                let sortedWilayah = Object.entries(groupData).sort((a, b) => b[1] - a[1]).slice(0, 5);
                let maxNilai = sortedWilayah.length > 0 ? sortedWilayah[0][1] : 1;
                
                let rank = 1;
                sortedWilayah.forEach(([kecamatan, totalNilai]) => {
                    let pct = Math.min((totalNilai / maxNilai) * 100, 100);
                    let colorClass = rank === 1 ? 'bg-error text-on-error' : (rank === 2 ? 'bg-amber-500 text-white' : 'bg-primary text-on-primary');
                    let barColor = rank === 1 ? 'bg-error' : (rank === 2 ? 'bg-amber-500' : 'bg-primary');
                    let iconColor = rank === 1 ? 'text-error' : (rank === 2 ? 'text-amber-500' : 'text-primary');
                    let icon = rank === 1 ? 'warning' : (rank === 2 ? 'report' : 'info');

                    let div = document.createElement('div');
                    div.className = "p-4 bg-surface-container-lowest rounded-xl border border-outline-variant hover:border-primary transition-colors cursor-pointer group";
                    div.innerHTML = `
                        <div class="flex items-center justify-between mb-3">
                            <span class="w-6 h-6 rounded ${colorClass} flex items-center justify-center font-bold text-xs">0${rank}</span>
                            <span class="material-symbols-outlined ${iconColor} text-[20px]">${icon}</span>
                        </div>
                        <h4 class="font-title-md text-title-md mb-1 line-clamp-2 text-sm">${kecamatan}</h4>
                        <div class="flex items-center justify-between">
                            <span class="font-label-sm text-label-sm text-on-surface-variant">Total Nilai Anomali</span>
                            <span class="font-bold ${iconColor}">${formatRupiah(totalNilai)}</span>
                        </div>
                        <div class="w-full bg-surface-container mt-3 h-1.5 rounded-full overflow-hidden">
                            <div class="${barColor} h-full rounded-full" style="width: ${pct}%"></div>
                        </div>
                    `;
                    wilayahKritisContainer.appendChild(div);
                    rank++;
                });
            }
        }
    });


    // 3. Fetch sentiment_results.csv for KPI 3 & FEED
    Papa.parse('/data/gold/sentiment_results.csv', {
        download: true,
        header: true,
        complete: function(results) {
            let data = results.data;
            let negativeCount = 0;
            let total = 0;
            
            const feedContainer = document.getElementById('sentiment-feed-container');
            if(feedContainer) feedContainer.innerHTML = '';

            data.forEach(row => {
                if(row.sentiment_label && (row.teks || row.text)) {
                    total++;
                    let txt = row.teks || row.text;
                    if(row.sentiment_label === 'Negatif' || row.sentiment_label === 'Netral') {
                        negativeCount++;
                    }

                    // Populate Feed
                    if(feedContainer) {
                        let labelColor = 'sentiment-neutral';
                        let labelText = row.sentiment_label;
                        if(labelText === 'Positif') labelColor = 'sentiment-positive';
                        if(labelText === 'Negatif') labelColor = 'sentiment-negative';
                        
                        let source = row.sumber || row.platform || 'X';
                        let initials = source.substring(0,2).toUpperCase();
                        
                        let div = document.createElement('div');
                        div.className = "p-4 border-b border-outline-variant hover:bg-surface-container-low transition-colors cursor-pointer";
                        div.innerHTML = `
                            <div class="flex justify-between items-start mb-2">
                                <div class="flex items-center gap-3">
                                    <div class="w-8 h-8 rounded-full bg-surface-container-highest flex items-center justify-center text-primary font-bold text-label-sm">${initials}</div>
                                    <div>
                                        <p class="font-label-lg text-label-lg">${source}</p>
                                        <p class="text-label-sm text-on-surface-variant">${row.tanggal || row.created_at || 'Baru saja'}</p>
                                    </div>
                                </div>
                                <span class="${labelColor} px-2 py-1 rounded text-label-sm font-bold">${labelText}</span>
                            </div>
                            <p class="text-body-md pl-11 text-on-surface">${txt}</p>
                            <div class="pl-11 mt-2 flex gap-4">
                                <button class="flex items-center gap-1 text-label-sm text-on-surface-variant hover:text-primary transition-colors"><span class="material-symbols-outlined text-[16px]">thumb_up</span> ${Math.floor(Math.random() * 50)}</button>
                                <button class="flex items-center gap-1 text-label-sm text-on-surface-variant hover:text-primary transition-colors"><span class="material-symbols-outlined text-[16px]">reply</span> Balas</button>
                            </div>
                        `;
                        feedContainer.appendChild(div);
                    }
                }
            });

            if(total > 0) {
                let pctNeg = Math.round((negativeCount / total) * 100);
                const el = document.getElementById('kpi-sentimen');
                if(el) {
                    el.innerHTML = `${pctNeg}% <span class="text-title-md font-normal text-on-surface-variant">Netral/Negatif</span>`;
                }

                // Update Sentiment tab gauge and percentages
                let positifCount = 0, netralCount = 0, negatifCount = 0;
                data.forEach(row => {
                    if(row.sentiment_label === 'Positif') positifCount++;
                    else if(row.sentiment_label === 'Negatif') negatifCount++;
                    else if(row.sentiment_label === 'Netral') netralCount++;
                });
                let pctPos = Math.round((positifCount / total) * 100);
                let pctNet = Math.round((netralCount / total) * 100);
                let pctNegOnly = Math.round((negatifCount / total) * 100);
                let gaugeScoreNum = (pctPos * 1.0 + pctNet * 0.5);
                let gaugeScore = gaugeScoreNum.toFixed(1);

                const elGauge = document.getElementById('sentiment-gauge-value');
                if(elGauge) elGauge.innerText = gaugeScore;

                // Update Gauge Arc Visual (126 is the half-circle stroke length)
                const arcGauge = document.getElementById('sentiment-gauge-arc');
                if(arcGauge) arcGauge.style.strokeDashoffset = 126 - (gaugeScoreNum / 100) * 126;

                // Update Label Text (Sangat Baik / Baik / Cukup / Buruk)
                const labelGauge = document.getElementById('sentiment-gauge-label');
                if(labelGauge) {
                    if (gaugeScoreNum >= 75) {
                        labelGauge.innerText = 'Sangat Baik';
                        labelGauge.className = 'text-label-md text-primary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#005faf'; // primary
                    } else if (gaugeScoreNum >= 50) {
                        labelGauge.innerText = 'Baik';
                        labelGauge.className = 'text-label-md text-primary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#005faf'; // primary
                    } else if (gaugeScoreNum >= 35) {
                        labelGauge.innerText = 'Cukup';
                        labelGauge.className = 'text-label-md text-secondary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#f59e0b'; // warning
                    } else {
                        labelGauge.innerText = 'Buruk';
                        labelGauge.className = 'text-label-md text-error font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#ba1a1a'; // error
                    }
                }

                // Update total interaction text
                const interactionText = document.getElementById('sentiment-interaction-text');
                if(interactionText) {
                    interactionText.innerText = `Berdasarkan ${total.toLocaleString()} interaksi media sosial & aduan masyarakat minggu ini.`;
                }

                const elPos = document.getElementById('sentiment-positif-pct');
                if(elPos) elPos.innerText = pctPos + '%';
                const elNet = document.getElementById('sentiment-netral-pct');
                if(elNet) elNet.innerText = pctNet + '%';
                const elNeg = document.getElementById('sentiment-negatif-pct');
                if(elNeg) elNeg.innerText = pctNegOnly + '%';
            }
        }
    });

    // 4. Fetch gold_jejaring_vendor.csv for Jejaring Entitas
    Papa.parse('/data/gold/gold_jejaring_vendor.csv', {
        download: true,
        header: true,
        complete: function(results) {
            let data = results.data.filter(r => r.nama_vendor);
            window.jejaringVendorData = data; // Store globally
            if(data && data.length > 0) {
                // Find top highest risk vendor
                let topVendor = data.find(v => v.is_fraud_vendor === 'True' || v.is_fraud_vendor === 'true') || data[0];
                // Auto-select the top vendor to populate right panel
                selectJejaringNode(
                    topVendor.nama_vendor,
                    topVendor.is_fraud_vendor === 'True' ? 'Indikasi Risiko Tinggi' : 'Penyedia Pengadaan',
                    parseFloat(topVendor.total_nilai_kontrak || 0),
                    parseInt(topVendor.total_kontrak || 0),
                    topVendor.is_fraud_vendor === 'True'
                );
            }
        }
    });
}

// Update Jejaring Entitas right panel when a node is clicked
window.selectJejaringNode = function(name, type, nilaiTotal, kontrakCount, isRisiko) {
    // Highlight: remove 'selected' from all nodes, add to clicked
    document.querySelectorAll('#tab-content-jejaring_entitas .node').forEach(n => n.classList.remove('selected'));
    // Find the clicked node by name and mark it
    document.querySelectorAll('#tab-content-jejaring_entitas .node-label').forEach(label => {
        if(label.innerText === name) label.closest('.node').classList.add('selected');
    });
    
    // Update right panel
    const elName = document.getElementById('jejaring-vendor-name');
    if(elName) elName.innerText = name;
    
    const elType = document.getElementById('jejaring-vendor-type');
    if(elType) elType.innerText = type;
    
    const elVal = document.getElementById('jejaring-vendor-value');
    if(elVal) elVal.innerText = nilaiTotal > 0 ? formatRupiah(nilaiTotal) : 'Data tidak tersedia';
    
    const elContracts = document.getElementById('jejaring-vendor-contracts');
    if(elContracts) elContracts.innerText = kontrakCount > 0 ? kontrakCount + ' Paket' : '-';
    
    // Show/hide risk badge
    const alertBadge = document.querySelector('#tab-content-jejaring_entitas .bg-error-container');
    if(alertBadge) alertBadge.style.display = isRisiko ? '' : 'none';
    
    // Also try to match from CSV data
    if(window.jejaringVendorData) {
        let matched = window.jejaringVendorData.find(v => v.nama_vendor === name);
        if(matched) {
            if(elVal) elVal.innerText = formatRupiah(parseFloat(matched.total_nilai_kontrak || 0));
            if(elContracts) elContracts.innerText = (matched.total_kontrak || '-') + ' Paket';
        }
    }
};



function createAnomalyRow(row) {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-surface-container transition-colors';
    
    let score = parseFloat(row.anomaly_score || 0);
    let statusLabel = score > 0.6 ? 
        '<span class="px-3 py-1 bg-error text-on-error rounded-full text-label-sm font-bold uppercase tracking-tighter">OUTLIER</span>' : 
        '<span class="px-3 py-1 bg-amber-500 text-white rounded-full text-label-sm font-bold uppercase tracking-tighter">WARNING</span>';
    
    let zScoreVal = parseFloat(row.zscore_per_rekening);
    let zScoreBadgeClass = Math.abs(zScoreVal) > 2 ? 'bg-error-container text-on-error-container' : 'bg-amber-100 text-amber-800';
    let zScoreStr = isNaN(zScoreVal) ? '-' : zScoreVal.toFixed(1);

    let realisasiVal = parseFloat(row.realisasi || 0);

    tr.innerHTML = `
        <td class="px-6 py-4">
            <p class="font-title-md text-title-md text-on-surface">${row.uraian_belanja || '-'}</p>
            <p class="font-label-sm text-label-sm text-on-surface-variant">${row.nama_skpd || '-'}</p>
        </td>
        <td class="px-6 py-4 font-body-md text-body-md">${row.jenis_pengadaan || row.kota || '-'}</td>
        <td class="px-6 py-4 font-title-md text-title-md text-right">${formatRupiah(realisasiVal)}</td>
        <td class="px-6 py-4 text-center">
            <span class="px-2 py-0.5 ${zScoreBadgeClass} rounded font-bold">${zScoreStr}</span>
        </td>
        <td class="px-6 py-4">${statusLabel}</td>
        <td class="px-6 py-4 text-center">
            <button class="text-primary hover:underline font-label-lg" onclick="showDetail(this)" data-id="${row.id_transaksi || ''}" data-kategori="${row.uraian_belanja || ''}" data-realisasi="${realisasiVal}" data-zscore="${zScoreStr}" data-persen="${row.persen_realisasi || ''}">Detail</button>
        </td>
    `;
    return tr;
}

function showDetail(btn) {
    let id = btn.dataset.id;
    let kategori = btn.dataset.kategori;
    let realisasi = formatRupiah(parseFloat(btn.dataset.realisasi));
    let zscore = btn.dataset.zscore;
    let skpd = btn.closest('tr').querySelector('td:nth-child(1) p:nth-child(2)').innerText;
    
    // Set UI elements in the Detail Anomali tab
    let elId = document.getElementById('detail-id-header');
    if(elId) elId.innerText = id || 'TRX-UNKNOWN';
    
    let elZscore = document.getElementById('detail-zscore');
    if(elZscore) elZscore.innerText = zscore || '-';
    
    let elKat = document.getElementById('detail-kategori');
    if(elKat) elKat.innerText = kategori || '-';
    
    let elReal = document.getElementById('detail-realisasi');
    if(elReal) elReal.innerText = realisasi || '-';
    
    let elSkpd = document.getElementById('detail-skpd');
    if(elSkpd) elSkpd.innerText = skpd || 'SKPD Tidak Diketahui';
    
    // Temukan tombol nav Detail Anomali di sidebar
    let detailTabBtn = document.querySelector('a[data-id="detail_anomali"]');
    if(detailTabBtn) {
        // Pindah ke tab Detail Anomali
        switchTab('detail_anomali', detailTabBtn);
    } else {
        alert('Fitur Detail belum tersedia.');
    }
}

// Search functionality
document.addEventListener('DOMContentLoaded', () => {
    const attachSearch = (inputId, tbodyId) => {
        const input = document.getElementById(inputId);
        const tbody = document.getElementById(tbodyId);
        if(input && tbody) {
            input.addEventListener('keyup', function(e) {
                let text = e.target.value.toLowerCase();
                let rows = tbody.querySelectorAll('tr');
                rows.forEach(r => {
                    r.style.display = r.innerText.toLowerCase().includes(text) ? '' : 'none';
                });
            });
        }
    };
    
    // Slight delay to ensure CSV is parsed and rendered
    setTimeout(() => {
        attachSearch('search-utama', 'tabel-anomali-body');
        attachSearch('search-detail', 'tabel-detail-anomali-body');
    }, 1500);
});

// --- LAPORAN BPK TAB LOGIC ---
window.filterBPK = function() {
    const searchVal = document.getElementById('bpk-search')?.value.toLowerCase() || '';
    const tahunVal = document.getElementById('bpk-filter-tahun')?.value || 'all';
    const auditorVal = document.getElementById('bpk-filter-auditor')?.value || 'all';
    
    const tbody = document.getElementById('bpk-tbody');
    const emptyState = document.getElementById('bpk-empty');
    if(!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const title = row.getAttribute('data-title')?.toLowerCase() || '';
        const rowTahun = row.getAttribute('data-tahun');
        const rowAuditor = row.getAttribute('data-auditor');
        
        const matchSearch = title.includes(searchVal);
        const matchTahun = tahunVal === 'all' || rowTahun === tahunVal;
        const matchAuditor = auditorVal === 'all' || rowAuditor === auditorVal;
        
        if (matchSearch && matchTahun && matchAuditor) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? 'flex' : 'none';
        
        // Also hide/show the table header if empty
        const table = document.getElementById('bpk-table');
        if (table) {
            const thead = table.querySelector('thead');
            if (thead) thead.style.display = visibleCount === 0 ? 'none' : '';
        }
    }
};

window.exportBPK = function() {
    alert('Memproses dokumen... Rekap Laporan BPK sedang diekspor dalam format PDF/CSV.');
};

// Bind real-time search for BPK
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('bpk-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', window.filterBPK);
    }
    
    const filterTahun = document.getElementById('bpk-filter-tahun');
    if (filterTahun) {
        filterTahun.addEventListener('change', window.filterBPK);
    }
    
    const filterAuditor = document.getElementById('bpk-filter-auditor');
    if (filterAuditor) {
        filterAuditor.addEventListener('change', window.filterBPK);
    }
});


// --- KATEGORI BELANJA HEATMAP FILTER LOGIC ---
const possibleCategories = ['Honorarium', 'Belanja Modal', 'Perjalanan Dinas', 'Hibah & Bansos'];
KECAMATAN_ANOMALI.forEach((k, i) => {
    k.kategori = [];
    k.kategori.push(possibleCategories[i % 4]);
    if (i % 3 === 0) k.kategori.push(possibleCategories[(i+1) % 4]);
});

window.updateHeatmapData = function() {
    const checkedBoxes = document.querySelectorAll('.hm-filter-kategori:checked');
    const selectedCats = Array.from(checkedBoxes).map(cb => cb.value);
    
    // filter data: if any checked category matches the item's category
    const filtered = KECAMATAN_ANOMALI.filter(k => {
        if (selectedCats.length === 0) return false;
        return k.kategori.some(cat => selectedCats.includes(cat));
    });
    
    // Update Leaflet heatmap (if initialized)
    const hmMap = leafletMaps['heatmap'];
    if (hmMap) {
        // Remove all layers except tile layer
        hmMap.eachLayer(layer => {
            if (!layer._url) hmMap.removeLayer(layer);
        });
        
        // Re-add heat layer
        const heatData = filtered.map(k => [k.lat, k.lng, k.skor]);
        L.heatLayer(heatData, { radius: 35, blur: 25, maxZoom: 14, gradient: {0.3:'#3b82f6', 0.6:'#f59e0b', 1.0:'#ef4444'} }).addTo(hmMap);
        
        // Re-add markers
        filtered.forEach(k => {
            const color = k.skor >= 0.75 ? '#ef4444' : k.skor >= 0.5 ? '#f59e0b' : '#22c55e';
            const fillOpacity = 0.2 + k.skor * 0.5;
            L.circle([k.lat, k.lng], {
                color: color, fillColor: color, fillOpacity: fillOpacity,
                radius: 800 + k.skor * 1200,
                weight: k.skor >= 0.75 ? 2.5 : 1
            }).bindPopup(`
                <div style="min-width:180px">
                <b style="font-size:14px">${k.nama}</b><br>
                <hr style="margin:6px 0">
                <b>Skor Risiko:</b> ${(k.skor*100).toFixed(0)}%<br>
                <b>Status:</b> <span style="color:${color};font-weight:bold">${k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN'}</span><br>
                <b>Kategori:</b> ${k.kategori.join(', ')}
                </div>
            `).addTo(hmMap);
        });
    }
    
    // Update Grid View
    const tbody = document.getElementById('heatmap-grid-tbody');
    if (tbody) {
        const sorted = [...filtered].sort((a, b) => b.skor - a.skor);
        if (sorted.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="p-4 text-center text-on-surface-variant">Tidak ada data untuk kategori yang dipilih</td></tr>';
        } else {
            tbody.innerHTML = sorted.map(k => {
                const colorClass = k.skor >= 0.75 ? 'text-error bg-error/10' : k.skor >= 0.5 ? 'text-amber-600 bg-amber-500/10' : 'text-green-600 bg-green-500/10';
                const label = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
                
                return `
                    <tr class="hover:bg-surface-container-lowest transition-colors">
                        <td class="p-4 font-bold">${k.nama}</td>
                        <td class="p-4">
                            <span class="px-2 py-1 rounded text-xs font-bold ${colorClass}">${label}</span>
                        </td>
                        <td class="p-4 text-xs text-on-surface-variant">${k.kategori.join(', ')}</td>
                        <td class="p-4 text-right font-mono">${(k.skor*100).toFixed(1)}%</td>
                    </tr>
                `;
            }).join('');
        }
    }
};

// Bind events
document.addEventListener('DOMContentLoaded', () => {
    const kategoriCheckboxes = document.querySelectorAll('.hm-filter-kategori');
    kategoriCheckboxes.forEach(cb => {
        cb.addEventListener('change', window.updateHeatmapData);
    });
    
    // Initial call to set up the filtered state
    setTimeout(window.updateHeatmapData, 500);
});

// --- YOUTUBE COMMENTS (REAL DATA) DYNAMIC FETCHING ---

// --- REAL API DATA DYNAMIC FETCHING (YouTube + GNews) ---
window.loadApiData = async function() {
    const container = document.getElementById('sentiment-feed-container');
    if (!container) return;
    
    try {
        let combinedData = [];
        
        // 1. Fetch YouTube JSON
        try {
            const ytResponse = await fetch('/data/bronze/yt_comments_raw.json');
            if (ytResponse.ok) {
                const ytData = await ytResponse.json();
                ytData.forEach(item => {
                    combinedData.push({
                        source: 'YouTube',
                        author: item.authorDisplayName || "Warganet",
                        text: item.textOriginal || "",
                        date: item.publishedAt,
                        likes: item.likeCount || 0
                    });
                });
            }
        } catch (e) {
            console.warn("Could not fetch YouTube data:", e);
        }
        
        // 2. Fetch GNews CSV
        try {
            const gnResponse = await fetch('/data/bronze/gnews_raw.csv');
            if (gnResponse.ok) {
                const csvText = await gnResponse.text();
                // Simple CSV parse (ignores quotes with commas for now as heuristic)
                const rows = csvText.split('\n').filter(r => r.trim().length > 0);
                if (rows.length > 1) {
                    const headers = rows[0].split(',');
                    for(let i=1; i<rows.length; i++) {
                        // Very naive split just to get it working in MVP without PapaParse
                        // Assuming format: title,description,publishedAt,source_name
                        // Since title/desc might contain commas, a real CSV parser is better. 
                        // For MVP, we will just regex split by comma outside quotes (simplified)
                        let row = rows[i];
                        if(!row) continue;
                        
                        // Extract using regex for CSV
                        const matches = row.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g);
                        if (matches && matches.length >= 4) {
                            const title = matches[0].replace(/^"|"$/g, '');
                            const desc = matches[1].replace(/^"|"$/g, '');
                            const date = matches[2].replace(/^"|"$/g, '');
                            const source = matches[3].replace(/^"|"$/g, '');
                            
                            combinedData.push({
                                source: 'GNews',
                                author: source || "Berita Lokal",
                                text: `[BERITA] ${title} - ${desc}`,
                                date: date,
                                likes: 0
                            });
                        } else {
                            // fallback if simple split fails
                            const cols = row.split(',');
                            combinedData.push({
                                source: 'GNews',
                                author: cols[cols.length-1] || "News",
                                text: cols[0] || row,
                                date: new Date().toISOString(),
                                likes: 0
                            });
                        }
                    }
                }
            }
        } catch (e) {
            console.warn("Could not fetch GNews data:", e);
        }
        
        if (combinedData.length === 0) {
            container.innerHTML = '<div class="p-8 text-center text-on-surface-variant">Belum ada data dari API.</div>';
            return;
        }
        
        // Simple heuristic sentiment logic
        const positiveWords = ['bagus', 'keren', 'mantap', 'terima kasih', 'lanjutkan', 'baik', 'dukung', 'maju', 'setuju', 'bantuan', 'bantu', 'kurangi'];
        const negativeWords = ['jelek', 'rusak', 'korupsi', 'macet', 'lambat', 'parah', 'buruk', 'kecewa', 'mangkrak', 'bodoh', 'goblok', 'salah paham', 'banjir'];
        
        let posCount = 0;
        let negCount = 0;
        let netCount = 0;
        
        // Sort by date descending
        combinedData.sort((a,b) => new Date(b.date) - new Date(a.date));
        
        const html = combinedData.map(item => {
            const text = item.text || "";
            const lowerText = text.toLowerCase();
            
            let sentiment = 'Netral';
            let sentimentClass = 'sentiment-neutral text-on-surface-variant bg-surface-container-high';
            
            if (positiveWords.some(w => lowerText.includes(w))) {
                sentiment = 'Positif';
                sentimentClass = 'sentiment-positive text-primary bg-primary/10';
                posCount++;
            } else if (negativeWords.some(w => lowerText.includes(w))) {
                sentiment = 'Negatif';
                sentimentClass = 'sentiment-negative text-error bg-error/10';
                negCount++;
            } else {
                netCount++;
            }
            
            const initials = (item.author || "AN").substring(0,2).toUpperCase();
            const dateStr = new Date(item.date).toLocaleDateString('id-ID', {day: 'numeric', month: 'short'});
            
            return `
                <div class="p-4 border-b border-outline-variant hover:bg-surface-container-low transition-colors cursor-pointer">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-surface-container-highest flex items-center justify-center text-primary font-bold text-label-sm">${initials}</div>
                            <div>
                                <p class="font-label-lg text-label-lg">${item.author}</p>
                                <p class="text-label-sm text-on-surface-variant">${dateStr} via ${item.source}</p>
                            </div>
                        </div>
                        <span class="px-2 py-1 rounded text-label-sm font-bold ${sentimentClass}">${sentiment}</span>
                    </div>
                    <p class="text-body-md pl-11 text-on-surface">${text.replace(/\n/g, '<br>')}</p>
                    <div class="pl-11 mt-2 flex gap-4">
                        <button class="flex items-center gap-1 text-label-sm text-on-surface-variant hover:text-primary transition-colors">
                            <span class="material-symbols-outlined text-[16px]">thumb_up</span> ${item.likes}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
        
        // Update stats
        const total = combinedData.length;
        document.getElementById('sentiment-positif-pct').innerText = ((posCount/total)*100).toFixed(1) + '%';
        document.getElementById('sentiment-netral-pct').innerText = ((netCount/total)*100).toFixed(1) + '%';
        document.getElementById('sentiment-negatif-pct').innerText = ((negCount/total)*100).toFixed(1) + '%';
        
        document.getElementById('sentiment-interaction-text').innerText = `Berdasarkan ${total} interaksi API (YouTube & GNews) minggu ini.`;
        
    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="p-8 text-center text-error">Gagal memuat data API: ${err.message}</div>`;
    }
};

// Override DOMContentLoaded
window.loadYouTubeComments = window.loadApiData;
// Call when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(window.loadYouTubeComments, 800);
});

