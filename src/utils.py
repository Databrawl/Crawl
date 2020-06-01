import logging
import time

CONFIG = 'dev'


def init_logging():
    log_level = logging.DEBUG if CONFIG == 'dev' else logging.INFO
    logging.basicConfig(
        format='%(name)s [%(threadName)s]: %(asctime)s %(levelname)-8s '
               '%(message)s',
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('prawcore').setLevel(logging.CRITICAL)


def timeit(func):
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()

        logging.info('%r took %2.2f sec\n' % (func.__name__, te - ts))
        return result

    return timed
