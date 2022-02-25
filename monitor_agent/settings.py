from multiprocessing.sharedctypes import Value
import os
import sys
import json
from types import SimpleNamespace

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
    "alert_url",
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


def dict_keys_iterator(dictionary: dict):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            dict_keys_iterator(value)
        yield key


class Settings:
    def __init__(self, rel_path: str = "settings.json"):
        dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        self.abs_file_path = os.path.join(dir, rel_path)
        self.settings = self.read_settings_file(self.abs_file_path)

    def _validate_json(self, config_parameters: list, data: dict):
        keys = [key for key in dict_keys_iterator(data)]

        diff_total = list(set(keys) - set(config_parameters))
        if len(diff_total) > 0:
            raise ValueError(f"Config file contains invalid parameters: {diff_total}")

        diff_main = list(set(main_parameters) - set(keys))
        if len(diff_main) > 0:
            raise ValueError(
                f"Config file does not contain main parameters: {diff_main}"
            )

        # Need to validate type of data

    def _fill_json(self, optional_parameters: list, json_dict: dict):
        fill_dict = json_dict.copy()
        for key in optional_parameters:
            if key not in fill_dict.keys():
                fill_dict[key] = None
        return fill_dict

    def read_settings_file(self, file_path: str):
        try:
            f = open(file_path, "r")
        except FileNotFoundError as msg:
            print(msg, file=sys.stderr)
            exit()
        data = f.read()

        try:
            json_dict = json.loads(data)
            self._validate_json(config_parameters, json_dict)
        except (json.JSONDecodeError, ValueError) as msg:
            print(msg, file=sys.stderr)
            exit()

        json_dict = self._fill_json(optional_parameters, json_dict)
        f = open(self.abs_file_path, "w")
        f.write(json.dumps(json_dict, indent=4, sort_keys=True))

        return self.read_settings(data)

    def read_settings(self, data: str):
        """Parse JSON into an object with attributes corresponding to dict keys."""
        # https://stackoverflow.com/a/15882054
        return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

    def write_settings(self, new_data: str):
        try:
            json_dict = json.loads(new_data)
            self._validate_json(config_parameters, json_dict)
        except (json.JSONDecodeError, ValueError) as msg:
            return {"status": f"Error: {msg}", "data": new_data}

        json_dict = self._fill_json(optional_parameters, json_dict)
        f = open(self.abs_file_path, "w")
        f.write(new_data)

        self.settings = self.read_settings(new_data)
        return {"status": "success", "data": json_dict}
