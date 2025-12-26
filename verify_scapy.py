#!/usr/bin/env python3
"""
Verify Scapy imports for KYKSKN
"""

try:
    from scapy.all import rdpcap, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp, Dot11AssoReq, Dot11AssoResp, Dot11Auth, Dot11Deauth, Dot11Disas
    print("✓ All Scapy imports successful!")
    print("✓ rdpcap")
    print("✓ Dot11")
    print("✓ Dot11Beacon")
    print("✓ Dot11ProbeReq")
    print("✓ Dot11ProbeResp")
    print("✓ Dot11AssoReq")
    print("✓ Dot11AssoResp")
    print("✓ Dot11Auth")
    print("✓ Dot11Deauth")
    print("✓ Dot11Disas")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nTrying alternative imports...")
    
    # Try individual imports to identify the problem
    imports = [
        ('rdpcap', 'rdpcap'),
        ('Dot11', 'Dot11'),
        ('Dot11Beacon', 'Dot11Beacon'),
        ('Dot11ProbeReq', 'Dot11ProbeReq'),
        ('Dot11ProbeResp', 'Dot11ProbeResp'),
        ('Dot11AssoReq', 'Dot11AssoReq'),
        ('Dot11AssoResp', 'Dot11AssoResp'),
        ('Dot11Auth', 'Dot11Auth'),
        ('Dot11Deauth', 'Dot11Deauth'),
        ('Dot11Disas', 'Dot11Disas'),
    ]
    
    for name, import_name in imports:
        try:
            exec(f"from scapy.all import {import_name}")
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT AVAILABLE")

