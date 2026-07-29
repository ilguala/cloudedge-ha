"""Constants for the CloudEdge integration."""

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "cloudedge"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_PHONE_CODE = "phone_code"
CONF_REFRESH_INTERVAL = "refresh_interval"

# Default values
DEFAULT_REFRESH_INTERVAL = 5  # minutes
DEFAULT_COUNTRY_CODE = "US"
DEFAULT_PHONE_CODE = "+1"

# Supported country codes and phone codes
COUNTRY_CODES = {
    "AF": "+93",
    "AL": "+355",
    "DZ": "+213",
    "AD": "+376",
    "AO": "+244",
    "AG": "+1",
    "AR": "+54",
    "AM": "+374",
    "AU": "+61",
    "AT": "+43",
    "AZ": "+994",
    "BS": "+1",
    "BH": "+973",
    "BD": "+880",
    "BB": "+1",
    "BY": "+375",
    "BE": "+32",
    "BZ": "+501",
    "BJ": "+229",
    "BT": "+975",
    "BO": "+591",
    "BA": "+387",
    "BW": "+267",
    "BR": "+55",
    "BN": "+673",
    "BG": "+359",
    "BF": "+226",
    "BI": "+257",
    "CV": "+238",
    "KH": "+855",
    "CM": "+237",
    "CA": "+1",
    "CF": "+236",
    "TD": "+235",
    "CL": "+56",
    "CN": "+86",
    "CO": "+57",
    "KM": "+269",
    "CG": "+242",
    "CD": "+243",
    "CR": "+506",
    "CI": "+225",
    "HR": "+385",
    "CU": "+53",
    "CY": "+357",
    "CZ": "+420",
    "DK": "+45",
    "DJ": "+253",
    "DM": "+1",
    "DO": "+1",
    "EC": "+593",
    "EG": "+20",
    "SV": "+503",
    "GQ": "+240",
    "ER": "+291",
    "EE": "+372",
    "SZ": "+268",
    "ET": "+251",
    "FJ": "+679",
    "FI": "+358",
    "FR": "+33",
    "GA": "+241",
    "GM": "+220",
    "GE": "+995",
    "DE": "+49",
    "GH": "+233",
    "GR": "+30",
    "GD": "+1",
    "GT": "+502",
    "GN": "+224",
    "GW": "+245",
    "GY": "+592",
    "HT": "+509",
    "HN": "+504",
    "HU": "+36",
    "IS": "+354",
    "IN": "+91",
    "ID": "+62",
    "IR": "+98",
    "IQ": "+964",
    "IE": "+353",
    "IL": "+972",
    "IT": "+39",
    "JM": "+1",
    "JP": "+81",
    "JO": "+962",
    "KZ": "+7",
    "KE": "+254",
    "KI": "+686",
    "KP": "+850",
    "KR": "+82",
    "KW": "+965",
    "KG": "+996",
    "LA": "+856",
    "LV": "+371",
    "LB": "+961",
    "LS": "+266",
    "LR": "+231",
    "LY": "+218",
    "LI": "+423",
    "LT": "+370",
    "LU": "+352",
    "MG": "+261",
    "MW": "+265",
    "MY": "+60",
    "MV": "+960",
    "ML": "+223",
    "MT": "+356",
    "MH": "+692",
    "MR": "+222",
    "MU": "+230",
    "MX": "+52",
    "FM": "+691",
    "MD": "+373",
    "MC": "+377",
    "MN": "+976",
    "ME": "+382",
    "MA": "+212",
    "MZ": "+258",
    "MM": "+95",
    "NA": "+264",
    "NR": "+674",
    "NP": "+977",
    "NL": "+31",
    "NZ": "+64",
    "NI": "+505",
    "NE": "+227",
    "NG": "+234",
    "MK": "+389",
    "NO": "+47",
    "OM": "+968",
    "PK": "+92",
    "PW": "+680",
    "PS": "+970",
    "PA": "+507",
    "PG": "+675",
    "PY": "+595",
    "PE": "+51",
    "PH": "+63",
    "PL": "+48",
    "PT": "+351",
    "QA": "+974",
    "RO": "+40",
    "RU": "+7",
    "RW": "+250",
    "KN": "+1",
    "LC": "+1",
    "VC": "+1",
    "WS": "+685",
    "SM": "+378",
    "ST": "+239",
    "SA": "+966",
    "SN": "+221",
    "RS": "+381",
    "SC": "+248",
    "SL": "+232",
    "SG": "+65",
    "SK": "+421",
    "SI": "+386",
    "SB": "+677",
    "SO": "+252",
    "ZA": "+27",
    "SS": "+211",
    "ES": "+34",
    "LK": "+94",
    "SD": "+249",
    "SR": "+597",
    "SE": "+46",
    "CH": "+41",
    "SY": "+963",
    "TW": "+886",
    "TJ": "+992",
    "TZ": "+255",
    "TH": "+66",
    "TL": "+670",
    "TG": "+228",
    "TO": "+676",
    "TT": "+1",
    "TN": "+216",
    "TR": "+90",
    "TM": "+993",
    "TV": "+688",
    "UG": "+256",
    "UA": "+380",
    "AE": "+971",
    "GB": "+44",
    "UK": "+44",
    "US": "+1",
    "UY": "+598",
    "UZ": "+998",
    "VU": "+678",
    "VA": "+379",
    "VE": "+58",
    "VN": "+84",
    "YE": "+967",
    "ZM": "+260",
    "ZW": "+263",
}

