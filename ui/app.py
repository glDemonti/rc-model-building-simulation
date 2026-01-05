from functools import partial
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import copy
import io
import zipfile
from pathlib import Path

from shiny import reactive
from shiny import ui as base_ui
from shiny.express import input, render, ui
from shiny.ui import page_navbar, nav_panel, navset_pill_list
from shinywidgets import render_widget, render_plotly
from datetime import datetime

from core.bootstrap import create_facade # imports the connection to the midlayer

PROJECT_ID_VAR_A = "simulation-variant-A"
PROJECT_ID_VAR_B = "simulation-variant-B"

VARIANT_ID_A = "A"
VARIANT_ID_B = "B"

facade_A = create_facade(PROJECT_ID_VAR_A, VARIANT_ID_A)
facade_B = create_facade(PROJECT_ID_VAR_B, VARIANT_ID_B)

cfg_A = facade_A.load_config(PROJECT_ID_VAR_A)
cfg_B = facade_B.load_config(PROJECT_ID_VAR_B)

cfg0 = copy.deepcopy(cfg_A) # static snapshot for UI initial values
cfg_state = reactive.Value(copy.deepcopy(cfg_A))    # initialize with variant A
active_variant = reactive.Value("A")                # "A" or "B"
unsaved_changes = reactive.Value(False)            # track unsaved changes


# # Import sim_io_mock from adapters, adjusting sys.path if necessary
# try:
#     from adapters import sim_io_mock
# except ModuleNotFoundError:
#     import sys, pathlib
#     ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (one above /ui)
#     if str(ROOT) not in sys.path:
#         sys.path.insert(0, str(ROOT))
#     from adapters import sim_io_mock


# Helper function to deeply set a value in a nested dictionary given a dot-separated path
def _deep_set(d, path, value):
    out = copy.deepcopy(d)
    cur = out
    parts = path.split(".")
    for k in parts[:-1]:
        cur = cur[k]
    cur[parts[-1]] = value
    return out


def _deep_get(d, path):
    cur = d
    parts = path.split(".")
    for k in parts:
        cur = cur[k]
    return cur


def _push_inputs_from_cfg():
    # Push current cfg_state values to input fields
    cur = cfg_state()
    for _id, (path, cast) in BINDINGS.items():
        try:
            ui.update_text(_id, value=str(_deep_get(cur, path)))
        except Exception:
            # if a field cannot be updated, skip it
            pass


def _refresh_schedules_from_cfg():
    cur = cfg_state()
    schedule_occupancy.set(_schedule_df_from_cfg(cur, 'occupancy_schedule'))
    schedule_lighting.set(_schedule_df_from_cfg(cur, 'lighting_schedule'))
    schedule_equipment.set(_schedule_df_from_cfg(cur, 'equipment_schedule'))


BINDINGS = {
    "unshaded_glazing_area_n": ("building_geometry.windows.north.unshaded_glazing_area.expression", str),
    "unshaded_glazing_area_e": ("building_geometry.windows.east.unshaded_glazing_area.expression", str),
    "unshaded_glazing_area_s": ("building_geometry.windows.south.unshaded_glazing_area.expression", str),
    "unshaded_glazing_area_w": ("building_geometry.windows.west.unshaded_glazing_area.expression", str),
    "shaded_glazing_area_n": ("building_geometry.windows.north.shaded_glazing_area.expression", str),
    "shaded_glazing_area_e": ("building_geometry.windows.east.shaded_glazing_area.expression", str),
    "shaded_glazing_area_s": ("building_geometry.windows.south.shaded_glazing_area.expression", str),
    "shaded_glazing_area_w": ("building_geometry.windows.west.shaded_glazing_area.expression", str),
    "unshaded_frame_area_n": ("building_geometry.windows.north.unshaded_frame_area.expression", str),
    "unshaded_frame_area_e": ("building_geometry.windows.east.unshaded_frame_area.expression", str),
    "unshaded_frame_area_s": ("building_geometry.windows.south.unshaded_frame_area.expression", str),
    "unshaded_frame_area_w": ("building_geometry.windows.west.unshaded_frame_area.expression", str),
    "shaded_frame_area_n": ("building_geometry.windows.north.shaded_frame_area.expression", str),
    "shaded_frame_area_e": ("building_geometry.windows.east.shaded_frame_area.expression", str),
    "shaded_frame_area_s": ("building_geometry.windows.south.shaded_frame_area.expression", str),
    "shaded_frame_area_w": ("building_geometry.windows.west.shaded_frame_area.expression", str),
    "wall_area_n": ("building_geometry.enclosure.outside_wall_areas.north.expression", str),
    "wall_area_e": ("building_geometry.enclosure.outside_wall_areas.east.expression", str),
    "wall_area_s": ("building_geometry.enclosure.outside_wall_areas.south.expression", str),
    "wall_area_w": ("building_geometry.enclosure.outside_wall_areas.west.expression", str),
    "roof_area": ("building_geometry.enclosure.roof_area.expression", str),
    "floor_area": ("building_geometry.enclosure.floor_area.expression", str),
    "int_wall_area": ("building_geometry.enclosure.int_wall_area.expression", str),
    "int_ceiling_area": ("building_geometry.enclosure.int_ceiling_area.expression", str),
    "wall_against_unheated_area": ("building_geometry.enclosure.wall_to_unheated_area.expression", str),
    "ebf_area": ("building_geometry.enclosure.ebf_area.expression", str),
    "building_height": ("building_geometry.building_height.expression", str),
    "glazing_u_value": ("thermal_properties.windows.u_value_glazing.expression", str),
    "glazing_g_value": ("thermal_properties.windows.g_value_glazing.expression", str),
    "shading_g_value_reduction_factor": ("thermal_properties.windows.shading_g_value_reduction_factor.expression", str),
    "frame_u_value": ("thermal_properties.windows.u_value_frame.expression", str),
    "wall_against_unheated_u_value": ("thermal_properties.enclosure.u_value_wall_against_unheated.expression", str),
    "wall_inside_lambda": ("thermal_properties.enclosure.inside_layer.lambda_wall_inside.expression", str),
    "roof_inside_lambda": ("thermal_properties.enclosure.inside_layer.lambda_roof_inside.expression", str),
    "floor_inside_lambda": ("thermal_properties.enclosure.inside_layer.lambda_floor_inside.expression", str),
    "wall_inside_capacity_density": ("thermal_properties.enclosure.inside_layer.capacity_density_wall_inside.expression", str),
    "roof_inside_capacity_density": ("thermal_properties.enclosure.inside_layer.capacity_density_roof_inside.expression", str),
    "floor_inside_capacity_density": ("thermal_properties.enclosure.inside_layer.capacity_density_floor_inside.expression", str),
    "wall_outside_lambda": ("thermal_properties.enclosure.outside_layer.lambda_wall_outside.expression", str),
    "roof_outside_lambda": ("thermal_properties.enclosure.outside_layer.lambda_roof_outside.expression", str),
    "floor_outside_lambda": ("thermal_properties.enclosure.outside_layer.lambda_floor_outside.expression", str),
    "wall_outside_capacity_density": ("thermal_properties.enclosure.outside_layer.capacity_density_wall_outside.expression", str),
    "roof_outside_capacity_density": ("thermal_properties.enclosure.outside_layer.capacity_density_roof_outside.expression", str),
    "floor_outside_capacity_density": ("thermal_properties.enclosure.outside_layer.capacity_density_floor_outside.expression", str),
    "int_wall_lambda": ("thermal_properties.enclosure.internal_walls_ceiling.lambda_internal_wall.expression", str),
    "int_ceiling_lambda": ("thermal_properties.enclosure.internal_walls_ceiling.lambda_internal_ceiling.expression", str),
    "int_wall_capacity_density": ("thermal_properties.enclosure.internal_walls_ceiling.capacity_density_internal_wall.expression", str),
    "int_ceiling_capacity_density": ("thermal_properties.enclosure.internal_walls_ceiling.capacity_density_internal_ceiling.expression", str),
    "wall_inside_thickness": ("building_geometry.enclosure.outside_wall_areas.thickness.inside_layer.expression", str),
    "wall_outside_thickness": ("building_geometry.enclosure.outside_wall_areas.thickness.outside_layer.expression", str),
    "roof_inside_thickness": ("building_geometry.enclosure.roof_area.thickness.inside_layer.expression", str),
    "roof_outside_thickness": ("building_geometry.enclosure.roof_area.thickness.outside_layer.expression", str),
    "floor_inside_thickness": ("building_geometry.enclosure.floor_area.thickness.inside_layer.expression", str),
    "floor_outside_thickness": ("building_geometry.enclosure.floor_area.thickness.outside_layer.expression", str),
    "int_wall_thickness": ("building_geometry.enclosure.int_wall_area.thickness.expression", str),
    "int_ceiling_thickness": ("building_geometry.enclosure.int_ceiling_area.thickness.expression", str),
    "infiltration_rate": ("thermal_properties.infiltration_rate_specific.expression", str),
    "air_ventilation_rate": ("thermal_properties.air_ventilation_rate_specific.expression", str),
    "heat_exchanger_efficiency": ("thermal_properties.heat_exchanger_efficiency.expression", str),
    "thermal_bridges": ("thermal_properties.thermal_bridges.expression", str),
    "occupancy_power": ("thermal_properties.power_input.occupancy_power_per_area.expression", str),
    "lighting_power": ("thermal_properties.power_input.lighting_power_per_area.expression", str),
    "equipment_power": ("thermal_properties.power_input.equipment_power_per_area.expression", str),
    "heating_setpoint": ("simulation_parameters.heating_setpoint.expression", str),
    "cooling_setpoint": ("simulation_parameters.cooling_setpoint.expression", str),
    "enable_cooling": ("simulation_parameters.enable_cooling.value", bool),
    "overheating_threshold": ("simulation_parameters.overheating_threshold.expression", str),
    "sim_timestep": ("simulation_parameters.time_step.expression", str),
    "surface_heat_transfer_in" : ("simulation_parameters.surface_heat_transfer_internal.expression", str),
    "surface_heat_transfer_out" : ("simulation_parameters.surface_heat_transfer_external.expression", str),
    "electricity_price": ("economic_parameters.electricity_price.expression", str),
    "heating_price": ("economic_parameters.heating_price.expression", str),
    "cooling_price": ("economic_parameters.cooling_price.expression", str),
    "Co2_emission_factor_heating": ("Co2_emission_factors.heating.expression", str),
    "Co2_emission_factor_cooling": ("Co2_emission_factors.cooling.expression", str),
    
}

