import os
import sys
import json
from monitor_agent.core.helper import save2log


main_parameters = [
    "host",
    "port",
    "workers",
    "reload",
    "debug",
    "log_level",
    "backlog",
    "timeout_keep_alive",
    "metric_endpoint",
    "post_metric_url",
    "post_interval",
    "metric_enable_file",
    "metric_file",
    "post_alert_url",
]

optional_parameters = [
    "ssl_keyfile",
    "ssl_keyfile_password",
    "ssl_certfile",
    "ssl_version",
    "ssl_cert_reqs",
    "ssl_ca_certs",
    "ssl_ciphers",
    "limit_concurrency",
    "limit_max_requests",
]

config_parameters = main_parameters + optional_parameters
rel_path = "settings.json"
dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
abs_file_path = os.path.join(dir, rel_path)


class Settings:
    def __init__(self):
        for key, value in self._read_settings_file().items():
            setattr(self, key, value)

    def _read_settings_file(self):
        try:
            f = open(abs_file_path, "r")
            data = f.read()
            data_dict = _validate_json(data)
            data_str, data_dict = _format_json_file(data_dict, abs_file_path)
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as msg:
            print(f"ERROR: Invalid JSON settings file - {msg}", file=sys.stderr)
            save2log(type="ERROR", data = f"Invalid JSON file - {msg}")
            exit()

        return data_dict

    def write_settings(self, data: str):
        try:
            data_dict = _validate_json(data)
            data_str, data_dict = _format_json_file(data_dict, abs_file_path)
        except (json.JSONDecodeError, ValueError) as msg:
            return {"status": f"Error: {msg}", "data": data}

        self.settings = data_dict
        return {"status": "success", "data": data_dict}


######################
## Helper functions ##
######################


def dict_keys_iterator(dictionary: dict):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            dict_keys_iterator(value)
        yield key


def _validate_json(data: str):
    data_dict = json.loads(data)

    keys = [key for key in dict_keys_iterator(data_dict)]

    diff_total = list(set(keys) - set(config_parameters))
    if len(diff_total) > 0:
        raise ValueError(f"Config file contains invalid parameters: {diff_total}")

    diff_main = list(set(main_parameters) - set(keys))
    if len(diff_main) > 0:
        raise ValueError(f"Config file does not contain main parameters: {diff_main}")
    return data_dict

    # Need to validate type of data


def _format_json_file(data: dict, path: str):
    data_dict = data.copy()
    for key in optional_parameters:
        if key not in data_dict.keys():
            data_dict[key] = None
    f = open(path, "w")
    data_str: str = json.dumps(data_dict, indent=4, sort_keys=True)
    f.write(data_str)
    return data_str, data_dict
