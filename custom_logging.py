import logging
import os



# define logging:
class CustomFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.INFO: "\033[97m",  # White
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.DEBUG: "\033[96m",  # Cyan (if you want to use it)
        logging.CRITICAL: "\033[91m",  # Red
        "RESET": "\033[0m",  # Reset color
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno, self.LOG_COLORS["RESET"])
        formatter = logging.Formatter(
            f"{log_color}%(asctime)s - %(name)s - %(levelname)s - %(message)s{self.LOG_COLORS['RESET']}")
        return formatter.format(record)


# Pfad für die Log-Datei setzen
log_file_path = os.path.join(os.path.dirname(__file__), './output_logs/notify_bot_python_internal_logging.log')

# Set up logging configuration with the custom formatter
logger = logging.getLogger(__name__)

# StreamHandler für die Konsole
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())
logger.addHandler(stream_handler)

# FileHandler für die Log-Datei
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Log-Level setzen
logger.setLevel(logging.INFO)