settings = """
TEMPLATES[0]['DIRS'] += [os.path.join(BASE_DIR, 'templates')]
import logging
logger = logging.getLogger('root')
logging.basicConfig(format="[%(levelname)s][%(name)s:%(lineno)s] %(message)s")
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
# In each py file, include "logger = logging.getLogger(__name__)"
"""
