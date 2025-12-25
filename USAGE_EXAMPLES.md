# KYKSKN - Kullanım Örnekleri

## 📖 Detaylı Kullanım Senaryoları

### Senaryo 1: Ev Ağı Güvenlik Testi

**Amaç**: Ev ağınızın deauth saldırılarına karşı dayanıklılığını test etmek

**Adımlar**:

```bash
# 1. Programı başlat
sudo python3 main.py

# 2. Ana menüden "Saldırıya Başla" seç

# 3. Kendi ağını seç
[0] 📶 MyHomeNetwork (Şu anda bağlı) ████████ -45 dBm

# 4. Test cihazını seç (örn: eski telefon veya tablet)
[✓] AA:BB:CC:DD:EE:FF  🖥️  Senin Cihazın (Hariç)
[✓] 11:22:33:44:55:66  📱 Test Telefonu

# 5. Saldırıyı başlat ve gözlemle
# - Telefonun WiFi bağlantısı kesilecek
# - Telefon otomatik olarak yeniden bağlanmaya çalışacak
# - Dashboard'da paket sayısını izle

# 6. Ctrl+C ile durdur
```

**Beklenen Sonuç**: Test cihazının WiFi bağlantısı kesilmeli ve tekrar bağlanmaya çalışmalı.

---

### Senaryo 2: Çoklu Cihaz Testi

**Amaç**: Birden fazla cihaza aynı anda saldırı testi

**Adımlar**:

```bash
# 1. Programı başlat
sudo python3 main.py

# 2. Hedef ağı seç

# 3. Birden fazla cihaz seç
[✓] AA:BB:CC:DD:EE:FF  🖥️  Senin Cihazın (Hariç)
[✓] 11:22:33:44:55:66  📱 Telefon 1
[✓] 22:33:44:55:66:77  📱 Telefon 2
[✓] 33:44:55:66:77:88  💻 Laptop

# 4. Saldırıyı başlat
# - Tüm seçili cihazlara eş zamanlı saldırı başlar
# - Dashboard'da her cihazın durumunu ayrı ayrı izle

# 5. İstatistikleri gözlemle
# - Hangi cihazlar daha hızlı etkilendi?
# - Hangi cihazlar daha dirençli?
```

---

### Senaryo 3: Whitelist Kullanımı

**Amaç**: Kritik cihazları koruyarak diğerlerine saldırı

**Adımlar**:

```bash
# 1. Ağdaki tüm cihazları listele

# 2. Kritik cihazları SEÇME (işaretleme)
# Örnek: Router, NAS, Güvenlik Kamerası

# 3. Sadece test cihazlarını seç
[✓] AA:BB:CC:DD:EE:FF  🖥️  Senin Cihazın (Hariç)
[ ] 11:11:11:11:11:11  🌐 Router (Seçme!)
[ ] 22:22:22:22:22:22  💾 NAS (Seçme!)
[✓] 33:33:33:33:33:33  📱 Test Telefonu
[✓] 44:44:44:44:44:44  💻 Test Laptop

# 4. Saldırıyı başlat
# - Sadece işaretli cihazlar hedef alınır
# - Router ve NAS etkilenmez
```

---

### Senaryo 4: "Hepsine Saldır" Modu

**Amaç**: Ağdaki tüm cihazlara (kendi cihazın hariç) saldırı

**Adımlar**:

```bash
# 1. Hedef ağı seç

# 2. Cihaz listesinde en alttaki seçeneği seç
[✓] AA:BB:CC:DD:EE:FF  🖥️  Senin Cihazın (Hariç)
[ ] 11:22:33:44:55:66  📱 Cihaz 1
[ ] 22:33:44:55:66:77  📱 Cihaz 2
...
[✓] ⚡ HEPSINE SALDIRI YAP  <-- Bunu seç

# 3. Onay ver
# - Tüm cihazlar (kendi cihazın hariç) hedef alınır

# 4. Gözlemle
# - Dashboard'da tüm hedeflerin durumunu izle
# - Hangi cihazlar daha hızlı etkileniyor?
```

---

## 🎯 Dashboard Kullanımı

### Dashboard Elemanları

```
╔═══════════════════════════════════════════════════════════╗
║  🎯 SALDIRI DURUMU - MyHomeNetwork                       ║
╠═══════════════════════════════════════════════════════════╣
║  Hedef Sayısı: 5 cihaz          ← Toplam hedef sayısı   ║
║  Gönderilen Paket: 4,523        ← Toplam paket          ║
║  Başarılı Deauth: 3/5           ← Başarılı/Toplam       ║
║  Süre: 00:02:34                 ← Geçen süre            ║
╚═══════════════════════════════════════════════════════════╝
```

### Hedef Durumları

