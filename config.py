from datetime import datetime,timedelta,time
import dukascopy_python as dk
import os
from dotenv import load_dotenv
from dukascopy_python.instruments import *

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
START = datetime.now()
END = None
OFFER_SIDE = dk.OFFER_SIDE_BID
SESSION_STARTTIME = time(7,30) #8:30 UTC+1
SESSION_ENDTIME = time(18,0)# 19:00 UTC+1
WATCHED_PAIRS=[("USD-JPY",INSTRUMENT_FX_MAJORS_USD_JPY),("AUD-USD",INSTRUMENT_FX_MAJORS_AUD_USD),("GBP-USD",INSTRUMENT_FX_MAJORS_GBP_USD)]
HOLIDAYS = [
    # New Year
    datetime(2024, 1, 1).date(),
    datetime(2025, 1, 1).date(),

    # Martin Luther King Jr Day (US)
    datetime(2024, 1, 15).date(),
    datetime(2025, 1, 20).date(),

    # Presidents' Day (US)
    datetime(2024, 2, 19).date(),
    datetime(2025, 2, 17).date(),

    # Good Friday 
    datetime(2024, 3, 29).date(),
    datetime(2025, 4, 18).date(),

    # Easter Monday (Europe/UK)
    datetime(2024, 4, 1).date(),
    datetime(2025, 4, 21).date(),

    # Early May Bank Holiday (UK)
    datetime(2024, 5, 6).date(),
    datetime(2025, 5, 5).date(),

    # Memorial Day (US)
    datetime(2024, 5, 27).date(),
    datetime(2025, 5, 26).date(),

    # US Independence Day
    datetime(2024, 7, 4).date(),
    datetime(2025, 7, 4).date(),

    # Summer Bank Holiday (UK)
    datetime(2024, 8, 26).date(),
    datetime(2025, 8, 25).date(),

    # Labor Day (US)
    datetime(2024, 9, 2).date(),
    datetime(2025, 9, 1).date(),

    # Thanksgiving (US)
    datetime(2024, 11, 28).date(),
    datetime(2025, 11, 27).date(),

    # Christmas Day
    datetime(2024, 12, 25).date(),
    datetime(2025, 12, 25).date(),
]