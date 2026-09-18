# RL Tabanlı Quadrotor Kontrolünde Kontrollü Dinamik Kayması Altında Transfer

Bu depo, **TOK 2026** bildirisi *"Pekiştirmeli Öğrenme Tabanlı Quadrotor Kontrolünde Kontrollü Dinamik Kayması Altında Transfer Genellenebilirliğinin Analizi"* çalışmasının deney kodunu, dinamik parametrelerini ve sonuç verilerini içerir.

Kod, [RLtools](https://github.com/rl-tools/rl-tools) kütüphanesi ve L2F (Learning to Fly) quadrotor simülatörü üzerine kuruludur.

---

## Deney Kurulumu

- **Simülatör:** L2F (RLtools), analitik rigid-body dinamiği
- **Model:** PX4 x500 quadrotor (`x500_sim` / `x500_real` dinamikleri)
- **Algoritma:** Soft Actor-Critic (SAC), MLP aktör/eleştirmen (32 gizli birim)
- **Gözlem:** pozisyon hatası (3) + rotation matrix (9) + doğrusal hız (3) + açısal hız (3) + 16 adımlık aksiyon geçmişi (64) = 82 boyut
- **Eylem:** 4 boyutlu, [−1, 1] normalize motor komutları
- **dt = 0,01 s (100 Hz)**, epizot **500 adım (5 s)**
- Batch 64, γ = 0,99, hedef entropi = −4, öğrenme hızı = 1×10⁻³
- Ödül: L2F "squared" maliyet fonksiyonu (pozisyon, oryantasyon, hız, aksiyon terimleri)

---

## Dosyalar

| Dosya | Açıklama |
|---|---|
| `l2f_sac.cpp` | Ana eğitim / ince-ayar kaynağı. Deney koşulu **derleme bayraklarıyla** seçilir (aşağıya bakın). |
| `sac.cpp` | RLtools Zoo SAC reçetesi (referans) |
| `x500_sim.h` | x500 simülasyon dinamikleri (Phase 2 kaynak; k_f = 8,74, τ = 0,03 s, T2W = 1,78) |
| `x500_real.h` | x500 gerçek-yakın dinamikler (Phase 1) |
| `plot_learning_curves.py` | Öğrenme eğrisi / şekil üretimi |
| `learning_curves_seed0.csv` | Nominal öğrenme eğrisi verisi |
| `learning_curves_largegap_seed0.csv` | Büyük dinamik kayma altında öğrenme eğrisi |
| `transfer_metrics_seed0.csv` | Transfer metrikleri (jumpstart / final / eşiğe-ulaşma) |
| `transfer_metrics_largegap_seed0.csv` | Büyük kayma transfer metrikleri |
| `mass_sweep_results.csv`, `mass_sweep_curriculum.csv` | Kütle taraması sonuçları |
| `train_seed1.log`, `train_seed2.log` | Eğitim logları |
| `train_seeds.sh` | Çok-tohumlu eğitim betiği |

---

## Deney Koşulları (derleme bayrakları)

`l2f_sac.cpp` tek dosyada üç koşulu ve ince ayarı destekler:

**Phase 1 — Domain Randomization ablasyonu**
- `-DCOND_NODR` : randomizasyon yok (baseline)
- `-DCOND_DR`   : domain randomization açık (kütle, atalet, itki-ağırlık)

**Phase 2 — Kontrollü dinamik kayması + transfer**
- `-DCOND_COMPLEX` : deterministik hedef kayması (kütle ×1,3, atalet ×1,3, motor τ ×2,0 → T2W 1,78 → 1,37)
- `-DFINETUNE`     : ince ayar reçetesi (ısınma **64 / eleştirmen 5000 / aktör 25000** adım)

**Çalıştırma**
```
./l2f_sac <seed> [onceden_egitilmis_aktor.h5] [critics.h5]
```
- `seed` — rastgele tohum
- `[aktor.h5]` — (zero-shot / ince ayar için) önceden eğitilmiş aktör
- `[critics.h5]` — (ince ayar için) eleştirmen transferi

No-DR koşumu, ince ayar için eleştirmenleri `critics.h5` olarak kaydeder.

---

## Bağımlılıklar

- [RLtools](https://github.com/rl-tools/rl-tools) — L2F simülatörü, SAC, sinir ağı katmanları
- HDF5 — checkpoint kaydetme / yükleme
- Python + matplotlib — çizim (`plot_learning_curves.py`)

---

## Atıf

> G. N. Kolçak ve B. Yılmaz, "Pekiştirmeli Öğrenme Tabanlı Quadrotor Kontrolünde Kontrollü Dinamik Kayması Altında Transfer Genellenebilirliğinin Analizi," *TOK 2026 — Otomatik Kontrol Ulusal Toplantısı*, 2026.
