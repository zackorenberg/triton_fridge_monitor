
LOG_PATH = ''
CALIBRATION_PATH = None
RECIPIENTS = []
SENDER = ''
PASSWORD = ''
SMTP_SERVER = ''
SMTP_PORT = -1

# TODO: turn this into a class so can be dynamically changed with gui

import os
ROOT_DIR = os.path.dirname(__file__)
"""
with open(os.path.join(ROOT_DIR, CONFIG_FILE), 'r') as f:
    lines = f.readlines()
    lines = [l for l in lines if l[0] != ';'] # Those are comments!
    # Set LOG_PATH
    try:
        LOG_PATH = [l.strip(' \n\t') for l in lines if 'LOG_PATH' in l][0].split('LOG_PATH=')[1]
        RECIPIENTS = [l.strip(' \n\t') for l in lines if 'RECIPIENTS' in l][0].split('RECIPIENTS=')[1].split(',')
        SENDER = [l.strip(' \n\t') for l in lines if 'SENDER' in l][0].split('SENDER=')[1]
        PASSWORD = [l.strip(' \n\t') for l in lines if 'PASSWORD' in l][0].split('PASSWORD=')[1]
        SMTP_SERVER = [l.strip(' \n\t') for l in lines if 'SMTP_SERVER' in l][0].split('SMTP_SERVER=')[1]
        SMTP_PORT = int([l.strip(' \n\t') for l in lines if 'SMTP_PORT' in l][0].split('SMTP_PORT=')[1])
    except KeyError:
        print("Invalid configuration file")
        exit(0)
"""



VERBOSE = True  # TODO: implement this stuff
DEBUG_MODE = False

SUBCHANNEL_DELIMITER = ':'

KV_CHANNELS = ['heaters', 'Status']
ERROR_CHANNEL = ['Errors']
MAXIGAUGE_CHANNEL = ['maxigauge']
VALVECONTROL_CHANNEL = ['Channels']

CHANNELS_WITH_UNDERSCORE = []

SUFFIX_FORMAT = "%y%m%d %H%M%S.vcl"
PREFIX_FORMAT = 'log '
EXTENSION = '.vcl'
DATETIME_FORMAT = "%y%m%d %H%M%S"
DATE_FORMAT = "%y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


ALL_CHANNELS = [
    'P2 Condense', 'P1 Tank', 'P5 ForepumpBack', 'P3 Still', 'P4 TurboBack',
    'Dewar',
    'Input Water Temp', 'Output Water Temp', 'Oil Temp', 'Helium Temp',
    'Motor Current', 'Low Pressure', 'High Pressure',
    'Channel A t', 'Channel A T', 'Channel A R',
    'PT2 Head t', 'PT2 Head T', 'PT2 Head R',
    'PT2 Plate t', 'PT2 Plate T', 'PT2 Plate R',
    'Still Plate t', 'Still Plate T', 'Still Plate R',
    'Cold Plate t', 'Cold Plate T', 'Cold Plate R',
    'MC Plate Cernox t', 'MC Plate Cernox T', 'MC Plate Cernox R',
    'PT1 Head t', 'PT1 Head T', 'PT1 Head R',
    'PT1 Plate t', 'PT1 Plate T', 'PT1 Plate R',
    'MC Plate RuO2 t', 'MC Plate RuO2 T', 'MC Plate RuO2 R',
    'Magnet t', 'Magnet T', 'Magnet R',
    'Channel 10 t', 'Channel 10 T', 'Channel 10 R',
    'Channel 11 t', 'Channel 11 T', 'Channel 11 R',
    'Channel 12 t', 'Channel 12 T', 'Channel 12 R',
    'Channel 13 t', 'Channel 13 T', 'Channel 13 R',
    'Channel 14 t', 'Channel 14 T', 'Channel 14 R',
    'Channel 15 t', 'Channel 15 T', 'Channel 15 R'
]

