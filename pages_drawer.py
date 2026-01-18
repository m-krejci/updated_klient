import pygame
from constants import *
from ui_elements import *
# from clientgui import ClientGUI
from card import Card
from logger import *

class PageDrawer:
    def __init__(self, screen, font, ui: UI):
        self.screen = screen
        self.font = font
        self.ui: UI = ui

    def draw_input_block(self, label, rect, text, active, error):
        label_surface = self.font.render(label, True, (0, 0, 0))
        self.screen.blit(label_surface, (rect.x, rect.y - 30))

        self.ui.draw_input(rect, text, active)

        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (rect.x + 10, rect.y + 8))

        self.ui.draw_error(rect, error)

    def draw_connect_screen(self, state):
        self.screen.fill((168, 255, 255))
        mouse_pos = pygame.mouse.get_pos()

        # Nadpis
        title = self.font.render("PŘÍHLÁŠENÍ DO HRY", True, (0, 0, 0))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))
        
        # Nickname
        self.draw_input_block("NICKNAME", state.login_name_input, state.login_text, state.active_input == "login", state.login_error)
        # nick_label = self.font.render("NICKNAME", True, (0, 0, 0))
        # self.screen.blit(nick_label, (self.login_name_input.x, self.login_name_input.y - 30))
        # self.draw_input(self.login_name_input, self.login_text, self.active_input == "login")
        # nick_text = self.font.render(self.login_text, True, (0, 0, 0))
        # self.screen.blit(nick_text, (self.login_name_input.x + 10, self.login_name_input.y + 8))

        

        # Server
        self.draw_input_block("SERVER", state.server_address_input, state.server_text, state.active_input == "server", state.server_error)
        # server_label = self.font.render("SERVER", True, (0, 0, 0))
        # self.screen.blit(server_label, (self.server_address_input.x, self.server_address_input.y - 30))
        # self.draw_input(self.server_address_input, self.server_text, self.active_input == "server")
        # server_text = self.font.render(self.server_text, True, (0, 0, 0))
        # self.screen.blit(server_text, (self.server_address_input.x + 10, self.server_address_input.y + 8))

        # Port
        self.draw_input_block("PORT", state.port_input, state.port_text, state.active_input == "port", state.port_error)
        # port_label = self.font.render("PORT", True, (0, 0, 0))
        # self.screen.blit(port_label, (self.port_input.x, self.port_input.y - 30))
        # self.draw_input(self.port_input, self.port_text, self.active_input == "port")
        # port_text = self.font.render(self.port_text, True, (0, 0, 0))
        # self.screen.blit(port_text, (self.port_input.x + 10, self.port_input.y + 8))

        # Button přihlásit
        if not state._reconnecting:
            self.ui.draw_button(state.connect_button, "Přihlásit se do hry", mouse_pos)

        # Chyby pod inputy
        self.ui.draw_error(state.login_name_input, state.login_error)
        self.ui.draw_error(state.server_address_input, state.server_error)
        self.ui.draw_error(state.port_input, state.port_error)

        # Čekání na server
        if state.waiting_for_login_response:
            wait_text = self.font.render("Čekám na server...", True, (120, 120, 120))
            self.screen.blit(wait_text, (WINDOW_WIDTH // 2 - wait_text.get_width() // 2, state.login_name_input.bottom + 200))

        if state._reconnecting:
            wait_text = self.font.render("Ztraceno spojení, pokouším se o reconnect...", True, (255, 165, 0))
            self.screen.blit(wait_text, (WINDOW_WIDTH // 2 - wait_text.get_width() // 2, state.login_name_input.bottom + 200))

        if state.connect_error:
            text = state.font_small.render(state.connect_error, True, (255, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (WINDOW_WIDTH // 2, state.login_name_input.bottom + 240)
            self.screen.blit(text, text_rect)

    def draw_create_room_popup(self, state):
        # Ztmavení pozadí
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_WIDTH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Okno popupu
        pygame.draw.rect(self.screen, (255, 255, 255), state.popup_rect, border_radius=20)
        pygame.draw.rect(self.screen, (150, 150, 150), state.popup_rect, 2, border_radius=20)

        # Nadpis
        title = self.font.render("Vytvořit místnost", True, (0, 0, 0))
        self.screen.blit(title, (state.popup_rect.x + 110, state.popup_rect.y + 20))

        # Input
        pygame.draw.rect(self.screen, (230, 230, 230), state.popup_input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 100), state.popup_input_rect, 2, border_radius=8)

        text = self.font.render(state.create_room_text, True, (0, 0, 0))
        self.screen.blit(text, (state.popup_input_rect.x + 8, state.popup_input_rect.y + 8))

        hint = self.font.render("ENTER = potvrdit | ESC = zrušit", True, (120, 120, 120))
        self.screen.blit(hint, (state.popup_rect.x + 60, state.popup_rect.y + 160))

    def draw_lobby_screen(self, state):
        # Vykreslení trojuhleniku
        pygame.draw.polygon(self.screen, MILKY, [(0, 0), (WINDOW_WIDTH //2, WINDOW_HEIGHT//2), (WINDOW_WIDTH, 0)])
        pygame.draw.polygon(self.screen, BROWN, [(0, 0), (WINDOW_WIDTH //2, WINDOW_HEIGHT//2), (0, WINDOW_HEIGHT)])
        pygame.draw.polygon(self.screen, LIGHT_BROWN, [(WINDOW_WIDTH, 0), (WINDOW_WIDTH //2, WINDOW_HEIGHT//2), (WINDOW_WIDTH, WINDOW_HEIGHT)])
        pygame.draw.polygon(self.screen, BROOM, [(0, WINDOW_HEIGHT), (WINDOW_WIDTH //2, WINDOW_HEIGHT//2), (WINDOW_WIDTH, WINDOW_HEIGHT)])

        # Vykresleni pole pro roomky
        mistnosti_rect = pygame.Rect(80, 100, 500, 400)
        sedy_preliv = pygame.Rect(80, 100, 500, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), mistnosti_rect, border_radius=35)
        pygame.draw.rect(self.screen, (192, 192, 192), sedy_preliv, border_top_left_radius=35, border_top_right_radius=35)
        napis_mistnosti = self.font.render("Místnosti", True, (0, 0, 0))
        self.screen.blit(napis_mistnosti, (290, 115))

        #vykresleni pole pro stav pripojeni
        if state.connected:
            stav_pripojeni = pygame.Rect(80, 10, 120, 40)
            pygame.draw.rect(self.screen, (255, 255, 255), stav_pripojeni, border_radius=35)

            # vypsani stavu
            stav_text = self.font.render("Připojeno", True, (34, 177, 76))
            self.screen.blit(stav_text, (90, 20))

        #vykresleni pro uzivatele
        uzivatel = self.font.render(f"Vítej, uživateli {state.login_text}", True, (255,255,255))
        self.screen.blit(uzivatel, (WINDOW_WIDTH // 2 + 250, WINDOW_HEIGHT//2))
        
        state.room_buttons = []
        mouse_pos = pygame.mouse.get_pos()
        # vykresleni roomek
        if state.rooms_list:
            offset_y = 50
            BUTTON_WIDTH = 120
            BUTTON_HEIGHT = 30
            
            for i, room in enumerate(state.rooms_list):
                room_text = f"{room['name']} {room['capacity']}"
                room_surface = self.font.render(room_text, True, (0, 0, 0))
                room_x = 100
                room_y = 160 + i * offset_y
                self.screen.blit(room_surface, (room_x, room_y))

                button_x = room_x + 300 
                button_y = room_y + (room_surface.get_height() // 2) - (BUTTON_HEIGHT // 2)
                
                button_rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)

                self.ui.draw_button(button_rect, "Vstoupit", mouse_pos)
                
                state.room_buttons.append({
                    "rect": button_rect,
                    "room_index": room["index"]
                })

        if state.show_create_room_popup:
            self.draw_create_room_popup(state)


        # 550
        # pygame.draw.rect(self.screen, (self.BROWN), self.lobby_button_obnovit)
        self.ui.draw_button(state.lobby_button_obnovit, "Obnovit", mouse_pos)
        self.ui.draw_button(state.lobby_button_vytvorit_mistnost, "Vytvořit", mouse_pos)
        self.ui.draw_button(state.lobby_disconnect, "Odpojit", mouse_pos, button_color=RED, hover_color=BRIGHT_RED)

        state.game_console.draw(self.screen)

    def draw_room_screen(self, state):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.fill(BROOM)

        mistnosti_rect = pygame.Rect(80, 100, 500, 400)
        sedy_preliv = pygame.Rect(80, 100, 500, 50)

        pygame.draw.rect(self.screen, (255, 255, 255), mistnosti_rect, border_radius=35)
        pygame.draw.rect(self.screen, (192, 192, 192), sedy_preliv, border_top_left_radius=35, border_top_right_radius=35)

        napis_mistnosti = self.font.render(f"Místnost {state.current_room_name}", True, (0, 0, 0))
        self.screen.blit(napis_mistnosti, (290, 115))

        svetle_sedy_preliv = pygame.Rect(80, 150, 500, 50)
        pygame.draw.rect(self.screen, (224, 224, 224), svetle_sedy_preliv)

        napis_uzivatele = self.font.render("Uživatelé", True, (0, 0, 0))
        self.screen.blit(napis_uzivatele, (110, 165))

        napis_ready = self.font.render("Status", True, (0, 0, 0))
        self.screen.blit(napis_ready, (450, 165))

        pripraveni_uzivatele = self.font.render(f"{state.room_inroom_players_ready}", True, (0, 0, 0))
        self.screen.blit(pripraveni_uzivatele, (310, 165))

        start_y = 170
        step_y = 30
        if state.room_inroom_players_ready:
            for i in range(len(state.room_players_info)):
                player = state.room_players_info[i]

                nick = player["nick"]
                status = player["status"]
                vlastnictvi = player["vlastnictvi"]

                nick_text = self.font.render(f"{nick}", True, (0, 0, 0))
                status_text = self.font.render(f"{status}", True, (0, 0, 0))
                vlastnictvi_text = self.font.render(f"{vlastnictvi}", True, (0, 0, 0))

                self.screen.blit(nick_text, (100, (i+1) * step_y + start_y))
                self.screen.blit(status_text, (450, (i+1) * step_y + start_y))
                self.screen.blit(vlastnictvi_text, (230, (i+1) * step_y + start_y))

        if state.room_owner:
            self.ui.draw_button(state.room_start, "Start", mouse_pos, BRIGHT_GREEN, GREEN)
        self.ui.draw_button(state.room_exit, "Odpojit", mouse_pos, BRIGHT_RED, RED)
        self.ui.draw_button(state.room_ready, "Ready", mouse_pos)

        state.game_console.draw(self.screen)

    def layout_cards(self, state):
        num_cards = len(state.card_objects)
        try:
            max_width = WINDOW_WIDTH
            card_width = state.card_objects[0].rect.width
            spacing = min((max_width // num_cards), card_width + 20)

            y = WINDOW_HEIGHT - state.card_objects[0].rect.height - WINDOW_HEIGHT // 6
            
            start_x = 3
            for i, card in enumerate(state.card_objects):
                x = start_x + spacing * i
                card.rect.topleft = (x, y)
        except Exception as e:
            log_msg(INFO, e)

    def draw_sequence(self, state):
        state.sequence_rects = []

        if not state.sequence_list:
            state.sequences_area_rect = None
            return
        
        width, height = self.screen.get_size()

        cols = 2
        col_width = 280
        row_height = 110

        area_width = (cols * col_width) + 20
        area_x = width - area_width - 10
        area_y = 10

        num_rows = (len(state.sequence_list) + cols - 1) // cols
        area_height = num_rows * row_height + 50

        state.sequences_area_rect = pygame.Rect(area_x, area_y, area_width, area_height)
        bg_color = (30, 30, 50)

        if getattr(state, 'prilozit_active', False):
            border_color = (0, 255, 0)
            border_width = 3
            title_color = (0, 255, 0)
        else:
            border_color = (100, 100, 150)
            border_width = 2
            title_color = (255, 255, 255)

        pygame.draw.rect(self.screen, bg_color, state.sequences_area_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, state.sequences_area_rect, border_width, border_radius=10)

        title = state.font_small.render("Vyložené postupky", True, title_color)
        self.screen.blit(title, (area_x + 10, area_y + 10))
        x_offset_cards = 18

        for seq_index, seq_text in enumerate(state.sequence_list):
            col = seq_index % cols
            row = seq_index // cols

            current_x = area_x + 40 + (col * col_width)
            current_y = area_y + 45 + (row * row_height)

            cards_in_seq = [seq_text[i:i+2] for i in range(0, len(seq_text), 2)]

            total_width = 60 + (len(cards_in_seq) - 1) * x_offset_cards
            click_rect = pygame.Rect(current_x, current_y, total_width, 87)

            state.sequence_rects.append({
                "rect": click_rect,
                "seq_str": seq_text
            })

            for i, card_code in enumerate(cards_in_seq):
                card_img = state.cards.get(card_code)

                if card_img:
                    small_card = pygame.transform.smoothscale(card_img, (60, 87))
                    self.screen.blit(small_card, (current_x + i * x_offset_cards, current_y))
            
            num_text = state.font_small.render(f"{seq_index + 1}.", True, (0, 255, 255))
            self.screen.blit(num_text, (current_x - 30, current_y + 35))

    def sort_cards(self, state):
        values={ 
            "S": 10, "C": 1011, "H": 101, "D": 10111, "X": 10, "Q": 12, "J": 11, "K": 13, "A": 1, "Y": 100000 
        }

        for i in range(len(state.cards_list)):
            for j in range(i, len(state.cards_list)):
                if i != j:
                    rank_first = state.cards_list[i][0]
                    if rank_first in values.keys():
                        rank_value = values[rank_first]
                    else:
                        try:
                            rank_value = int(rank_first)
                        except Exception as e:
                            log_msg(ERROR, e)

                    suit_first = values[state.cards_list[i][1]]
                    rank_second = state.cards_list[j][0]
                    if rank_second in values.keys():
                        rank_value_2 = values[rank_second]
                    else:
                        try:
                            rank_value_2 = int(rank_second)
                        except Exception as e:
                            log_msg(ERROR, e)
                    suit_second = values[state.cards_list[j][1]]
                    first = rank_value + suit_first
                    second = rank_value_2 + suit_second

                    if first > second:
                        temp = state.cards_list[i]
                        state.cards_list[i] = state.cards_list[j]
                        state.cards_list[j] = temp
        state.new_cards = True 

    def draw_game_screen(self, state):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.fill(BROWN)

        if state.user_seradit:
            self.sort_cards(state)

        if state.seq_existing:
            self.draw_sequence(state)

        state.user_seradit = False
        if state.new_cards:
            state.card_objects = [
                Card(name, state.cards[name], 0, 0) for name in state.cards_list
            ]

            self.layout_cards(state)
        state.new_cards = False

        text = f"Protiháč: {state.enemy_name if state.enemy_name else 'Unknown'}, počet karet: {state.enemy_hand_count}"
        text = state.font_small.render(text, True, (255, 255, 255))
        self.screen.blit(text, (5, 5))
        if not state.enemy_hand_count:
            state.enemy_hand_count = 14

        start_x, start_y = 20, 40
        x_offset, y_offset = 25, 0
        card_back = state.cards.get("BS", None)

        for i in range(state.enemy_hand_count):
            x, y = start_x + i * x_offset, start_y + i * y_offset
            self.screen.blit(card_back, (x, y))

        deck_x, deck_y = 20, 260
        card_back = state.cards.get("BS", None)
        self.screen.blit(card_back, (deck_x, deck_y))

        if state.discard:
            discard_x, discard_y = 110, 260
            card = state.cards.get(state.discard, None)
            self.screen.blit(card, (discard_x, discard_y))

        state.game_console.draw(self.screen)
        if state.game_on_turn:
            # aktivuj tlacitka
            self.ui.draw_button(state.game_vyhodit_rect, "Vyhodit", mouse_pos)
            self.ui.draw_button(state.game_liznout_rect, "Líznout", mouse_pos)
            self.ui.draw_button(state.game_zavrit_rect, "Zavřít", mouse_pos)
            self.ui.draw_button(state.game_vylozit_rect, "Vyložit", mouse_pos)
            self.ui.draw_button(state.game_liznout_vyhozenou_rect, "Líznout vyhozenou", mouse_pos)
            self.ui.draw_button(state.game_prilozit_rect, "Přiložit", mouse_pos)
            self.ui.draw_button(state.game_seradit_rect, "Seřadit", mouse_pos)
        
        elif not state.game_on_turn:
            # deaktivuj tlacitka
            pass

        for card in state.card_objects:
            card.draw(self.screen)

    def prepare_rows(self, data):
        rows = []

        rows.append(data["winner_stat"])
        rows.append(data["loser_stat"])

        return rows
    
    def draw_game_done_screen(self, state):
        self.screen.fill(LIGHT_BROWN)
        mouse_pos = pygame.mouse.get_pos()

        if state.clicked_plag == True:
            self.ui.draw_button(state.playagain_button, "Hrát znovu", mouse_pos)
        
        else:
            self.ui.draw_button(state.playagain_button, "Zrušit", mouse_pos, RED, BRIGHT_RED)

        self.ui.draw_button(state.back_to_lobby, "Zpátky do lobby", mouse_pos)

        if state.results:
            headers = ["Player", "Score", "Played Cards", "Rounds"]
            rows = self.prepare_rows(state.results)

            col_widths = [160, 100, 160, 100]
            row_height = 36
            table_width = sum(col_widths)
            table_height = row_height * (len(rows) + 1)

            start_x = (self.screen.get_width() - table_width) // 2
            start_y = (self.screen.get_height() - table_height) // 2

            x = start_x
            for i, header in enumerate(headers):
                text = state.bold_font.render(header, True, (220, 220, 220))
                self.screen.blit(text, (x + 10, start_y))
                x += col_widths[i] 

            pygame.draw.line(self.screen, (180, 180, 180), 
                             (start_x, start_y + row_height - 6), (start_x + table_width, start_y + row_height - 6), 2)
            
            y = start_y + row_height
            for row in rows:
                name = row[0]
                is_winner = (name == state.results["winner"])
                color = (180, 255, 180) if is_winner else (220, 220, 220)

                x=start_x
                for i, cell in enumerate(row):
                    txt = state.table_font.render(cell, True, color)
                    self.screen.blit(txt, (x+10, y))
                    x += col_widths[i]
                y += row_height

            title = state.bold_font.render("GAME RESULTS", True, (255, 215, 0))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, start_y - 40))
            self.screen.blit(title, title_rect)

    def draw_player_disconnected(self, state):
        self.screen.fill((255, 255, 255))

        
        text = state.bold_font.render(state.user_disconnected, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.screen.blit(text, text_rect)

        text = state.font_small.render("Má dvě minuty na připojení", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        self.screen.blit(text, text_rect)