def _schedule_df_from_cfg(cfg, key):
    # key ∈ {"occupancy_schedule", "lighting_schedule", "equipment_schedule"}
    # returns a DataFrame with 1 row and 24 columns
    row_name = {"occupancy_schedule": "Occupancy",
                "lighting_schedule": "Lighting",
                "equipment_schedule": "Equipment"}[key]
    return pd.DataFrame(
        columns=[f'{i:02d}:00' for i in range(24)],
        index=[row_name],
        data=[cfg['thermal_properties']['schedules'][key]],
        dtype=float
    )

# def _safe_grid_vector(grid_fn, row_name: str, fallback: list[float]) -> list[float]:
#     try:
#         df = grid_fn.data_patched().astype(float)
#         return[float(x) for x in df.loc[row_name].tolist()]
#     except Exception as e:
#         print(f"WARN: grid not ready or row missing:", row_name, e)
#         return fallback

def _safe_grid_row_or_cfg(grid_fn, row_name: str, cfg: dict, cfg_path_expr: str) -> list[float]:
    """
    Try to read a row from the DataFrame-renderer.
    If the renderer is not mounted yet or the row is missing, fall back to the cfg value at cfg_path_expr.
    """
    try:
        df = grid_fn.data_patched().astype(float)       # returns processed values when Tab is active
        return [float(x) for x in df.loc[row_name].tolist()]
    except Exception as e:
        print(f"WARN: grid'{row_name}':{e}")
        # --- fall back: resolve structure in cfg
        cur = cfg
        for key in cfg_path_expr.split("."):
            cur = cur[key]

        # 1) allow list directly 
        if isinstance(cur, list):
            return [float(x) for x in cur]

        # 2) allow dict with 'expression' or 'value' as list
        if isinstance(cur, dict):
            for k in ("expression", "value", "data"):
                v = cur.get(k)
                if isinstance(v, list):
                    return [float(x) for x in v]
                
            hours = [f"{i:02d}:00" for i in range(24)]
            if all(h in cur for h in hours):
                return [float(cur[h]) for h in hours]
            
            # 3) Heuristics: take the first list value if it is a plausible 24-hour list
            for k, v in cur.items():
                if isinstance(v, list) and (len(v) == 24 or all(isinstance(x, (int, float)) for x in v)):
                    return [float(x) for x in v]
            
            # 4) Diagnosis, so that we can see the true form
            keys = list(cur.keys())
            raise ValueError(f"{cfg_path_expr} ist ein Dict ohne passend Liste/Stunden-Mapping. Keys={keys}")
        
        # 5) all other cases: clearly name
        keys = list(cfg.keys())
        raise ValueError(f"{cfg_path_expr} hat Typ {type(cur).__name__}, erwartet list oder dict")


# reactive schedules
schedule_occupancy = reactive.Value(_schedule_df_from_cfg(cfg0, 'occupancy_schedule'))
schedule_lighting = reactive.Value(_schedule_df_from_cfg(cfg0, 'lighting_schedule'))
schedule_equipment = reactive.Value(_schedule_df_from_cfg(cfg0, 'equipment_schedule'))

# Register reactive bindings for input fields to update cfg_state
def _register_binding(input_id: str, path: str, cast):
    @reactive.effect
    @reactive.event(getattr(input, input_id))
    def _on_change():
        raw = getattr(input, input_id)()
        try:
            if cast is bool:
                if isinstance(raw, bool):
                    val = raw
                elif isinstance(raw, str):
                    val = raw.lower() in ("1", "true", "yes", "y", "on")
                else:
                    val = bool(raw)
            else:
                val = cast(raw) if cast else raw
        except Exception:
            # Optional: Validation/Fehlerfeedback
            ui.notification_show(f"Ungültiger Wert für {input_id}: {raw}", type="warning", duration=4)
            return
        cfg_state.set(_deep_set(cfg_state(), path, val))
        unsaved_changes.set(True)

for _id, (path, cast) in BINDINGS.items():
    _register_binding(_id, path, cast)

# Helper function to attach a numeric guard to a DataGrid render
def attach_numeric_guard(
    table_render,
    *,
    schedule_name: str, # name of schedule for error messages
    min_value=0.0,
    max_value=1.0,
    decimals=2,
    toast=True,  # show toast notification on invalid input
    keep_last=5,
):
    """
    Attach a guard to a DataGrid render to restrict the input values to the following range.
    - only numeric values in the range [min_value, max_value] are accepted
    - values are rounded to the specified number of decimals
    - if toast is True, a notification is shown for invalid values
    Gives a reactive.Values back, which contains the last error message (for inline warning display)
    """
    last_error = reactive.Value("") # last error message
    error_log = reactive.Value([])  # keep a log of the last errors


    @table_render.set_patches_fn
    def _validate(*, patches: list[render.CellPatch]) -> list[render.CellPatch]:
        accepted: list[render.CellPatch] = []
        msg = ""

        for p in patches:
            # extract value and cell info from patch (robust to different key namings)
            col = (
                p.get("column_key")     # preferred
                or p.get("columnId")    # fallback
                or p.get("col")         # fallback
            )
            # inidices as further fallback (if only index is given)
            if col is None and "column_index" in p:
                try:
                    # read the current column name from the grid
                    col_idx = int(p["column_index"])
                    col = list(table_render.data_patched().columns)[col_idx]
                except Exception:
                    col = "unknown"

            # row info
            row = (
                p.get("row_key")        # preferred
                or p.get("row")         # fallback
                or schedule_name        # fallback to schedule name if no row info is given (e.g. only one row present)
            )

            cell_label = f"{row}@{col}"

            # validate the value
            raw = str(p["value"]).strip().replace(",", ".")
            try:
                v = float(raw)
            except ValueError:
                msg = f"{schedule_name} - cell {cell_label}:Invalid number, please enter a numeric value between {min_value} and {max_value}."
                continue     # skip invalid values

            if not (min_value <= v <= max_value):
                msg = f"{schedule_name} - cell {cell_label}:Value {v} out of range, please enter a value between {min_value} and {max_value}."
                continue    # skip values outside the range

            p["value"] = round(v, decimals) # round to specified decimal places
            accepted.append(p) # only accept valid values

        # feedback
        last_error.set(msg)
        if msg:
            # keep a log of the last errors
            log = error_log.get() or []
            error_log.set(([msg] + log)[:keep_last]) # keep only the last n errors
        if msg and toast:
            ui.notification_show(msg, type="error", duration=4)
            
        return accepted
    
    return last_error, error_log


summary_A = reactive.Value(None)
summary_B = reactive.Value(None)
timeseries_A = reactive.Value(None)
timeseries_B = reactive.Value(None)
measurements = reactive.Value(None)
monthly_timeseries_A = reactive.Value(None)
monthly_timeseries_B = reactive.Value(None)


@reactive.effect
def _load_initial_results():
    try:
        summary_A.set(facade_A.get_summary(PROJECT_ID_VAR_A, "A"))
        summary_B.set(facade_B.get_summary(PROJECT_ID_VAR_B, "B"))
        timeseries_A.set(facade_A.get_timeseries(PROJECT_ID_VAR_A, "A"))
        timeseries_B.set(facade_B.get_timeseries(PROJECT_ID_VAR_B, "B"))
        measurements.set(facade_A.get_measurements())
        monthly_timeseries_A.set(facade_A.get_monthly_timeseries(PROJECT_ID_VAR_A, "A"))
        monthly_timeseries_B.set(facade_B.get_monthly_timeseries(PROJECT_ID_VAR_B, "B"))
    except RuntimeError:
        pass

summary_all = reactive.Value(None)

@reactive.effect
def _compute_combined_summary():
    a = summary_A()
    b = summary_B()

    if a is None and b is None:
        summary_all.set(None)
        return
    
    dfs = []
    # Variant A
    if isinstance(a, pd.DataFrame) and not a.empty:
        da = a.copy()
        if 'variant_id' not in da.columns:
            # check that all variant values are 'A'
            if not (da['variant'] == 'A').all():
                # preserve original vlues and force variant_id to 'A'
                da["source_variant"] = da["variant_id"]  
                da["variant_id"] = "A"
                ui.notification_show("Warnung: Summary A enthält unerwartete variant-Werte.", type="warning", duration=6)
        else:
            # if column missing, set it to 'A'
            da["variant_id"] = "A"
        dfs.append(da)
    # Variant B
    if isinstance(b, pd.DataFrame) and not b.empty:
        db = b.copy()
        if 'variant_id' not in db.columns:
            # check that all variant values are 'B'
            if not (db['variant'] == 'B').all():
                # preserve original vlues and force variant_id to 'B'
                db["source_variant"] = db["variant_id"]  
                db["variant_id"] = "B"
                ui.notification_show("Warnung: Summary B enthält unerwartete variant-Werte.", type="warning", duration=6)
        else:
            # if column missing, set it to 'B'
            db["variant_id"] = "B"
        dfs.append(db)
        
    if not dfs:
        summary_all.set(pd.DataFrame())
        return

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.drop_duplicates().reset_index(drop=True)
    summary_all.set(combined)
    

timeseries_all = reactive.Value(None)

