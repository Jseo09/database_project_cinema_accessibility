# config.py
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "!Yy970912",
    "database": "cinema",
}

# ===== Table / column names =====
TABLE_THEATERS = "Theater"
COL_TID = "theater_id"
COL_NAME = "theater_name"
COL_CITY = "city"
COL_STATE = "state"
COL_STATUS = "status"
COL_URL = "website"
COL_ADDR = "address"
COL_T_LAT = "latitude"
COL_T_LON = "longitude"
COL_PHONE = "phone_number"

ROAD_VIEW_DIR = os.path.join(APP_DIR, "image", "road_view")
ROAD_ALLOWED_EXTS = (".png", ".jpg", ".jpeg", ".webp")

TABLE_FEAT = "TheaterFeatures"
COL_WHEEL = "wheel_chair_accessibility"
COL_AL = "assistive_listening"
COL_CC = "caption_device"
COL_AD = "audio_description"
COL_SRC = "info_source"
COL_CONF = "data_confidence"

TABLE_SHOW = "ShowDates"
COL_SHOWID = "show_id"
COL_DT = "show_date"
COL_IS_CC = "is_captioned"
COL_IS_AD = "is_audio_described"

TABLE_MOV = "Movies"
COL_MID = "show_id"
COL_MNAME = "movie_title"

TABLE_TTRANSIT = "TheaterTransit"
TT_THEATER_ID = "theater_id"
TT_STOP_ID = "stop_id"
TT_WALK_M = "walk_distance_m"
TT_WALK_MIN = "walk_time_min"

TABLE_TSTOPS = "TransitStops"
TS_STOP_ID = "stop_id"
TS_NAME = "stop_name"
TS_ACCESSIBLE = "accessibility"
TS_LAT = "latitude"
TS_LON = "longitude"

TABLE_SROUTES = "StopRoutes"
SR_STOP_ID = "stop_id"
SR_ROUTE = "route"

# ===== Posters =====
POSTER_DIR = os.path.join(APP_DIR, "image", "movie_poster")
POSTER_DEFAULT = os.path.join(POSTER_DIR, "question.png")
ALLOWED_EXTS = (".png", ".jpg", ".jpeg", ".webp")

# ===== Choices =====
STATUS_CHOICES = ("Open", "Temporarily Closed", "Closed")
US_STATES = (
    "TX","CA","NY","FL","IL","GA","PA","OH","NC","MI",
    "AZ","WA","MA","NJ","VA","IN","TN","MO","MD","WI",
    "CO","MN","SC","AL","LA","KY","OR","OK","CT","UT",
    "IA","NV","AR","MS","KS","NM","NE","WV","ID","HI",
    "NH","ME","RI","MT","DE","SD","ND","AK","VT","DC",
)
