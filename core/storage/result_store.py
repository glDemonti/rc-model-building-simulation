from pathlib import Path
import pandas as pd

class ResultRepository:
    def save_raw(self, project_id: str, variant_id: str, df: pd.DataFrame) -> None:
        
        df_raw = df

        # build paths
        base_dir = Path("projects") / project_id / "results"
        base_dir.mkdir(parents=True, exist_ok=True)

        out_path = base_dir / f"raw_results_{variant_id}.parquet"

        # save results
        df_raw.to_parquet(out_path, compression="snappy")


    def load_raw(self, project_id: str, variant_id: str) -> pd.DataFrame | None:
        path = Path("projects") / project_id / "results" / f"raw_results_{variant_id}.parquet"
        if not path.exists():
            return None
        df_raw = pd.read_parquet(path)
        return df_raw