@reactive.effect
def _compute_combined_timeseries():
    a = timeseries_A()
    b = timeseries_B()

    if a is None and b is None:
        timeseries_all.set(None)
        return
    
    dfs = []
    # Variant A
    if isinstance(a, pd.DataFrame) and not a.empty:
        da = a.copy()
        if 'variant_id' not in da.columns:
            # check that all variant values are 'A'
            if not (da['variant'] == 'A').all():
                # preserve original vlues and force variant_id to 'A'
                da["source_variant"] = da["variant_id"]  
                da["variant_id"] = "A"
                ui.notification_show("Warnung: Summary A enthält unerwartete variant-Werte.", type="warning", duration=6)
        else:
            # if column missing, set it to 'A'
            da["variant_id"] = "A"
        dfs.append(da)
    # Variant B
    if isinstance(b, pd.DataFrame) and not b.empty:
        db = b.copy()
        if 'variant_id' not in db.columns:
            # check that all variant values are 'B'
            if not (db['variant'] == 'B').all():
                # preserve original vlues and force variant_id to 'B'
                db["source_variant"] = db["variant_id"]  
                db["variant_id"] = "B"
                ui.notification_show("Warnung: Summary B enthält unerwartete variant-Werte.", type="warning", duration=6)
        else:
            # if column missing, set it to 'B'
            db["variant_id"] = "B"
        dfs.append(db)

    if not dfs:
        timeseries_all.set(pd.DataFrame())
        return
    
    combined = pd.concat(dfs, axis=0)
    combined = combined.sort_index()
    timeseries_all.set(combined)

timeseries_wide = reactive.Value(None)

@reactive.effect
def _compute_timeseries_wide():
    df = timeseries_all()
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        timeseries_wide.set(pd.DataFrame())
        return
    
    # transform from long to wide format
    wide = df.pivot(
        index="datetime",
        columns="variant_id",
        values=[
            "temp_air_room",
            "temp_outdoor_air",
            "heating_power",
            "cooling_power",
        ],
    )

    # flatten multiindex columns
    wide.columns = [f"{var}_{variant}" for (var, variant) in wide.columns]

    wide = wide.sort_index()
    wide = wide.reset_index()

    timeseries_wide.set(wide)

monthly_timeseries_all = reactive.Value(None)

@reactive.effect
def _compute_monthly_combined_timeseries():
    a = monthly_timeseries_A()
    b = monthly_timeseries_B()

    if a is None and b is None:
        monthly_timeseries_all.set(None)
        return
    
    dfs = []
    # Variant A
    if isinstance(a, pd.DataFrame) and not a.empty:
        da = a.copy()
        if 'variant_id' not in da.columns:
            da["variant_id"] = "A"
        dfs.append(da)
    # Variant B
    if isinstance(b, pd.DataFrame) and not b.empty:
        db = b.copy()
        if 'variant_id' not in db.columns:
            db["variant_id"] = "B"
        dfs.append(db)

    if not dfs:
        monthly_timeseries_all.set(pd.DataFrame())
        return
    
    combined = pd.concat(dfs, axis=0)
    combined = combined.sort_index()
    monthly_timeseries_all.set(combined)

monthly_timeseries_wide = reactive.Value(None)

@reactive.effect
def _compute_monthly_timeseries_wide():
    df = monthly_timeseries_all()
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        monthly_timeseries_wide.set(pd.DataFrame())
        return
    
    # transform from long to wide format
    wide = df.pivot(
        index="datetime",
        columns="variant_id",
        values=[
            "heating_energy_MWh",
            "cooling_energy_MWh",
        ],
    )

    # flatten multiindex columns
    wide.columns = [f"{var}_{variant}" for (var, variant) in wide.columns]

    wide = wide.sort_index()
    wide = wide.reset_index()

    monthly_timeseries_wide.set(wide)

def get_summary_values(summary_df, *, variant: str, end_use: str, metric: str, default="-"):
    """
    Funktion for extracting a single summary value from the summary DataFrame.
    Args:
        summary_df (pd.DataFrame): The summary DataFrame containing the results.
        variant (str): The variant ID to filter by (e.g., "A" or "B").
        end_use (str): The end use to filter by (e.g., "heating", "cooling", "temperature").
        metric (str): The metric to filter by (e.g., "energy_year", "power_max", "overheating_hours").
        default (str, optional): The default value to return if no matching entry is found. Defaults to "-".
    """
    if summary_df is None:
        return default
    if not isinstance(summary_df, pd.DataFrame) or summary_df.empty:
        return default
    
    rows = summary_df[
        (summary_df["variant_id"] == variant) &
        (summary_df["end_use"] == end_use) &
        (summary_df["metric"] == metric)
    ]
    if rows.empty:
        return default
    
    value = rows.iloc[0]["value"]
    try:   
        return f"{float(value):.1f}"
    except Exception:
        return str(value)




