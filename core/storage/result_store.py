class ResulstRepository:
    def save_raw(self, project_id: str, df: pd.DataFrame) -> None:
        pass
    def load_raw(self, project_id: str, run_id="latest") -> pd.DataFrame | None:
        pass
