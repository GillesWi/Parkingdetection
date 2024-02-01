def check_object(logger, succes):
    if succes is None:
        logger.critical("No more frames to read. Exiting...")
        exit(1)
