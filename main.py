import sys
import asyncio

# На винде выпадает ошибка: aiodns needs a SelectorEventLoop on Windows.
# See more: https://github.com/saghul/aiodns/issues/86
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

from src.config import get_config


config = get_config()


if __name__ == '__main__':
    uvicorn.run(
        'src.app:app',
        host=config.API_HOST,
        port=config.API_PORT,
        log_level='info',
        ssl_certfile=config.SSL_CERT_PATH,
        ssl_keyfile=config.SSL_PRIVATE_KEY_PATH
    )
