# KYKSKN - Proje Yapısı

## 📁 Dizin Yapısı

```
KYKSKN/
│
├── 📄 main.py                      # Ana giriş noktası (çalıştırılabilir)
├── 📄 requirements.txt             # Python bağımlılıkları
├── 📄 install.sh                   # Otomatik kurulum scripti
├── 📄 .gitignore                   # Git ignore dosyası
├── 📄 LICENSE                      # Lisans (Educational Use)
│
├── 📚 Dokümantasyon
│   ├── README.md                   # Ana dokümantasyon
│   ├── QUICKSTART.md               # Hızlı başlangıç kılavuzu
│   ├── USAGE_EXAMPLES.md           # Detaylı kullanım örnekleri
│   └── PROJECT_STRUCTURE.md        # Bu dosya
│
├── 🔧 core/                        # Çekirdek modüller
│   ├── __init__.py
│   ├── wireless_manager.py         # Wireless interface yönetimi
│   │   ├── WirelessManager sınıfı
│   │   ├── Monitor mode yönetimi
│   │   ├── Kanal ayarlama
│   │   └── Interface kontrolü
│   │
│   ├── network_scanner.py          # Ağ ve cihaz tarama
│   │   ├── NetworkScanner sınıfı
│   │   ├── AccessPoint dataclass
│   │   ├── Client dataclass
│   │   ├── airodump-ng entegrasyonu
│   │   └── CSV parsing
│   │
│   └── deauth_engine.py            # Deauth saldırı motoru
│       ├── DeauthEngine sınıfı
│       ├── AttackTarget dataclass
│       ├── Multi-threading
│       ├── aireplay-ng entegrasyonu
│       └── İstatistik toplama
│
├── 🎨 ui/                          # Kullanıcı arayüzü
│   ├── __init__.py
│   ├── banner.py                   # ASCII art ve banner
│   │   ├── show_banner()
│   │   ├── show_legal_warning()
│   │   ├── show_section_header()
│   │   └── Mesaj fonksiyonları
│   │
│   ├── menu.py                     # İnteraktif menüler
│   │   ├── show_main_menu()
│   │   ├── select_network()
│   │   ├── select_clients()
│   │   ├── confirm_attack()
│   │   └── show_help()
│   │
│   └── dashboard.py                # Canlı saldırı dashboard'u
│       ├── AttackDashboard sınıfı
│       ├── Gerçek zamanlı güncelleme
│       ├── İstatistik panelleri
│       └── show_attack_summary()
│
├── 🛠️ utils/                       # Yardımcı fonksiyonlar
│   ├── __init__.py
│   ├── validators.py               # Validasyon fonksiyonları
│   │   ├── is_valid_mac()
│   │   ├── is_root()
│   │   ├── check_tool_exists()
│   │   └── is_monitor_mode()
│   │
│   ├── logger.py                   # Loglama sistemi
│   │   ├── Logger sınıfı (Singleton)
│   │   ├── Dosya loglama
│   │   └── Konsol loglama
│   │
│   └── helpers.py                  # Genel yardımcılar
│       ├── run_command()
│       ├── signal_handler()
│       ├── format_mac()
│       ├── format_signal_strength()
│       └── cleanup fonksiyonları
│
├── ⚙️ config/                      # Konfigürasyon
│   ├── __init__.py
│   └── settings.py                 # Ayarlar ve sabitler
│       ├── Uygulama bilgileri
│       ├── Renk şemaları
│       ├── Deauth ayarları
│       ├── Tarama ayarları
│       └── Threading ayarları
│
└── 📝 logs/                        # Log dosyaları (otomatik oluşur)
    └── kykskn_YYYYMMDD_HHMMSS.log
```

---

## 🔍 Modül Detayları

### 1. Core Modüller

#### wireless_manager.py
**Amaç**: Wireless interface yönetimi

**Ana Fonksiyonlar**:
- `get_wireless_interfaces()`: Wireless adaptörleri tespit et
- `enable_monitor_mode()`: Monitor mode'u aktif et
- `disable_monitor_mode()`: Normal mode'a dön
- `set_channel()`: Wireless kanalı ayarla
- `get_connected_network()`: Mevcut bağlantıyı tespit et

