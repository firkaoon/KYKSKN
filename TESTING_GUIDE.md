# Testing Guide - Client Detection Fix

## 🎯 Goal
Verify that the refactored scanner detects **ALL active clients** (3+) instead of just 2.

---

## ✅ Prerequisites

1. **Kali Linux** or similar penetration testing distribution
2. **Wireless adapter** in monitor mode (Realtek 802.11ac or similar)
3. **Controlled lab environment** with:
   - 1 Access Point (your test AP)
   - 3+ active client devices (phones, laptops, etc.)
   - Clients actively transmitting (browsing, streaming, etc.)

---

## 🔧 Setup

### 1. Install Dependencies
```bash
cd /path/to/KYKSKN
sudo ./install.sh
```

Or manually:
```bash
sudo apt update
sudo apt install -y aircrack-ng python3-scapy python3-rich python3-netifaces python3-psutil
sudo pip3 install --break-system-packages -r requirements.txt
```

### 2. Verify Installation
```bash
# Check Python packages
python3 -c "import scapy; print('✓ scapy')"
python3 -c "import rich; print('✓ rich')"

# Check aircrack-ng suite
which airodump-ng
which aireplay-ng
which airmon-ng
```

### 3. Enable Monitor Mode
```bash
# Find your wireless interface
iwconfig

# Enable monitor mode
sudo airmon-ng start wlan0

# Verify monitor interface (wlan0mon or similar)
iwconfig
```

---

## 🧪 Test 1: Baseline - Manual airodump-ng

**Purpose**: Establish ground truth for client count

```bash
# Terminal 1: Run manual airodump-ng
sudo airodump-ng wlan0mon

# Let it run for 30 seconds
# Observe the "Station" section (bottom half)
# Count the number of unique client MACs
# Example output:
#
# BSSID              STATION            PWR   Rate    Lost    Frames  Probe
# AA:BB:CC:DD:EE:FF  11:22:33:44:55:66  -45   54e-24   0       123    
# AA:BB:CC:DD:EE:FF  77:88:99:AA:BB:CC  -52   54e-24   0       89     
# AA:BB:CC:DD:EE:FF  DD:EE:FF:00:11:22  -48   54e-24   0       156    
#
# ✅ Ground Truth: 3 clients detected

# Press Ctrl+C to stop
```

**Expected Result**: You should see 3+ clients in the "Station" section.

**Record**:
- AP BSSID: `AA:BB:CC:DD:EE:FF`
- AP Channel: `6`
- Client Count: `3`
- Client MACs: `11:22:33:44:55:66`, `77:88:99:AA:BB:CC`, `DD:EE:FF:00:11:22`

---

## 🧪 Test 2: KYKSKN - Initial Scan

**Purpose**: Test the refactored scanner with initial 30-second scan

```bash
# Terminal 2: Run KYKSKN
cd /path/to/KYKSKN
sudo python3 main.py

# Follow the prompts:
# 1. Accept legal warning
# 2. Select "Start Attack"
# 3. Wait for 30-second scan
# 4. Observe output
```

**Expected Output**:
```
═══════════════════════════════════════════════════════════════════════════════
HYBRID PARSING: CSV (APs) + PCAP (Clients)
═══════════════════════════════════════════════════════════════════════════════

📊 Step 1: Parsing CSV for Access Points...
✓ AP: MyTestAP (AA:BB:CC:DD:EE:FF) - Ch6
✓ Found 1 Access Points

📦 Step 2: Parsing PCAP for ALL clients...
🔍 Reading PCAP file: /tmp/kykskn/scan-01.cap
📦 Analyzing 1234 packets...
✓ NEW CLIENT from PCAP: 11:22:33:44:55:66 -> AA:BB:CC:DD:EE:FF
✓ NEW CLIENT from PCAP: 77:88:99:AA:BB:CC -> AA:BB:CC:DD:EE:FF
✓ NEW CLIENT from PCAP: DD:EE:FF:00:11:22 -> AA:BB:CC:DD:EE:FF
✓ PCAP Analysis Complete!
  • New clients from PCAP: 3
  • Total clients in registry: 3

🔗 Step 3: Linking clients to APs...
✓ Client-AP associations updated

═══════════════════════════════════════════════════════════════════════════════
✓ SCAN COMPLETE!
📊 Access Points: 1
📱 Clients (this scan): 3
📜 All-time clients: 3
═══════════════════════════════════════════════════════════════════════════════
```

**Validation**:
- ✅ All 3+ clients detected (matches manual airodump-ng)
- ✅ PCAP analysis shows client extraction
- ✅ No "only 2 clients" limitation

---

## 🧪 Test 3: KYKSKN - Deep Scan

**Purpose**: Test deep scan accumulation (no client deletion)

```bash
# Continue from Test 2
# 5. Select your test AP from the list
# 6. Wait for 60-second deep scan
# 7. Observe real-time client discovery
```

