import logging
import logfire
import time

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_system_metrics()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('financial_analyzer.log'),
                              logfire.LogfireLoggingHandler()]
                    )
logger = logging.getLogger(__name__)


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
