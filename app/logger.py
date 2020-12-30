import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

FORMAT = ('%(asctime)-15s %(threadName)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')

path = 'logs'
logname = 'app.log'
error_logname = 'error.log'

results_logger = logging.getLogger('results_logger')
results_logger.setLevel(logging.INFO)


logger = logging.getLogger('tank_sticker_app')
logger.setLevel(logging.INFO)

formatter = logging.Formatter(FORMAT)
logHandler = TimedRotatingFileHandler(f'{path}/{logname}', when='midnight', interval=1)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logHandler.suffix = "%Y%m%d"

errorLogHandler = TimedRotatingFileHandler(f'{path}/error/{error_logname}', when='midnight', interval=1)
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(formatter)
errorLogHandler.suffix = "%Y%m%d"

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)

logger.addHandler(logHandler)
logger.addHandler(errorLogHandler)
logger.addHandler(streamHandler)

logHandler = TimedRotatingFileHandler(f'{path}/results/results.log', when='midnight', interval=1)
results_logger.addHandler(logHandler)