"""
Základní definované konstanty pro fungování klienta.
Obsahuje i barvy pro aplikaci.
"""

# Magic pro zprávy
MAGIC = "JOKE"

# Délka MAGIC slova
MAGIC_LEN = len(MAGIC)

# Délka typu zprávy (STRT)
TYPE_LEN = 4

# Délka délky zprávy (0001)
LENGTH_LEN = 4

# Délka headeru (bez zprávy)
HEADER_LEN = MAGIC_LEN + TYPE_LEN + LENGTH_LEN  # 12

# Maximimální délka zprávy (maximální rozsah podle LENGTH_LEN)
MAX_MESSAGE_LEN = 9999 

# Maximální délka zpráv pro konzoli (herní)
MAX_LINES = 3

# Omezení herního okna
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 720

# Omezení herní místnosti
MAX_ROOM_PLAYERS = 2

# Cesta + velikost karty
CARDS_PATH = "cards"
CARD_SIZE = (80, 120)

# Maximální délka nicku
MAX_NICK_LEN = 10

# Základní použité barvy
DARK_GRAY = (100, 100, 100)
MILKY = (247, 244, 239)
LIGHT_BROWN = (216, 199, 179)
BROWN = (92, 74, 56)
BLACK = (42, 42, 42)
BROOM = (184, 168, 158)
RED = (255, 0, 0)
BRIGHT_RED = (222, 33, 36)
BRIGHT_GREEN = (102, 255, 102)
GREEN = (0, 153, 0)

# Barva tlačítka
BUTTON_COLOR = (70, 130, 180)   # Modrá sytá
BUTTON_HOVER = (100, 150, 240)  # Modrá světlá

# PONG
PONG_INTERVAL = 10

