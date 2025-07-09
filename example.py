import time
from settings import logger
import logfire


@logfire.instrument("Function Instrumented 1")
def instrumented_function():
    time.sleep(1)
    logger.info("Instrumented function called")


def main():
    while True:
        with logfire.span("First span"):
            logger.info('Starting example')
            logger.warning('This is an example message')

        with logfire.span("Second span"):
            logger.error('This is an example message')
            logger.debug('This is an example message')
            logger.critical('This is an example message')

        instrumented_function()
        time.sleep(5)


if __name__ == '__main__':
    main()