**Expected Output**:
```
🔍 DEEP SCAN STARTING...
📡 Target: AA:BB:CC:DD:EE:FF
📻 Channel: 6
⏱️  Duration: 60 seconds
💡 This scan will find ALL clients on this network...

Scanning for clients (REAL-TIME)... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 20% 0:00:48
🆕 Found 3 client(s) so far!

Scanning for clients (REAL-TIME)... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00

✓ Deep scan completed!

═══════════════════════════════════════════════════════════════════════════════
✓ SCAN COMPLETE!
📊 Access Points: 1
📱 Clients (this scan): 3
📜 All-time clients: 3
═══════════════════════════════════════════════════════════════════════════════

✓ 3 total clients found for this AP!
```

**Validation**:
- ✅ Real-time client discovery (progress updates every 3 seconds)
- ✅ All clients accumulated (not deleted)
- ✅ Final count matches initial scan (persistent registry)

---

## 🧪 Test 4: Manual PCAP Verification

**Purpose**: Verify PCAP files contain all client frames

```bash
# After running KYKSKN, check the PCAP file
ls -lh /tmp/kykskn/

# You should see:
# scan-01.cap     (initial scan PCAP)
# scan-01.csv     (initial scan CSV)
# deepscan-01.cap (deep scan PCAP)
# deepscan-01.csv (deep scan CSV)

# Analyze PCAP with tcpdump
sudo tcpdump -r /tmp/kykskn/scan-01.cap -e | grep -i "11:22:33:44:55:66"
sudo tcpdump -r /tmp/kykskn/scan-01.cap -e | grep -i "77:88:99:AA:BB:CC"
sudo tcpdump -r /tmp/kykskn/scan-01.cap -e | grep -i "DD:EE:FF:00:11:22"

# Each command should show multiple frames
```

**Expected Result**:
```
12:34:56.123456 -45dBm signal antenna 0 11:22:33:44:55:66 > AA:BB:CC:DD:EE:FF, ...
12:34:57.234567 -45dBm signal antenna 0 11:22:33:44:55:66 > AA:BB:CC:DD:EE:FF, ...
12:34:58.345678 -45dBm signal antenna 0 11:22:33:44:55:66 > AA:BB:CC:DD:EE:FF, ...
...
```

**Validation**:
- ✅ PCAP contains frames from all 3+ clients
- ✅ Multiple frames per client (not just one)
- ✅ Both directions (client->AP and AP->client)

---

## 🧪 Test 5: Scapy PCAP Analysis

**Purpose**: Verify scapy correctly extracts clients from PCAP

```bash
# Python script to analyze PCAP
sudo python3 << 'EOF'
from scapy.all import rdpcap, Dot11
import re

pcap_file = '/tmp/kykskn/scan-01.cap'
packets = rdpcap(pcap_file)

print(f"Total packets: {len(packets)}")

# Extract unique client MACs
clients = set()
ap_bssids = set()

# First pass: Find APs
for pkt in packets:
    if pkt.haslayer(Dot11):
        if pkt.type == 0 and pkt.subtype == 8:  # Beacon
            bssid = pkt[Dot11].addr3.upper()
            ap_bssids.add(bssid)

print(f"APs found: {ap_bssids}")

# Second pass: Find clients
for pkt in packets:
    if pkt.haslayer(Dot11):
        addr1 = pkt[Dot11].addr1.upper() if pkt[Dot11].addr1 else None
        addr2 = pkt[Dot11].addr2.upper() if pkt[Dot11].addr2 else None
        
        # Skip broadcast
        if addr1 and not addr1.startswith('FF:FF') and addr1 not in ap_bssids:
            if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr1):
                clients.add(addr1)
        
        if addr2 and not addr2.startswith('FF:FF') and addr2 not in ap_bssids:
            if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr2):
                clients.add(addr2)

print(f"\nUnique clients found: {len(clients)}")
for client in sorted(clients):
    print(f"  • {client}")
EOF
```

**Expected Output**:
```
Total packets: 1234
APs found: {'AA:BB:CC:DD:EE:FF'}

Unique clients found: 3
  • 11:22:33:44:55:66
  • 77:88:99:AA:BB:CC
  • DD:EE:FF:00:11:22
```

**Validation**:
- ✅ Scapy correctly reads PCAP
- ✅ All 3+ clients extracted
- ✅ APs correctly identified (not counted as clients)

---

## 🧪 Test 6: Continuous Scan (Optional)

**Purpose**: Test unlimited scan duration with accumulation

```bash
# Modify main.py line 150:
# Change: success = self.network_scanner.start_scan(duration=30)
# To:     success = self.network_scanner.start_scan(duration=None)

sudo python3 main.py

# Let it run for several minutes
# Add/remove clients from the network
# Observe that new clients are discovered and accumulated
# Press Ctrl+C to stop

# Verify graceful shutdown:
# - Should see "Stopping scan gracefully..."
# - Should see "Waiting for buffer flush (up to 10s)..."
# - Should see "✓ Stopped gracefully"
```

