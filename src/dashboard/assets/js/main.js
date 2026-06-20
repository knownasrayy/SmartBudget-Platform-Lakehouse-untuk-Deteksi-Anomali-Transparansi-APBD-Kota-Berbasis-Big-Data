// ---- SURABAYA KECAMATAN HEATMAP DATA (real coordinates) ----
// [lat, lng, intensity] — intensity based on anomaly score weighting
const SURABAYA_CENTER = [-7.2575, 112.7521];
const KECAMATAN_ANOMALI = window.KECAMATAN_ANOMALI || [
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

// Load GeoJSON
window.surabayaGeoJSON = null;
fetch('assets/data/surabaya_kecamatan.geojson')
    .then(r => r.json())
    .then(data => { window.surabayaGeoJSON = data; })
    .catch(e => console.error("Failed to load GeoJSON:", e));

function initLeafletMaps() {
    // Guard: Leaflet must be loaded
    if (typeof L === 'undefined') return;

    // ---- 1. MINI MAP (Dashboard Utama) ----
    if (!leafletMaps['mini'] && document.getElementById('mini-map')) {
        try {
            const miniMap = L.map('mini-map', { zoomControl: false, attributionControl: false, dragging: false, scrollWheelZoom: false })
                .setView(SURABAYA_CENTER, 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(miniMap);
            
            if (window.surabayaGeoJSON) {
                L.geoJSON(window.surabayaGeoJSON, {
                    style: function(feature) {
                        const kecName = feature.properties.KECAMATAN;
                        const k = KECAMATAN_ANOMALI.find(x => x.nama.toUpperCase() === kecName.toUpperCase());
                        if (k) {
                            const isHigh = k.skor >= 0.75;
                            const isMed = k.skor >= 0.5;
                            const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
                            return { color: 'white', weight: 1, fillColor: color, fillOpacity: 0.6 };
                        }
                        return { color: 'white', weight: 1, fillColor: '#ccc', fillOpacity: 0.3 };
                    }
                }).addTo(miniMap);
            } else {
                // Fallback if GeoJSON not loaded
                KECAMATAN_ANOMALI.forEach(k => {
                    const isHigh = k.skor >= 0.75;
                    const isMed = k.skor >= 0.5;
                    const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
                    L.circle([k.lat, k.lng], { color: color, fillColor: color, fillOpacity: 0.35, radius: 1800, weight: 1 }).addTo(miniMap);
                });
            }
            
            KECAMATAN_ANOMALI.filter(k => k.skor >= 0.75).forEach(k => {
                L.marker([k.lat, k.lng], {
                    icon: L.divIcon({ className: '', html: `<div style="background:#ef4444;color:white;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:bold;white-space:nowrap;box-shadow:0 2px 4px rgba(0,0,0,0.3)">${k.nama}</div>`, iconAnchor: [30, 10] })
                }).addTo(miniMap);
            });
            leafletMaps['mini'] = miniMap;
            setTimeout(() => miniMap.invalidateSize(), 100);
        } catch(e) {
            console.error("Mini Map Error:", e);
        }
    }

    // ---- 2. HEATMAP ANOMALI (Full tab) ----
    if (!leafletMaps['heatmap'] && document.getElementById('heatmap-main-map')) {
        const hmMap = L.map('heatmap-main-map', { zoomControl: true, attributionControl: true })
            .setView(SURABAYA_CENTER, 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(hmMap);
        
        leafletMaps['heatmap'] = hmMap;
        setTimeout(() => { 
            try {
                window.renderTop5Anomali(); 
                // Prevent Canvas getImageData error when display: none
                let mapContainer = document.getElementById('heatmap-main-map');
                if (mapContainer && mapContainer.offsetWidth > 0) {
                    hmMap.invalidateSize(); 
                    window.renderHeatmapLayer(); 
                }
            } catch(e) {
                console.error("Heatmap Render Error:", e);
                const container = document.getElementById('dynamic-top5-container');
                if(container) container.innerHTML = `<div class='p-4 text-error'>Gagal memuat peta: ${e.message}</div>`;
            }
        }, 100);
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
        
        // Fix Leaflet hidden canvas issue when tab becomes visible
        if (tabId === 'heatmap_anomali' && leafletMaps['heatmap']) {
            setTimeout(() => {
                leafletMaps['heatmap'].invalidateSize();
                if (!window.heatmapActiveLayer) {
                    window.renderHeatmapLayer();
                }
            }, 100);
        }
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
    try {
        initDashboard();
    } catch(e) {
        console.error("Dashboard Init Error:", e);
    }
    
    try {
        // Init maps after a short delay to ensure DOM is rendered
        setTimeout(initLeafletMaps, 300);
    } catch(e) {
        console.error("Map Init Error:", e);
    }
    
    try {
        // Populate Grid View
        populateHeatmapGrid();
    } catch(e) {
        console.error("Grid Init Error:", e);
    }
});

function toggleHeatmapView(view) {
    const mapDiv = document.getElementById('heatmap-main-map');
    const gridDiv = document.getElementById('heatmap-grid-view');
    const btnMap = document.getElementById('btn-hm-map');
    const btnGrid = document.getElementById('btn-hm-grid');
    
    if (view === 'map') {
        mapDiv.style.display = 'block';
        gridDiv.style.display = 'none';
        if(btnMap) btnMap.className = "px-4 py-1.5 bg-white shadow-sm rounded-md font-label-lg text-label-lg text-primary flex items-center gap-2";
        if(btnGrid) btnGrid.className = "px-4 py-1.5 font-label-lg text-label-lg text-on-surface-variant flex items-center gap-2 hover:text-primary transition-colors";
        setTimeout(() => { if (leafletMaps['heatmap']) leafletMaps['heatmap'].invalidateSize(); }, 100);
    } else {
        mapDiv.style.display = 'none';
        gridDiv.style.display = 'block';
        if(btnGrid) btnGrid.className = "px-4 py-1.5 bg-white shadow-sm rounded-md font-label-lg text-label-lg text-primary flex items-center gap-2";
        if(btnMap) btnMap.className = "px-4 py-1.5 font-label-lg text-label-lg text-on-surface-variant flex items-center gap-2 hover:text-primary transition-colors";
    }
}

window.heatmapLevelFilters = ['High', 'Medium', 'Low'];
window.heatmapKategoriFilters = ['Honorarium', 'Belanja Modal', 'Perjalanan Dinas', 'Hibah & Bansos'];
window.heatmapActiveLayer = null;
window.heatmapMarkersLayer = null;

window.toggleAnomalyFilter = function(level) {
    if(window.heatmapLevelFilters.includes(level)) {
        window.heatmapLevelFilters = window.heatmapLevelFilters.filter(l => l !== level);
        let icon = document.getElementById('icon-anomali-' + level.toLowerCase());
        if(icon) { icon.innerText = 'radio_button_unchecked'; icon.classList.add('opacity-50'); }
    } else {
        window.heatmapLevelFilters.push(level);
        let icon = document.getElementById('icon-anomali-' + level.toLowerCase());
        if(icon) { icon.innerText = 'check_circle'; icon.classList.remove('opacity-50'); }
    }
    window.renderHeatmapLayer();
    window.renderTop5Anomali();
};

window.renderHeatmapLayer = function() {
    let hmMap = leafletMaps['heatmap'];
    if(!hmMap) return;
    
    if(window.heatmapActiveLayer) hmMap.removeLayer(window.heatmapActiveLayer);
    if(window.heatmapMarkersLayer) hmMap.removeLayer(window.heatmapMarkersLayer);
    
    let filteredData = KECAMATAN_ANOMALI.filter(k => {
        const level = k.skor >= 0.75 ? 'High' : k.skor >= 0.5 ? 'Medium' : 'Low';
        const levelMatch = window.heatmapLevelFilters.includes(level);
        const catMatch = k.kategori && k.kategori.some(cat => window.heatmapKategoriFilters.includes(cat));
        return levelMatch && catMatch;
    });
    
    window.heatmapActiveLayer = L.layerGroup().addTo(hmMap);
    window.heatmapMarkersLayer = L.layerGroup().addTo(hmMap);
    
    if (window.surabayaGeoJSON) {
        L.geoJSON(window.surabayaGeoJSON, {
            style: function(feature) {
                const kecName = feature.properties.KECAMATAN;
                const k = filteredData.find(x => x.nama.toUpperCase() === kecName.toUpperCase());
                if (k) {
                    const isHigh = k.skor >= 0.75;
                    const isMed = k.skor >= 0.5;
                    const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
                    return { color: 'white', weight: 1.5, fillColor: color, fillOpacity: 0.6 };
                }
                return { color: 'white', weight: 1, fillColor: '#e2e8f0', fillOpacity: 0.2 };
            },
            onEachFeature: function(feature, layer) {
                const kecName = feature.properties.KECAMATAN;
                const k = filteredData.find(x => x.nama.toUpperCase() === kecName.toUpperCase());
                if (k) {
                    const isHigh = k.skor >= 0.75;
                    const isMed = k.skor >= 0.5;
                    const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
                    
                    layer.bindTooltip(`<b>${k.nama}</b><br>Skor Anomali: ${(k.skor*100).toFixed(0)}%`);
                    layer.on('click', () => {
                        if (window.openDrillDown) window.openDrillDown(k);
                    });
                }
            }
        }).addTo(window.heatmapActiveLayer);
    } else {
        // Fallback
        filteredData.forEach(k => {
            const isHigh = k.skor >= 0.75;
            const isMed = k.skor >= 0.5;
            const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
            const label = isHigh ? 'KRITIS' : isMed ? 'WASPADA' : 'AMAN';
            
            L.circle([k.lat, k.lng], {
                color: color, fillColor: color, fillOpacity: 0.35, radius: 1800, weight: 1
            }).addTo(window.heatmapActiveLayer);
        });
    }
    
    // Labels for high risk only
    filteredData.forEach(k => {
        const isHigh = k.skor >= 0.75;
        const isMed = k.skor >= 0.5;
        const color = isHigh ? '#ef4444' : isMed ? '#f59e0b' : '#22c55e';
        const label = isHigh ? 'KRITIS' : isMed ? 'WASPADA' : 'AMAN';
        
        if(!isMed && filteredData.length > 10) return;
        
        L.marker([k.lat, k.lng], {
            icon: L.divIcon({ className: '', html: `<div style="background:${color};color:white;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.4)">${k.nama}</div>`, iconAnchor: [40, 10] })
        }).on('click', () => {
            if (window.openDrillDown) window.openDrillDown(k);
        }).addTo(window.heatmapMarkersLayer);
    });
    
    // Also update grid
    if (window.renderHeatmapGrid) {
        window.renderHeatmapGrid(filteredData);
    }
    
    // Generate Smart Insight
    if (window.generateSmartInsight) {
        window.generateSmartInsight(filteredData);
    }
    
    let totalEl = document.getElementById('heatmap-anomali-total');
    if(totalEl) totalEl.innerText = filteredData.length;
};

window.renderTop5Anomali = function() {
    const container = document.getElementById('dynamic-top5-container');
    if(!container) return;
    
    // Always use the full dataset for Top 5 SKPD, not affected by map filters
    let sorted = [...KECAMATAN_ANOMALI].sort((a,b) => b.skor - a.skor).slice(0, 5);
    
    let html = '';
    sorted.forEach((k, idx) => {
        let isHigh = k.skor >= 0.75;
        let isMed = k.skor >= 0.5;
        let colorClass = isHigh ? 'error' : isMed ? 'amber-500' : 'primary';
        let bgClass = isHigh ? 'bg-error text-on-error' : isMed ? 'bg-amber-500 text-white' : 'bg-primary text-on-primary';
        let icon = isHigh ? 'warning' : isMed ? 'report' : 'info';
        
        let skpdMap = ['Belanja Modal', 'Honorarium', 'Bansos', 'Belanja Jasa', 'Pemeliharaan'];
        let skpd = skpdMap[idx % skpdMap.length];
        let val = (k.skor * 15).toFixed(1) + 'M';
        let pct = Math.round(k.skor * 100);
        
        html += `
        <div onclick="window.flyToKecamatan(${k.lat}, ${k.lng})" class="p-4 bg-surface-container-lowest rounded-xl border border-${colorClass === 'amber-500' ? 'outline-variant' : colorClass+'/30'} hover:border-${colorClass} transition-colors cursor-pointer group">
            <div class="flex items-center justify-between mb-3">
                <span class="w-6 h-6 rounded ${bgClass} flex items-center justify-center font-bold text-xs">0${idx+1}</span>
                <span class="material-symbols-outlined text-${colorClass} text-[20px]">${icon}</span>
            </div>
            <h4 class="font-title-md text-title-md mb-1">${k.nama}</h4>
            <div class="flex items-center justify-between">
                <span class="font-label-sm text-label-sm text-on-surface-variant">${skpd}</span>
                <span class="font-bold text-${colorClass}">Rp ${val}</span>
            </div>
            <div class="w-full bg-surface-container mt-3 h-1.5 rounded-full overflow-hidden">
                <div class="bg-${colorClass} h-full rounded-full" style="width: ${pct}%"></div>
            </div>
        </div>`;
    });
    
    if(sorted.length === 0) {
        html = '<div class="p-4 text-center text-on-surface-variant">Tidak ada data sesuai filter.</div>';
    }
    
    container.innerHTML = html;
};

window.flyToKecamatan = function(lat, lng) {
    let hmMap = leafletMaps['heatmap'];
    if(hmMap) {
        hmMap.flyTo([lat, lng], 15, { duration: 1.5 });
    }
};

window.openReportModal = function() {
    const modal = document.getElementById('report-modal');
    if(modal) {
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.remove('opacity-0'), 10);
        const content = document.getElementById('report-modal-content');
        if(content) content.classList.remove('scale-95');
    }
};

window.closeReportModal = function() {
    const modal = document.getElementById('report-modal');
    if(modal) {
        modal.classList.add('opacity-0');
        const content = document.getElementById('report-modal-content');
        if(content) content.classList.add('scale-95');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }
};

window.submitReport = function() {
    window.closeReportModal();
    const toast = document.getElementById('toast-notification');
    if(toast) {
        document.getElementById('toast-message').innerText = 'Laporan berhasil dibuat dan masuk antrean investigasi.';
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => {
            toast.classList.add('translate-y-20', 'opacity-0');
        }, 3000);
    }
};

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
        tbodyUtama.innerHTML = '<tr><td colspan="7" class="text-center py-4">Tidak ada anomali terdeteksi</td></tr>';
    } else {
        paginated.forEach((row, idx) => {
            tbodyUtama.appendChild(createAnomalyRow(row, startIndex + idx + 1));
        });
    }
    
    const infoSpan = document.getElementById('anomaly-pagination-info');
    if(infoSpan) {
        infoSpan.innerText = `Menampilkan ${Math.min(startIndex + 1, window.tableAnomalies.length)}-${Math.min(endIndex, window.tableAnomalies.length)} dari ${window.tableAnomalies.length} anomali`;
    }
    
    // Generate Pagination Controls
    const totalPages = Math.ceil(window.tableAnomalies.length / ITEMS_PER_PAGE);
    const paginationContainer = document.getElementById('anomaly-pagination-controls');
    if(paginationContainer) {
        let html = `<button onclick="prevAnomalyPage()" class="w-8 h-8 flex items-center justify-center rounded border border-outline-variant bg-white hover:bg-surface-container transition-colors disabled:opacity-50" ${window.currentAnomalyPage === 1 ? 'disabled' : ''}><span class="material-symbols-outlined text-[18px]">chevron_left</span></button>`;
        
        for(let i = 1; i <= totalPages; i++) {
            if(totalPages > 7) {
                if(i !== 1 && i !== totalPages && Math.abs(i - window.currentAnomalyPage) > 1) {
                    if(i === 2 || i === totalPages - 1) html += `<span class="w-8 h-8 flex items-center justify-center text-on-surface-variant">...</span>`;
                    continue;
                }
            }
            const activeClass = i === window.currentAnomalyPage ? 'bg-primary text-white border-primary' : 'bg-white text-on-surface-variant border-outline-variant hover:bg-surface-container';
            html += `<button onclick="goToAnomalyPage(${i})" class="w-8 h-8 flex items-center justify-center rounded border ${activeClass} transition-colors text-label-sm font-bold">${i}</button>`;
        }
        
        html += `<button onclick="nextAnomalyPage()" class="w-8 h-8 flex items-center justify-center rounded border border-outline-variant bg-white hover:bg-surface-container transition-colors disabled:opacity-50" ${window.currentAnomalyPage === totalPages ? 'disabled' : ''}><span class="material-symbols-outlined text-[18px]">chevron_right</span></button>`;
        paginationContainer.innerHTML = html;
    }
};

