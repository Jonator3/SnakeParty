from configparser import ConfigParser

DEF_LEN = None
DEF_SIZE = None
MAX_LEN = None
SIZE_SET = None
FRAME_TIME = None

# These settings are not ment to be changed, and represent fixed limitations of this software
MAX_PLAYERS = 10
KEY_LEN = 5


def reset_conf():
    global DEF_LEN, DEF_SIZE, MAX_LEN, SIZE_SET, FRAME_TIME
    DEF_LEN = 3
    DEF_SIZE = 1
    MAX_LEN = 5
    SIZE_SET = [15, 20, 25, 30]
    FRAME_TIME = 250


reset_conf()


def load_conf(path):
    global DEF_LEN, DEF_SIZE, MAX_LEN, SIZE_SET, FRAME_TIME
    conf = ConfigParser()
    conf.read(path)

    FRAME_TIME = int(conf.get("GAME", "step_time", fallback=FRAME_TIME))
    DEF_LEN = int(conf.get("GAME", "default_time", fallback=DEF_LEN))
    MAX_LEN = int(conf.get("GAME", "max_time", fallback=MAX_LEN))
    SIZE_SET = eval(conf.get("GAME", "size_set", fallback=str(SIZE_SET)))
    DEF_SIZE = int(conf.get("GAME", "default_size", fallback=DEF_SIZE))