THERMOMETERS = [
    'Channel A',
    'PT2 Head',
    'PT2 Plate',
    'Still Plate',
    'Cold Plate',
    'MC Plate Cernox',
    'PT1 Head',
    'PT1 Plate',
    'MC Plate RuO2',
    'Magnet',
]

CHANNEL_BLACKLIST = ['Channel A t', 'PT2 Head t', 'PT2 Plate t', 'Still Plate t', 'Cold Plate t', 'MC Plate Cernox t', 'PT1 Head t', 'PT1 Plate t', 'MC Plate RuO2 t', 'Magnet t', 'Channel 10 t', 'Channel 11 t', 'Channel 12 t', 'Channel 13 t', 'Channel 14 t', 'Channel 15 t']
CHANNEL_BLACKLIST = [f"{channel} t" for channel in THERMOMETERS] + ['Channel 10 t', 'Channel 11 t', 'Channel 12 t', 'Channel 13 t', 'Channel 14 t', 'Channel 15 t']

PRESSURE_CHANNELS = ['P2 Condense', 'P1 Tank', 'P5 ForepumpBack', 'P3 Still', 'P4 TurboBack', 'Dewar']
COMPRESSOR_CHANNELS = ['Input Water Temp', 'Output Water Temp', 'Oil Temp', 'Helium Temp', 'Motor Current', 'Low Pressure', 'High Pressure',]
THERMOMETER_TEMPERATURE_CHANNELS = [f"{channel} T" for channel in THERMOMETERS]
THERMOMETER_RESISTANCE_CHANNELS = [f"{channel} R" for channel in THERMOMETERS]
MISC_CHANNELS = []

MONITOR_CHANNELS = {
    'Pressure and Flow':PRESSURE_CHANNELS,
    'Compressor':COMPRESSOR_CHANNELS,
    'Thermometry: Temperature':THERMOMETER_TEMPERATURE_CHANNELS,
    'Thermometry: Resistance':THERMOMETER_RESISTANCE_CHANNELS,
    'Misc':MISC_CHANNELS,
}


TABULATE_TABLE_FMT = 'fancy_grid'  # See here for options: https://pypi.org/project/tabulate/
INDENT_EMAIL_INFORMATION = False

MAXIMUM_DATAPOINT_HISTORY = 300
MAX_COLLAPSEABLE_HEIGHT = 400

FIX_CONSOLE_HEIGHT = True
FIX_ACTIVE_WIDTH = True

SEND_TEST_EMAIL_ON_LAUNCH = False

SPLIT_MONITOR_WIDGETS = True # This will make it so monitor selector is left, active monitors are right, and console is full bottom
# If false, monitor will be top left, console will be bottom left, and active monitor will be entirely right

CONFIG_FILE = 'config'
CONFIG_MANDATORY_FIELDS = ['LOG_PATH', 'RECIPIENTS', 'SENDER', 'PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
CONFIG_OPTIONAL_FIELDS = ['CHANNEL_BLACKLIST', 'VERBOSE', 'DEBUG_MODE', 'KEEP_LOGFILES_OPEN']

CONFIGTYPE_FIELDS_DIRECTORY = ['LOG_PATH']
CONFIGTYPE_FIELDS_EMAIL = ['RECIPIENTS']

CONFIG_MAILER_FIELDS = ['RECIPIENTS', 'SENDER', 'PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']


CHANGE_PROCESS_CHECK = 1 # Number of seconds between checking for changes (We do this instead of immediate processing because many files sometimes get modified concurrently and we want as accurate a result as possible when a monitor goes off
ICON_PATH = 'Resources/TritonIcon.ico'

KEEP_LOGFILES_OPEN = True

MAX_CHANNELS_COUNT: int = 128


def load_globals(module, global_dict):
    attrs = []
    for attr in dir(module):

        if not attr[0] == '_' and attr.upper() == attr: # all uppercase
            attrs.append(attr)
            global_dict[attr] = getattr(module, attr)
    return attrs