import socket
import threading
import queue
from message_handler import *
import time
from message_types import *
from gamestate import *


class Network(threading.Thread):
    def __init__(self, sock: socket.socket, message_queue: queue.Queue):
        super().__init__(daemon=True)
        self.sock = sock
        self.message_queue = message_queue
        self.running = True

        self.heartbeat_interval = PONG_INTERVAL
        self.timeout_limit = 10
        self.heartbeat_thread = None

        self.last_contact = time.time()
        self.connected = False
        self.first_ping_received = False
        
        self._stop_lock = threading.Lock()

    def _heartbeat_loop(self):
        """Sleduje heartbeat a detekuje ztrátu spojení"""
        print("[HEARTBEAT] ========== Thread start ==========")
        
        while self.running and not self.first_ping_received:
            print(f"[HEARTBEAT] Čekám na první PING... running={self.running}")
            time.sleep(0.5)
        
        if not self.running:
            print("[HEARTBEAT] ========== Thread end (stopped before first ping) ==========")
            return
            
        print("[HEARTBEAT] ========== První PING přijat, spouštím monitoring ==========")
        
        check_counter = 0
        while self.running:
            time.sleep(1)
            check_counter += 1
            elapsed = time.time() - self.last_contact
            
            # Vypíšeme stav každých 5 sekund
            if check_counter % 5 == 0:
                print(f"[HEARTBEAT] Check #{check_counter}: elapsed={elapsed:.1f}s, limit={self.timeout_limit}sekund, running={self.running}")
            
            if elapsed > self.timeout_limit:
                print(f"[HEARTBEAT] !!!!! TIMEOUT DETEKOVÁN !!!!!")
                print(f"[HEARTBEAT] elapsed={elapsed:.1f}s > limit={self.timeout_limit}s")
                
                with self._stop_lock:
                    print(f"[HEARTBEAT] Zámek získán, running={self.running}")
                    if self.running:
                        print(f"[HEARTBEAT] Nastavuji running=False a connected=False")
                        self.running = False
                        self.connected = False
                        
                        print(f"[HEARTBEAT] Posílám network_lost do fronty")
                        self.message_queue.put(("network_lost", "heartbeat timeout"))
                        
                        print(f"[HEARTBEAT] Zavírám socket...")
                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            print(f"[HEARTBEAT] Socket.shutdown() OK")
                        except Exception as e:
                            print(f"[HEARTBEAT] Socket.shutdown() failed: {e}")
                        
                        try:
                            self.sock.close()
                            print(f"[HEARTBEAT] Socket.close() OK")
                        except Exception as e:
                            print(f"[HEARTBEAT] Socket.close() failed: {e}")
                    else:
                        print(f"[HEARTBEAT] running už byl False, skip")
                break
                    
        print("[HEARTBEAT] ========== Thread end ==========")

    def start_heartbeat(self, interval=PONG_INTERVAL):
        """Spustí heartbeat monitoring vlákno"""
        print(f"[NETWORK] Startuji heartbeat s intervalem {interval}s")
        self.heartbeat_interval = interval
        self.timeout_limit = 2 * interval
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self.heartbeat_thread.start()

    def run(self):
        """Hlavní přijímací smyčka"""
        print("[NETWORK] ========== Receive thread start ==========")
        self.last_contact = time.time()
        self.start_heartbeat()

        try:
            self.sock.settimeout(2.0)
            print(f"[NETWORK] Socket timeout nastaven na 2.0s")
        except Exception as e:
            print(f"[NETWORK] Nepodařilo se nastavit timeout: {e}")

        loop_counter = 0
        while self.running:
            loop_counter += 1
            try:
                print(f"[NETWORK] Loop #{loop_counter}: Čekám na zprávu (running={self.running})...")
                type_msg, message = receive_full_message(self.sock)
                print(f"[NETWORK] Loop #{loop_counter}: Zpráva přijata: {type_msg}")

                self.last_contact = time.time()

                if type_msg == Message_types.PING.value:
                    if not self.first_ping_received:
                        self.first_ping_received = True
                        print("[NETWORK] !!!!! První PING přijat !!!!!")
                    
                    if not self.connected:
                        self.connected = True
                        self.message_queue.put(("reconnect_success", None))
                        print("[NETWORK] Posílám reconnect_success")

                    try:
                        packet = build_message(Message_types.PONG.value, "")
                        self.sock.sendall(packet)
                        print(f"[NETWORK] PONG odeslán")
                    except Exception as e:
                        print(f"[NETWORK] !!! Chyba při odesílání PONG: {e}")
                        raise
                    continue

                if type_msg == Message_types.RECO.value:
                    print(f"[NETWORK] RECO přijato: {message}")
                    self.message_queue.put(("message", type_msg, message))
                    continue

                if type_msg:
                    msg_preview = message[:50] if len(message) > 50 else message
                    print(f"[NETWORK] Normální zpráva: {type_msg} - {msg_preview}")
                    self.message_queue.put(("message", type_msg, message))

            except socket.timeout:
                print(f"[NETWORK] Loop #{loop_counter}: Socket timeout (normální, pokračuji)")
                continue

            except (ConnectionAbortedError, BrokenPipeError, 
                    OSError, ConnectionError) as e:
                print(f"[NETWORK] !!! Chyba spojení: {type(e).__name__}: {e}")
                
                with self._stop_lock:
                    print(f"[NETWORK] Zámek získán v error handleru, running={self.running}")
                    if self.running:
                        self.running = False
                        self.connected = False
                        print(f"[NETWORK] Posílám network_lost (connection error)")
                        self.message_queue.put(("network_lost", f"{type(e).__name__}: {str(e)}"))
                break

            except ConnectionResetError:
                print(e)
                break
            except Exception as e:
                print(f"[NETWORK] !!! Neočekávaná chyba: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
                with self._stop_lock:
                    if self.running:
                        self.running = False
                        self.message_queue.put(("error", str(e)))
                break
        
        print("[NETWORK] ========== Receive thread ukončen ==========")

    def stop(self):
        """Zastaví Network vlákno"""
        print("[NETWORK] ========== Stop() voláno ==========")
        
        with self._stop_lock:
            if not self.running:
                print("[NETWORK] Už není running, skip")
                return
            print("[NETWORK] Nastavuji running=False")
            self.running = False
        
        print("[NETWORK] Zavírám socket...")
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            print("[NETWORK] Socket.shutdown() OK")
        except Exception as e:
            print(f"[NETWORK] Socket.shutdown() failed: {e}")
        
        try:
            self.sock.close()
            print("[NETWORK] Socket.close() OK")
        except Exception as e:
            print(f"[NETWORK] Socket.close() failed: {e}")
        
        print("[NETWORK] ========== Stop() dokončeno ==========")