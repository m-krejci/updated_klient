import pygame
from constants import *
import os
import socket
from network import *
from typing import Optional
from gamestate import *
from message_types import *
from console import *
from ui_elements import UI
from card import *
from pages_drawer import *
import sys
import queue
import threading


class ClientGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("JOKERS!")
        self.clock = pygame.time.Clock()

        # Fonty
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.table_font = pygame.font.SysFont(None, 32)
        self.bold_font = pygame.font.SysFont(None, 34, bold=True)

        # Inicializace kresliče obrazovek
        self.ui = UI(self.screen, self.font, self.font_small)
        self.page_drawer = PageDrawer(self.screen, self.font, self.ui)

        # Obrázky karet (slovník) a struktury pro karty
        self.cards = dict()
        self.cards_list = []
        self.new_cards = True
        self.card_objects: list[Card] = []

        # Stav aplikace
        self.running: bool = True
        self.connected = False
        self.sock: Optional[socket.socket] = None
        self.network_thread: Optional[Network] = None
        self.message_queue: Optional[queue.Queue] = queue.Queue()

        # STAV : DISCONNECTED
        # Pomocné proměnné:
        self.waiting_for_login_response = False
        self.login_error = ""
        self.connect_error = ""

        # STAV : CONNECTED
        # Pomocné proměnné
        self.rooms_list: list[dict] = []
        self.current_room = ""
        self.current_room_name = ""
        self.room_status_ready = False
        

        # STAV : IN_ROOM
        # Pomocné proměnné
        self.room_owner = False
        self.room_inroom_players_ready = f"(0/{MAX_ROOM_PLAYERS})"
        self.room_players_info = []
        self.game_on_turn = False
        self.room_buttons = []

        # STAV : IN_GAME
        # Pomocné proměnné
        self.discard = ""
        self.sequence_list = []
        self.seq_existing = False
        self.enemy_hand_count = 0
        self.results = dict()
        self.user_seradit = False
        self.prilozit_active = False
        self.sequences_area_rect = None
        self.sequence_rects = []
        self.game_enemy_hand_count = ""
        self.enemy_name = ""

        # GAMESCREEN : CONNECT
        self.login_text = "tigo"
        self.login_error = ""
        self.server_text = "192.168.0.159"
        self.server_error = ""
        self.port_text = "10000"
        self.port_error = ""

        # GAMESCREEN : LOBBY
        self.show_create_room_popup = False
        self.create_room_text = ""
        self.popup_rect = pygame.Rect(400, 250, 400, 200)
        self.popup_input_rect = pygame.Rect(420, 320, 360, 40)

        # GAMESCREEN : GAMEDONE
        self.clicked_plag = True
        self.user_disconnected = ""

        # RECONNECT
        self._reconnecting = False

        # Buttons
        self.connect_button = pygame.Rect(WINDOW_WIDTH // 2 - (250 // 2), WINDOW_HEIGHT // 2 + 200, 250, 40)    # login screen
        self.lobby_button_obnovit = pygame.Rect(60, 550, 240, 60)                                               # lobby screen
        self.lobby_button_vytvorit_mistnost = pygame.Rect(360, 550, 240, 60)                                    # lobby screen
        self.lobby_disconnect = pygame.Rect(WINDOW_WIDTH-100, 30, 70, 30)                                       # lobby screen        
        self.room_exit = pygame.Rect(WINDOW_WIDTH - 200, 30, 100, 60)                                           # room screen
        self.room_ready = pygame.Rect(WINDOW_WIDTH - 200, 100, 100, 60)                                         # room screen
        self.room_start = pygame.Rect(WINDOW_WIDTH - 200, 170, 100, 60)                                         # room screen
        self.game_vyhodit_rect = pygame.Rect(20, WINDOW_HEIGHT - 60, 100, 40)
        self.game_liznout_rect = pygame.Rect(130, WINDOW_HEIGHT - 60, 100, 40)
        self.game_liznout_vyhozenou_rect = pygame.Rect(460, WINDOW_HEIGHT - 60, 200, 40)
        self.game_vylozit_rect = pygame.Rect(350, WINDOW_HEIGHT - 60, 100, 40)
        self.game_zavrit_rect = pygame.Rect(240, WINDOW_HEIGHT - 60, 100, 40)
        self.game_seradit_rect = pygame.Rect(670, WINDOW_HEIGHT - 110, 100, 40)
        self.game_prilozit_rect = pygame.Rect(670, WINDOW_HEIGHT - 60, 100, 40)
        self.playagain_button = pygame.Rect(20, 20, 180, 40)
        self.back_to_lobby = pygame.Rect(20, 75, 180, 40)
        

        # LOGIN INPUT SETTINGS
        self.active_input = "login"
        CENTER_X = WINDOW_WIDTH // 2
        START_Y = WINDOW_HEIGHT // 2 - 200
        INPUT_WIDTH = 260
        INPUT_HEIGHT = 40
        INPUT_GAP = 90

        self.login_name_input = pygame.Rect(CENTER_X - INPUT_WIDTH // 2, START_Y, INPUT_WIDTH, INPUT_HEIGHT)
        self.server_address_input = pygame.Rect(CENTER_X - INPUT_WIDTH // 2, START_Y + INPUT_GAP, INPUT_WIDTH, INPUT_HEIGHT)
        self.port_input = pygame.Rect(CENTER_X - INPUT_WIDTH // 2, START_Y + INPUT_GAP * 2, INPUT_WIDTH, INPUT_HEIGHT)

        # Herní konzole
        self.game_console_font = pygame.font.Font(None, 22)
        self.game_console = Console(
            rect=pygame.Rect(790, 625, 400, 60),
            font=self.game_console_font,
            max_lines=3
        )

        # nastavení gamestatu
        self.game_state = GameState.DISCONNECTED

        # načtení karet
        self._load_assets()


    def _load_assets(self):
        # Struktury pro uchování definovaných názvů karet
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A"]
        suits = ["S", "H", "C", "D"]

        # Načtení karet
        for rank in ranks:
            for suit in suits:
                name = f"{rank}{suit}"
                path = os.path.join(CARDS_PATH, name + ".png")
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.cards[name] = pygame.transform.smoothscale(img, size=CARD_SIZE)
                
                except:
                    print(f"Nebylo možné načíst kartu [{name}.png]")

        # Načtení zadní strany karet
        try:
            img = pygame.image.load(os.path.join(CARDS_PATH, "BS.png"))
            self.cards["BS"] = pygame.transform.smoothscale(img, size=CARD_SIZE)

        except:
            print(f"Nebylo možné načíst kartu [BS.png]")

        try:
            img = pygame.image.load(os.path.join(CARDS_PATH, "YY.png"))
            self.cards["YY"] = pygame.transform.smoothscale(img, size=CARD_SIZE)

        except:
            print(f"Nebylo možné načíst kartu [YY.png]")
    
    def _threaded_connect_process(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0) 
            
            print(f"Pokus o připojení k: {self.server_text}:{self.port_text}")
            self.sock.connect((self.server_text, int(self.port_text)))
            
            self.sock.settimeout(None)
            self.connected = True
            
            self.network_thread = Network(self.sock, self.message_queue)
            self.network_thread.start()
            self.send_message(Message_types.LOGI.value, self.login_text)
            
        except Exception as e:
            print(f"Chyba při navazování spojení: {e}")
            self.connected = False
            self.waiting_for_login_response = False
            self.connect_error = f"Chyba připojení: {e}"

    def send_message(self, type_msg: str, msg: str):
        """Odesílá zprávu na server"""
        print(f"[SEND] Pokus o odeslání: type={type_msg}, msg={msg[:50] if len(msg) > 50 else msg}")
        print(f"[SEND] connected={self.connected}, sock={'OK' if self.sock else 'NONE'}")
        
        if not self.connected:
            print(f"[SEND] !!! NELZE ODESLAT - není connected")
            self.game_console.log("Nelze odeslat - odpojeno", True)
            return
        
        if not self.sock:
            print(f"[SEND] !!! NELZE ODESLAT - sock je None")
            self.game_console.log("Nelze odeslat - chybí socket", True)
            return
        
        try:
            packet = build_message(type_msg, msg)
            print(f"[SEND] Odesílám packet...")
            self.sock.sendall(packet)
            print(f"[SEND] ✓ Odesláno úspěšně")

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"[SEND] !!! Chyba při odesílání: {type(e).__name__}: {e}")
            self.game_console.log("Chyba při odesílání - spojení ztraceno", True)
            
            # Spustí reconnect
            self.connected = False
            self.message_queue.put(("network_lost", f"send failed: {e}"))
            
        except Exception as e:
            print(f"[SEND] !!! Neočekávaná chyba: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def sort_cards(self):
        """ Řadí karty v ruce hráče podle hodnoty a barvy"""
        values = {
            "S": 10, "C": 1011, "H": 101, "D": 10111, "X": 10, "J": 11, "Q": 12, "K": 13, "A": 1, "Y": 100000
        }

        for i in range(len(self.cards_list)):
            for j in range(i, len(self.cards_list)):
                if i != j:
                    rank_first = self.cards_list[i][0]
                    if rank_first in values.keys():
                        rank_value = values[rank_first]
                    else:
                        try:
                            rank_value = int(rank_first)
                        except Exception as e:
                            print(e)
                    
                    suit_first = values[self.cards_list[i][1]]
                    rank_second = self.cards_list[j][0]

                    if rank_second in values.keys():
                        rank_value_2 = values[rank_second]
                    
                    else:
                        try:
                            rank_value_2 = int(rank_second)
                        except Exception as e:
                            print(e)

                    suit_second = values[self.cards_list[j][1]]
                    first = rank_value + suit_first
                    second = rank_value_2 + suit_second

                    if first > second:
                        temp = self.cards_list[i]
                        self.cards_list[i] = self.cards_list[j]
                        self.cards_list[j] = temp

        self.new_cards = True

    def start_reconnect_thread(self):
        """Spustí reconnect vlákno pokud již neběží"""
        print(f"[RECONNECT] start_reconnect_thread() voláno, _reconnecting={getattr(self, '_reconnecting', False)}")
        
        if getattr(self, "_reconnecting", False):
            print(f"[RECONNECT] Už běží, skip")
            return
        
        print(f"[RECONNECT] Nastavuji _reconnecting=True")
        self._reconnecting = True
        self.connected = False
        self.game_state = GameState.DISCONNECTED
        
        print(f"[RECONNECT] Spouštím reconnect thread")
        t = threading.Thread(target=self._threaded_reconnect_process, daemon=True)
        t.start()
        print(f"[RECONNECT] Thread spuštěn")

    def _threaded_reconnect_process(self):
        print(f"[RECONNECT] ========== Reconnect thread START ==========")
        attempts = 0
        max_attempts = 10
        backoff_time = 2
        
        while attempts < max_attempts and self.running:
            attempts += 1
            wait_time = min(backoff_time * (2 ** (attempts - 1)), 30)
            
            print(f"[RECONNECT] Pokus #{attempts}/{max_attempts}, čekám {wait_time}s...")
            time.sleep(wait_time)
            
            if not self.running:
                print(f"[RECONNECT] self.running=False, končím")
                break
            
            try:
                print(f"[RECONNECT] Pokus #{attempts}: Cleanup starého spojení...")
                # 1. Cleanup starého spojení
                if self.network_thread:
                    print(f"[RECONNECT] Zastavuji staré network vlákno...")
                    self.network_thread.stop()
                    self.network_thread = None
                    print(f"[RECONNECT] Staré vlákno zastaveno")
                
                if self.sock:
                    print(f"[RECONNECT] Zavírám starý socket...")
                    try:
                        self.sock.close()
                    except:
                        pass
                    self.sock = None
                    print(f"[RECONNECT] Starý socket zavřen")
                
                # 2. Vytvoření nového socketu
                print(f"[RECONNECT] Vytvářím nový socket...")
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_sock.settimeout(5.0)
                
                print(f"[RECONNECT] Připojuji se k {self.server_text}:{self.port_text}...")
                new_sock.connect((self.server_text, int(self.port_text)))
                new_sock.settimeout(None)
                print(f"[RECONNECT] ✓ Spojení navázáno!")
                
                # 3. Odeslání LOGI
                print(f"[RECONNECT] Odesílám LOGI zprávu...")
                packet = build_message(Message_types.LOGI.value, self.login_text)
                new_sock.sendall(packet)
                print(f"[RECONNECT] ✓ LOGI odeslán")
                
                # 4. Předání řízení síťovému vláknu
                print(f"[RECONNECT] Předávám socket network threadu...")
                self.sock = new_sock
                self.network_thread = Network(self.sock, self.message_queue)
                self.network_thread.start()
                self.connected = True
                print(f"[RECONNECT] ✓ Network thread spuštěn")
                
                print(f"[RECONNECT] ========== Reconnect proces iniciován, čekám na OKAY/RECO ==========")
                return 
                
            except Exception as e:
                print(f"[RECONNECT] !!! Pokus {attempts} selhal: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
                # Cleanup po chybě
                if 'new_sock' in locals():
                    try:
                        new_sock.close()
                    except:
                        pass
        
        # Pokud jsme vyčerpali všechny pokusy
        print(f"[RECONNECT] ========== Reconnect FAILED po {attempts} pokusech ==========")
        self._reconnecting = False
        self.game_console.log(f"Reconnect selhal po {attempts} pokusech", True)
    
    def process_queue(self):
        processed_count = 0
        max_process = 50  # Ochrana proti nekonečné smyčce
        
        while processed_count < max_process:
            try:
                item = self.message_queue.get_nowait()
                processed_count += 1
                
                # PRIORITA 1: network_lost - okamžitá reakce
                if item[0] == "network_lost":
                    print(f"[GUI] !!! NETWORK_LOST DETEKOVÁN: {item[1]} !!!")
                    self.game_console.log("Spojení ztraceno, pokouším se o reconnect", True)
                    self.connected = False
                    self.game_state = GameState.DISCONNECTED
                    if "10054" in item[1]:
                        self.waiting_for_login_response = False
                        self.connect_error = item[1]
                    else:
                        self.start_reconnect_thread()
                    continue  # Zpracuj další zprávy
                
                # PRIORITA 2: error
                if item[0] == "error":
                    print(f"[GUI] ERROR: {item[1]}")
                    self.connected = False
                    self.game_state = GameState.DISCONNECTED
                    continue
                
                # PRIORITA 3: reconnect_success
                if item[0] == "reconnect_success":
                    print(f"[GUI] Reconnect success signal")
                    # Toto je jen informativní, skutečný reconnect potvrdí RECO zpráva
                    continue

                # Normální zprávy
                if item[0] == "message":
                    _, type_msg, message = item

                    if self.game_state == GameState.DISCONNECTED:
                        if type_msg == Message_types.OKAY.value:
                            self.waiting_for_login_response = False
                            if message == "LOBBY":
                                self.game_state = GameState.CONNECTED
                            elif message == "TURN":
                                self.game_on_turn = True
                                self.game_state = GameState.IN_GAME
                            elif message == "WAIT":
                                self.game_on_turn = False
                            elif message == "PAUSED":
                                pass
                            else:
                                self.game_state = GameState.CONNECTED

                            self.game_state = GameState.CONNECTED
                            self.game_console.log(message, False)
                        
                        elif type_msg == Message_types.RECO.value:
                            print(f"[GUI] ✓ RECO přijato - reconnect úspěšný!")
                            self.connected = True
                            self.game_state = GameState.CONNECTED
                            self._reconnecting = False
                            self.waiting_for_login_response = False
                            self.game_console.log("Reconnect úspěšný", False)

                        elif type_msg == Message_types.ERRR.value:
                            self.waiting_for_login_response = False
                            self.login_error = message

                        elif type_msg == Message_types.STAT.value:
                            self.game_state = GameState.IN_GAME
                            zprava = message.split("|")
                            karty = zprava[0]
                            self.cards_list = []
                            start, end = 0, 2

                            for i in range(len(karty) // 2):
                                self.cards_list.append(karty[start:end])
                                start += 2
                                end += 2
                            
                            self.discard = zprava[1]

                            sekvence = zprava[2]
                            self.sequence_list = sekvence.split(",")

                            if len(sekvence) >= 1:
                                self.seq_existing = True
                            else:
                                self.seq_existing = False

                            poradi = zprava[3]
                            if poradi == "TURN":
                                self.game_on_turn = True
                            else:
                                self.game_on_turn = False

                            self.enemy_hand_count = int(zprava[4])
                            self.new_cards = True

                        
                    elif self.game_state == GameState.CONNECTED:
                        if type_msg == Message_types.RLIS.value:
                            self.rooms_list.clear()
                            rooms = message.split(",")

                            for room in rooms:
                                if not room.strip():
                                    continue

                                parts = room.split("|")
                                if len(parts) != 4:
                                    continue

                                room_index = int(parts[0].strip())
                                room_name = parts[1].strip()
                                room_capacity = parts[2].strip()
                                room_status = parts[3].strip()

                                self.rooms_list.append({
                                    "index": room_index,
                                    "name": room_name,
                                    "capacity": room_capacity,
                                    "status": room_status
                                })

                        if type_msg == Message_types.OKAY.value:
                            self.game_console.log(message, False)

                        elif type_msg == Message_types.STAT.value:
                            zprava = message.split("|")
                            karty = zprava[0]
                            self.cards_list = []
                            start, end = 0, 2

                            for i in range(len(karty) // 2):
                                self.cards_list.append(karty[start:end])
                                start += 2
                                end += 2
                            
                            self.discard = zprava[1]

                            sekvence = zprava[2]
                            self.sequence_list = sekvence.split(",")

                            if len(sekvence) >= 1:
                                self.seq_existing = True
                            else:
                                self.seq_existing = False

                            poradi = zprava[3]

                            self.enemy_hand_count = int(zprava[4])
                            
                            self.new_cards = True
                            self.game_state = GameState.IN_GAME
                            self.room_owner = False
                            self.room_players_info.clear()
                            self.sequence_list = []
                            self.discard = ""
                        
                        elif type_msg == Message_types.ELIS.value:
                            self.rooms_list = []
                            self.game_console.log(message, True)

                        elif type_msg == Message_types.OCRT.value:
                            try:
                                self.current_room = int(message)
                                self.game_state = GameState.IN_ROOM
                                self.game_console.delete()
                            except Exception as e:
                                self.game_console.log(f"Ze serveru přišlo nevalidní číslo místnosti", True)

                        elif type_msg == Message_types.OCNT.value:
                            self.game_state = GameState.IN_ROOM
                            self.game_console.delete()
                            try:
                                for i in range(len(self.rooms_list)):
                                    if self.rooms_list[i] == message:
                                        self.current_room = message
                                        break
                            except Exception as e:
                                print("Neexistující místnost.")
                        
                        elif type_msg == Message_types.QUIT.value:
                            self.connected = False
                            self.game_state = GameState.DISCONNECTED
                    
                    elif self.game_state == GameState.IN_ROOM:
                        if type_msg == Message_types.BOSS.value:
                            self.room_owner = True

                        elif type_msg == Message_types.ODIS.value:
                            self.game_state = GameState.CONNECTED

                        elif type_msg == Message_types.PRDY.value:
                            self.room_inroom_players_ready = message

                        elif type_msg == Message_types.STRT.value:
                            try:
                                splitted = message.split("|")
                                karty = splitted[0].strip()
                                poradi = splitted[1].strip()
                                vyhozena_karta = splitted[2].strip()
                                karta_v_balicku = splitted[3].strip()
                                pocet_karet_protihrace = splitted[4].strip()
                                postupky = splitted[5].strip()
                                print(karty + "\n" + poradi + "\n" + vyhozena_karta + "\n" + karta_v_balicku + "\n" + pocet_karet_protihrace + "\n" + postupky)
                            except:
                                print(f"Špatný formát STRT {message}")
                            self.game_state = GameState.IN_GAME
                            self.game_console.delete()

                            self.room_owner = False
                            self.room_players_info.clear()
                            self.sequence_list = []
                            self.discard = ""

                        elif type_msg == Message_types.RINF.value:
                            self.room_players_info = []
                            for p in message.split(","):
                                p = p.strip()
                                if not p:
                                    continue

                                parts = p.split("|")
                                if len(parts) != 3:
                                    continue

                                nick, status, vlastnictvi = parts
                                if nick != self.login_text:
                                    self.enemy_name = nick
                                self.room_players_info.append({
                                    "nick": nick,
                                    "status": status,
                                    "vlastnictvi": vlastnictvi
                                })

                        elif type_msg == Message_types.CRDS.value:
                            splitted_cards = message.split("|")
                            self.cards_list = []
                            for i in range(len(splitted_cards)):
                                self.cards_list.append(splitted_cards[i])

                            print(self.cards_list)

                            self.new_cards = True

                        elif type_msg == Message_types.WAIT.value:
                            self.game_on_turn = False

                        elif type_msg == Message_types.TURN.value:
                            self.game_on_turn = True

                        elif type_msg == Message_types.ESTR.value:
                            self.game_console.log(message, True)

                    elif self.game_state == GameState.IN_GAME:
                        if type_msg == Message_types.WAIT.value:
                            self.game_on_turn = False
                            self.game_console.log(message, False)
                        
                        elif type_msg == Message_types.TURN.value:
                            self.game_on_turn = True
                            self.game_console.log(message, False)

                        elif type_msg == Message_types.CRDS.value:
                            splitted_cards = message.split("|")
                            self.cards_list = []
                            for i in range(len(splitted_cards)):
                                self.cards_list.append(splitted_cards[i])

                            self.new_cards = True

                        elif type_msg == Message_types.ERRR.value:
                            self.game_console.log(message, True)

                        elif type_msg == Message_types.OKAY.value:
                            self.game_console.log(message, False)

                        elif type_msg == Message_types.STAT.value:
                            zprava = message.split("|")
                            karty = zprava[0]
                            self.cards_list = []
                            start, end = 0, 2

                            for i in range(len(karty) // 2):
                                self.cards_list.append(karty[start:end])
                                start += 2
                                end += 2
                            
                            self.discard = zprava[1]

                            sekvence = zprava[2]
                            self.sequence_list = sekvence.split(",")

                            if len(sekvence) >= 1:
                                self.seq_existing = True
                            else:
                                self.seq_existing = False

                            poradi = zprava[3]

                            self.enemy_hand_count = int(zprava[4])
                            self.new_cards = True

                        elif type_msg == Message_types.GEND.value:
                            splitted = message.split("|")
                            temp = splitted[0].split(":")
                            self.results["winner"] = temp[1]

                            temp = splitted[1].split(":")
                            if temp[1] == self.results["winner"]:
                                self.results["winner_stat"] = [temp[1], temp[2], temp[3], temp[4]]
                            else:
                                self.results["loser_stat"] = [temp[1], temp[2], temp[3], temp[4]]

                            temp = splitted[2].split(":")
                            if temp[1] == self.results["winner"]:
                                self.results["winner_stat"] = [temp[1], temp[2], temp[3], temp[4]]
                            else:
                                self.results["loser_stat"] = [temp[1], temp[2], temp[3], temp[4]]

                            self.game_state = GameState.GAME_DONE

                        elif type_msg == Message_types.PAUS.value:
                            self.game_state = GameState.PAUSED
                            self.user_disconnected = message

                    elif self.game_state == GameState.GAME_DONE:
                        if type_msg == Message_types.LBBY.value:
                            self.game_state = GameState.CONNECTED

                        elif type_msg == Message_types.PAUS.value:
                            self.game_state = GameState.CONNECTED

                        elif type_msg == Message_types.ESTR.value:
                            print(message)

                        elif type_msg == Message_types.STRT.value:
                            self.sequence_list = []
                            self.discard = False
                            self.game_console.delete()
                            self.game_state = GameState.IN_GAME
                            self.clicked_plag = True

                    elif self.game_state == GameState.PAUSED:
                        if type_msg == Message_types.RESU.value:
                            self.game_state = GameState.IN_GAME
                            self.user_disconnected = ""
                            self.game_console.log(message, False)

                        elif type_msg == Message_types.LBBY.value:
                            self.game_state = GameState.CONNECTED
                            self.game_console.delete()
                            self.game_console.log(message, True)

            except queue.Empty:
                break
        
        if processed_count > 0:
            print(f"[GUI] Zpracováno {processed_count} zpráv")

    def try_connect(self):
        if not self.login_text.strip():
            self.login_error = "Nickname nesmí být prázdný"
            return
        
        self.login_error = ""

        if not self.server_text.strip():
            self.server_error = "Server nesmí zůstat prázdný"
            return
        
        splitted = self.server_text.split(".")
        if len(splitted) != 4:
            self.server_error = "Neplatná adresa serveru"
            return
        
        for part in splitted:
            if not part.isdigit():
                self.server_error = "Adresa musí obsahovat pouze číslice"
                return
            
            num = int(part)
            if num < 0 or num > 255:
                self.server_error = "Neplatná adresa serveru"
                return
        
        self.server_error = ""

        if not self.port_text.isdigit():
            self.port_error = "Port musí být číslo"
            return
        
        port = int(self.port_text)
        if port < 0 or port > 65535:
            self.port_error = "Neplatný port"
            return
        
        self.port_error = ""

        self.waiting_for_login_response = True
        self.connect_error = ""  # Vymazání staré chyby

        # SPUŠTĚNÍ VLÁKNA: Aby volání connect() nezablokovalo Pygame
        connection_thread = threading.Thread(target=self._threaded_connect_process)
        connection_thread.daemon = True
        connection_thread.start()

    def sort_unlo(self, s):
        # Definice hodnot pro porovnávání
        values = {
            "A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, 
            "8": 8, "9": 9, "X": 10, "J": 11, "Q": 12, "K": 13, "Y": 50
        }

        # 1. Rozsekání na karty
        cards = [s[i:i+2] for i in range(0, len(s), 2)]
        normal = [c for c in cards if c != "YY"]
        jokers = [c for c in cards if c == "YY"]
        
        if not normal:
            return "".join(jokers)

        # 2. Rozhodnutí o Esu (A)
        # Pokud máme Eso a zároveň máme v ruce nějakou vysokou kartu (J, Q, K) 
        # a nemáme tam zároveň nízké karty (2, 3), budeme Eso brát jako 14.
        has_ace = any(c[0] == 'A' for c in normal)
        has_high_cards = any(c[0] in "JQK" for c in normal)
        has_low_cards = any(c[0] in "2345" for c in normal)

        actual_values = values.copy()
        if has_ace and has_high_cards and not has_low_cards:
            actual_values["A"] = 14  # Přepneme Eso na vysoké
            print(f"[LOG] Detekováno vysoké Eso")

        # 3. Seřazení podle aktuálních hodnot
        normal.sort(key=lambda c: actual_values[c[0]])
        
        # 4. Skládání výsledku a vkládání žolíků do mezer
        result = [normal[0]]
        current_jokers = len(jokers)
        
        for i in range(len(normal) - 1):
            v1 = actual_values[normal[i][0]]
            v2 = actual_values[normal[i+1][0]]
            gap = v2 - v1
            
            # Vkládání žolíků tam, kde je v hodnotách mezera
            while gap > 1 and current_jokers > 0:
                result.append("YY")
                current_jokers -= 1
                gap -= 1
                
            result.append(normal[i+1])
        
        # Zbytek žolíků na konec
        result.extend(["YY"] * current_jokers)
        
        return "".join(result)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        
        if self.show_create_room_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_create_room_popup = False
                    return
                elif event.key == pygame.K_RETURN:
                    if self.create_room_text.strip():
                        self.send_message(Message_types.RCRT.value, self.create_room_text)
                    self.show_create_room_popup = False
                    return
                
                elif event.key == pygame.K_BACKSPACE:
                    self.create_room_text = self.create_room_text[:-1]
                    return
                
                else:
                    if event.unicode and event.unicode.isprintable():
                        if len(self.create_room_text) < 16:
                            self.create_room_text += event.unicode
                    return
            return
        
        if self.game_state == GameState.DISCONNECTED:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.login_name_input.collidepoint(event.pos):
                    self.active_input = "login"
                elif self.server_address_input.collidepoint(event.pos):
                    self.active_input = "server"
                elif self.port_input.collidepoint(event.pos):
                    self.active_input = "port"
                elif self.connect_button.collidepoint(event.pos):
                    self.try_connect()
                else:
                    self.active_input = None
            
            if event.type == pygame.KEYDOWN:
                if self.waiting_for_login_response:
                    return
                
                if event.key == pygame.K_BACKSPACE:
                    if self.active_input == "login":
                        self.login_text = self.login_text[:-1]
                    elif self.active_input == "server":
                        self.server_text = self.server_text[:-1]
                    elif self.active_input == "port":
                        self.port_text = self.port_text[:-1]
                
                elif event.key == pygame.K_RETURN:
                    self.try_connect()

                elif event.key == pygame.K_TAB:
                    if not self.active_input:
                        self.active_input = "login"
                    elif self.active_input == "login":
                        self.active_input = "server"
                    elif self.active_input == "server":
                        self.active_input = "port"
                    elif self.active_input == "port":
                        self.active_input = "login"
                
                else:
                    if event.unicode.isprintable():
                        if self.active_input == "login":
                            self.login_text += event.unicode
                        elif self.active_input == "server":
                            self.server_text += event.unicode
                        elif self.active_input == "port":
                            self.port_text += event.unicode

        elif self.game_state == GameState.CONNECTED:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                for button in self.room_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        print(f"RCNT|{button['room_index']}")
                        self.current_room_name = button["room_index"]
                        self.send_message(Message_types.RCNT.value, f"{button['room_index']}")
                
                if self.lobby_button_obnovit.collidepoint(mouse_pos):
                    self.send_message(Message_types.RLIS.value, "")

                if self.lobby_button_vytvorit_mistnost.collidepoint(mouse_pos):
                    self.show_create_room_popup = True
                    self.create_room_text = ""
                
                if self.lobby_disconnect.collidepoint(mouse_pos):
                    self.running = False


        elif self.game_state == GameState.IN_ROOM:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.room_exit.collidepoint(mouse_pos):
                    self.send_message("RDIS", "")

                elif self.room_ready.collidepoint(mouse_pos):
                    if self.room_status_ready:
                        self.send_message("REDY", "")
                        self.room_status_ready = not self.room_status_ready
                    else:
                        self.send_message("REDY", "1")
                        self.room_status_ready = not self.room_status_ready
                elif self.room_start.collidepoint(mouse_pos):
                    self.send_message(Message_types.STRT.value, "1")

        elif self.game_state == GameState.IN_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # JOKELOGI0005mrdkaJOKERCNT00010JOKEREDY0000
                mouse_pos = event.pos

                for card in self.card_objects:
                    card.handle_click(mouse_pos)

                if self.game_vyhodit_rect.collidepoint(mouse_pos):
                    selected = [c.name for c in self.card_objects if c.selected]
                    string = ""
                    for i in range(len(selected)):
                        string += selected[i]

                    for card in self.card_objects:
                        if card.get_state():
                            card.unselect()

                    if len(selected) > 1:
                        self.game_console.log("Tolik karet nelze vyhodit", True)
                    elif not len(selected):
                        self.game_console.log("Vyber kartu k vyhození", True)
                    else:
                        self.send_message(Message_types.THRW.value, string)

                elif self.game_liznout_rect.collidepoint(mouse_pos):
                    self.send_message(Message_types.TAKP.value, "1")

                elif self.game_liznout_vyhozenou_rect.collidepoint(mouse_pos):
                    self.send_message(Message_types.TAKT.value, "1")

                elif self.game_vylozit_rect.collidepoint(mouse_pos):
                    selected = [c.name for c in self.card_objects if c.selected]
                    string = ""
                    if len(selected) < 3:
                        self.game_console.log("Málo karet", True)
                    
                    else:
                        for i in range(len(selected)):
                            string += selected[i]
                        string = self.sort_unlo(string)
                        
                        self.send_message(Message_types.UNLO.value, string)

                elif self.game_zavrit_rect.collidepoint(mouse_pos):
                    selected = [c.name for c in self.card_objects if c.selected]

                    if len(selected) == 0:
                        self.game_console.log("Vyber alespoň jednu kartu k zavření.", True)
                    
                    elif len(selected) > 1:
                        self.game_console.log("Vybráno moc karet k zavření.", True)
                    
                    else:
                        string = ""
                        for i in range(len(selected)):
                            string += selected[i]
                        self.send_message(Message_types.CLOS.value, string)

                if self.game_seradit_rect.collidepoint(mouse_pos):
                    self.user_seradit = not self.user_seradit
                    self.game_console.log("Karty seřazeny", False)
                
                if hasattr(self, 'game_prilozit_rect') and self.game_prilozit_rect.collidepoint(mouse_pos):
                    self.prilozit_active = not self.prilozit_active
                    selected = [c.name for c in self.card_objects if c.selected]
                    if not selected:
                        self.game_console.log("Nejdříve vyber kartu!", True)
                        self.prilozit_active = False
                    else:
                        self.prilozit_active = True
                    return
                if self.prilozit_active:
                    if(getattr(self, 'sequences_area_rect', None) and self.sequences_area_rect.collidepoint(mouse_pos)):
                        found_match = False
                        for item in self.sequence_rects:
                            if item["rect"].collidepoint(mouse_pos):
                                selected = [c.name for c in self.card_objects if c.selected]

                                if len(selected) > 1:
                                    self.game_console.log("Vybráno moc karet k přiložení", True)

                                if selected:
                                    prev_seq = item["seq_str"]
                                    new_card = selected[0]

                                    self.send_message(Message_types.ADDC.value, f"{prev_seq}|{new_card}")
                                    self.prilozit_active = False
                                    for c in self.card_objects: c.selected = False

                                    found_match = True
                                    break
                        if found_match:
                            self.game_console.log("Režim přikládání ukončen", True)
                        else:
                            self.game_console.log("Klikl jsi vedle.", True)

        elif self.game_state == GameState.GAME_DONE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.playagain_button.collidepoint(mouse_pos):
                    if self.clicked_plag:
                        self.send_message(Message_types.PLAG.value, "")
                    
                    else:
                        self.send_message(Message_types.PLAG.value, "1")
                    

                    self.clicked_plag = not self.clicked_plag
                if self.back_to_lobby.collidepoint(mouse_pos):
                    self.send_message(Message_types.LBBY.value, "")
    
    def run(self):
        while self.running:
            self.process_queue()

            for event in pygame.event.get():
                self.handle_event(event)

            

            if self.game_state == GameState.DISCONNECTED:
                self.page_drawer.draw_connect_screen(self)

            elif self.game_state == GameState.CONNECTED:
                self.page_drawer.draw_lobby_screen(self)

            elif self.game_state == GameState.IN_ROOM:
                self.page_drawer.draw_room_screen(self)

            elif self.game_state == GameState.IN_GAME:
                self.page_drawer.draw_game_screen(self)
            
            elif self.game_state == GameState.GAME_DONE:
                self.page_drawer.draw_game_done_screen(self)

            elif self.game_state == GameState.PAUSED:
                self.page_drawer.draw_player_disconnected(self)

            self.clock.tick(60)
            pygame.display.flip()
        
        if self.network_thread:
            self.network_thread.stop()

        if self.sock:
            self.sock.close()

        pygame.quit()
        sys.exit()

