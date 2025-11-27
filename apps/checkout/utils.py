from datetime import datetime

def format_timestamp(timestamp):
    """
    Convert a UNIX timestamp to a human-readable date string.
    
    Args:
        timestamp (int): The UNIX timestamp to convert.
        
    Returns:
        str: The formatted date string in "YYYY-MM-DD HH:MM:SS" format
    """
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