# Helper: sichere Zeitachse → Millisekunden (vermeidet ns-Probleme)
def ts_ms(series_dt):
    dt = pd.to_datetime(series_dt, errors="raise").dt.tz_localize(None)
    return (dt.view("int64") // 1_000_000).astype("int64")

def ensure_datetime(col):
    s = pd.Series(col)
    if np.issubdtype(s.dtype, np.datetime64):
        return pd.to_datetime(s)  # schon ok
    if np.issubdtype(s.dtype, np.number):
        m = np.nanmax(s.astype("float64"))
        # Heuristik für Einheit
        if m > 1e15:        # ns
            unit = "ns"
        elif m > 1e12:      # ms
            unit = "ms"
        else:               # s
            unit = "s"
        return pd.to_datetime(s, unit=unit)
    # Strings etc.
    return pd.to_datetime(s, errors="coerce")


ui.page_opts(
    title="Einfache Simulationsanwendung für ein RC-Gebäudemodell",
    page_fn=partial(page_navbar, id="page"),
)

with ui.nav_panel("Simulationsresultate"):
    with ui.card():
        ui.input_action_button(
            id="button_start_simulation",
            label="Simulation starten",
            disabled=False,
        )
        
        ui.br()
        ui.br()
        
        ui.markdown("**Ergebnisse herunterladen:**")
        ui.markdown("ZIP-Datei enthält alle Ergebnisse beider Varianten: Config JSON, Rohdaten (Parquet & CSV), Zeitreihen, Zusammenfassung und Einheiten-Beschreibung")

        @reactive.effect
        @reactive.event(input.button_start_simulation)
        def on_simulation_clicked():
            ui.notification_show("Simulation gestartet", type="info", duration=4)
            facade_A.run_simulation(PROJECT_ID_VAR_A, "A")
            facade_B.run_simulation(PROJECT_ID_VAR_B, "B")

            # actualize summaries and timeseries
            summary_A.set(facade_A.get_summary(PROJECT_ID_VAR_A, "A"))
            summary_B.set(facade_B.get_summary(PROJECT_ID_VAR_B, "B"))
            timeseries_A.set(facade_A.get_timeseries(PROJECT_ID_VAR_A, "A"))
            timeseries_B.set(facade_B.get_timeseries(PROJECT_ID_VAR_B, "B"))
            monthly_timeseries_A.set(facade_A.get_monthly_timeseries(PROJECT_ID_VAR_A, "A"))
            monthly_timeseries_B.set(facade_B.get_monthly_timeseries(PROJECT_ID_VAR_B, "B"))

        
        @render.download(
            filename=lambda: f"rc_model_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip",
            media_type="application/zip",
        )
        def dl_all_results_zip():
            """Download ZIP file with results from both variants"""
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Get files from Variant A
                try:
                    zip_data_a = facade_A.download_all_results_zip("A", PROJECT_ID_VAR_A)
                    # Extract the inner zip and add all files to the main zip
                    with zipfile.ZipFile(io.BytesIO(zip_data_a), 'r') as inner_zip_a:
                        for file_info in inner_zip_a.infolist():
                            file_data = inner_zip_a.read(file_info.filename)
                            zip_file.writestr(file_info.filename, file_data)
                except Exception as e:
                    ui.notification_show(f"Fehler beim Herunterladen von Variante A: {str(e)}", type="error", duration=5)
                
                # Get files from Variant B
                try:
                    zip_data_b = facade_B.download_all_results_zip("B", PROJECT_ID_VAR_B)
                    # Extract the inner zip and add all files to the main zip
                    with zipfile.ZipFile(io.BytesIO(zip_data_b), 'r') as inner_zip_b:
                        for file_info in inner_zip_b.infolist():
                            file_data = inner_zip_b.read(file_info.filename)
                            zip_file.writestr(file_info.filename, file_data)
                except Exception as e:
                    ui.notification_show(f"Fehler beim Herunterladen von Variante B: {str(e)}", type="error", duration=5)
            
            zip_buffer.seek(0)
            yield zip_buffer.getvalue()
    # # -------------------------
    # # debuging cards DataFrames
    # # -------------------------          
    # with ui.card():
    #     ui.card_header("Debug: Summary Heizung/Kühlung Variante A")
    #     @render.data_frame
    #     def debug_summary_all():
    #         df = summary_all()
    #         if df is None:
    #             # Noch nix geladen
    #             return pd.DataFrame({"info": ["summary_all is None (noch nicht geladen)"]})
    #         if isinstance(df, pd.DataFrame) and df.empty:
    #             return pd.DataFrame({"info": ["summary_all ist ein leerer DataFrame"]})
    #         return df
        
    #     ui.card_header("Debug:Timeseries")
    #     @render.data_frame
    #     def debug_timeseries_wide():
    #         df = timeseries_wide()
    #         if df is None:
    #             # Noch nix geladen
    #             return pd.DataFrame({"info": ["timeseries_all is None (noch nicht geladen)"]})
    #         if isinstance(df, pd.DataFrame) and df.empty:
    #             return pd.DataFrame({"info": ["timeseries_all ist ein leerer DataFrame"]})
    #         return df
        
    #     ui.card_header("Debug: Monatliche Zeitreihen")
    #     @render.data_frame
    #     def monthly_timeseries_energy():
    #         df = monthly_timeseries_all()
    #         if df is None:
    #             # Noch nix geladen
    #             return pd.DataFrame({"info": ["monthly_timeseries_all is None (noch nicht geladen)"]})
    #         if isinstance(df, pd.DataFrame) and df.empty:
    #             return pd.DataFrame({"info": ["monthly_timeseries_all ist ein leerer DataFrame"]})
    #         return df
        
    #     ui.card_header("Debug: monthly_timeseries_wide")
    #     @render.data_frame
    #     def debug_monthly_timeseries_wide():
    #         df = monthly_timeseries_wide()
    #         if df is None:
    #             # Noch nix geladen
    #             return pd.DataFrame({"info": ["monthly_timeseries_wide is None (noch nicht geladen)"]})
    #         if isinstance(df, pd.DataFrame) and df.empty:
    #             return pd.DataFrame({"info": ["monthly_timeseries_wide ist ein leerer DataFrame"]})
    #         return df
        
    with ui.card():
        @render_plotly
        def plot_temperatures():
            df_temp = timeseries_wide()

            if df_temp is None or df_temp.empty:
                return go.Figure()
            
            df_temp["ts_ms"] = ts_ms(df_temp["datetime"])

            fig = px.line(
                df_temp,
                x="ts_ms",
                y=[
                    "temp_air_room_A",
                    "temp_outdoor_air_A",
                    "temp_air_room_B",
                    "temp_outdoor_air_B",
                   ],
                labels={
                    "ts_ms": "Zeit",
                    "temp_air_room": "Innenlufttemperatur [°C]",
                    "variant_id": "Variante",
                },
                ).update_xaxes(
                    type="date",
                    tickformat="%d-%m-%y %H:%M",
                    tickangle=45,
                    showgrid=True,
                ).update_layout(
                title="Temperaturverläufe",
                hovermode="x unified",
                xaxis_title="Zeit [h]",
                yaxis_title="Temperatur [°C]",
                )
            return fig

        ui.input_radio_buttons(
            id="temp_variant_selector",
            label="Variante auswählen",
            choices={
                "A": "Variante A",
                "B": "Variante B",
            },
            selected="A",
        )

        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_overheating_hours",
                width=4,
            ):
                "Überhitzungsstunden"
                @render.text
                def overheating_hour_value():
                    value = get_summary_values(summary_all(), variant=input.temp_variant_selector(), end_use="temperature", metric="overheating_hours")
                    return f"{value} h"
                
            with ui.value_box(
                id="value_box_outdoor_temp_min",
                width=4,
            ):
                "Minimale Aussentemperatur"
                @render.text
                def outdoor_temp_min_value():
                    value = get_summary_values(summary_all(), variant=input.temp_variant_selector(), end_use="temperature", metric="temp_outdoor_min")
                    return f"{value} °C"
                @render.text
                def min_outdoor_temp_timestamp():
                    ts = get_summary_values(
                        summary_all(),
                        variant=input.temp_variant_selector(),
                        end_use="temperature",
                        metric="timestamp_temp_outdoor_min",
                    )
                    return f"am {ts}" 
            
            with ui.value_box(
                id="value_box_outdoor_temp_max",
                width=4,
            ):
                "Maximale Aussentemperatur"
                @render.text
                def outdoor_temp_max_value():
                    value = get_summary_values(summary_all(), variant=input.temp_variant_selector(), end_use="temperature", metric="temp_outdoor_max")
                    return f"{value} °C"
                @render.text
                def max_outdoor_temp_timestamp():
                    ts = get_summary_values(
                        summary_all(),
                        variant=input.temp_variant_selector(),
                        end_use="temperature",
                        metric="timestamp_temp_outdoor_max",
                    )
                    return f"am {ts}"

    with ui.card():
        with ui.navset_card_tab(id="heating_cooling_tabs"):
            with ui.nav_panel("Heiz- und Kühlleistung"):
                @render_widget
                def plot_cooling_heating_power():
                    df_load = timeseries_wide()

                    # time stamp in ms
                    df_load["ts_ms"] = ts_ms(df_load["datetime"])

                    fig = px.line(
                        df_load,
                        x="ts_ms",
                        y=[
                            "cooling_power_A",
                            "heating_power_A",
                            "cooling_power_B",
                            "heating_power_B",
                            ],
                        labels={
                            "ts_ms": "Zeit", 
                            "value": "Leistung [W]",
                            "variable": "Legende",
                        },
                        ).update_xaxes(
                            type="date",
                            tickformat="%d-%m-%y %H:%M",
                            tickangle=45,
                            showgrid=True,
                    ).update_layout(
                        title="Heiz- und Kühlleistung",
                        xaxis_title="Zeit [h]",
                        yaxis_title="Leistung [W]",
                        )
                    return fig
                
            with ui.nav_panel("Heiz- und Kühlenergie"):        
                @render_widget
                def plot_coling_heating_energy():
                    df_monthly = monthly_timeseries_wide()
                    if df_monthly is None or df_monthly.empty:
                        return go.Figure()

                    # Ensure datetime is datetime type and convert to string for display
                    df_monthly["datetime"] = pd.to_datetime(df_monthly["datetime"]).dt.strftime("%Y-%m")

                    # Prepare data with heating and cooling combined
                    data = []
                    for _, row in df_monthly.iterrows():
                        month = row["datetime"]
                        data.append({"Monat": month, "Variante": "A", "Energie [MWh]": row["heating_energy_MWh_A"], "Typ": "Heizung"})
                        data.append({"Monat": month, "Variante": "B", "Energie [MWh]": row["heating_energy_MWh_B"], "Typ": "Heizung"})
                        data.append({"Monat": month, "Variante": "A", "Energie [MWh]": row["cooling_energy_MWh_A"], "Typ": "Kühlung"})
                        data.append({"Monat": month, "Variante": "B", "Energie [MWh]": row["cooling_energy_MWh_B"], "Typ": "Kühlung"})
                    
                    df_long = pd.DataFrame(data)

                    fig = px.bar(
                        df_long,
                        x="Monat",
                        y="Energie [MWh]",
                        color="Variante",
                        pattern_shape="Typ",
                        barmode="group",
                        labels={
                            "Monat": "Monat",
                            "Energie [MWh]": "Energie [MWh]",
                            "Variante": "Variante",
                        },
                    ).update_xaxes(
                        tickangle=45,
                        showgrid=True,
                    ).update_layout(
                        title="Monatlicher Heiz- und Kühlenergiebedarf",
                        xaxis_title="Monat",
                        yaxis_title="Energie [MWh]",
                        bargap=0.2,
                        bargroupgap=0.1,
                    )
                    return fig
        
        ui.input_radio_buttons(
            id="power_variant_selector",
            label="Variante auswählen",
            choices={
                "A": "Variante A",
                "B": "Variante B",
            },
            selected="A",
        )

        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_heating_demand",
                width=4,
            ):
                "Jährlicher Heizwärmebedarf"

                @render.text
                def heating_energy_value():
                    value_energy_h = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="heating", metric="energy_year")
                    return f"{value_energy_h} kWh"

            with ui.value_box(
                id="value_box_cooling_demand",
                width=4,
            ):
                "Jährlicher Kühlbedarf"

                @render.text
                def cooling_energy_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="cooling", metric="energy_year")
                    return f"{value} kWh"

            with ui.value_box(
                id="value_box_max_heating_power",
                width=4,
            ):
                "Maximale Heizleistung [W]"

                @render.text
                def max_heating_power_value():
                    value = get_summary_values(
                        summary_all(),
                        variant=input.power_variant_selector(),
                        end_use="heating",
                        metric="power_max",
                    )
                    return f"{value} kW"
                @render.text
                def max_heating_power_timestamp():
                    ts = get_summary_values(
                        summary_all(),
                        variant=input.power_variant_selector(),
                        end_use="heating",
                        metric="power_max_timestamp",
                    )
                    return f"am {ts}"


            with ui.value_box(
                id="value_box_max_cooling_power",
                width=4,
            ):
                "Maximale Kühlleistung [W]"
                @render.text
                def max_cooling_power_value():
                    value = get_summary_values(
                        summary_all(),
                        variant=input.power_variant_selector(),
                        end_use="cooling",
                        metric="power_max")
                    return f"{value} kW"
                @render.text
                def max_cooling_power_timestamp():
                    ts = get_summary_values(
                        summary_all(),
                        variant=input.power_variant_selector(),
                        end_use="cooling",
                        metric="power_max_timestamp",
                    )
                    return f"am {ts}"


            with ui.value_box(
                id="value_box_spec_heating_load",
                width=4,
            ):
                "Spezifische Heizlast [kW/m²]"
                @render.text
                def spec_heating_load_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="heating", metric="load_specific")
                    return f"{value} W/m²"

            with ui.value_box(
                id="value_box_spec_cooling_load",
                width=4,
            ):
                "Spezifische Kühllast [kW/m²]"
                @render.text
                def spec_cooling_load_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="cooling", metric="load_specific")
                    return f"{value} W/m²"
                
            with ui.value_box(
                id="value_box_spec_heating_energy",
                width=4,
            ):
                "Spezifischer Heizenergiebedarf [kWh/m²]"
                @render.text
                def spec_heating_energy_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="heating", metric="energy_specific")
                    return f"{value} kWh/m²"
            
                 
            with ui.value_box(
                id="value_box_spec_cooling_energy",
                width=4,
            ):
                "Spezifischer Kühlenergiebedarf [kWh/m²]"
                @render.text
                def spec_cooling_energy_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="cooling", metric="energy_specific")
                    return f"{value} kWh/m²"
           

            with ui.value_box(
                id="value_box_total_energy_costs_heating",
                width=4,
            ):
                "Jährliche Stromkosten Heizung"
                @render.text
                def total_energy_costs_heating_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="heating", metric="costs_year")
                    return f"{value} CHF"

            with ui.value_box(
                id="value_box_total_energy_costs_cooling",
                width=4,
            ):
                "Jährliche Stromkosten Kühlung"
                @render.text
                def total_energy_costs_cooling_value():
                    value = get_summary_values(summary_all(), variant=input.power_variant_selector(), end_use="cooling", metric="costs_year")
                    return f"{value} CHF"



    # with ui.card():

    #     @render_plotly
    #     def plot_wall_nodes_over_year():
    #         df = sim_io_mock.make_df_temperatures().copy()
    #         df["ts_ms"] = ts_ms(df["datetime"])

    #         node_cols = ["Temperatur 1. Knoten Aussenwand Nord", "Temperatur 2. Knoten Aussenwand Nord", "Temperatur 3. Knoten Aussenwand Nord", "Temperatur 4. Knoten Aussenwand Nord"]  # anpassen, falls nötig
    #         df_long = df.melt(id_vars=["ts_ms"], value_vars=node_cols,
    #                         var_name="Knoten", value_name="Temperatur [°C]")

    #         fig = (
    #             px.line(
    #                 df_long, x="ts_ms", y="Temperatur [°C]", color="Knoten",
    #                 labels={"ts_ms": "Zeit", "Knoten": "Knoten"}
    #             )
    #             .update_xaxes(type="date", tickformat="%d.%m.%Y %H:%M", tickangle=45, showgrid=True)
    #             .update_layout(
    #                 title="Temperaturverlauf in den 4 Wandknoten (Jahresverlauf)",
    #                 xaxis_title="Zeit", yaxis_title="Temperatur [°C]",
    #                 hovermode="x unified"
    #             )
    #         )
    #         return fig
        
        # # === 2) Temperatur durch die Wand (Zeit × Knoten) als Heatmap ===
        # @render_plotly
        # def plot_wall_nodes_heatmap():
        #     df = sim_io_mock.make_df_temperatures().copy()
        #     X = ts_ms(df["datetime"])                 # Zeit
        #     node_cols = ["Temperatur 1. Knoten Aussenwand Nord", "Temperatur 2. Knoten Aussenwand Nord", "Temperatur 3. Knoten Aussenwand Nord", "Temperatur 4. Knoten Aussenwand Nord"]      # von innen nach außen
        #     Z = df[node_cols].to_numpy().T            # (knoten × zeit)

        #     # Optional: echte Tiefen statt Knotenlabels (mm) – falls vorhanden:
        #     # depths_mm = [0, 50, 150, 300]
        #     # y_labels = [f"{d} mm" for d in depths_mm]
        #     y_labels = node_cols

        #     fig = go.Figure(
        #         data=go.Heatmap(z=Z, x=X, y=y_labels, colorbar=dict(title="°C"), zsmooth=False)
        #     )
        #     fig.update_xaxes(type="date", tickformat="%d.%m.%Y", tickangle=45, showgrid=False)
        #     fig.update_layout(
        #         title="Temperaturen in der Wand (Zeit × Knoten)",
        #         xaxis_title="Zeit", yaxis_title="Knoten (innen → außen)"
        #     )
        #     return fig
        
        
        # @render_plotly
        # def plot_temperature_wall_over_nodes():
        #     df = sim_io_mock.make_df_temperatures().copy()

        #     # x-axis: time in ms
        #     df["ts_ms"] = ts_ms(df["datetime"])

        #     # y-axis: wall nodes
        #     node_cols = [
        #         "Temperatur 1. Knoten Aussenwand Nord",
        #         "Temperatur 2. Knoten Aussenwand Nord",
        #         "Temperatur 3. Knoten Aussenwand Nord",
        #         "Temperatur 4. Knoten Aussenwand Nord"
        #     ]

        #     # z-values: temperatures matrix (nodes × time)
        #     Z = df[node_cols].to_numpy().T
        #     X = df["ts_ms"].to_numpy()
        #     Y = node_cols

        #     fig = go.Figure(
        #         data=go.Heatmap(
        #             x=X,
        #             y=Y,
        #             z=Z,
        #             colorbar=dict(title="Temperatur [°C]"),
        #             zsmooth=False, # True = smoothed, False = original values
        #         )
        #     )

        #     fig.update_xaxes(
        #         type="date",
        #         tickformat="%d-%m %H:%M",
        #         tickangle=45,
        #         showgrid=False,
        #         title_text="Zeit",
        #     )

        #     fig.update_yaxes(
        #         categoryorder="array",
        #         categoryarray=Y,
        #         title_text="Knoten",
        #     )
        #     fig.update_layout(
        #         title="Temperaturverlauf in den Wandknoten (Zeit x Knoten)",
        #         margin=dict(l=0, r=0, b=0, t=40),
        #     )
        #     fig.update_traces(
        #         hovertemplate="Zeit: %{x|%d-%m %H:%M}<br>Knoten: %{y}<br>Temperatur: %{z} °C<extra></extra>"
        #     )
        #     return fig

        # @render_plotly
        # def plot_wall_3d_surface():
        #     df = sim_io_mock.make_df_temperatures().copy()
        #     df["datetime"] = pd.to_datetime(df["datetime"], errors="raise").dt.tz_localize(None)
        #     df = df.sort_values("datetime")

        #     node_cols = [
        #         "Temperatur 1. Knoten Aussenwand Nord",
        #         "Temperatur 2. Knoten Aussenwand Nord",
        #         "Temperatur 3. Knoten Aussenwand Nord",
        #         "Temperatur 4. Knoten Aussenwand Nord"
        #     ]

        #     # node_cols_rev = node_cols[::-1]  # reverse for better visualization (innenseite unten)

        #     # x as time in ms, format ticks as datetime later
        #     X_num = ts_ms(df["datetime"]).to_numpy()  # Zeit in ms
        #     Y_idx = np.arange(len(node_cols))    # Knotenindex [0, 1, 2, 3]
        #     Z = df[node_cols].to_numpy()         # shape: (n_time × n_knoten)

        #     # make meshgrid for surface
        #     Xgrid, Ygrid = np.meshgrid(X_num, Y_idx, indexing="ij")  # shape: (n_time × n_knoten)
        #     Zgrid = Z                                     # shape: (n_time × n_knoten)

        #     start = pd.Timestamp(df["datetime"].dt.year.min(), 1, 1)
        #     end = pd.Timestamp(df["datetime"].dt.year.max(), 12, 31, 23, 59, 59)
            
        #     x_ticks_dt = pd.date_range(start, end, freq="MS")
        #     x_ticksvals =(x_ticks_dt.view("int64") // 1_000_000).astype("int64")
        #     x_ticktext = [d.strftime("%b") for d in x_ticks_dt]

        #     fig = go.Figure(data=[
        #         go.Surface(
        #             x=Xgrid,
        #             y=Ygrid,
        #             z=Zgrid,
        #             colorscale="RdYlBu_r",
        #             colorbar=dict(title="Temperatur [°C]"),
        #             showscale=True,
        #         )
        #     ])
        #     fig.update_layout(
        #         title="3D-Temperaturfeld in der Wand (Zeit × Knoten × Temperatur)",
        #         scene=dict(
        #             xaxis=dict(
        #                 title="Zeit",
        #                 tickmode="array",
        #                 tickvals=x_ticksvals,
        #                 ticktext=x_ticktext,
        #                 showspikes=False,
        #             ),
        #             yaxis=dict(
        #                 title="Knoten",
        #                 tickmode="array",
        #                 tickvals=Y_idx,
        #                 ticktext=node_cols,
        #                 showspikes=False,
        #             ),
        #             zaxis=dict(
        #                 title="Temperatur [°C]",
        #                 showspikes=False,
        #             ),
        #         ),
        #         margin=dict(l=0, r=0, b=0, t=40),
        #     )
        #     return fig
        


    # with ui.card():
    #     @render_widget
    #     def plot_electricity_consumption():
    #         fig = px.line(
    #             df_results[['lighting_electricity', 'equipment_electricity']],
    #             color_discrete_sequence=["orange", "red"]
    #             ).update_layout(
    #                 title="Stromverbrauch",
    #                 xaxis_title="Zeit [h]",
    #                 yaxis_title="Leistung [W]",
    #             )
    #         return fig    
        
    #     with ui.layout_column_wrap():
    #         with ui.value_box(
    #             id="value_box_total_electricity",
    #             value="8901",
    #             width=4,
    #         ):
    #             "Jährlicher Stromverbrauch [kWh]"

    #         with ui.value_box(
    #             id_="value_box_energy_costs_electricity",
    #             value="123.45",
    #             width=4,
    #         ):
    #             "Jährliche Stromkosten Beleuchtung und Geräte [CHF]"
    #         with ui.value_box(
    #             id="value_box_energy_costs_heating_cooling",
    #             value="67.89",
    #             width=4,
    #         ):
    #             "Jährliche Stromkosten Heizung und Kühlung [CHF]"
                
    with ui.card():
        ui.card_header("CO2-Emissionen")
        with ui.card():
            ui.card_header("Variante A")
            with ui.layout_column_wrap():
                with ui.value_box(
                    id="value_box_co2_emissions_heating_A",
                    width=4,
                ):
                    "Jährliche CO2-Emissionen Heizung [kg CO2]"
                    @render.text
                    def co2_emissions_heating_value_A():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_A, end_use="heating", metric="co2_year")
                        return f"{value} kg CO2"

                with ui.value_box(
                    id="value_box_co2_emissions_cooling_A",
                    width=4,
                ):
                    "Jährliche CO2-Emissionen Kühlung [kg CO2]"
                    @render.text
                    def co2_emissions_cooling_value_A():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_A, end_use="cooling", metric="co2_year")
                        return f"{value} kg CO2"
                    
                with ui.value_box(
                    id="value_box_total_co2_emissions_A",
                    width=4,
                ):
                    "Gesamte jährliche CO2-Emissionen [kg CO2]"
                    @render.text
                    def total_co2_emissions_value_A():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_A, end_use="total", metric="co2_total_year")
                        return f"{value} kg CO2"
        
        with ui.card():
            ui.card_header("Variante B")
            with ui.layout_column_wrap():
                with ui.value_box(
                    id="value_box_co2_emissions_heating_B",
                    width=4,
                ):
                    "Jährliche CO2-Emissionen Heizung [kg CO2]"
                    @render.text
                    def co2_emissions_heating_value_B():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_B, end_use="heating", metric="co2_year")
                        return f"{value} kg CO2"

                with ui.value_box(
                    id="value_box_co2_emissions_cooling_B",
                    width=4,
                ):
                    "Jährliche CO2-Emissionen Kühlung [kg CO2]"
                    @render.text
                    def co2_emissions_cooling_value_B():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_B, end_use="cooling", metric="co2_year")
                        return f"{value} kg CO2"
                    
                with ui.value_box(
                    id="value_box_total_co2_emissions_B",
                    width=4,
                ):
                    "Gesamte jährliche CO2-Emissionen [kg CO2]"
                    @render.text
                    def total_co2_emissions_value_B():
                        value = get_summary_values(summary_all(), variant=VARIANT_ID_B, end_use="total", metric="co2_total_year")
                        return f"{value} kg CO2"