# Device types mapping
DEVICE_TYPE_CAMERA = "Camera"
DEVICE_TYPE_DOORBELL = "Doorbell"
DEVICE_TYPE_SENSOR = "Sensor"

# Entity categories
ENTITY_CATEGORY_CONFIG = "config"
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"

# Parameter names for switches
SWITCH_PARAMETERS = {
    "front_light": "FRONT_LIGHT_SWITCH",
    "motion_detection": "MOTION_DET_ENABLE",
    "led_enable": "LED_ENABLE",
    "sound_detection": "SOUND_DET_ENABLE",
    "push_notifications": "PUSH_ENABLE",
    "email_notifications": "EMAIL_ENABLE",
}

# Parameter names for sensors (mapped to parameter codes, not names)
SENSOR_PARAMETERS = {
    "battery_level": "154",        # BATTERY_PERCENT
    "wifi_strength": "1007",       # WIFI_STRENGTH
    "motion_sensitivity": "151",   # MOTION_DET_SENSITIVITY
    "speaker_volume": "152",       # SPEAK_VOLUME
    "device_temperature": "1012",  # DEVICE_TEMPERATURE
}

# Parameter codes that should be enabled by default for generic sensors (DIAGNOSTIC)
ENABLED_BY_DEFAULT_SENSOR_PARAMS = [
    "154",   # BATTERY_PERCENT - Battery percentage (diagnostic)
]

# Parameter names that should be enabled by default for switches (CONFIG)
ENABLED_BY_DEFAULT_SWITCH_PARAMS = [
    "MOTION_DET_ENABLE",  # Motion detection enable (config)
    "LED_ENABLE",         # LED enable (config)
]

# Sensor device classes
SENSOR_DEVICE_CLASS_BATTERY = "battery"
SENSOR_DEVICE_CLASS_SIGNAL_STRENGTH = "signal_strength"
SENSOR_DEVICE_CLASS_TEMPERATURE = "temperature"

# Sensor units
SENSOR_UNIT_PERCENTAGE = "%"
SENSOR_UNIT_CELSIUS = "°C"
SENSOR_UNIT_DECIBEL = "dB"

# --- Meari brand: Cococam (fork-only) --------------------------------------
# Meari is a white-label platform: the same backend serves several apps, and
# sourceApp/brand select the brand namespace. Upstream targets the CloudEdge
# brand (sourceApp=8, brand=77), and a Cococam account is rejected there with
# resultCode 1017. The values below were read from the com.cococam.cam 6.1.1
# APK and confirmed against the app's own runtime logs.
#
# This has to run before any CloudEdgeClient call. const.py is imported by
# both __init__.py and config_flow.py, so it is the earliest common point and
# covers the login performed during the config flow as well.
# Setting an attribute the library does not read fails SILENTLY: Python simply
# creates a new one, the library keeps its own default, and the login comes back
# as resultCode 1017 with nothing in the logs to explain why. That already cost
# one debugging round, so rather than assuming a set of names: apply whichever
# name the installed library actually declares, and complain loudly when a
# parameter cannot be applied at all.
#
# The alternatives exist because upstream names these APP_VERSION /
# APP_VERSION_CODE, while an earlier revision of the patched fork used APP_VER /
# APP_VER_CODE. Accepting both means the library and this integration can be
# updated in any order instead of having to move in lockstep.
_MEARI_BRAND_PARAMETERS = (
    ("sourceApp", ("SOURCE_APP",), "82"),
    ("appVersion", ("APP_VERSION", "APP_VER"), "6.1.1"),
    ("appVersionCode", ("APP_VERSION_CODE", "APP_VER_CODE"), "611"),
    ("partnerId", ("PARTNER_ID",), "82"),
    ("p2pBrand", ("P2P_BRAND",), "82"),
    ("p2pAppVersion", ("P2P_APP_VER",), "6.1.1a8.0.0"),
)

try:
    from cloudedge import constants as _meari_constants
except ImportError:  # requirement not installed yet — nothing to override
    pass
else:
    for _label, _candidate_names, _value in _MEARI_BRAND_PARAMETERS:
        for _name in _candidate_names:
            if hasattr(_meari_constants, _name):
                setattr(_meari_constants, _name, _value)
                break
        else:
            _LOGGER.error(
                "Cococam brand parameter %s was not applied: none of %s exist in "
                "pycloudedge.constants. Login will fail with resultCode 1017 "
                "until this is fixed",
                _label,
                ", ".join(_candidate_names),
            )