**Kullanılan Araçlar**: airmon-ng, iwconfig, iw, ip

---

#### network_scanner.py
**Amaç**: Ağ ve cihaz tarama

**Ana Fonksiyonlar**:
- `start_scan()`: airodump-ng ile tarama başlat
- `parse_scan_results()`: CSV sonuçlarını parse et
- `get_sorted_aps()`: Sinyal gücüne göre sıralı AP listesi
- `get_clients_for_ap()`: Belirli AP'nin clientlarını getir

**Veri Yapıları**:
- `AccessPoint`: BSSID, ESSID, kanal, şifreleme, sinyal gücü
- `Client`: MAC, BSSID, sinyal gücü, paket sayısı

**Kullanılan Araçlar**: airodump-ng

---

#### deauth_engine.py
**Amaç**: Çoklu hedef deauth saldırısı

**Ana Fonksiyonlar**:
- `add_target()`: Hedef ekle
- `start_attack()`: Saldırıyı başlat (multi-threaded)
- `stop_attack()`: Saldırıyı durdur
- `get_attack_stats()`: Genel istatistikler
- `get_all_targets_status()`: Tüm hedeflerin durumu

**Threading**: Her hedef için ayrı thread

**Kullanılan Araçlar**: aireplay-ng

---

### 2. UI Modülleri

#### banner.py
**Amaç**: Görsel öğeler ve mesajlar

**Özellikler**:
- ASCII art banner (pyfiglet)
- Renkli mesajlar (rich)
- Yasal uyarı paneli
- Bölüm başlıkları

---

#### menu.py
**Amaç**: İnteraktif kullanıcı menüleri

**Özellikler**:
- Ana menü (questionary)
- Ağ seçim menüsü (tablo + seçim)
- Cihaz seçim menüsü (checkbox)
- Yardım ekranı

---

#### dashboard.py
**Amaç**: Canlı saldırı izleme

**Özellikler**:
- Gerçek zamanlı güncelleme (rich.live)
- İstatistik panelleri
- Hedef durum tablosu
- Saldırı özeti

---

### 3. Utils Modülleri

#### validators.py
**Amaç**: Girdi ve sistem validasyonu

**Fonksiyonlar**:
- MAC adresi validasyonu
- Root kontrolü
- Araç varlık kontrolü
- Interface kontrolü
- Monitor mode kontrolü

---

#### logger.py
**Amaç**: Merkezi loglama sistemi

