# Kali Linux Python Hatası Çözümü

## 🐛 Sorun

Kali Linux'un yeni sürümlerinde (Python 3.11+) şu hatayı alabilirsiniz:

```
error: externally-managed-environment
```

Bu, Kali'nin sistem Python'unu korumak için aldığı bir önlemdir.

---

## ✅ Çözüm 1: Güncellenmiş Install Script (Önerilen)

Güncellenmiş `install.sh` dosyası artık bu sorunu otomatik çözer:

```bash
sudo ./install.sh
```

Script şimdi `--break-system-packages` bayrağını kullanır.

---

## ✅ Çözüm 2: Manuel Kurulum

### Yöntem A: Break System Packages (Hızlı)

```bash
sudo pip3 install --break-system-packages -r requirements.txt
```

### Yöntem B: Sistem Paketleri + PIP (Güvenli)

```bash
# Önce sistem paketlerini kur
sudo apt install -y python3-scapy python3-rich python3-netifaces python3-psutil

# Sonra eksik olanları pip ile kur
sudo pip3 install --break-system-packages questionary pyfiglet colorama
```

### Yöntem C: Virtual Environment (En Güvenli)

```bash
# Virtual environment oluştur
python3 -m venv kykskn-venv

# Aktif et
source kykskn-venv/bin/activate

# Kütüphaneleri kur
pip install -r requirements.txt

# Programı çalıştır
sudo ./kykskn-venv/bin/python3 main.py
```

---

## ✅ Çözüm 3: Pipx Kullanımı

```bash
# Pipx kur
sudo apt install pipx

# Her kütüphaneyi pipx ile kur
pipx install scapy
pipx install rich
# ... diğerleri
```

---

## 🚀 Hızlı Çözüm (Tek Komut)

En hızlı çözüm:

```bash
sudo pip3 install --break-system-packages scapy rich questionary pyfiglet netifaces psutil colorama
```

Sonra programı çalıştır:

```bash
sudo python3 main.py
```

---

## ⚠️ Güvenlik Notu

`--break-system-packages` kullanmak sistem Python'unu etkileyebilir, ancak:

- ✅ Kali Linux bir test dağıtımıdır
- ✅ Genellikle VM/container'da çalışır
- ✅ Bu paketler zararsızdır
- ✅ Kali düzenli güncellenir

**Üretim sistemlerinde virtual environment kullanın!**

---

## 🔍 Kurulum Doğrulama

Kütüphanelerin kurulu olup olmadığını kontrol edin:

```bash
python3 -c "import scapy; print('✓ scapy')"
python3 -c "import rich; print('✓ rich')"
python3 -c "import questionary; print('✓ questionary')"
python3 -c "import pyfiglet; print('✓ pyfiglet')"
python3 -c "import netifaces; print('✓ netifaces')"
python3 -c "import psutil; print('✓ psutil')"
python3 -c "import colorama; print('✓ colorama')"
```

Hepsi "✓" gösteriyorsa kurulum başarılı!

---

## 🎯 Programı Çalıştır

```bash
sudo python3 main.py
```

---

## 📚 Daha Fazla Bilgi

- [Kali Python Packages Guide](https://www.kali.org/docs/general-use/python3-external-packages/)
- [PEP 668 - Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)

---

**Sorun devam ediyorsa GitHub Issues'da bildirin!**

