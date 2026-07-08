import re
import datetime

def is_yellow_color(color_hex):
    if not color_hex or not isinstance(color_hex, str):
        return False
    color_clean = color_hex.upper().strip()
    if color_clean.startswith('#'):
        color_clean = color_clean[1:]
    if len(color_clean) == 8:
        color_clean = color_clean[2:]
    if len(color_clean) == 6:
        try:
            r = int(color_clean[0:2], 16)
            g = int(color_clean[2:4], 16)
            b = int(color_clean[4:6], 16)
            # Yellow: high Red/Green, low Blue
            return r > 180 and g > 180 and b < 150
        except ValueError:
            return False
    return False

def is_green_color(color_hex):
    if not color_hex or not isinstance(color_hex, str):
        return False
    color_clean = color_hex.upper().strip()
    if color_clean.startswith('#'):
        color_clean = color_clean[1:]
    if len(color_clean) == 8:
        color_clean = color_clean[2:]
    if len(color_clean) == 6:
        try:
            r = int(color_clean[0:2], 16)
            g = int(color_clean[2:4], 16)
            b = int(color_clean[4:6], 16)
            # Green: high Green, low Red/Blue
            return g > 120 and r < 100 and b < 100
        except ValueError:
            return False
    return False

def is_red_color(color_hex):
    if not color_hex or not isinstance(color_hex, str):
        return False
    color_clean = color_hex.upper().strip()
    if color_clean.startswith('#'):
        color_clean = color_clean[1:]
    if len(color_clean) == 8:
        color_clean = color_clean[2:]
    if len(color_clean) == 6:
        try:
            r = int(color_clean[0:2], 16)
            g = int(color_clean[2:4], 16)
            b = int(color_clean[4:6], 16)
            # Red: high Red, low Green/Blue
            return r > 150 and g < 100 and b < 100
        except ValueError:
            return False
    return False

def clean_phone_number(phone_val):
    if not phone_val:
        return None
    # Remove non-digits
    digits = "".join(c for c in str(phone_val) if c.isdigit())
    if not digits:
        return None
    if len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"
    if len(digits) == 9:
        return f"+998{digits}"
    if digits.startswith("998"):
        return f"+{digits}"
    return f"+998{digits}"

def parse_enrollment_date(date_val, current_year, current_month):
    if not date_val:
        return datetime.date(current_year, current_month, 1)
    if isinstance(date_val, (datetime.date, datetime.datetime)):
        d = date_val.date() if isinstance(date_val, datetime.datetime) else date_val
        if d.year < current_year - 5:
            try:
                return datetime.date(current_year, d.month, d.day)
            except ValueError:
                return datetime.date(current_year, d.month, 1)
        return d
    
    date_str = str(date_val).lower().strip()
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
            
    match = re.search(r'(\d+)\s*([a-zа-я]+|\/\s*[a-z]+)', date_str)
    if not match:
        return datetime.date(current_year, current_month, 1)
    
    day = int(match.group(1))
    month_part = match.group(2).replace('/', '').strip()
    
    month_map = {
        'yan': 1, 'yanvar': 1, 'jan': 1,
        'fev': 2, 'fevral': 2, 'feb': 2,
        'mar': 3, 'mart': 3,
        'apr': 4, 'aprel': 4,
        'may': 5,
        'iyun': 6, 'jun': 6,
        'iyul': 7, 'jul': 7,
        'avg': 8, 'avgust': 8, 'aug': 8,
        'sen': 9, 'sentyabr': 9, 'sep': 9,
        'okt': 10, 'oktyabr': 10, 'oct': 10,
        'noy': 11, 'noyabr': 11, 'nov': 11,
        'dek': 12, 'dekabr': 12, 'dec': 12
    }
    
    month = month_map.get(month_part, current_month)
    try:
        return datetime.date(current_year, month, day)
    except ValueError:
        return datetime.date(current_year, current_month, 1)