- ✅ **Bağlantı kesildi**: Cihaz başarıyla deauth edildi
- 🔄 **Saldırı devam ediyor**: Paketler gönderiliyor
- ⏸️  **Beklemede**: Henüz başlamadı veya durdu

---

## 🔍 İleri Seviye Kullanım

### Log Dosyalarını İnceleme

```bash
# Son log dosyasını görüntüle
tail -f logs/kykskn_*.log

# Tüm logları ara
grep "ERROR" logs/*.log

# Belirli bir MAC için logları filtrele
grep "11:22:33:44:55:66" logs/*.log
```

### Manuel Monitor Mode

```bash
# Monitor mode'u manuel aktif et
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# KYKSKN'yi çalıştır
sudo python3 main.py

# Monitor mode'u kapat
sudo airmon-ng stop wlan0mon
sudo systemctl start NetworkManager
```

### Belirli Kanal Üzerinde Çalışma

Program otomatik olarak hedef ağın kanalını tespit eder ve ayarlar.
Manuel kanal ayarı için `core/wireless_manager.py` dosyasını düzenleyebilirsiniz.

---

## 📊 Sonuçları Yorumlama

### Başarılı Saldırı

```
Toplam Hedef: 5
Başarılı Saldırı: 5
Toplam Paket Gönderildi: 12,450

✅ Başarılı Hedefler:
  • 11:22:33:44:55:66 - 2,490 paket
  • 22:33:44:55:66:77 - 2,480 paket
  • 33:44:55:66:77:88 - 2,495 paket
  • 44:55:66:77:88:99 - 2,492 paket
  • 55:66:77:88:99:AA - 2,493 paket
```

**Yorum**: Tüm cihazlar başarıyla deauth edildi. Ağ deauth saldırılarına karşı savunmasız.

### Kısmi Başarı

```
Toplam Hedef: 5
Başarılı Saldırı: 3
Toplam Paket Gönderildi: 8,320

✅ Başarılı Hedefler:
  • 11:22:33:44:55:66 - 2,100 paket
  • 22:33:44:55:66:77 - 2,050 paket
  • 33:44:55:66:77:88 - 2,080 paket

⚠️  Devam Eden/Başarısız Hedefler:
  • 44:55:66:77:88:99 - 1,045 paket
  • 55:66:77:88:99:AA - 1,045 paket
```

**Yorum**: Bazı cihazlar deauth koruması kullanıyor olabilir (802.11w).

---

## 🛡️ Savunma Testleri

### 802.11w (PMF) Testi

Modern cihazlar 802.11w (Protected Management Frames) kullanır.
Bu cihazlar deauth saldırılarına karşı korumalıdır.

**Test**:
1. PMF etkin bir cihazı hedef al
2. Saldırıyı başlat
3. Gözlemle: Cihaz etkilenmemeli

### Router Ayarları

Saldırıdan sonra router ayarlarını kontrol et:
- WPA3 kullan (mümkünse)
- 802.11w/PMF'yi aktif et
- MAC filtering kullan
- Güçlü şifre kullan

---

## ⚠️ Yaygın Hatalar ve Çözümleri

### Hata: "Wireless adapter bulunamadı"

**Çözüm**:
```bash
iwconfig  # Adaptörleri kontrol et
lsusb     # USB adaptör kontrolü
```

### Hata: "Monitor mode aktif edilemedi"

**Çözüm**:
```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan0
```

### Hata: "Hiç ağ bulunamadı"

**Çözüm**:
- Tarama süresini artır (kod içinde SCAN_TIMEOUT)
- Adaptörün antenini kontrol et
- Farklı lokasyonda dene

### Hata: "Bağlı cihaz yok"

**Çözüm**:
- Daha uzun süre tara
- Cihazların aktif olduğundan emin ol
- Farklı zamanda dene

---

## 💡 İpuçları

1. **En İyi Sonuç İçin**:
   - Hedef ağa yakın ol
   - Güçlü sinyal gücü olan ağları seç
   - Aktif veri transferi olan cihazları hedef al

2. **Performans**:
   - Aynı anda çok fazla hedef seçme (max 20-30)
   - Güçlü bir wireless adapter kullan
   - Sistem kaynaklarını izle

3. **Güvenlik**:
   - Sadece kendi ağında test yap
   - Test sonrası router'ı yeniden başlat
   - Logları düzenli temizle

---

## 📚 Daha Fazla Bilgi

- Ana Dokümantasyon: [README.md](README.md)
- Hızlı Başlangıç: [QUICKSTART.md](QUICKSTART.md)
- Sorun Bildirimi: [GitHub Issues](https://github.com/yourusername/KYKSKN/issues)

---

**Başarılı testler! 🎯**

