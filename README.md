# KYKSKN - Multi-Target Deauth Attack Framework

<div align="center">

```
   ██╗  ██╗██╗   ██╗██╗  ██╗███████╗██╗  ██╗███╗   ██╗
   ██║ ██╔╝╚██╗ ██╔╝██║ ██╔╝██╔════╝██║ ██╔╝████╗  ██║
   █████╔╝  ╚████╔╝ █████╔╝ ███████╗█████╔╝ ██╔██╗ ██║
   ██╔═██╗   ╚██╔╝  ██╔═██╗ ╚════██║██╔═██╗ ██║╚██╗██║
   ██║  ██╗   ██║   ██║  ██╗███████║██║  ██╗██║ ╚████║
   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

**Modern, Otomatik, Çoklu Hedef Deauthentication Saldırı Aracı**

[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-blue)](https://www.kali.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Educational-red)](LICENSE)

</div>

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Gereksinimler](#-gereksinimler)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Yasal Uyarı](#-yasal-uyarı)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## 🚀 Özellikler

### Temel Özellikler

- ✅ **Otomatik Wireless Adapter Tespiti** - Sistem otomatik olarak uygun wireless adaptörü bulur
- ✅ **Monitor Mode Yönetimi** - Tek tuşla monitor mode aktif/deaktif
- ✅ **Gerçek Zamanlı Ağ Tarama** - Çevredeki tüm WiFi ağlarını tarar
- ✅ **Sinyal Gücüne Göre Sıralama** - En güçlü sinyalden en zayıfa doğru
- ✅ **Mevcut Bağlantı Tespiti** - Bağlı olduğunuz ağı otomatik tespit eder
- ✅ **Cihaz Listeleme** - Ağdaki tüm cihazları MAC adresleriyle gösterir
- ✅ **Kendi Cihazını Tanıma** - Kendi MAC adresinizi otomatik tespit ve vurgular
- ✅ **Çoklu Hedef Seçimi** - İstediğiniz kadar cihazı seçebilirsiniz
- ✅ **Whitelist Sistemi** - Belirli cihazları saldırıdan muaf tutun
- ✅ **Eş Zamanlı Saldırı** - Tüm hedeflere aynı anda saldırı
- ✅ **Canlı Dashboard** - Gerçek zamanlı saldırı istatistikleri
- ✅ **Modern Terminal UI** - Rich kütüphanesi ile güzel arayüz
- ✅ **İnteraktif Menüler** - Ok tuşları ile kolay navigasyon
- ✅ **Detaylı Loglama** - Tüm işlemler log dosyasına kaydedilir
- ✅ **Otomatik Bağımlılık Yükleme** - Eksik kütüphaneler otomatik yüklenir

### Gelişmiş Özellikler

- 🎯 **Multi-Threading** - Her hedef için ayrı thread
- 🎯 **Adaptive Rate Limiting** - Ağ yoğunluğuna göre paket hızı ayarı
- 🎯 **Graceful Shutdown** - Ctrl+C ile güvenli kapatma
- 🎯 **Auto-Recovery** - Hata durumunda otomatik kurtarma
- 🎯 **Comprehensive Error Handling** - Tüm hatalar yakalanır ve loglanır

---

## 📦 Kurulum

### Otomatik Kurulum (Önerilen)

```bash
# Repository'yi klonlayın
git clone https://github.com/yourusername/KYKSKN.git
cd KYKSKN

# Kurulum scriptini çalıştırın
chmod +x install.sh
sudo ./install.sh
```

### Manuel Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/yourusername/KYKSKN.git
cd KYKSKN

# Sistem bağımlılıklarını yükleyin
sudo apt update
sudo apt install aircrack-ng python3 python3-pip

# Python kütüphanelerini yükleyin
pip3 install -r requirements.txt

# Çalıştırılabilir yapın
chmod +x main.py
```

---

## 🎮 Kullanım

### Temel Kullanım

```bash
# Root yetkisiyle çalıştırın
sudo python3 main.py

# veya
sudo ./main.py
```

