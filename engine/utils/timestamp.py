from datetime import datetime

def now_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_readable() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