window.goToAnomalyPage = function(page) {
    window.currentAnomalyPage = page;
    window.renderAnomalyTable();
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

window.filterAnomalyTable = function() {
    const input = document.getElementById('search-utama');
    const statusSelect = document.getElementById('filter-status-utama');
    
    const query = input ? input.value.toLowerCase() : '';
    const statusFilter = statusSelect ? statusSelect.value : '';
    
    if(!window.originalTableAnomalies) return;
    
    window.tableAnomalies = window.originalTableAnomalies.filter(row => {
        let matchQuery = true;
        if(query !== '') {
            matchQuery = (row.uraian_belanja && row.uraian_belanja.toLowerCase().includes(query)) ||
                         (row.nama_skpd && row.nama_skpd.toLowerCase().includes(query)) ||
                         (row.jenis_pengadaan && row.jenis_pengadaan.toLowerCase().includes(query));
        }
        
        let matchStatus = true;
        if(statusFilter !== '') {
            let score = parseFloat(row.anomaly_score || 0);
            let statusStr = score > 0.6 ? 'outlier' : 'warning';
            matchStatus = statusStr === statusFilter;
        }
        
        return matchQuery && matchStatus;
    });
    
    window.currentAnomalyPage = 1;
    window.renderAnomalyTable();
};


// --- NEW SENTIMENT FUNCTIONS ---

window.activeSentimentFilter = { hashtag: null, keyword: '', sentiments: ['Positif', 'Negatif', 'Netral'] };

window.applySentimentFilter = function() {
    let kw = document.getElementById('sentiment-filter-keyword').value;
    let sents = [];
    if(document.getElementById('filter-cb-positif').checked) sents.push('Positif');
    if(document.getElementById('filter-cb-negatif').checked) sents.push('Negatif');
    if(document.getElementById('filter-cb-netral').checked) sents.push('Netral');
    
    window.activeSentimentFilter.keyword = kw;
    window.activeSentimentFilter.sentiments = sents;
    
    document.getElementById('sentiment-filter-panel').classList.add('hidden');
    window.renderSentimentFeed(window.sentimentData);
};

window.setHashtagFilter = function(hashtag) {
    window.activeSentimentFilter.hashtag = hashtag;
    window.renderSentimentFeed(window.sentimentData);
};

window.renderSentimentFeed = function(data) {
    const feedContainer = document.getElementById('sentiment-feed-container');
    if(!feedContainer) return;
    feedContainer.innerHTML = '';
    
    let renderCount = 0;
    let filter = window.activeSentimentFilter;
    
    data.forEach(row => {
        if(row.sentiment_label && (row.teks || row.text)) {
            let txt = row.teks || row.text;
            let labelText = row.sentiment_label || 'Netral';
            
            // Check filters
            if (filter.hashtag && !txt.toLowerCase().includes(filter.hashtag.toLowerCase())) return;
            if (filter.keyword && !txt.toLowerCase().includes(filter.keyword.toLowerCase())) return;
            if (filter.sentiments && filter.sentiments.length > 0 && !filter.sentiments.includes(labelText)) return;
            
            renderCount++;
            
            let labelColor = 'sentiment-neutral';
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
    });

    if (renderCount === 0) {
        let msg = filter.hashtag ? `Topik #${filter.hashtag}` : `Filter saat ini`;
        feedContainer.innerHTML = `<div class="p-8 text-center text-on-surface-variant">Tidak ada tanggapan ditemukan untuk ${msg}.</div>`;
    }
};
window.extractTrendingTopics = function(data) {
    let wordCounts = {};
    const stopwords = ['yang', 'di', 'ke', 'dari', 'pada', 'dan', 'atau', 'dengan', 'untuk', 'ini', 'itu', 'juga', 'dalam', 'tidak', 'ada', 'bisa', 'akan', 'sudah', 'saya', 'kita', 'kami', 'mereka', 'sebagai', 'oleh', 'kepada', 'bagi', 'karena', 'banyak', 'sangat', 'buat', 'lebih', 'lagi', 'nya', 'aku', 'kamu', 'dia', 'sama', 'apa', 'terus', 'kalau', 'aja', 'jadi', 'kalo', 'udah', 'bikin', 'kok', 'tapi', 'masih'];
    
    data.forEach(row => {
        let txt = row.teks || row.text;
        if(txt) {
            let words = txt.toLowerCase().match(/[a-z]+/g) || [];
            words.forEach(w => {
                if(w.length > 4 && !stopwords.includes(w)) {
                    wordCounts[w] = (wordCounts[w] || 0) + 1;
                }
            });
        }
    });
    
    let sortedWords = Object.entries(wordCounts).sort((a,b) => b[1] - a[1]).slice(0, 7);
    
    const container = document.getElementById('trending-topics-container');
    if(container) {
        let html = '';
        sortedWords.forEach(sw => {
            let word = sw[0].charAt(0).toUpperCase() + sw[0].slice(1);
            let count = sw[1];
            html += `<span onclick="window.setHashtagFilter('${word}')" class="px-4 py-2 bg-surface-container-high text-on-surface rounded-full font-label-lg text-label-lg flex items-center gap-2 cursor-pointer hover:bg-primary hover:text-on-primary transition-colors shadow-sm border border-outline-variant">#${word} <span class="bg-on-surface/10 px-2 py-0.5 rounded text-[10px] font-bold">${count}</span></span>`;
        });
        html += `<span onclick="window.setHashtagFilter(null)" class="px-4 py-2 bg-error-container text-on-error-container rounded-full font-label-lg text-label-lg flex items-center gap-2 cursor-pointer hover:bg-error hover:text-white transition-colors shadow-sm">Clear Filter</span>`;
        container.innerHTML = html;
    }
};



window.renderSentimentChart = function(data, range='day') {
    const ctx = document.getElementById('sentiment-trend-chart');
    if(!ctx) return;
    if(!data || data.length === 0) return;
    
    let dateMap = {};
    data.forEach(row => {
        if(!row.tanggal) return;
        let dStrRaw = row.tanggal;
        // Fix string if needed
        let d = new Date(dStrRaw);
        if (isNaN(d.getTime())) return;
        
        let dStr;
        if(range === 'day') {
            dStr = d.toISOString().split('T')[0];
        } else if(range === 'week') {
            let dClone = new Date(d);
            dClone.setDate(dClone.getDate() - dClone.getDay()); 
            dStr = dClone.toISOString().split('T')[0]; 
        } else if(range === 'month') {
            dStr = d.toISOString().substring(0, 7); 
        } else if(range === 'year') {
            dStr = d.getFullYear().toString();
        }
        
        if(!dateMap[dStr]) dateMap[dStr] = { Positif: 0, Negatif: 0, Netral: 0 };
        let label = row.sentiment_label || 'Netral';
        if(dateMap[dStr][label] !== undefined) dateMap[dStr][label]++;
    });
    
    let sortedDates = Object.keys(dateMap).sort();
    
    let limit = 30; 
    if(range === 'week') limit = 12; 
    if(range === 'month') limit = 12; 
    if(range === 'year') limit = 5;   
    
    if(sortedDates.length > limit) sortedDates = sortedDates.slice(sortedDates.length - limit);
    
    let labels = [];
    let posData = [];
    let negData = [];
    
    sortedDates.forEach(d => {
        let labelStr = d;
        if(range === 'day' || range === 'week') {
            let dateObj = new Date(d);
            labelStr = dateObj.toLocaleDateString('id-ID', {day: 'numeric', month: 'short'});
            if(range === 'week') labelStr = 'Pekan ' + labelStr;
        } else if(range === 'month') {
            let parts = d.split('-');
            let dateObj = new Date(parts[0], parseInt(parts[1])-1, 1);
            labelStr = dateObj.toLocaleDateString('id-ID', {month: 'long', year: 'numeric'});
        }
        
        labels.push(labelStr);
        posData.push(dateMap[d].Positif);
        negData.push(dateMap[d].Negatif);
    });
    
    ['day', 'week', 'month', 'year'].forEach(r => {
        let btn = document.getElementById('btn-chart-' + r);
        if(btn) {
            if(r === range) {
                btn.className = "px-3 py-1 rounded-md text-label-sm font-bold bg-white shadow-sm text-primary transition-all";
            } else {
                btn.className = "px-3 py-1 rounded-md text-label-sm font-bold text-on-surface-variant hover:text-primary transition-all";
            }
        }
    });

    if(window.sentimentChartInst) {
        window.sentimentChartInst.destroy();
    }
    
    window.sentimentChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Positif',
                    data: posData,
                    borderColor: '#005faf',
                    backgroundColor: 'rgba(0, 95, 175, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Negatif',
                    data: negData,
                    borderColor: '#ba1a1a',
                    backgroundColor: 'rgba(186, 26, 26, 0.1)',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#e0e0e0' } },
                x: { grid: { display: false } }
            }
        }
    });
};