### Kullanım Adımları

1. **Programı Başlatın**
   ```bash
   sudo python3 main.py
   ```

2. **Yasal Uyarıyı Okuyun ve Kabul Edin**
   - Program başladığında yasal uyarı gösterilir
   - Devam etmek için kabul etmelisiniz

3. **Ana Menüden "Saldırıya Başla"yı Seçin**
   - Ok tuşları ile menüde gezinin
   - Enter ile seçim yapın

4. **Hedef Ağı Seçin**
   - Program otomatik olarak çevredeki ağları tarar
   - Sinyal gücüne göre sıralanmış liste gösterilir
   - İstediğiniz ağı seçin

5. **Hedef Cihazları Seçin**
   - Seçilen ağdaki tüm cihazlar listelenir
   - Kendi cihazınız otomatik olarak vurgulanır
   - Space tuşu ile hedef cihazları işaretleyin
   - "Hepsine Saldır" seçeneği ile tümünü seçebilirsiniz

6. **Saldırıyı Başlatın**
   - Onay verin
   - Canlı dashboard'da saldırıyı izleyin
   - Ctrl+C ile durdurun

### Örnek Senaryo

```bash
# 1. Programı başlat
sudo python3 main.py

# 2. Ana menüden "Saldırıya Başla" seç

# 3. Ev ağını seç
[0] 📶 MyHomeNetwork (Şu anda bağlı) ████████ -45 dBm

# 4. Test cihazını seç (kendi cihazın hariç)
[✓] AA:BB:CC:DD:EE:FF  🖥️  Senin Cihazın (Hariç)
[ ] 11:22:33:44:55:66  📱 Samsung Galaxy  <-- Bu seçildi

# 5. Saldırıyı başlat ve izle
```

---

## 🔧 Gereksinimler

### Sistem Gereksinimleri

- **İşletim Sistemi**: Kali Linux 2020.1 veya üzeri
- **Python**: 3.8 veya üzeri
- **Yetkiler**: Root (sudo)
- **Wireless Adapter**: Monitor mode destekleyen

### Yazılım Gereksinimleri

#### Sistem Araçları (Kali'de varsayılan)
- `aircrack-ng` - Wireless security testing
- `airmon-ng` - Monitor mode management
- `airodump-ng` - Network scanning
- `aireplay-ng` - Packet injection
- `iwconfig` - Wireless configuration
- `iw` - Wireless configuration (modern)

#### Python Kütüphaneleri (Otomatik yüklenir)
- `scapy>=2.5.0` - Packet manipulation
- `rich>=13.0.0` - Terminal UI
- `questionary>=2.0.0` - Interactive menus
- `pyfiglet>=1.0.0` - ASCII art
- `netifaces>=0.11.0` - Network interfaces
- `psutil>=5.9.0` - System utilities
- `colorama>=0.4.6` - Terminal colors

### Donanım Gereksinimleri

- **Wireless Adapter**: Monitor mode ve packet injection destekleyen
  - Önerilen chipset'ler: Atheros (ath9k), Ralink (rt2800usb)
  - Test edilmiş adaptörler: Alfa AWUS036NHA, TP-Link TL-WN722N v1

---

## 📸 Ekran Görüntüleri

### Ana Menü
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗  ██╗██╗   ██╗██╗  ██╗███████╗██╗  ██╗███╗   ██╗   ║
║   ██║ ██╔╝╚██╗ ██╔╝██║ ██╔╝██╔════╝██║ ██╔╝████╗  ██║   ║
║   █████╔╝  ╚████╔╝ █████╔╝ ███████╗█████╔╝ ██╔██╗ ██║   ║
║   ██╔═██╗   ╚██╔╝  ██╔═██╗ ╚════██║██╔═██╗ ██║╚██╗██║   ║
║   ██║  ██╗   ██║   ██║  ██╗███████║██║  ██╗██║ ╚████║   ║
║   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ║
║                                                           ║
║           Multi-Target Deauth Attack Framework           ║
║                      v1.0.0 - 2025                       ║
╚═══════════════════════════════════════════════════════════╝