with ui.nav_panel("Vergleich mit Messdaten"):
    with ui.card():
        ui.card_header("Einlesen von Messtdaten")
        ui.input_file(
            id="file_input_measured_data",
            label="Wählen Sie eine Datei mit Messtdaten aus",
            accept=[".csv"],
        )
        ui.input_action_button(
            id="button_load_measured_data",
            label="Messtdaten laden",
            disabled=False,
        )
        @render.text
        def measurement_file_properties():
            return input.file_input_measured_data()

        @reactive.effect
        @reactive.event(input.button_load_measured_data)
        def on_load_measure_clicked():
            file_info = input.file_input_measured_data()
            if file_info:
                info = file_info[0]
                path = info["datapath"]
                original_name = info["name"]
                try:
                    facade_A.update_measurement_file(path, original_name)
                    ui.notification_show(f"Messdaten '{original_name}' erfolgreich hochgeladen.", type="success", duration=4)
                except Exception as e: 
                    ui.notification_show(F"Fehler beim hochladen der Messdaten: {e}", type="error", duration=6)
    
    with ui.card():
        @render.data_frame
        def measurements_df():
            df = measurements()
            if df is None:
                return pd.DataFrame({"info:"["measurements ist None (noch nicht geladen)"]})
            if isinstance(df, pd.DataFrame) and df.empty:
                return pd.DataFrame({"info:" ["measurements ist ein leerer DataFrame"]})
            return df
        
        @render_plotly
        def plot_measurements():
            df = measurements()
            if df is None:
                return go.Figure()
            fig = px.line(
                df,
                x="Unnamed: 0",
                y=[
                    "Raumtemperatur S235",
                    "Raumtemperatur N235"
                ]
            )
            return fig
