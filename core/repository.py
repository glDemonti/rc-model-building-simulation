import json
import os

from dataclasses import dataclass

@dataclass
class SafeReport:
    ok : bool
    written_to : str
    fingerprint : str | None = None
    msg : str | None = None


class ConfigRepository:
    def __init__(self, path):
        self._path = path

    def read_raw(self) -> dict:
        # open(self.path, "r", encoding="utf-8") → json.load → return dict
        with open(self._path, "r", encoding="utf-8") as f:
            parameters_raw = json.load(f)
            return parameters_raw

    def write_raw(self,cfg: dict):
        tmp = f"{self._path}.tmp" # create temp file path
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False, sort_keys=True)  # write to temp file
            f.flush() # flush internal buffer
            os.fsync(f.fileno())  # ensure data is written
        os.replace(tmp, self._path)  # replace original file


