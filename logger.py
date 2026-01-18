import logging
import sys
import threading
from datetime import datetime
from enum import IntEnum

class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    FATAL = 4

class Logger:
    _level_str = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
    
    def __init__(self):
        self.min_level = LogLevel.INFO
        self.log_file = sys.stdout
        self.lock = threading.Lock()

    def log_init(self, filename: str = None, min_level: LogLevel = LogLevel.INFO):
        """Inicializace loggeru (ekvivalent log_init v C)"""
        self.min_level = min_level
        if filename:
            try:
                self.log_file = open(filename, "a", encoding="utf-8")
            except Exception as e:
                print(f"Nepodařilo se otevřít log soubor: {e}")
                return -1
        else:
            self.log_file = sys.stdout
        return 0

    def log_close(self):
        """Zavření souboru (ekvivalent log_close v C)"""
        if self.log_file and self.log_file != sys.stdout:
            self.log_file.close()

    def log_msg(self, level: LogLevel, file: str, line: int, message: str):
        """Hlavní logovací metoda (ekvivalent log_msg v C)"""
        if level < self.min_level:
            return

        with self.lock:
            now = datetime.now()
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            tid = threading.get_ident()

            log_line = (
                f"[{time_str}] [{self._level_str[level]}] [TID:{tid}] "
                f"{file}:{line}: {message}"
            )

            print(log_line, file=self.log_file)
            self.log_file.flush()

logger = Logger()

def LOG_INFO(msg):
    import inspect
    frame = inspect.currentframe().f_back
    logger.log_msg(LogLevel.INFO, frame.f_code.co_filename, frame.f_lineno, msg)

def LOG_ERROR(msg):
    import inspect
    frame = inspect.currentframe().f_back
    logger.log_msg(LogLevel.ERROR, frame.f_code.co_filename, frame.f_lineno, msg)