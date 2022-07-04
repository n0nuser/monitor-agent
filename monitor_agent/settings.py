import os
import json
import logging
import typing


rel_path = "settings.json"
directory = os.path.dirname(__file__)  # <-- absolute dir the script is in
abs_file_path = os.path.join(directory, rel_path)


class Settings:
    def __init__(self):
        self.as_dict: dict = self._read_settings_file()
        _obj = toObj(self.as_dict)
        self.alerts = _obj.alerts
        self.auth = _obj.auth
        self.logging = _obj.logging
        self.metrics = _obj.metrics
        self.endpoints = _obj.endpoints
        self.thresholds = _obj.thresholds
        self.uvicorn = _obj.uvicorn

    def _read_settings_file(self) -> dict:
        """Reads the settings file and returns the data as a dict.

        Returns:
            dict: Dictionary with the data from the settings file.
        """
        try:
            f = open(abs_file_path, "r")
            data_dict = json.loads(f.read())
            _, data_dict = _write_to_json(data_dict, abs_file_path)
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            logging.error("Invalid JSON settings file.", exc_info=True)
            exit()

        return data_dict

    def write_settings(self, data: str) -> dict:
        """Writes the settings to the settings file.

        Args:
            data (str): The data to write to the settings file.

        Returns:
            dict: Dict with status of the write operation, and the data as a dictionary if successful.
        """
        try:
            data_dict = json.loads(data)
            _, data_dict = _write_to_json(data_dict, abs_file_path)
        except (json.JSONDecodeError, ValueError) as msg:
            return {"status": f"Error: {msg}", "data": data}

        self.settings = data_dict
        return {"status": "success", "data": data_dict}


####################
# Helper functions #
####################


def toObj(item) -> object:
    """Converts a dictionary to an object.

    Reference: Jakub Dóka: https://stackoverflow.com/a/65969444

    Returns:
        object: An object with the same data as the dictionary

    """
    if isinstance(item, dict):
        obj = type("__object", (object,), {})

        for key, value in item.items():
            setattr(obj, key, toObj(value))

        return obj
    elif isinstance(item, list):
        return map(toObj, item)
    else:
        return item


def _write_to_json(data: dict, path: str) -> typing.Tuple(str, dict):
    """Given a dictionary, write it to a json file with 4 space indentation.

    Args:
        data (dict): Dictionary to write to file
        path (str): Path to the file

    Returns:
        typing.Tuple(str, dict): Data written to the file; and the dictionary itself
    """
    f = open(path, "w")
    data_str: str = json.dumps(data, indent=4, sort_keys=True)
    f.write(data_str)
    return data_str, data