[1] 🎯 Saldırıya Başla
[2] ❓ Yardım ve Kullanım Kılavuzu
[3] ⚙️  Ayarlar
[0] 🚪 Çıkış
```

### Saldırı Dashboard
```
╔═══════════════════════════════════════════════════════════╗
║  🎯 SALDIRI DURUMU - MyHomeNetwork                       ║
╠═══════════════════════════════════════════════════════════╣
║  Hedef Sayısı: 11 cihaz                                  ║
║  Gönderilen Paket: 4,523                                 ║
║  Başarılı Deauth: 8/11                                   ║
║  Süre: 00:02:34                                          ║
╚═══════════════════════════════════════════════════════════╝
```

---

## ⚖️ Yasal Uyarı

**ÖNEMLİ: BU ARACI SADECE YASAL VE ETİK AMAÇLARLA KULLANIN!**

Bu araç **sadece** aşağıdaki durumlarda kullanılmalıdır:

✅ **Kendi ağınızda** güvenlik testleri yapmak için
✅ **İzin alınmış** ağlarda profesyonel güvenlik denetimi için
✅ **Eğitim amaçlı** kontrollü ortamlarda

❌ **İzinsiz kullanım YASADIDIR** ve ciddi yasal sonuçları vardır:
- Bilgisayar sistemlerine yetkisiz erişim (TCK 243)
- Haberleşmenin gizliliğini ihlal (TCK 132)
- Hukuka aykırı veri elde etme (TCK 136)

**Sorumluluk Reddi**: Bu aracın geliştiricileri, kullanıcıların yasa dışı veya etik olmayan kullanımlarından sorumlu değildir. Kullanıcı tüm sorumluluğu kabul eder.

---

## 🏗️ Mimari

### Proje Yapısı

```
KYKSKN/
├── main.py                    # Ana giriş noktası
├── requirements.txt           # Python bağımlılıkları
├── install.sh                 # Kurulum scripti
├── README.md                  # Dokümantasyon
│
├── core/                      # Çekirdek modüller
│   ├── wireless_manager.py    # Wireless interface yönetimi
│   ├── network_scanner.py     # Ağ ve cihaz tarama
│   └── deauth_engine.py       # Deauth saldırı motoru
│
├── ui/                        # Kullanıcı arayüzü
│   ├── banner.py              # ASCII art ve banner
│   ├── menu.py                # İnteraktif menüler
│   └── dashboard.py           # Canlı saldırı dashboard'u
│
├── utils/                     # Yardımcı fonksiyonlar
│   ├── validators.py          # Validasyon fonksiyonları
│   ├── logger.py              # Loglama sistemi
│   └── helpers.py             # Genel yardımcılar
│
├── config/                    # Konfigürasyon
│   └── settings.py            # Ayarlar ve sabitler
│
└── logs/                      # Log dosyaları
```

### Teknoloji Stack

- **Backend**: Python 3.8+
- **Wireless**: Aircrack-ng Suite
- **UI**: Rich, Questionary
- **Networking**: Scapy, Netifaces
- **Threading**: Python threading module

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen aşağıdaki adımları izleyin:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

---

## 📝 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım yasaktır.

---

## 👨‍💻 Geliştirici

**KYKSKN Team**

- GitHub: [@kykskn](https://github.com/kykskn)

---

## 🙏 Teşekkürler

- [Aircrack-ng](https://www.aircrack-ng.org/) - Wireless security tools
- [Scapy](https://scapy.net/) - Packet manipulation
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Questionary](https://github.com/tmbo/questionary) - Interactive prompts

---

## 📞 Destek

Sorunuz veya öneriniz mi var?

- 🐛 [Issue açın](https://github.com/yourusername/KYKSKN/issues)
- 💬 [Discussions](https://github.com/yourusername/KYKSKN/discussions)

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

Made with ❤️ for Cybersecurity Education

</div>

