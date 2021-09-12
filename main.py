import logging
from services.service import BluebirdService
import schedule
import traceback
import time
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, f"logs/migrator_bluebird.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)


def handler_service():
    try:
        handler_migration = BluebirdService(logger)
        handler_migration.handler_bluebird_migration()
    except Exception:
        logger.error(msg=f'An Error occurred while handling bluebird migration: {traceback.format_exc()}')


if __name__ == '__main__':
    #minutes = int(CONTAINER_NUMBER)
    schedule.every(1).minutes.do(handler_service)
    while True:
        schedule.run_pending()
        time.sleep(1)

