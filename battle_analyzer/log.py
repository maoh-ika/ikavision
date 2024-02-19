from logging import getLogger, INFO, ERROR, DEBUG, WARNING, StreamHandler
from logging.handlers import RotatingFileHandler
import sys
import os
from timestamp import timestamp, to_string

def create_file_logger(file_name, root_name='ikavision', level=DEBUG):
    logger = getLogger(root_name)
    logger.setLevel(level)
    error_file_handler = RotatingFileHandler(f'{file_name}.error', maxBytes=(1024)*(1024), backupCount=10)
    error_file_handler.setLevel(ERROR)
    error_file_handler.addFilter(lambda r: r.levelno == ERROR)
    logger.addHandler(error_file_handler)
    debug_file_handler = RotatingFileHandler(f'{file_name}.debug', maxBytes=(1024)*(1024), backupCount=10)
    debug_file_handler.setLevel(DEBUG)
    debug_file_handler.addFilter(lambda r: r.levelno == DEBUG)
    logger.addHandler(debug_file_handler)
    stream_hamdler = StreamHandler(sys.stdout)
    stream_hamdler.setLevel(INFO)
    logger.addHandler(stream_hamdler)
    logger.propagate = False
    return Logger(root_name)

def create_prod_logger(root_name='ikavision'):
    logger = getLogger(root_name)
    logger.setLevel(DEBUG)
    stream_hamdler = StreamHandler(sys.stdout)
    stream_hamdler.setLevel(INFO)
    logger.addHandler(stream_hamdler)
    logger.propagate = False
    return Logger(root_name)

class Logger:
    def __init__(self, name):
        self.name = name
        self.logger = getLogger(name)

    def info(self, msg):
        msg = self._make_log_str(msg, 'INFO', self.name)
        self.logger.info(msg)

    def error(self, msg):
        msg = self._make_log_str(msg, 'ERROR', self.name)
        self.logger.error(msg)

    def debug(self, msg):
        msg = self._make_log_str(msg, 'DEBUG', self.name)
        self.logger.debug(msg)
    
    def warning(self, msg):
        msg = self._make_log_str(msg, 'WARNING', self.name)
        self.logger.warning(msg)

    def _make_log_str(self, msg, severity, sender):
        res = '[' + to_string(timestamp()) + ']'
        res += '[' + str(os.getpid()) + ']'
        res += '[' + str(severity) + ']'
        res += '[' + str(sender) + ']'
        res += ' ' + str(msg)
        return res
