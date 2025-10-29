import json
import os
class ConfigRepository:
    def __init__(self, path):
        self._path = path

    def read_raw(self) -> dict:
        # open(self.path, "r", encoding="utf-8") → json.load → return dict
        with open(self._path, "r", encoding="utf-8") as f:
            parameters_raw = json.load(f)
            return parameters_raw

    # def write_raw(self, cfg: dict) -> SafeReport:
    #     tmp = f"{self._path}.tmp" # create temp file path
    #     with open(tmp, "w", encoding="utf-8") as f:
    #         json.dump(cfg, f, indent=2, ensure_ascii=False, sort_keys=True)  # write to temp file
    #     fsync + os.replace(tmp, self._path)  # ensure data is written and replace original file
    #     return SaveReport(ok=True, written_to=self._path, fingerprint=compute_hash(cfg))

    #     # tmp = f"{self.path}.tmp"
    #     # open(tmp, "w", encoding="utf-8") → json.dump(indent=2, ensure_ascii=False, sort_keys=True)
    #     # fsync + os.replace(tmp, self.path)
    #     # return SaveReport(ok=True, written_to=self.path, fingerprint=compute_hash(cfg))    