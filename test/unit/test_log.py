from src.log import DEBUG, create_global, create_log, create_trace


def test_init():
    class simple:
        GLOBAL_LOGGER_LEVEL = DEBUG
        GLOBAL_TRACER_LEVEL = DEBUG

    _ = create_global(config=simple)
    return


def test_create_log():
    log = create_log("app", DEBUG)
    log.info("test log")


def test_create_trace():
    trace = create_trace("job", DEBUG)
    trace.trace("test trace")
