import re

html_file = r'src/dashboard/index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'(<div id="tab-content-detail_anomali" class="tab-pane".*?>\s*)(.*?)(?=^\s*<div id="tab-content-peta_spasial")', re.DOTALL | re.MULTILINE)

new_content = r'''<!-- TopNavBar Integration -->
  <header class="flex justify-between items-center w-full px-container-margin-desktop h-16 sticky top-0 z-50 bg-surface-container-lowest dark:bg-surface-container-low border-b border-outline-variant dark:border-outline">
      <div class="flex items-center gap-4">
          <span class="font-headline-lg text-headline-lg font-bold text-primary dark:text-primary-fixed-dim">Investigasi Forensik</span>
          <div class="h-6 w-px bg-outline-variant mx-2"></div>
          <div class="flex items-center gap-1 text-on-surface-variant">
              <span class="material-symbols-outlined text-[20px]">gavel</span>
              <span class="font-label-lg text-label-lg" id="detail-id-header">TRX-000000</span>
          </div>
      </div>
      <div class="flex items-center gap-4">
          <button onclick="alert('Mengekspor laporan investigasi...')" class="px-4 py-2 bg-surface-container-highest text-on-surface rounded-full font-label-lg text-label-lg flex items-center gap-2 hover:bg-outline-variant transition-colors">
              <span class="material-symbols-outlined text-[18px]">download</span> Unduh Dossier
          </button>
      </div>
  </header>

  <!-- Dashboard Canvas -->
  <div class="p-container-margin-desktop space-y-6 max-w-[1440px] mx-auto w-full">
      
      <!-- Top Row: Overview Cards -->
      <section class="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          <div class="bg-error-container p-6 rounded-xl border border-red-200 flex flex-col justify-between group hover:shadow-lg transition-shadow md:col-span-1">
              <div class="flex justify-between items-start">
                  <div class="p-3 bg-error text-on-error rounded-lg">
                      <span class="material-symbols-outlined">warning</span>
                  </div>
                  <span class="text-error font-label-sm text-label-sm flex items-center bg-white/50 px-2 py-1 rounded-full font-bold">Status Kritis</span>
              </div>
              <div class="mt-4">
                  <p class="font-label-lg text-label-lg text-on-error-container/70">Skor Z-Score</p>
                  <h3 id="detail-zscore" class="font-headline-lg text-headline-lg text-on-error-container">-</h3>
              </div>
          </div>

          <div class="bg-surface-container-lowest p-6 rounded-xl border border-outline-variant flex flex-col justify-between group hover:shadow-lg transition-shadow md:col-span-3">
              <h4 class="font-title-md text-title-md mb-4 text-on-surface-variant">Informasi Transaksi</h4>
              <div class="grid grid-cols-2 gap-4">
                  <div>
                      <p class="text-sm text-outline">Kategori Belanja</p>
                      <p id="detail-kategori" class="font-body-lg text-body-lg font-semibold">-</p>
                  </div>
                  <div>
                      <p class="text-sm text-outline">Nilai Realisasi</p>
                      <p id="detail-realisasi" class="font-body-lg text-body-lg font-semibold text-primary">-</p>
                  </div>
                  <div class="col-span-2">
                      <p class="text-sm text-outline">Unit Kerja (SKPD)</p>
                      <p id="detail-skpd" class="font-body-lg text-body-lg font-semibold">Dinas Tidak Diketahui</p>
                  </div>
              </div>
          </div>

      </section>

      <!-- Bottom Row: Timeline & Actions -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-surface-container-lowest p-6 rounded-xl border border-outline-variant md:col-span-2">
              <h4 class="font-title-md text-title-md mb-6">Jejak Forensik (Simulasi)</h4>
              <div class="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-outline-variant before:to-transparent">
                  <div class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div class="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-error text-on-error shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow">
                          <span class="material-symbols-outlined text-[18px]">policy</span>
                      </div>
                      <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-lg border border-outline-variant bg-surface-container-lowest shadow-sm">
                          <div class="flex items-center justify-between space-x-2 mb-1">
                              <div class="font-bold text-on-surface">Deteksi Anomali</div>
                              <time class="font-label-sm text-on-surface-variant">Otomatis</time>
                          </div>
                          <div class="text-on-surface-variant font-body-sm">Sistem mendeteksi deviasi pengeluaran sangat ekstrem melebihi ambang batas historis.</div>
                      </div>
                  </div>
              </div>
          </div>
          
          <div class="bg-surface-container-lowest p-6 rounded-xl border border-outline-variant flex flex-col gap-4">
              <h4 class="font-title-md text-title-md mb-2">Rekomendasi Tindakan</h4>
              
              <button onclick="alert('Melakukan pemblokiran...')" class="w-full py-3 bg-error text-on-error rounded-lg font-label-lg flex justify-center items-center gap-2 hover:opacity-90 transition-opacity">
                  <span class="material-symbols-outlined">block</span> Bekukan Anggaran
              </button>
              
              <button onclick="alert('Membuka panel audit BPK...')" class="w-full py-3 bg-primary text-on-primary rounded-lg font-label-lg flex justify-center items-center gap-2 hover:opacity-90 transition-opacity">
                  <span class="material-symbols-outlined">fact_check</span> Eskalasi ke BPK
              </button>

              <button onclick="switchTab('dashboard_utama', document.querySelector('.nav-item[data-id=\'dashboard_utama\']'))" class="w-full py-3 mt-auto bg-surface-container text-on-surface rounded-lg font-label-lg flex justify-center items-center gap-2 hover:bg-surface-container-highest transition-colors border border-outline-variant">
                  <span class="material-symbols-outlined">arrow_back</span> Kembali ke Dasbor
              </button>
          </div>
      </section>

  </div>
</div>
'''

new_html = pattern.sub(r'\1' + new_content, content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("UI Updated successfully.")