**Özellikler**:
- Singleton pattern
- Dosya ve konsol loglama
- Log seviyeleri (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Otomatik dosya adlandırma

---

#### helpers.py
**Amaç**: Genel yardımcı fonksiyonlar

**Fonksiyonlar**:
- Komut çalıştırma
- Signal handling (Ctrl+C)
- MAC formatla
- Sinyal gücü formatla
- Temizlik işlemleri

---

### 4. Config Modülü

#### settings.py
**Amaç**: Merkezi konfigürasyon

**İçerik**:
- Uygulama sabitleri
- Renk şemaları
- Timeout değerleri
- Threading limitleri
- Dosya yolları

---

## 🔄 Veri Akışı

### 1. Başlangıç Akışı

```
main.py
  ↓
check_and_install_dependencies()  # Otomatik kütüphane yükleme
  ↓
KYKSKN.__init__()                 # Ana sınıf başlatma
  ↓
setup_signal_handlers()           # Ctrl+C handler
  ↓
logger.setup()                    # Loglama başlat
  ↓
show_banner()                     # Banner göster
  ↓
show_legal_warning()              # Yasal uyarı
  ↓
check_requirements()              # Sistem kontrolleri
```

---

### 2. Saldırı Akışı

```
attack_workflow()
  ↓
setup_wireless()
  ├─ WirelessManager.get_wireless_interfaces()
  └─ WirelessManager.enable_monitor_mode()
  ↓
scan_networks()
  ├─ NetworkScanner.start_scan()
  └─ NetworkScanner.parse_scan_results()
  ↓
select_target_network()
  └─ ui.menu.select_network()
  ↓
select_target_clients()
  └─ ui.menu.select_clients()
  ↓
execute_attack()
  ├─ WirelessManager.set_channel()
  ├─ DeauthEngine.add_target() (her hedef için)
  ├─ DeauthEngine.start_attack()
  ├─ AttackDashboard.run() (canlı izleme)
  ├─ DeauthEngine.stop_attack()
  └─ show_attack_summary()
```

---

### 3. Deauth Saldırı Akışı

```
DeauthEngine.start_attack()
  ↓
Her hedef için ayrı thread başlat
  ↓
Thread: _attack_target()
  ├─ aireplay-ng process başlat
  ├─ Sürekli döngü:
  │   ├─ Process kontrolü
  │   ├─ Paket sayısı güncelle
  │   └─ Başarı kontrolü
  └─ Process sonlandır
```

---

## 🧩 Bağımlılıklar

### Sistem Bağımlılıkları
```
Kali Linux → aircrack-ng suite → wireless adapter
```

### Python Bağımlılıkları
```
main.py
  ├─ core/
  │   ├─ wireless_manager (netifaces, subprocess)
  │   ├─ network_scanner (csv, re, subprocess)
  │   └─ deauth_engine (threading, subprocess)
  │
  ├─ ui/
  │   ├─ banner (pyfiglet, rich)
  │   ├─ menu (questionary, rich)
  │   └─ dashboard (rich.live, rich.table)
  │
  ├─ utils/
  │   ├─ validators (subprocess, re)
  │   ├─ logger (logging)
  │   └─ helpers (subprocess, signal)
  │
  └─ config/
      └─ settings (sabitler)
```

---

## 🔒 Güvenlik Özellikleri

1. **Root Kontrolü**: Program root yetkisi olmadan çalışmaz
2. **Yasal Uyarı**: Kullanıcı kabul etmeden devam edilmez
3. **Whitelist**: Kendi cihazı otomatik hariç tutulur
4. **Loglama**: Tüm işlemler kayıt altına alınır
5. **Graceful Shutdown**: Ctrl+C ile güvenli kapatma
6. **Cleanup**: Geçici dosyalar otomatik temizlenir

---

## 📈 Performans Özellikleri

1. **Multi-Threading**: Her hedef için ayrı thread
2. **Async Operations**: Blocking olmayan işlemler
3. **Efficient Parsing**: CSV streaming parse
4. **Resource Management**: Otomatik kaynak temizleme
5. **Rate Limiting**: Ağ yoğunluğuna göre ayarlama

---

## 🧪 Test Edilebilirlik

Her modül bağımsız test edilebilir:

```python
# wireless_manager testi
from core.wireless_manager import WirelessManager
wm = WirelessManager()
interfaces = wm.get_wireless_interfaces()

# network_scanner testi
from core.network_scanner import NetworkScanner
scanner = NetworkScanner("wlan0mon")
scanner.start_scan()

# deauth_engine testi
from core.deauth_engine import DeauthEngine
engine = DeauthEngine("wlan0mon")
engine.add_target("AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66")
```

---

## 🔧 Genişletilebilirlik

### Yeni Özellik Ekleme

1. **Yeni Saldırı Türü**:
   - `core/` altına yeni modül ekle
   - `main.py`'de entegre et

2. **Yeni UI Öğesi**:
   - `ui/` altına yeni modül ekle
   - Mevcut menülere entegre et

3. **Yeni Konfigürasyon**:
   - `config/settings.py`'ye ekle
   - İlgili modülde kullan

---

## 📊 Kod İstatistikleri

- **Toplam Satır**: ~3000+ satır
- **Modül Sayısı**: 13 modül
- **Sınıf Sayısı**: 8 ana sınıf
- **Fonksiyon Sayısı**: 100+ fonksiyon
- **Dokümantasyon**: 5 MD dosyası

---

## 🎯 Kod Kalitesi

- ✅ Type hints kullanımı
- ✅ Docstring'ler
- ✅ Error handling
- ✅ Logging
- ✅ Modüler yapı
- ✅ DRY prensibi
- ✅ SOLID prensipleri

---

**Proje yapısı hakkında daha fazla bilgi için ilgili modül dosyalarını inceleyin.**

