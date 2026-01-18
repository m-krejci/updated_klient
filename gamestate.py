from enum import Enum

class GameState(Enum):
    """ Enum třída, která definuje stavy hry

    Args:
        Enum (_type_): _description_
    """
    DISCONNECTED = 1
    CONNECTED = 2
    IN_ROOM = 3
    WAIT = 4
    TURN = 5
    PAUSEDd = 6
    GAME_DONE = 7
    IN_GAME = 8
    PAUSED = 9