window.refreshSentiment = function() {
    const feedContainer = document.getElementById('sentiment-feed-container');
    if(feedContainer) feedContainer.innerHTML = '<div class="p-8 text-center text-on-surface-variant"><span class="material-symbols-outlined text-[32px] animate-spin mb-2">sync</span><p>Memuat live updates...</p></div>';
    
    fetch('/api/sentiment')
        .then(response => response.json())
        .then(data => {
            window.sentimentData = data;
            
            let negativeCount = 0, total = 0, positifCount = 0, netralCount = 0;
            data.forEach(row => {
                if(row.sentiment_label && (row.teks || row.text)) {
                    total++;
                    if(row.sentiment_label === 'Positif') positifCount++;
                    else if(row.sentiment_label === 'Negatif') negativeCount++;
                    else if(row.sentiment_label === 'Netral') netralCount++;
                }
            });
            
            if(total > 0) {
                let pctNeg = Math.round((negativeCount / total) * 100);
                const el = document.getElementById('kpi-sentimen');
                if(el) el.innerHTML = `${pctNeg}% <span class="text-title-md font-normal text-on-surface-variant">Netral/Negatif</span>`;

                let pctPos = Math.round((positifCount / total) * 100);
                let pctNet = Math.round((netralCount / total) * 100);
                let pctNegOnly = pctNeg;
                let gaugeScoreNum = (pctPos * 1.0 + pctNet * 0.5);
                let gaugeScore = gaugeScoreNum.toFixed(1);

                const elGauge = document.getElementById('sentiment-gauge-value');
                if(elGauge) elGauge.innerText = gaugeScore;

                const arcGauge = document.getElementById('sentiment-gauge-arc');
                if(arcGauge) arcGauge.style.strokeDashoffset = 126 - (gaugeScoreNum / 100) * 126;

                const labelGauge = document.getElementById('sentiment-gauge-label');
                if(labelGauge) {
                    if (gaugeScoreNum >= 75) {
                        labelGauge.innerText = 'Sangat Baik';
                        labelGauge.className = 'text-label-md text-primary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#005faf'; 
                    } else if (gaugeScoreNum >= 50) {
                        labelGauge.innerText = 'Baik';
                        labelGauge.className = 'text-label-md text-primary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#005faf'; 
                    } else if (gaugeScoreNum >= 35) {
                        labelGauge.innerText = 'Cukup';
                        labelGauge.className = 'text-label-md text-secondary font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#f59e0b'; 
                    } else {
                        labelGauge.innerText = 'Buruk';
                        labelGauge.className = 'text-label-md text-error font-bold uppercase tracking-widest mt-1';
                        arcGauge.style.stroke = '#ba1a1a'; 
                    }
                }

                const interactionText = document.getElementById('sentiment-interaction-text');
                if(interactionText) interactionText.innerText = `Berdasarkan ${total.toLocaleString()} interaksi media sosial & aduan masyarakat minggu ini.`;

                const elPos = document.getElementById('sentiment-positif-pct');
                if(elPos) elPos.innerText = pctPos + '%';
                const elNet = document.getElementById('sentiment-netral-pct');
                if(elNet) elNet.innerText = pctNet + '%';
                const elNegL = document.getElementById('sentiment-negatif-pct');
                if(elNegL) elNegL.innerText = pctNegOnly + '%';
            }
            
            window.extractTrendingTopics(data);
            window.renderSentimentFeed(data);
            window.renderSentimentChart(data);
        });
};

