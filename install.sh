#!/bin/bash

# KYKSKN Installation Script
# For Kali Linux

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   KYKSKN - Multi-Target Deauth Attack Framework          ║"
echo "║   Installation Script                                    ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Lütfen root olarak çalıştırın: sudo ./install.sh"
    exit 1
fi

echo "✓ Root yetkisi: OK"
echo ""

# Check if running on Linux
if [ "$(uname)" != "Linux" ]; then
    echo "❌ Bu script sadece Linux sistemlerde çalışır"
    exit 1
fi

echo "✓ İşletim sistemi: Linux"
echo ""

# Update package list
echo "📦 Paket listesi güncelleniyor..."
apt update -qq

# Install system dependencies
echo "📦 Sistem bağımlılıkları kontrol ediliyor..."

# Check and install aircrack-ng
if ! command -v aircrack-ng &> /dev/null; then
    echo "  ⚙️  aircrack-ng kuruluyor..."
    apt install -y aircrack-ng > /dev/null 2>&1
    echo "  ✓ aircrack-ng kuruldu"
else
    echo "  ✓ aircrack-ng zaten kurulu"
fi

# Check and install Python 3
if ! command -v python3 &> /dev/null; then
    echo "  ⚙️  python3 kuruluyor..."
    apt install -y python3 > /dev/null 2>&1
    echo "  ✓ python3 kuruldu"
else
    echo "  ✓ python3 zaten kurulu"
fi

# Check and install pip
if ! command -v pip3 &> /dev/null; then
    echo "  ⚙️  python3-pip kuruluyor..."
    apt install -y python3-pip > /dev/null 2>&1
    echo "  ✓ python3-pip kuruldu"
else
    echo "  ✓ python3-pip zaten kurulu"
fi

echo ""

# Install Python dependencies
echo "🐍 Python kütüphaneleri kuruluyor..."

# Try with --break-system-packages for Kali Linux
pip3 install -q --break-system-packages -r requirements.txt 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Python kütüphaneleri kuruldu"
else
    # If that fails, try system packages
    echo "  ⚙️  Sistem paketlerinden kuruluyor..."
    apt install -y python3-scapy python3-rich python3-netifaces python3-psutil > /dev/null 2>&1
    pip3 install -q --break-system-packages questionary pyfiglet colorama 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✓ Python kütüphaneleri kuruldu"
    else
        echo "❌ Python kütüphaneleri kurulumunda hata oluştu"
        echo "ℹ️  Manuel kurulum: pip3 install --break-system-packages -r requirements.txt"
        exit 1
    fi
fi

echo ""

# Make main.py executable
echo "⚙️  Yetkilendirme yapılıyor..."
chmod +x main.py
echo "✓ main.py çalıştırılabilir yapıldı"

echo ""

# Create logs directory
mkdir -p logs
echo "✓ Log dizini oluşturuldu"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ✅ Kurulum başarıyla tamamlandı!                       ║"
echo "║                                                           ║"
echo "║   Çalıştırmak için:                                      ║"
echo "║   sudo python3 main.py                                   ║"
echo "║                                                           ║"
echo "║   veya:                                                  ║"
echo "║   sudo ./main.py                                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