# ===================================================================
# region: Settings Panel
# ===================================================================
with ui.nav_panel("Einstellungen"):
    ui.input_action_button(
        id="button_save_settings",
        label=" Speichern",
        disabled=False,
    )
    def _extract_schedule(df, row):
        # helper to extract schedule row as list of floats
        return [float(x) for x in df.loc[row].tolist()]
    
    @reactive.effect
    @reactive.event(input.button_save_settings)
    def on_save_clicked():
        # temp for debugging
        ui.notification_show("Speichern der Einstellungen...", type="info", duration=2)
        import traceback
        try:


            # # Extract schedules from data tables
            # occupancy_df = table_occupancy.data_patched().astype(float)
            # lighting_df = table_lighting.data_patched().astype(float)
            # equipment_df = table_equipment.data_patched().astype(float)
            cur = cfg_state()

            occ = _safe_grid_row_or_cfg(
                table_occupancy,
                "Occupancy",
                cur,
                "thermal_properties.schedules.occupancy_schedule",)
            lig = _safe_grid_row_or_cfg(
                table_lighting,
                "Lighting",
                cur,
                "thermal_properties.schedules.lighting_schedule",)
            eqp = _safe_grid_row_or_cfg(
                table_equipment,
                "Equipment",
                cur,
                "thermal_properties.schedules.equipment_schedule",)
            

            # Update cfg_state with new schedules
            cur = _deep_set(cur, "thermal_properties.schedules.occupancy_schedule", occ)
            cur = _deep_set(cur, "thermal_properties.schedules.lighting_schedule", lig)
            cur = _deep_set(cur, "thermal_properties.schedules.equipment_schedule", eqp)
            cfg_state.set(cur)

            # Save current variant
            current_variant = active_variant()
            current_cfg = cfg_state()

            if current_variant == "A":
                ok, msg = facade_A.save_config(PROJECT_ID_VAR_A, current_cfg)
                if ok:
                    global cfg_A
                    cfg_A = copy.deepcopy(current_cfg)

                    # safe weather file if uploaded
                    file_info = input.input_weather_file()
                    if file_info:
                        info = file_info[0]
                        temp_path = info["datapath"]
                        original_name = info["name"]

                        try:
                            facade_A.update_weather_file(temp_path, original_name)
                            ui.notification_show(f"Wetterdatei '{original_name}' erfolgreich hochgeladen.", type="success", duration=4)
                        except Exception as e:
                            ui.notification_show(f"Fehler beim Hochladen der Wetterdatei für Variante {current_variant}: {e}", type="error", duration=6)
                else:
                    ui.notification_show(f"Fehler beim Speichern von Variante A: {msg}", type="error", duration=6)
                    return
            else:
                ok, msg = facade_B.save_config(PROJECT_ID_VAR_B, current_cfg)
                if ok:
                    global cfg_B
                    cfg_B = copy.deepcopy(current_cfg)
                    
                    # safe weather file if uploaded
                    file_info = input.input_weather_file()
                    if file_info:
                        info = file_info[0]
                        temp_path = info["datapath"]
                        original_name = info["name"]

                        try:
                            facade_B.update_weather_file(temp_path, original_name)
                            ui.notification_show(f"Wetterdatei '{original_name}' erfolgreich hochgeladen.", type="success", duration=4)
                        except Exception as e:
                            ui.notification_show(f"Fehler beim Hochladen der Wetterdatei für Variante {current_variant}: {e}", type="error", duration=6)

                else:
                    ui.notification_show(f"Fehler beim Speichern von Variante B: {msg}", type="error", duration=6)
                    return




            unsaved_changes.set(False)
            ui.notification_show(f"Einstellungen für Variante {current_variant} erfolgreich gespeichert.", type="success", duration=4)
        except Exception as e:
            tb = traceback.format_exc(limit=3)
            ui.notification_show(f"Fehler beim Speichern der Einstellungen: {e}\n{tb}", type="error", duration=10)

    ui.input_radio_buttons(
        id="radio_variant_selection",
        label="Variante auswählen",
        choices={
            "A": "Variante A",
            "B": "Variante B",
        },
        selected="A"
    )
    @reactive.effect
    @reactive.event(input.radio_variant_selection)
    def on_variant_change():
        new_variant = input.radio_variant_selection()   # "A" or "B"

        # warning if unsaved changes
        if unsaved_changes() is True:
            ui.notification_show(
                "Warnung: Es gibt ungespeicherte Änderungen! Bitte speichern Sie diese, bevor Sie die Variante wechseln.",
                type="warning",
                duration=6
            )

        # Set working state from saved source
        if new_variant == "A":
            cfg_state.set(copy.deepcopy(cfg_A))
        else:
            cfg_state.set(copy.deepcopy(cfg_B))
        active_variant.set(new_variant)
        unsaved_changes.set(False)  # reset unsaved changes flag
        
        # 
        for _id, (path, cast) in BINDINGS.items():
            try:
                val = _deep_get(cfg_state(), path)
                ui.update_text(_id, value=str(val))
            except Exception:
                pass  # skipp fields that cannot be updated

        cur_cfg = cfg_state()
        schedule_occupancy.set(_schedule_df_from_cfg(cur_cfg, 'occupancy_schedule'))
        schedule_lighting.set(_schedule_df_from_cfg(cur_cfg, 'lighting_schedule'))
        schedule_equipment.set(_schedule_df_from_cfg(cur_cfg, 'equipment_schedule'))

        _push_inputs_from_cfg()
        try:
            ui.update_switch(
                "enable_cooling",
                value=bool(_deep_get(cfg_state(), "simulation_parameters.enable_cooling.value"))
            )
        except Exception:
            pass  # skip if cannot be updated    
            
        _refresh_schedules_from_cfg()


    with ui.navset_pill_list(id="tab"):
        
        # Basic Settings tab
        with ui.nav_panel("Grundeinstellungen"):
            with ui.card():
                ui.card_header("Sollwerte für Heizen und Kühlen")
                ui.input_text(
                    id="heating_setpoint",
                    label="Heizsollwert [°C]",
                    value=cfg0['simulation_parameters']['heating_setpoint']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="cooling_setpoint",
                    label="Kühlsollwert [°C]",
                    value=cfg0['simulation_parameters']['cooling_setpoint']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_switch(
                    id="enable_cooling",
                    label="Kühlung aktivieren",
                    value=cfg0['simulation_parameters']['enable_cooling']['value'],
                )
            with ui.card():
                ui.card_header("Primärenergiefaktoren")

            with ui.card():
                ui.card_header("Co2-Emissionsfaktoren")
                ui.input_text(
                    id="Co2_emission_factor_heating",
                    label="CO2-Emissionsfaktor Heizen [kg CO2/kWh]",
                    value=cfg0['Co2_emission_factors']['heating']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="Co2_emission_factor_cooling",
                    label="CO2-Emissionsfaktor Kühlen [kg CO2/kWh]",
                    value=cfg0['Co2_emission_factors']['cooling']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )

            with ui.card():
                ui.card_header("Ecopoints Faktoren")
            
            with ui.card():
                ui.card_header("Energiekosten")
                # ui.input_text(
                #     id="electricity_price",
                #     label="Strompreis [CHF/kWh]",
                #     value=cfg0['economic_parameters']['electricity_price']['expression'],
                #     width="600px",
                #     placeholder="Geben Sie eine Zahl ein",
                # )
                ui.input_text(
                    id="heating_price",
                    label="Preis Heizen [CHF/kWh]",
                    value=cfg0['economic_parameters']['heating_price']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="cooling_price",
                    label="Preis Kühlen [CHF/kWh]",
                    value=cfg0['economic_parameters']['cooling_price']['expression'],
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
        
        # # Advanced Settings tab
        # with ui.nav_menu("erweiterte Einstellungen"):

            
        with ui.nav_panel("Gebäudeeigenschaften"):

            with ui.accordion(id="acc", open="Gebäudegeometrie"):
                with ui.accordion_panel("Gebäudegeometrie"):
                    with ui.card():
                        ui.card_header("Unbeschattete Verglasungsflächen")
                        ui.input_text(
                            id="unshaded_glazing_area_n",
                            label="Unbeschattete Verglasungsfläche (Nord) [m²]",
                            value=cfg0['building_geometry']['windows']['north']['unshaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                            update_on="blur",
                        )

                        ui.input_text(
                            id="unshaded_glazing_area_e",
                            label="Unbeschattete Verglasungsfläche (Ost) [m²]",
                            value=cfg0['building_geometry']['windows']['east']['unshaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )

                        ui.input_text(
                            id="unshaded_glazing_area_s",
                            label="Unbeschattete Verglasungsfläche (Süd) [m²]",
                            value=cfg0['building_geometry']['windows']['south']['unshaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )

                        ui.input_text(
                            id="unshaded_glazing_area_w",
                            label="Unbeschattete Verglasungsfläche (West) [m²]",
                            value=cfg0['building_geometry']['windows']['west']['unshaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )


                    with ui.card():
                        ui.card_header("Beschattete Verglasungsflächen")
                        ui.input_text(
                            id="shaded_glazing_area_n",
                            label="Beschattete Verglasungsfläche (Nord) [m²]",
                            value=cfg0['building_geometry']['windows']['north']['shaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_glazing_area_e",
                            label="Beschattete Verglasungsfläche (Ost) [m²]",
                            value=cfg0['building_geometry']['windows']['east']['shaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_glazing_area_s",
                            label="Beschattete Verglasungsfläche (Süd) [m²]",
                            value=cfg0['building_geometry']['windows']['south']['shaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_glazing_area_w",
                            label="Beschattete Verglasungsfläche (West) [m²]",
                            value=cfg0['building_geometry']['windows']['west']['shaded_glazing_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        
                    with ui.card():
                        ui.card_header("Unbeschattete Rahmenflächen")
                        ui.input_text(
                            id="unshaded_frame_area_n",
                            label="Unbeschattete Rahmenfläche (Nord) [m²]",
                            value=cfg0['building_geometry']['windows']['north']['unshaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="unshaded_frame_area_e",
                            label="Unbeschattete Rahmenfläche (Ost) [m²]",
                            value=cfg0['building_geometry']['windows']['east']['unshaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="unshaded_frame_area_s",
                            label="Unbeschattete Rahmenfläche (Süd) [m²]",
                            value=cfg0['building_geometry']['windows']['south']['unshaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="unshaded_frame_area_w",
                            label="Unbeschattete Rahmenfläche (West) [m²]",
                            value=cfg0['building_geometry']['windows']['west']['unshaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                    
                    with ui.card():
                        ui.card_header("Beschattete Rahmenflächen")
                        ui.input_text(
                            id="shaded_frame_area_n",
                            label="Beschattete Rahmenfläche (Nord) [m²]",
                            value=cfg0['building_geometry']['windows']['north']['shaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_frame_area_e",
                            label="Beschattete Rahmenfläche (Ost) [m²]",
                            value=cfg0['building_geometry']['windows']['east']['shaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_frame_area_s",
                            label="Beschattete Rahmenfläche (Süd) [m²]",
                            value=cfg0['building_geometry']['windows']['south']['shaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="shaded_frame_area_w",
                            label="Beschattete Rahmenfläche (West) [m²]",
                            value=cfg0['building_geometry']['windows']['west']['shaded_frame_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                    
                    with ui.card():
                        ui.card_header("Wandflächen (inkl. Verglasungen)")
                        ui.input_text(
                            id="wall_area_n",
                            label="Wandfläche (Nord) [m²]",
                            value=cfg0['building_geometry']['enclosure']['outside_wall_areas']['north']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="wall_area_e",
                            label="Wandfläche (Ost) [m²]",
                            value=cfg0['building_geometry']['enclosure']['outside_wall_areas']['east']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="wall_area_s",
                            label="Wandfläche (Süd) [m²]",
                            value=cfg0['building_geometry']['enclosure']['outside_wall_areas']['south']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="wall_area_w",
                            label="Wandfläche (West) [m²]",
                            value=cfg0['building_geometry']['enclosure']['outside_wall_areas']['west']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                    with ui.card():
                        ui.card_header("Andere Gebäudeflächen und Abmessungen")
                        ui.input_text(
                            id="ebf_area",
                            label="Energiebezugsfläche (EBF) [m²]",
                            value=cfg0['building_geometry']['enclosure']['ebf_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="roof_area",
                            label="Dachfläche [m²]",
                            value=cfg0['building_geometry']['enclosure']['roof_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="floor_area",
                            label="Bodenfläche [m²]",
                            value=cfg0['building_geometry']['enclosure']['floor_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="int_wall_area",
                            label="Innenwandflächen (beide seiten sollen vorhanden sein) [m²]",
                            value=cfg0["building_geometry"]['enclosure']['int_wall_area']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="int_ceiling_area",
                            label="Innendeckenfläche (beide seiten sollen vorhanden sein) [m²]",
                            value=cfg0["building_geometry"]["enclosure"]["int_ceiling_area"]["expression"],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="wall_against_unheated_area",
                            label="Wandfläche gegen unbeheizte Zonen [m²]",
                            value=cfg0["building_geometry"]["enclosure"]["wall_to_unheated_area"]["expression"],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                        ui.input_text(
                            id="building_height",
                            label="Höhe des Gebäudes [m]",
                            value=cfg0['building_geometry']['building_height']['expression'],
                            width="600px",
                            placeholder="Geben Sie eine Zahl ein",
                        )
                    # with ui.card():
                    #     with ui.layout_column_wrap():
                    #         with ui.value_box(
                    #             id="value_box_total_outerwall_area",
                    #             value="1234",
                    #             width=6,
                    #         ):
                    #             "Gesammte Aussenwandfläche (Verglasung) [m²]"
                    #         with ui.value_box(
                    #             id="value_box_total_glazing_area",
                    #             value="567",
                    #             width=6,
                    #         ):
                    #             "Gesammte Verglasungsfläche [m²]"
                    #         with ui.value_box(
                    #             id="value_box_window_to_wall_ratio",
                    #             value="89",
                    #             width=6,
                    #         ):
                    #             "Fenster-zu-Wand-Verhältnis [%]"
                    #         with ui.value_box(
                    #             id="value_box_window_shadowing_ratio",
                    #             value="90",
                    #             width=6,
                    #         ):
                    #             "Fenster-Beschattungsverhältnis [%]"
                with ui.accordion_panel("Thermische Eigenschaften"):
                    # input fields for thermal properties
                    ui.input_text(
                        id="glazing_u_value",
                        label="U-Wert der Verglasung [W/m²K]",
                        value=cfg0['thermal_properties']['windows']['u_value_glazing']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="glazing_g_value",
                        label="g-Wert der Verglasung (Anteil der solaren Strahlung, welche in das Gebäude gelangt) []",
                        value=cfg0['thermal_properties']['windows']['g_value_glazing']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shading_g_value_reduction_factor",
                        label="Reduktionsfaktor des g-Werts aufgrund von Beschattung (z.B. Balkone) []",
                        value=cfg0['thermal_properties']['windows']['shading_g_value_reduction_factor']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="frame_u_value",
                        label="U-Wert des Fensterrahmens [W/m²K]",
                        value=cfg0['thermal_properties']['windows']['u_value_frame']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_against_unheated_u_value",
                        label="U-Wert der Wand gegen unbeheizte Zonen [W/m²K]",
                        value=cfg0['thermal_properties']['enclosure']['u_value_wall_against_unheated']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_inside_lambda",
                        label="Wärmeleitfähigkeit der inneren Schicht der Wand [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['lambda_wall_inside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_inside_lambda",
                        label="Wärmeleitfähigkeit der inneren Schicht des Daches [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['lambda_roof_inside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_inside_lambda",
                        label="Wärmeleitfähigkeit der inneren Schicht des Fußbodens [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['lambda_floor_inside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_inside_capacity_density",
                        label="Speicherdichte der inneren Schicht der Wand (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['capacity_density_wall_inside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_inside_capacity_density",
                        label="Speicherdichte der inneren Schicht des Daches (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['capacity_density_roof_inside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_inside_capacity_density",
                        label="Speicherdichte der inneren Schicht des Fußbodens (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['inside_layer']['capacity_density_floor_inside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_outside_lambda",
                        label="Wärmeleitfähigkeit der äusseren Schicht der Wand [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['lambda_wall_outside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_outside_lambda",
                        label="Wärmeleitfähigkeit der äusseren Schicht des Daches [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['lambda_roof_outside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_outside_lambda",
                        label="Wärmeleitfähigkeit der äusseren Schicht des Fußbodens [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['lambda_floor_outside']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_outside_capacity_density",
                        label="Kapazitätsdichte der äusseren Schicht der Wand (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['capacity_density_wall_outside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_outside_capacity_density",
                        label="Kapazitätsdichte der äusseren Schicht des Daches (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['capacity_density_roof_outside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_outside_capacity_density",
                        label="Kapazitätsdichte der äusseren Schicht des Fussbodens (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['outside_layer']['capacity_density_floor_outside']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_wall_lambda",
                        label="Wärmeleitfähigkeit der Innenwand [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['internal_walls_ceiling']['lambda_internal_wall']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_ceiling_lambda",
                        label="Wärmeleitfähigkeit der Innendecke [W/mK]",
                        value=cfg0['thermal_properties']['enclosure']['internal_walls_ceiling']['lambda_internal_ceiling']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_wall_capacity_density",
                        label="Kapazitätsdichte der Innenwand (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['internal_walls_ceiling']['capacity_density_internal_wall']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_ceiling_capacity_density",
                        label="Kapazitätsdichte der Innendecke (rho * c) [J/m³K]",
                        value=cfg0['thermal_properties']['enclosure']['internal_walls_ceiling']['capacity_density_internal_ceiling']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                with ui.accordion_panel("Dicken der Bauteilschichten"):
                    # input fields for thicknesses of building components
                    ui.input_text(
                        id="wall_inside_thickness",
                        label="Dicke der inneren Schicht der Wand (Ziegel) [m]",
                        value=cfg0["building_geometry"]['enclosure']['outside_wall_areas']['thickness']['inside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_outside_thickness",
                        label="Dicke der äusseren Schicht der Wand (Dämmung) [m]",
                        value=cfg0["building_geometry"]['enclosure']['outside_wall_areas']['thickness']['outside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_inside_thickness",
                        label="Dicke der inneren Schicht des Daches (Beton) [m]",
                        value=cfg0["building_geometry"]['enclosure']['roof_area']['thickness']['inside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="roof_outside_thickness",
                        label="Dicke der äusseren Schicht des Daches (Dämmung) [m]",
                        value=cfg0["building_geometry"]['enclosure']['roof_area']['thickness']['outside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_inside_thickness",
                        label="Dicke der inneren Schicht des Fussbodens (Beton) [m]",
                        value=cfg0["building_geometry"]['enclosure']['floor_area']['thickness']['inside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_outside_thickness",
                        label="Dicke der äusseren Schicht des Fussbodens (Dämmung) [m]",
                        value=cfg0["building_geometry"]['enclosure']['floor_area']['thickness']['outside_layer']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_wall_thickness",
                        label="Dicke der Innenwand (Gipskarton) [m]",
                        value=cfg0["building_geometry"]['enclosure']['int_wall_area']['thickness']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_ceiling_thickness",
                        label="Dicke der Innendecke (Gipskarton) [m]",
                        value=cfg0["building_geometry"]['enclosure']['int_ceiling_area']['thickness']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                with ui.accordion_panel("Gebäude thermische Parameter"):
                    #input fields for building thermal parameters
                    ui.input_text(
                        id="infiltration_rate",
                        label="Infiltrationsrate des Gebäudes [m³/s]",
                        value=cfg0["thermal_properties"]['infiltration_rate_specific']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="air_ventilation_rate",
                        label="Mechanischer Luftwechselrate des Gebäudes (angenommen, immer eingeschaltet) [m³/s]",
                        value=cfg0["thermal_properties"]['air_ventilation_rate_specific']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="heat_exchanger_efficiency",
                        label="Wirkungsgrad des Wärmetauschers im Belüftungssystem []",
                        value=cfg0["thermal_properties"]['heat_exchanger_efficiency']['expression'],
                        width=None,
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="thermal_bridges",
                        label="Wärmebrücken [W/K]",
                        value=cfg0["thermal_properties"]['thermal_bridges']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="lighting_power",
                        label="Beleuchtungsstromverbrauch [W]",
                        value=cfg0['thermal_properties']['power_input']['lighting_power_per_area']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="equipment_power",
                        label="Geräte-Stromverbrauch [W]",
                        value=cfg0['thermal_properties']['power_input']['equipment_power_per_area']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="overheating_threshold",
                        label="Temperaturgrenzwert für Überhitzung [°C]",
                        value=cfg0['simulation_parameters']['overheating_threshold']['expression'],
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
        # Settings for scheduled parameters
        with ui.nav_panel("Zeitpläne"):
            base_ui.tags.p(
                "Tragen Sie stündliche Werte zwischen 0 und 1 ein (entspricht 0–100 %). 0 = aus, 1 = volle Nutzung.",
                class_="text-muted"
            )
                
            with ui.card():
                ui.card_header("Belegungszeitplan")

                @render.data_frame
                def table_occupancy():
                    return render.DataGrid(schedule_occupancy(), editable=True)
                
                occ_last_error, occ_error_log = attach_numeric_guard(
                    table_occupancy,
                    schedule_name="Belegung",
                    min_value=0.0,
                    max_value=1.0,
                    decimals=2
                )

                # @render.ui
                # def occ_last_error_msg():
                #     msg = occ_last_error.get()
                #     if not msg:
                #         return ui.div()
                #     return ui.div({"style":"color:#b91c1c;margin-top:6px;"}, f"⚠ {msg}")
                # @render.ui
                # def occ_error_list():
                #     items = occ_error_log.get() or []
                #     if not items:
                #         return ui.div()
                #     return ui.div(
                #         {"style":"margin-top:6px;font-size:0.9rem;"},
                #         ui.tags.ul(*[ui.tags.li(it) for it in items])
                #     )
                
                @render.plot(alt="Plot of occupancy schedule")
                def plot_occupancy():
                    df = table_occupancy.data_patched().astype(float)
                    y = df.loc['Occupancy'].tolist()
                    x = list(df.columns)
                    plt.figure(figsize=(10, 5))
                    plt.bar(x, y, color='skyblue')
                    plt.title('Belegungszeitplan')
                    plt.xlabel('Stunde')
                    plt.ylabel('Belegung []')
                    plt.xticks(rotation=45)
                    plt.grid()
                    plt.tight_layout()
                    return plt.gcf()

            with ui.card():
                ui.card_header("Beleuchtungszeitplan")
                @render.data_frame
                def table_lighting():
                    return render.DataGrid(schedule_lighting(), editable=True)
                
                light_last_error, light_error_log = attach_numeric_guard(
                    table_lighting,
                    schedule_name="Beleuchtung",
                    min_value=0.0,
                    max_value=1.0,
                    decimals=2
                )

                # @render.ui
                # def light_last_error_msg():
                #     msg = light_last_error.get()
                #     if not msg:
                #         return ui.div()
                #     return ui.div({"style":"color:#b91c1c;margin-top:6px;"}, f"⚠ {msg}")

                # @render.ui
                # def light_error_list():
                #     items = light_error_log.get() or []
                #     if not items:
                #         return ui.div()
                #     return ui.div(
                #         {"style":"margin-top:6px;font-size:0.9rem;"},
                #         ui.tags.ul(*[ui.tags.li(it) for it in items])
                #     )

                
                @render.plot(alt="Plot of lighting schedule")
                def plot_lighting():
                    df = table_lighting.data_patched().astype(float)
                    y = df.loc['Lighting'].tolist()
                    x = list(df.columns)
                    plt.figure(figsize=(10, 5))
                    plt.bar(x, y, color='orange')
                    plt.title('Beleuchtungszeitplan')
                    plt.xlabel('Stunde')
                    plt.ylabel('Beleuchtung []')
                    plt.xticks(rotation=45)
                    plt.grid()
                    plt.tight_layout()
                    return plt.gcf()

            with ui.card():
                ui.card_header("Geräte-Zeitplan")
                @render.data_frame
                def table_equipment():
                    return render.DataGrid(schedule_equipment(), editable=True)
                
                equip_error, equip_error_log = attach_numeric_guard(
                    table_equipment,
                    schedule_name="Geräte",
                    min_value=0.0,
                    max_value=1.0,
                    decimals=2
                )

                # @render.ui
                # def equip_last_error_msg():
                #     msg = equip_error.get()
                #     if not msg:
                #         return ui.div()
                #     return ui.div({"style":"color:#b91c1c;margin-top:6px;"}, f"⚠ {msg}")

                # @render.ui
                # def equip_error_list():
                #     items = equip_error_log.get() or []
                #     if not items:
                #         return ui.div()
                #     return ui.div(
                #         {"style":"margin-top:6px;font-size:0.9rem;"},
                #         ui.tags.ul(*[ui.tags.li(it) for it in items])
                #     )     

                @render.plot(alt="Plot of equipment schedule")
                def plot_equipment():
                    df = table_equipment.data_patched().astype(float)
                    y = df.loc['Equipment'].tolist()
                    x = list(df.columns)
                    plt.figure(figsize=(10, 5))
                    plt.bar(x, y, color='green')
                    plt.title('Geräte-Zeitplan')
                    plt.xlabel('Stunde')
                    plt.ylabel('Geräte []')
                    plt.xticks(rotation=45)
                    plt.grid()
                    plt.tight_layout()
                    return plt.gcf()

        # settings for weather data input       
        with ui.nav_panel("Wetterdaten"):
            with ui.card():
                ui.card_header("Wetterdaten-Datei (.mat, .csv, .epw)")
                ui.markdown("**Erforderliche Spalten (in dieser Reihenfolge):**")
                ui.markdown("""
| Spalte | Einheit | Beschreibung |
|--------|---------|-------------|
| timestamp | Stunden | Zeit ab Jahresbeginn (z.B. 0–8760 h) |
| air_temperature | °C | Außenlufttemperatur |
| relative_humidity | % | Relative Luftfeuchte |
| wind_speed_x | m/s | Windgeschwindigkeit X-Richtung |
| wind_speed_y | m/s | Windgeschwindigkeit Y-Richtung |
| solar_radiation_direct | W/m² | Direkte Sonneneinstrahlung |
| solar_radiation_diffuse | W/m² | Diffuse Sonneneinstrahlung |
| sky_cover | % | Bewölkung |
| sun_elevation | ° | Sonnenelevationswinkel |
| sun_azimuth | ° | Sonnenazimut |
                """)
                ui.markdown("**Wichtig: Nur die Spaltenreihenfolge zählt!** Die Spaltennamen werden ignoriert. Die Positionen der Spalten müssen exakt dieser Tabelle entsprechen.")
                ui.markdown("**Unterstützte Formate:** MATLAB .mat-Datei mit numerischer Tabelle (erste nicht-`__` Variable wird verwendet), CSV-Dateien, oder EnergyPlus .epw-Dateien")
                ui.markdown("**Zeitauflösung:** Stundenwerte, lückenlos aufeinanderfolgend")
                ui.markdown("**Settling-in Phase:** Falls die Wetterdatei länger als ein Jahr (>8760 h) ist, wird das RC-Modell über die zusätzlichen Stunden durchlaufen, um ein thermisches Gleichgewicht zu erreichen. Nur das letzte Jahr wird in den Ergebnissen ausgegeben.")
                
                ui.input_file(
                    "input_weather_file",
                    "Wetterdatei hochladen",
                    accept=".mat,.csv,.epw",
                    width="600px",
                    multiple=False
                )


with ui.nav_panel("über"):
    "über diese App"