**Expected Behavior**:
- ✅ Scan runs indefinitely until Ctrl+C
- ✅ New clients discovered in real-time
- ✅ Graceful shutdown (no frame loss)
- ✅ All clients accumulated in registry

---

## 📊 Results Comparison

| Test | Manual airodump-ng | OLD KYKSKN | NEW KYKSKN | Status |
|------|-------------------|-----------|-----------|--------|
| Initial Scan | 3 clients | 2 clients ❌ | 3 clients ✅ | **FIXED** |
| Deep Scan | 3 clients | 2 clients ❌ | 3 clients ✅ | **FIXED** |
| PCAP Analysis | 3 clients | N/A (no PCAP) | 3 clients ✅ | **FIXED** |
| Accumulation | 3 clients | Reset to 2 ❌ | Keeps 3 ✅ | **FIXED** |

---

## 🐛 Troubleshooting

### Issue: "No PCAP file found"
**Cause**: airodump-ng didn't create PCAP file
**Solution**:
```bash
# Check if airodump-ng is installed correctly
which airodump-ng

# Check if monitor mode is active
iwconfig

# Check if interface has permissions
sudo chmod 666 /tmp/kykskn/
```

### Issue: "Scapy import error"
**Cause**: Scapy not installed
**Solution**:
```bash
sudo apt install python3-scapy
# OR
sudo pip3 install --break-system-packages scapy
```

### Issue: "Only 1 client detected (should be 3)"
**Cause**: Clients not actively transmitting
**Solution**:
- Ensure clients are browsing/streaming (not idle)
- Increase scan duration (60+ seconds)
- Move clients closer to AP (better signal)

### Issue: "Permission denied"
**Cause**: Not running as root
**Solution**:
```bash
sudo python3 main.py  # Always use sudo!
```

---

## ✅ Success Criteria

The fix is successful if:

1. ✅ **Initial scan detects 3+ clients** (matches manual airodump-ng)
2. ✅ **Deep scan accumulates clients** (doesn't delete previous)
3. ✅ **PCAP files are created** (both CSV and PCAP output)
4. ✅ **PCAP parsing extracts all clients** (frame-level analysis)
5. ✅ **Graceful shutdown** (10-second timeout + 2-second sync)
6. ✅ **Persistent registry** (clients accumulate over time)
7. ✅ **Real-time monitoring** (progress updates every 5 seconds)

---

## 📝 Test Report Template

```
=== KYKSKN Client Detection Test Report ===

Date: _______________
Tester: _______________
Environment: _______________

Lab Setup:
- AP BSSID: _______________
- AP Channel: _______________
- AP ESSID: _______________
- Active Clients: _______________

Test 1: Manual airodump-ng
- Clients Detected: _______________
- Client MACs: _______________

Test 2: KYKSKN Initial Scan
- Clients Detected: _______________
- Client MACs: _______________
- Match Manual? [ ] Yes [ ] No

Test 3: KYKSKN Deep Scan
- Clients Detected: _______________
- Client MACs: _______________
- Accumulation Working? [ ] Yes [ ] No

Test 4: PCAP Verification
- PCAP File Size: _______________
- Packets in PCAP: _______________
- Clients in PCAP: _______________

Test 5: Scapy Analysis
- Clients Extracted: _______________
- Match KYKSKN? [ ] Yes [ ] No

Overall Result:
[ ] PASS - All tests successful
[ ] FAIL - Issues found (describe below)

Notes:
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## 🎉 Expected Final Result

After all tests, you should see:

```
✅ KYKSKN detects ALL 3+ active clients
✅ Matches manual airodump-ng accuracy
✅ PCAP-based extraction working correctly
✅ Graceful shutdown (zero frame loss)
✅ Persistent client registry (accumulation)
✅ Real-time monitoring (progress feedback)

🎯 GOAL ACHIEVED: Maximum clients = RF limit (not software limit)
```

---

## 📚 Additional Resources

- **airodump-ng manual**: `man airodump-ng`
- **Scapy documentation**: https://scapy.readthedocs.io/
- **802.11 frame format**: https://en.wikipedia.org/wiki/IEEE_802.11
- **PCAP file format**: https://wiki.wireshark.org/Development/LibpcapFileFormat

---

## 🆘 Support

If tests fail or you need help:

1. Check logs: `cat logs/kykskn_*.log`
2. Enable debug mode: `config/settings.py` → `DEBUG_MODE = True`
3. Review documentation: `CLIENT_DETECTION_FIX.md`
4. Compare with manual airodump-ng (ground truth)

**Remember**: The fix works if KYKSKN matches manual airodump-ng accuracy! 🎯

