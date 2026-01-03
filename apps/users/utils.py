
def validate_required_keys(data : dict, required_keys : list):
    """
    Validate that all required keys are present in the data dictionary.
    
    Args:
        data (dict): The data dictionary to validate.
        required_keys (list): A list of keys that are required to be present in the data.
        
    Raises:
        KeyError: If any required key is missing from the data dictionary.
    """
    if not all(key in data for key in required_keys):
            missing = required_keys - data.keys()
            raise KeyError(
                f'Missing keys : {','.join(missing)}'
            )
    return True