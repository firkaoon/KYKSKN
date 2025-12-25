# KYKSKN - Hızlı Başlangıç Kılavuzu

## 🚀 5 Dakikada Başla

### 1️⃣ Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/yourusername/KYKSKN.git
cd KYKSKN

# Otomatik kurulum
sudo ./install.sh
```

### 2️⃣ Çalıştır

```bash
sudo python3 main.py
```

### 3️⃣ Kullan

1. **Yasal uyarıyı kabul et**
2. **"Saldırıya Başla" seç**
3. **Hedef ağı seç**
4. **Hedef cihazları seç**
5. **Saldırıyı başlat**

## 📋 Kontrol Listesi

Başlamadan önce kontrol edin:

- [ ] Kali Linux kullanıyorum
- [ ] Root yetkisi var (sudo)
- [ ] Wireless adapter takılı
- [ ] Monitor mode destekli adapter
- [ ] Sadece kendi ağımda test yapacağım

## ⚡ Hızlı Komutlar

```bash
# Kurulum
sudo ./install.sh

# Çalıştır
sudo python3 main.py

# Yardım
sudo python3 main.py --help

# Log görüntüle
tail -f logs/kykskn_*.log
```

## 🎯 İlk Test

### Senaryo: Ev Ağında Test

1. Programı başlat
2. Kendi ev ağını seç
3. Test cihazını (örn: eski telefon) seç
4. Saldırıyı başlat
5. Telefonun WiFi bağlantısının kesildiğini gözlemle
6. Saldırıyı durdur (Ctrl+C)

## ❓ Sorun mu Yaşıyorsun?

### Wireless adapter bulunamıyor
```bash
# Adaptörleri kontrol et
iwconfig

# USB adaptör takılıysa
lsusb
```

### Monitor mode aktif edilemiyor
```bash
# Manuel olarak dene
sudo airmon-ng check kill
sudo airmon-ng start wlan0
```

### Kütüphane hatası
```bash
# Manuel kütüphane yükleme
pip3 install -r requirements.txt
```

### Root yetkisi hatası
```bash
# sudo ile çalıştır
sudo python3 main.py
```

## 📚 Daha Fazla Bilgi

- Detaylı dokümantasyon: [README.md](README.md)
- Sorun bildirimi: [GitHub Issues](https://github.com/yourusername/KYKSKN/issues)

## ⚠️ Önemli Hatırlatma

Bu araç **sadece eğitim amaçlıdır**. İzinsiz kullanım **yasadışıdır**!

---

**Başarılar! 🎉**

