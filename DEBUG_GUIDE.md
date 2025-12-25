# KYKSKN - Debug Rehberi

## 🐛 Debug Modu

Program şu anda **debug modu aktif** durumda. Tarama sırasında detaylı bilgiler gösterecek.

### Debug Mesajları

Tarama sırasında şu bilgileri göreceksiniz:

```
🔍 DEBUG: CSV dosyası kontrol ediliyor: /tmp/kykskn/scan-01.csv
✓ CSV dosyası bulundu
🔍 DEBUG: CSV boyutu: 12543 byte
🔍 DEBUG: Windows format split: 1 bölüm
🔍 DEBUG: Linux format split: 2 bölüm
🔍 DEBUG: AP satır sayısı: 15
🔍 DEBUG: 8 AP başarıyla parse edildi
🔍 DEBUG: Client satır sayısı: 23
📊 Toplam: 8 ağ, 12 cihaz bulundu
```

---

## 🔍 Sorun Giderme

### Problem: "CSV dosyası bulunamadı"

**Neden:**
- `/tmp/kykskn/` dizini oluşturulamıyor
- Yazma izni yok
- airodump-ng çalışmıyor

**Çözüm:**
```bash
# Temp dizini kontrol et
ls -la /tmp/kykskn/

# Manuel oluştur
sudo mkdir -p /tmp/kykskn
sudo chmod 777 /tmp/kykskn

# Test et
sudo airodump-ng --output-format csv -w /tmp/kykskn/test wlan0mon
```

---

### Problem: "CSV dosyası çok küçük"

**Neden:**
- Tarama süresi çok kısa
- Çevrede ağ yok
- Wireless adapter sinyal almıyor

**Çözüm:**
```bash
# Manuel tarama yap (30 saniye)
sudo timeout 30 airodump-ng --output-format csv -w /tmp/test wlan0mon

# Dosya boyutunu kontrol et
ls -lh /tmp/test-01.csv

# İçeriğini görüntüle
cat /tmp/test-01.csv
```

---

### Problem: "Hiç ağ parse edilemedi"

**Neden:**
- CSV formatı beklenenden farklı
- ESSID boş (hidden network)
- BSSID formatı hatalı

**Debug:**
Program CSV'nin ilk 5 satırını gösterecek:
```
🔍 DEBUG: CSV ilk 5 satır:
  0: BSSID, First time seen, Last time seen, channel, Speed, Privacy...
  1: AA:BB:CC:DD:EE:FF, 2025-12-26 10:30:00, 2025-12-26 10:30:15, 6, 54...
```

**Çözüm:**
```bash
# CSV'yi manuel kontrol et
cat /tmp/kykskn/scan-01.csv | head -20

# Kolonları say
head -1 /tmp/kykskn/scan-01.csv | tr ',' '\n' | nl
```

---

### Problem: "Filtreleme sonrası 0 ağ"

**Neden:**
- Tüm ağların ESSID'si boş (hidden)
- Tüm ağların sinyali çok zayıf (< -100 dBm)

**Debug Çıktısı:**
```
🔍 DEBUG: get_sorted_aps - Toplam 5 ağ
🔍 DEBUG: Filtreleme sonrası 0 ağ (ESSID var ve sinyal > -100)
```

**Çözüm:**
Hidden network desteği için `core/network_scanner.py` dosyasında:
```python
# Satır 258'i değiştir
aps = [ap for ap in aps if ap.power > -100]  # ESSID kontrolünü kaldır
```

---

## 📊 Log Dosyası İnceleme

### Log Konumu
```bash
ls -lh logs/kykskn_*.log
```

### Son Logları Görüntüle
```bash
tail -50 logs/kykskn_*.log
```

### Hata Loglarını Filtrele
```bash
grep "ERROR" logs/kykskn_*.log
grep "WARNING" logs/kykskn_*.log
```

### Parse Detaylarını Görüntüle
```bash
grep "Parsing AP" logs/kykskn_*.log
grep "AP added" logs/kykskn_*.log
grep "AP skipped" logs/kykskn_*.log
```

---

## 🧪 Manuel Test

### 1. Wireless Interface Kontrolü
```bash
# Interface'leri listele
iwconfig

# Monitor mode kontrolü
iwconfig wlan0mon
```

### 2. Manuel Tarama
```bash
# 30 saniye tarama
sudo timeout 30 airodump-ng --output-format csv -w /tmp/test wlan0mon

# Sonuçları kontrol et
cat /tmp/test-01.csv
```

### 3. CSV Parse Testi
```python
# Python ile test
python3 << 'EOF'
import csv

with open('/tmp/test-01.csv', 'r') as f:
    content = f.read()
    sections = content.split('\n\n')
    print(f"Bölüm sayısı: {len(sections)}")
    
    ap_lines = sections[0].strip().split('\n')
    print(f"AP satır sayısı: {len(ap_lines)}")
    print(f"İlk satır: {ap_lines[0][:100]}")
    
    if len(ap_lines) > 1:
        print(f"İkinci satır: {ap_lines[1][:100]}")
EOF
```

---

## ⚙️ Debug Modunu Kapatma

Debug mesajlarını kapatmak için:

### Yöntem 1: Config Dosyası
`config/settings.py` dosyasında:
```python
DEBUG_MODE = False  # True'dan False'a çevir
```

### Yöntem 2: Kod Değişikliği
Debug mesajlarını yorum satırına al:
```python
# console.print(f"[dim]🔍 DEBUG: ...[/dim]")
```

---

## 📈 Başarılı Tarama Örneği

```
═══ Ağ Tarama ═══
Çevredeki kablosuz ağlar taranıyor...

🔍 DEBUG: Monitor interface: wlan0mon
⏳ 15 saniye tarama başlatılıyor...
📡 Ağlar taranıyor... (15 saniye)

🔍 DEBUG: CSV dosyası kontrol ediliyor: /tmp/kykskn/scan-01.csv
✓ CSV dosyası bulundu
🔍 DEBUG: CSV boyutu: 8432 byte
🔍 DEBUG: Linux format split: 2 bölüm
🔍 DEBUG: AP satır sayısı: 12
🔍 DEBUG: 8 AP başarıyla parse edildi
🔍 DEBUG: Client satır sayısı: 15
📊 Toplam: 8 ağ, 12 cihaz bulundu

🔍 DEBUG: get_sorted_aps - Toplam 8 ağ
🔍 DEBUG: Filtreleme sonrası 8 ağ (ESSID var ve sinyal > -100)

✓ 8 ağ bulundu
```

---

## 🎯 Sonraki Adımlar

1. **Programı çalıştır**: `sudo python3 main.py`
2. **Debug çıktılarını izle**: Hangi aşamada sorun var?
3. **Log dosyasını kontrol et**: `tail -f logs/kykskn_*.log`
4. **Sorunu belirle**: CSV, parse, veya filtreleme?
5. **GitHub'da issue aç**: Detaylı bilgi ile

---

**Debug modunu kullanarak sorunun tam kaynağını bulabiliriz!** 🔍

