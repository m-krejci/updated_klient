import logging
import sys
import os
from threading import Lock

# Definice úrovní (odpovídá vašemu log_level_t)
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
FATAL = logging.CRITICAL

class Logger:
    def __init__(self):
        self._logger = logging.getLogger("AppLogger")
        self._logger.propagate = False
        self._handler = None
        self._lock = Lock()

    def log_init(self, filename=None, min_level=INFO):
        """Inicializace loggeru (ekvivalent log_init v C)"""
        # Odstraníme staré handlery, pokud existují
        if self._logger.handlers:
            for h in self._logger.handlers[:]:
                self._logger.removeHandler(h)

        if filename:
            self._handler = logging.FileHandler(filename, mode='a', encoding="utf-8")
        else:
            self._handler = logging.StreamHandler(sys.stdout)

        # Formát odpovídající vašemu fprintf: 
        # [Čas] [Level] [TID] Soubor:Linka: Zpráva
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [TID:%(thread)d] %(filename)s:%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self._handler.setFormatter(formatter)
        self._logger.addHandler(self._handler)
        self._logger.setLevel(min_level)

    def log_msg(self, level, message, *args):
        """Zápis zprávy (v Pythonu se file a line doplňují automaticky)"""
        # Python logging je thread-safe, ale pro 100% shodu s C verzí můžeme použít zámek
        with self._lock:
            if args:
                self._logger.log(level, message % args)
            else:
                self._logger.log(level, message)

    def log_delete(self):
        """Promazání logovacího souboru (ekvivalent ftruncate)"""
        if isinstance(self._handler, logging.FileHandler):
            with self._lock:
                filepath = self._handler.baseFilename
                # Otevření v režimu 'w' soubor vymaže
                with open(filepath, 'w'):
                    pass

    def log_close(self):
        """Zavření loggeru"""
        if self._handler:
            self._handler.close()
            self._logger.removeHandler(self._handler)

# --- Globální instance pro snadné použití ---
_instance = Logger()
log_init = _instance.log_init
log_msg = _instance.log_msg
log_delete = _instance.log_delete
log_close = _instance.log_close