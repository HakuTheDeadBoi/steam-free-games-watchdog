from datetime import datetime
import logging

from src.main import main

if __name__ == '__main__':
    logging.info(f"Script started at {datetime.now()}.")
    try:
        result = main()
        if not result:
            logging.info(f"Script successfully ended at {datetime.now()}.")
        else:
            for recipient in result:
                logging.error(f"Failed to send a report to the recipient: {recipient}")
    except Exception as e:
        logging.error(f"An error occured while performing the script: {e}")
