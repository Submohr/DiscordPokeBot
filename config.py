import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))

class Config(object):
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

    EXTREME_PATH = os.environ.get('EXTREME_PATH')
    STATS_PATH = os.environ.get('STATS_PATH')
    PLOTS_PATH = os.environ.get('PLOTS_PATH')
    WATCHLISTS_PATH = os.environ.get('WATCHLISTS_PATH')
    SEARCH_EVOS = os.environ.get('DISCORD_TOKEN') or True

    LOG_LEVEL = os.environ.get('LOG_LEVEL') or "DEBUG"
    LOG_FOLDER = os.environ.get('LOG_FOLDER')
    LOG_NAME = os.environ.get('LOG_NAME')
