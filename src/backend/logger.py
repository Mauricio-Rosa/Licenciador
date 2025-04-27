import logging
from logging.handlers import RotatingFileHandler
import os

def configurar_logger():
    """
    Configura e retorna um logger para registro de eventos.
    
    Returns:
        logging.Logger: Logger configurado para registro de eventos.
    """
    # Definir o caminho para o arquivo de log
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'event_log.log')

    # Configurar o logger
    logger = logging.getLogger('licence_generator')
    logger.setLevel(logging.INFO)

    # Criar um manipulador de arquivo rotativo
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    # Criar um formatador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Adicionar o manipulador ao logger
    logger.addHandler(file_handler)

    return logger

# Criar uma instância global do logger
logger = configurar_logger()
