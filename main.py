from clientgui import *
from logger import *

def main():
    log_init("klient.log", DEBUG)
    log_delete()

    log_msg(INFO, "Klient startuje...")
    gui = ClientGUI()
    gui.run()
    log_close()

if __name__ == "__main__":
    main()