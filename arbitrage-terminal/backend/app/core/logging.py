import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    # Some APIs include credentials in URL paths, so library-level request logs
    # must stay disabled. Application services log sanitized failures explicitly.
    logging.getLogger("httpx").setLevel(logging.WARNING)