window.exportSentimentData = function() {
    if(!window.sentimentData) return alert('Data belum dimuat.');
    let csv = "tanggal,sumber,teks,sentiment_label,sentiment_score\n";
    window.sentimentData.forEach(row => {
        let txt = (row.teks || row.text || "").replace(/"/g, '""');
        csv += `"${row.tanggal || ''}","${row.sumber || ''}","${txt}","${row.sentiment_label || ''}","${row.sentiment_score || ''}"\n`;
    });
    let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "sentimen_publik.csv";
    link.click();
};

function initDashboard() {
    // 1. Fetch gold_skpd_summary.csv for KPI 1 (Total Anggaran)
    fetch('/api/summary')
        .then(response => response.json())
        .then(data => {
            let totalAnggaran = 0;
            data.forEach(row => {
                if(row.total_pagu) {
                    totalAnggaran += parseFloat(row.total_pagu);
                }
            });
            const el = document.getElementById('kpi-total-anggaran');
            if(el && totalAnggaran > 0) el.innerText = formatRupiah(totalAnggaran);
        });

    // 2. Fetch apbd_scored.csv for KPI 2 & Tables & Heatmap
    fetch('/api/anomalies')
        .then(response => response.json())
        .then(data => {
            data = data.filter(r => r.id_transaksi); // filter empty rows
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
            window.originalTableAnomalies = [...anomalies];
            window.tableAnomalies = [...anomalies];
            window.tableAnomalies.sort((a, b) => parseFloat(b.ensemble_score || b.anomaly_score || 0) - parseFloat(a.ensemble_score || a.anomaly_score || 0));
            window.originalTableAnomalies.sort((a, b) => parseFloat(b.ensemble_score || b.anomaly_score || 0) - parseFloat(a.ensemble_score || a.anomaly_score || 0));
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
        });


    // 3. Fetch sentiment_results.csv for KPI 3 & FEED
    window.refreshSentiment();

    // 4. Fetch gold_jejaring_vendor.csv for Jejaring Entitas
    fetch('/api/vendors')
        .then(response => response.json())
        .then(data => {
            data = data.filter(r => r.nama_vendor);
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



function createAnomalyRow(row, index = '-') {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-surface-container transition-colors';
    
    let score = parseFloat(row.anomaly_score || 0);
    let statusLabel = (score > 0.4 || String(row.is_flagged) === '1') ? 
        '<span class="px-3 py-1 bg-error text-on-error rounded-full text-label-sm font-bold uppercase tracking-tighter">OUTLIER</span>' : 
        '<span class="px-3 py-1 bg-amber-500 text-white rounded-full text-label-sm font-bold uppercase tracking-tighter">WARNING</span>';
    
    let zScoreVal = parseFloat(row.zscore_per_rekening);
    let zScoreBadgeClass = Math.abs(zScoreVal) > 2 ? 'bg-error-container text-on-error-container' : 'bg-amber-100 text-amber-800';
    let zScoreStr = isNaN(zScoreVal) ? '-' : zScoreVal.toFixed(1);

    let realisasiVal = parseFloat(row.realisasi || 0);

    tr.innerHTML = `
        <td class="px-6 py-4 font-label-md text-label-md text-on-surface-variant">${index}</td>
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
    
    // Find SKPD. It's now in the second td because of the index column.
    let skpdEl = btn.closest('tr').querySelector('td:nth-child(2) p:nth-child(2)');
    let skpd = skpdEl ? skpdEl.innerText : 'SKPD Tidak Diketahui';
    
    // Set UI elements in the Detail Anomali tab
    let elId = document.getElementById('detail-id-header');
    if(elId) elId.innerText = id || 'TRX-UNKNOWN';
    
    let elZscore = document.getElementById('detail-zscore');
    if(elZscore) elZscore.innerText = zscore || '-';
    
    let elKat = document.getElementById('detail-kategori');
    if(elKat) elKat.innerText = kategori || '-';
    
    let elReal = document.getElementById('detail-realisasi');
    if(elReal) elReal.innerText = realisasi || '-';
    
    let elSkpd = document.getElementById('detail-skpd-name');
    if(elSkpd) elSkpd.innerText = skpd;

    // Optional: Fetch detail data from backend if available
    // fetch(`/api/silver/lpse/detail?id=${id}`).then(...)
    
    // Auto switch to Detail tab
    if (window.switchTab) {
        window.switchTab('detail_anomali');
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
    window.heatmapKategoriFilters = Array.from(checkedBoxes).map(cb => cb.value);
    
    // Just re-render the unified heatmap layer and it will handle both map and grid
    window.renderHeatmapLayer();
};

window.renderHeatmapGrid = function(filtered) {
    const tbody = document.getElementById('heatmap-grid-tbody');
    if (!tbody) return;
    
    const sorted = [...filtered].sort((a, b) => b.skor - a.skor);
    if (sorted.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="p-4 text-center text-on-surface-variant">Tidak ada data untuk kategori yang dipilih</td></tr>';
    } else {
        tbody.innerHTML = sorted.map(k => {
            const colorClass = k.skor >= 0.75 ? 'text-error bg-error/10' : k.skor >= 0.5 ? 'text-amber-600 bg-amber-500/10' : 'text-green-600 bg-green-500/10';
            const label = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
            const cats = k.kategori ? k.kategori.join(', ') : '-';
            
            return `
                <tr class="hover:bg-surface-container-lowest transition-colors">
                    <td class="p-4 font-bold">${k.nama}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded text-xs font-bold ${colorClass}">${label}</span>
                    </td>
                    <td class="p-4 text-xs text-on-surface-variant">${cats}</td>
                    <td class="p-4 text-right font-mono">${(k.skor*100).toFixed(1)}%</td>
                </tr>
            `;
        }).join('');
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
    if (!window.jspdf || !window.jspdf.jsPDF) {
        alert("Pustaka PDF sedang dimuat atau tidak tersedia. Pastikan koneksi internet aktif.");
        return;
    }
    
    let filteredData = KECAMATAN_ANOMALI.filter(k => {
        const level = k.skor >= 0.75 ? 'High' : k.skor >= 0.5 ? 'Medium' : 'Low';
        const levelMatch = window.heatmapLevelFilters.includes(level);
        const catMatch = k.kategori && k.kategori.some(cat => window.heatmapKategoriFilters.includes(cat));
        return levelMatch && catMatch;
    });
    
    const doc = new window.jspdf.jsPDF();
    doc.setFontSize(16);
    doc.text("Laporan Deteksi Anomali APBD Surabaya", 14, 20);
    
    doc.setFontSize(10);
    doc.text(`Tanggal Unduh: ${new Date().toLocaleDateString('id-ID')}`, 14, 30);
    doc.text(`Filter Level Aktif: ${window.heatmapLevelFilters.join(', ')}`, 14, 36);
    doc.text(`Kategori Belanja Aktif: ${window.heatmapKategoriFilters.join(', ')}`, 14, 42);
    
    const tableData = filteredData.map((k, i) => {
        const status = k.skor >= 0.75 ? 'KRITIS' : k.skor >= 0.5 ? 'WASPADA' : 'AMAN';
        const cats = k.kategori ? k.kategori.join(', ') : '-';
        return [i + 1, k.nama, `${(k.skor*100).toFixed(1)}%`, status, cats];
    });
    
    doc.autoTable({
        startY: 50,
        head: [['No', 'Kecamatan', 'Skor Anomali', 'Status', 'Pos Belanja Terindikasi']],
        body: tableData,
        theme: 'grid',
        headStyles: { fillColor: [52, 168, 83] }, // primary color approximate
        styles: { fontSize: 9 }
    });
    
    doc.save("Laporan_Anomali_APBD_Surabaya.pdf");
    
    // Show toast
    const toast = document.getElementById('toast-notification');
    const msg = document.getElementById('toast-message');
    if(toast && msg) {
        msg.innerText = "Laporan PDF berhasil diunduh!";
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
    }
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

window.originalKecamatanData = null;
window.updateTimeSimulation = function(month) {
    if (!window.originalKecamatanData) {
        window.originalKecamatanData = JSON.parse(JSON.stringify(KECAMATAN_ANOMALI));
    }
    
    document.getElementById('time-slider-label').innerText = `Bulan: ${month}`;
    
    const ratio = parseInt(month) / 12.0;
    
    KECAMATAN_ANOMALI.forEach((k, i) => {
        const orig = window.originalKecamatanData[i];
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

window.openSettingsModal = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            modal.querySelector('#settings-modal-content').classList.remove('scale-95');
        }, 10);
    }
};

window.closeSettingsModal = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.add('opacity-0');
        modal.querySelector('#settings-modal-content').classList.add('scale-95');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }
};

window.saveSettings = function() {
    const btn = document.getElementById('btn-save-settings');
    btn.innerHTML = `<span class="material-symbols-outlined animate-spin">refresh</span> Menyimpan...`;
    btn.classList.add('opacity-80', 'cursor-not-allowed');
    
    setTimeout(() => {
        btn.innerHTML = `Simpan`;
        btn.classList.remove('opacity-80', 'cursor-not-allowed');
        window.closeSettingsModal();
        
        // Show success toast
        const toast = document.getElementById('toast-notification');
        const msg = document.getElementById('toast-message');
        if(toast && msg) {
            msg.innerText = "Konfigurasi Lakehouse Berhasil Disimpan!";
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
        }
    }, 1500);
};

