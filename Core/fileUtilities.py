import os
import localvars
localvars.load_globals(localvars, globals())
from datetime import datetime

from Core.fileReader import parse


def load_all_log_files(log_path = LOG_PATH):
    files = os.listdir(log_path)
    return {datetime.strptime(f[4:-4], DATETIME_FORMAT):f for f in files if f[:4] == 'log ' and f[-4:] == '.vcl'}
    ret = {}
    for file in files:
        if not (file[:4] == 'log ' and file[-4:] == '.vcl'):
            continue
        date = datetime.strptime(file[4:-4], DATETIME_FORMAT)
        ret[date] = file
    return ret

def load_latest_log_file(log_path = LOG_PATH):
    files = os.listdir(log_path)
    latest_time = 0
    latest_file = None
    for file in files:
        if not (file[:4] == 'log ' and file[-4:] == '.vcl'):
            continue
        creation_time = datetime.strptime(file[4:-4], DATETIME_FORMAT).timestamp()
        if creation_time > latest_time:
            latest_time = creation_time
            latest_file = file
    return latest_file

def determine_creation_time(fname, log_path = LOG_PATH):
    if fname[:-len(SUFFIX_FORMAT)] != PREFIX_FORMAT:
        return
    date = datetime.strptime(fname[len(PREFIX_FORMAT):-len(EXTENSION)], DATETIME_FORMAT)
    return date.timestamp()

def get_all_channels(log_path = LOG_PATH):
    # We need literally any file from the log path
    lf = load_latest_log_file(log_path)
    titles, _ = parse(os.path.join(log_path, lf))

    labels = [s.split('(')[0].strip(' ') if '(' in s else s for s in titles[2:]]
    return labels


if __name__ == "__main__":
    os.chdir(ROOT_DIR)
    print(get_all_channels('tests/test_logs'))
    exit(0)
    print(load_all_log_files('tests/test_logs'))
