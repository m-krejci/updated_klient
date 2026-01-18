from constants import *
import socket


def build_message(type_msg: str, message: str):
    """ Korektní nabuildění zprávy pro server.

    Args:
        type_msg (str): Typ zprávy
        message (str): Zpráva k odeslání

    Returns:
        _type_: Vrací -1 při chybě a celou zprávu při úspěchu
    """
    msg_len = len(message)
    if msg_len > MAX_MESSAGE_LEN:
        print("Moc dlouhá zpráva")
        return -1
    
    header = f"{MAGIC}{type_msg:<{TYPE_LEN}}{msg_len:04d}"
    return header.encode("utf-8") + message.encode("utf-8")


def receive_full_message(sock: socket.socket) -> tuple[str, str]:
    """ Přijímá celou zprávu po částech, aby byla zajištěna celistvost zprávy

    Args:
        sock (socket.socket): Socket k serveru

    Raises:
        ConnectionError: Při nenalezení žádné zprávy
        ConnectionError: Pokud se nepodařilo přečíst celou zprávu

    Returns:
        tuple[str, str]: Vrací typ a konkrétní zprávu pro manipulaci
    """
    # Čtení headeru po částech, dokud se nepřečte celý nebo nenastane chyba
    header_bytes = b""
    while(len(header_bytes) < HEADER_LEN):
        chunk = sock.recv(HEADER_LEN - len(header_bytes))
        if not chunk:
            raise ConnectionError("Spojení se serverem uzavřeno.")
        header_bytes += chunk
    
    # Naparsování zprávy
    header_str = header_bytes.decode("utf-8")
    magic = header_str[:MAGIC_LEN]
    type_msg = header_str[MAGIC_LEN:MAGIC_LEN+TYPE_LEN].strip()
    length = header_str[MAGIC_LEN+TYPE_LEN:LENGTH_LEN + MAGIC_LEN + TYPE_LEN]
    msg_len = int(length)

    # Čtení zprávy po částech, dokud se nepřečte celá nebo nenastane chyba
    message = b""
    while len(message) < msg_len:
        chunk = sock.recv(msg_len - len(message))
        if not chunk:
            raise ConnectionError("Nepodařilo se přečíst tělo zprávy")
        message += chunk
    
    message_final = message.decode("utf-8")
    print(f"Přijímám: {magic}{type_msg}{length}{message_final}")
    return type_msg, message_final