import logging


def get_logger(
    log_level: str,
    name: str,
    logs_path: str,
) -> logging.Logger:
    """
    Настроивает и получает экземпляр логгера.

    Parameters:
    - log_level str: Уровень логирования.
    - name (str): Имя логгера.
    - logs_path (str): Директория с логами

    Return:
    - logging.Logger: экземляр класса Logger
    """

    log_lvl_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    logger = logging.getLogger(name)
    logger.setLevel(log_lvl_map.get(log_level.lower(), logging.ERROR))

    main_handler = logging.FileHandler(
        f'{logs_path}/{name}.log',
        encoding='utf-8'
    )

    formatter = logging.Formatter(
        '[%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d] %(message)s'
    )
    main_handler.setFormatter(formatter)

    logger.addHandler(main_handler)

    return logger
