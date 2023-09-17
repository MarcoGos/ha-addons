import colorlog
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    fmt='[%(asctime)s] %(levelname)s: %(log_color)s%(message)s%(reset)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
		'DEBUG':    'black',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
        'FATAL':    'red,bg_white',
		'CRITICAL': 'red,bg_white',
	}))
logger = colorlog.getLogger()
logger.addHandler(handler)

log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'fatal': logging.FATAL,
    'critical': logging.CRITICAL
}