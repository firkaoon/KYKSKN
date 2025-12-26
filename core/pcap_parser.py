"""
KYKSKN - PCAP Parser for Client Extraction
Extracts all clients from PCAP files using frame-level analysis
"""

import os
from typing import Set, Dict, Tuple
from scapy.all import rdpcap, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp, Dot11AssoReq, Dot11AssoResp, Dot11Auth, Dot11Deauth, Dot11Disas, Dot11QoS
from rich.console import Console
from utils.logger import logger

console = Console()


class PcapClientExtractor:
    """Extract client MAC addresses from PCAP files"""
    
    def __init__(self):
        self.clients: Dict[str, Dict[str, any]] = {}  # MAC -> {bssid, packets, power}
        
    def extract_clients_from_pcap(self, pcap_file: str, target_bssid: str = None) -> Set[str]:
        """
        Extract all client MAC addresses from PCAP file
        
        Args:
            pcap_file: Path to PCAP file
            target_bssid: Optional BSSID filter (only clients for this AP)
            
        Returns:
            Set of client MAC addresses (uppercase)
        """
        clients = set()
        
        if not os.path.exists(pcap_file):
            logger.warning(f"PCAP file not found: {pcap_file}")
            return clients
        
        try:
            logger.info(f"Parsing PCAP: {pcap_file}")
            console.print(f"[dim]🔍 PCAP: Reading {pcap_file}...[/dim]")
            
            # Read PCAP file
            packets = rdpcap(pcap_file)
            logger.info(f"PCAP: {len(packets)} packets read")
            console.print(f"[dim]🔍 PCAP: {len(packets)} packets loaded[/dim]")
            
            frame_count = 0
            client_frames = 0
            
            for pkt in packets:
                if not pkt.haslayer(Dot11):
                    continue
                
                frame_count += 1
                dot11 = pkt.getlayer(Dot11)
                
                # Extract addresses
                # addr1 = Receiver Address (RA)
                # addr2 = Transmitter Address (TA) 
                # addr3 = BSSID (usually)
                # addr4 = Used in WDS
                
                addr1 = dot11.addr1
                addr2 = dot11.addr2
                addr3 = dot11.addr3
                
                if not addr1 or not addr2:
                    continue
                
                # Normalize MAC addresses
                addr1 = addr1.upper()
                addr2 = addr2.upper()
                addr3 = addr3.upper() if addr3 else None
                
                # Skip broadcast/multicast
                if addr1.startswith('FF:FF:FF:FF:FF:FF'):
                    continue
                if addr2.startswith('FF:FF:FF:FF:FF:FF'):
                    continue
                
                # Determine BSSID and client MAC
                bssid = None
                client_mac = None
                
                # Frame type analysis
                frame_type = dot11.type
                frame_subtype = dot11.subtype
                
                # Management frames (type 0)
                if frame_type == 0:
                    # Beacon (subtype 8)
                    if frame_subtype == 8:
                        # addr2 is AP BSSID, skip
                        continue
                    
                    # Probe Request (subtype 4)
                    elif frame_subtype == 4:
                        # addr2 is client MAC (source)
                        client_mac = addr2
                        # No BSSID in probe request (broadcast)
                        bssid = None
                    
                    # Probe Response (subtype 5)
                    elif frame_subtype == 5:
                        # addr1 is client MAC (destination)
                        # addr2 is AP BSSID
                        client_mac = addr1
                        bssid = addr2
                    
                    # Authentication (subtype 11)
                    elif frame_subtype == 11:
                        # addr1 = receiver, addr2 = transmitter, addr3 = BSSID
                        bssid = addr3
                        # Direction: To DS or From DS
                        if dot11.FCfield & 0x01:  # To DS
                            client_mac = addr2  # Client is transmitter
                        else:  # From DS
                            client_mac = addr1  # Client is receiver
                    
                    # Association Request (subtype 0)
                    elif frame_subtype == 0:
                        # addr1 is AP BSSID
                        # addr2 is client MAC
                        client_mac = addr2
                        bssid = addr1
                    
                    # Association Response (subtype 1)
                    elif frame_subtype == 1:
                        # addr1 is client MAC
                        # addr2 is AP BSSID
                        client_mac = addr1
                        bssid = addr2
                    
                    # Reassociation Request (subtype 2)
                    elif frame_subtype == 2:
                        client_mac = addr2
                        bssid = addr1
                    
                    # Reassociation Response (subtype 3)
                    elif frame_subtype == 3:
                        client_mac = addr1
                        bssid = addr2
                    
                    # Deauthentication (subtype 12)
                    elif frame_subtype == 12:
                        bssid = addr3
                        if dot11.FCfield & 0x01:  # To DS
                            client_mac = addr2
                        else:
                            client_mac = addr1
                    
                    # Disassociation (subtype 10)
                    elif frame_subtype == 10:
                        bssid = addr3
                        if dot11.FCfield & 0x01:  # To DS
                            client_mac = addr2
                        else:
                            client_mac = addr1
                
                # Data frames (type 2)
                elif frame_type == 2:
                    # addr3 is usually BSSID
                    bssid = addr3
                    
                    # Check direction
                    to_ds = dot11.FCfield & 0x01
                    from_ds = dot11.FCfield & 0x02
                    
                    if to_ds and not from_ds:
                        # Client to AP
                        client_mac = addr2  # Source (client)
                        bssid = addr1  # Destination (AP)
                    elif from_ds and not to_ds:
                        # AP to Client
                        client_mac = addr1  # Destination (client)
                        bssid = addr2  # Source (AP)
                    elif to_ds and from_ds:
                        # WDS (skip for now)
                        continue
                    else:
                        # IBSS (ad-hoc, skip)
                        continue
                
                # If we found a client
                if client_mac:
                    # Filter by target BSSID if specified
                    if target_bssid:
                        target_bssid_upper = target_bssid.upper()
                        if bssid and bssid != target_bssid_upper:
                            continue
                    
                    # Add to clients set
                    clients.add(client_mac)
                    client_frames += 1
                    
                    # Store in detailed dict
                    if client_mac not in self.clients:
                        self.clients[client_mac] = {
                            'bssid': bssid,
                            'packets': 1,
                            'power': -100  # Will be updated from CSV
                        }
                    else:
                        self.clients[client_mac]['packets'] += 1
                        if bssid:
                            self.clients[client_mac]['bssid'] = bssid
            
            logger.info(f"PCAP: {frame_count} 802.11 frames, {client_frames} client frames, {len(clients)} unique clients")
            console.print(f"[green]✓ PCAP: {len(clients)} unique clients extracted from {client_frames} frames[/green]")
            
            return clients
            
        except Exception as e:
            logger.error(f"Error parsing PCAP: {e}")
            console.print(f"[red]✗ PCAP parse error: {e}[/red]")
            import traceback
            logger.debug(traceback.format_exc())
            return clients
    
    def get_client_details(self, mac: str) -> Dict[str, any]:
        """Get detailed info for a client MAC"""
        return self.clients.get(mac.upper(), None)
    
    def merge_with_csv_data(self, csv_clients: Dict[str, any]):
        """Merge PCAP clients with CSV data (power, BSSID confirmation)"""
        for mac, csv_data in csv_clients.items():
            if mac in self.clients:
                # Update with CSV data (more accurate)
                self.clients[mac]['power'] = csv_data.get('power', -100)
                self.clients[mac]['bssid'] = csv_data.get('bssid', self.clients[mac]['bssid'])
            else:
                # Add CSV-only client
                self.clients[mac] = csv_data



