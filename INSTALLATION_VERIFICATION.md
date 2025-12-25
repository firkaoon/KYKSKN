# KYKSKN - Kurulum Doğrulama

## ✅ Kurulum Kontrol Listesi

Kurulumun başarılı olduğunu doğrulamak için aşağıdaki adımları takip edin.

---

## 1️⃣ Dosya Yapısı Kontrolü

Aşağıdaki dosya ve klasörlerin mevcut olduğundan emin olun:

```bash
cd KYKSKN
ls -la
```

**Olması Gerekenler**:
```
✓ main.py
✓ requirements.txt
✓ install.sh
✓ README.md
✓ LICENSE
✓ core/
✓ ui/
✓ utils/
✓ config/
```

---

## 2️⃣ Python Sürümü Kontrolü

```bash
python3 --version
```

**Beklenen**: Python 3.8 veya üzeri

```
✓ Python 3.8.x
✓ Python 3.9.x
✓ Python 3.10.x
✓ Python 3.11.x
✓ Python 3.12.x
```

---

## 3️⃣ Sistem Araçları Kontrolü

```bash
# Aircrack-ng kontrolü
which aircrack-ng
which airmon-ng
which airodump-ng
which aireplay-ng

# Wireless araçları kontrolü
which iwconfig
which iw
```

**Her komut için bir yol dönmeli**:
```
✓ /usr/bin/aircrack-ng
✓ /usr/sbin/airmon-ng
✓ /usr/sbin/airodump-ng
✓ /usr/sbin/aireplay-ng
✓ /sbin/iwconfig
✓ /sbin/iw
```

---

## 4️⃣ Python Kütüphaneleri Kontrolü

```bash
python3 -c "import scapy; print('scapy OK')"
python3 -c "import rich; print('rich OK')"
python3 -c "import questionary; print('questionary OK')"
python3 -c "import pyfiglet; print('pyfiglet OK')"
python3 -c "import netifaces; print('netifaces OK')"
python3 -c "import psutil; print('psutil OK')"
python3 -c "import colorama; print('colorama OK')"
```

**Her komut için "OK" çıktısı almalısınız**.

---

## 5️⃣ Wireless Adapter Kontrolü

```bash
# Wireless interface'leri listele
iwconfig
```

**Beklenen Çıktı**:
```
wlan0     IEEE 802.11  ESSID:off/any  
          Mode:Managed  Access Point: Not-Associated   
          ...
```

**Kontrol**:
- ✓ En az bir `wlan` veya `wl` interface görünüyor
- ✓ "IEEE 802.11" yazısı var
- ✓ Interface "UP" durumunda

---

## 6️⃣ Monitor Mode Desteği Kontrolü

```bash
# Monitor mode testi
sudo airmon-ng start wlan0
```

**Beklenen**:
```
PHY     Interface       Driver          Chipset
phy0    wlan0           ath9k           Atheros...

                (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
```

**Temizlik**:
```bash
sudo airmon-ng stop wlan0mon
```

---

## 7️⃣ Yetki Kontrolü

```bash
# Root kontrolü
id
```

**Kontrol**:
- ✓ `uid=0(root)` görünüyor (sudo ile çalıştırıldığında)

---

## 8️⃣ Program Çalıştırma Testi

```bash
# Programı başlat (test modu)
sudo python3 main.py
```

**Beklenen**:
1. ✓ Banner gösterildi
2. ✓ Yasal uyarı gösterildi
3. ✓ Ana menü gösterildi
4. ✓ Hata mesajı yok

**Çıkış**: Ana menüden "Çıkış" seçin

---

## 9️⃣ Log Sistemi Kontrolü

```bash
# Program çalıştıktan sonra
ls -la logs/
```

**Beklenen**:
```
✓ logs/ klasörü oluştu
✓ kykskn_*.log dosyası var
```

**Log içeriği kontrol**:
```bash
cat logs/kykskn_*.log
```

---

## 🔟 Tam Fonksiyonellik Testi

### Test 1: Ağ Tarama

```bash
sudo python3 main.py
# 1. "Saldırıya Başla" seç
# 2. Ağ taramasını bekle
# 3. Ağlar listelendi mi?
```

**Beklenen**:
- ✓ Çevredeki WiFi ağları listelendi
- ✓ Sinyal güçleri gösterildi
- ✓ Kanal bilgileri doğru

### Test 2: Cihaz Listeleme

```bash
# Bir ağ seçtikten sonra
# Cihazlar listelendi mi?
```

**Beklenen**:
- ✓ Bağlı cihazlar listelendi
- ✓ MAC adresleri gösterildi
- ✓ Kendi cihazın vurgulandı

### Test 3: Saldırı Başlatma

```bash
# Bir test cihazı seç
# Saldırıyı başlat
```

**Beklenen**:
- ✓ Dashboard açıldı
- ✓ İstatistikler güncelleniyor
- ✓ Paket sayısı artıyor
- ✓ Ctrl+C ile durduruluyor

---

## 🐛 Sorun Giderme

### Sorun: "ModuleNotFoundError"

**Çözüm**:
```bash
pip3 install -r requirements.txt
```

### Sorun: "Permission denied"

**Çözüm**:
```bash
sudo python3 main.py  # sudo ile çalıştır
```

### Sorun: "Wireless adapter bulunamadı"

**Çözüm**:
```bash
# USB adaptör takılı mı kontrol et
lsusb

# Interface'i manuel kontrol et
ip link show
```

### Sorun: "Monitor mode aktif edilemedi"

**Çözüm**:
```bash
# Interfering process'leri kapat
sudo airmon-ng check kill

# Manuel monitor mode
sudo airmon-ng start wlan0
```

### Sorun: "Hiç ağ bulunamadı"

**Çözüm**:
- Adaptörün antenini kontrol et
- Farklı lokasyonda dene
- Tarama süresini artır

---

## ✅ Başarılı Kurulum Kriterleri

Tüm aşağıdakiler sağlanmalı:

- [x] Python 3.8+ kurulu
- [x] Aircrack-ng suite kurulu
- [x] Python kütüphaneleri kurulu
- [x] Wireless adapter tespit ediliyor
- [x] Monitor mode çalışıyor
- [x] Program başlatılabiliyor
- [x] Banner gösteriliyor
- [x] Menüler çalışıyor
- [x] Ağ tarama çalışıyor
- [x] Log sistemi çalışıyor

---

## 📊 Kurulum Skoru

Yukarıdaki kontrolleri yapın ve puanlayın:

- **10/10**: Mükemmel! Tüm özellikler çalışıyor ✅
- **8-9/10**: İyi! Küçük sorunlar var, çözülebilir ⚠️
- **6-7/10**: Orta! Bazı özellikler çalışmıyor 🔧
- **<6/10**: Sorunlu! Yeniden kurulum gerekebilir ❌

---

## 🎓 Sonraki Adımlar

Kurulum başarılı ise:

1. ✅ [QUICKSTART.md](QUICKSTART.md) ile hızlı başla
2. ✅ [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) ile örnekleri incele
3. ✅ Kendi ağında güvenlik testi yap
4. ✅ Sonuçları analiz et

---

## 📞 Yardım

Sorun devam ediyorsa:

- 📖 [README.md](README.md) oku
- 🐛 [GitHub Issues](https://github.com/yourusername/KYKSKN/issues) aç
- 💬 [Discussions](https://github.com/yourusername/KYKSKN/discussions) katıl

---

**Başarılı kurulum! 🎉**

