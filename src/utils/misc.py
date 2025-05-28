def filter():
    import logging
    import warnings

    from urllib3.exceptions import InsecureRequestWarning

    # ignore all warnings
    warnings.filterwarnings("ignore")

    # ignore UserWarning
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="opensearchpy.connection.http_urllib3"
    )

    # ignore InsecureRequestWarning
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    # disable logs
    logging.basicConfig(level=logging.ERROR)
