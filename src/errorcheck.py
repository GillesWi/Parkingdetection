def check_video_capture(logger, cap):
    if not cap.isOpened():
        logger.critical("Video capture failed to open. Exiting...")
        exit(1)


def check_object(logger, succes):
    if not succes:
        logger.critical("No more frames to read. Exiting...")
        exit(1)
