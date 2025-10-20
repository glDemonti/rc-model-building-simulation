from functools import partial
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import page_navbar, nav_panel, navset_pill_list
from shinywidgets import render_widget, render_plotly
 
# Import sim_io_mock from adapters, adjusting sys.path if necessary
try:
    from adapters import sim_io_mock
except ModuleNotFoundError:
    import sys, pathlib
    ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (one above /ui)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from adapters import sim_io_mock

# Example of a calculated default value for an input field

unshaded_glazing_area_n = "0.825 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)"  # North facade  [m²]
unshaded_glazing_area_e = "0.825 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)"   # East facade   [m²]
unshaded_glazing_area_s = "0.825 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)"  # South facade  [m²]
unshaded_glazing_area_w = "0.825 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)"  # West facade   [m²]
shaded_glazing_area_n = "0.0" # North facade  [m²]
shaded_glazing_area_e = "0.825 * (1.98 * 2)" # East facade   [m²]
shaded_glazing_area_s = "0.825 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2)" # South facade  [m²]
shaded_glazing_area_w = "0.825 * (2.07 * 2)" # West facade   [m²]

unshaded_frame_area_n = "0.175 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)"   # North facade  [m²]
unshaded_frame_area_e = "0.175 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)"   # East facade   [m²]
unshaded_frame_area_s = "0.175 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)"  # South facade  [m²]
unshaded_frame_area_w = "0.175 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)"  # West facade   [m²]

shaded_frame_area_n = "0.0"  # North facade  [m²]
shaded_frame_area_e = "0.175 * (1.98 * 2)"  # East facade   [m²]
shaded_frame_area_s = "0.175 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2)"   # South facade  [m²]
shaded_frame_area_w = "0.175 * (2.07 * 2)"  # West facade   [m²]


wall_area_n = "2.5 * 3 * (32.6 + 1.6 - 6.0)"  # North facade [m^2], including glazings
wall_area_e = "2.5 * 3 * 14.0"    # East facade [m^2], including glazings
wall_area_s = "2.5 * 3 * (32.6 + 1.6)"  # South facade [m^2], including glazings
wall_area_w = "2.5 * 3 * 14.0"    # West facade [m^2], including glazings

roof_area = "313.8"  # Roof area [m^2]
floor_area = "313.8"  # Floor area [m^2]

int_wall_area =  "(72.975 + 91.9 + 2.0 *19.75) * 3.0"     # Internal wall area [m²] (both sides should be present)
int_ceiling_area = "313.8 * 2.0 * 2.0"     # Internal ceiling area [m²] (both sides should be present)
wall_against_unheated_area = "(21.5 + 12.5 + 5.3) * 3.0"  # Wall area against unheated zones [m²]

building_height = "2.5 * 3"  # Height of the building [m]

# Thermal Properties of window components
glazing_u_value = 0.7       # U-value of glazing [W/m²K]
glazing_g_value = 0.45      # g-value of glazing (fraction of solar radiation transmitted into the building) []
shading_g_value_reduction_factor = 0.14  # Reduction factor of g-value due to shading (e.g. balconies) []
frame_u_value = 2.0         # U-value of window frame [W/m²K]

# Thermal properties of opaque building components
wall_against_unheated_u_value = "1 / (2 / 8.0 + 0.17 / 0.79)" # u-value of Wall against unheated zones [W/m²K]

# Thermal properties of inside layers of building components
wall_inside_lambda = 1.8 
roof_inside_lambda = 1.8
floor_inside_lambda = 1.8

# capacity density of inside layers of building components. (rho * c) [J/m³K]
wall_inside_capacity_density = "2400 * 1100"
roof_inside_capacity_density = "2400 * 1100"
floor_inside_capacity_density = "2400 * 1100"

# thermal properties of outside layers of building components 
wall_outside_lambda = 0.031
roof_outside_lambda = 0.02
floor_outside_lambda = 0.03

# capacity density of outside layers of building components. (rho * c) [J/m³K]
wall_outside_capacity_density = "16 * 1400"
roof_outside_capacity_density = "30 * 1400"
floor_outside_capacity_density = "18 * 1400"

# thermal properties of internal building components
int_wall_lambda = 0.79
int_ceiling_lambda = 1.8

# capacity density of internal building components. (rho * c) [J/m³K]
int_wall_capacity_density = "1070.0 * 850.0"
int_ceiling_capacity_density = "2400.0 * 1100.0"

# Thermal properties of opaque building components
wall_against_unheated_u_value = 1 / (2 / 8.0 + 0.17 / 0.79) # u-value of Wall against unheated zones [W/m²K]

# Thermal properties of inside layers of building components
wall_inside_lambda = 1.8 
roof_inside_lambda = 1.8
floor_inside_lambda = 1.8

# capacity density of inside layers of building components. (rho * c) [J/m³K]
wall_inside_capacity_density = 2400 * 1100
roof_inside_capacity_density = 2400 * 1100
floor_inside_capacity_density = 2400 * 1100

# thermal properties of outside layers of building components 
wall_outside_lambda = 0.031
roof_outside_lambda = 0.02
floor_outside_lambda = 0.03

# capacity density of outside layers of building components. (rho * c) [J/m³K]
wall_outside_capacity_density = 16 * 1400
roof_outside_capacity_density = 30 * 1400
floor_outside_capacity_density = 18 * 1400

# thermal properties of internal building components
int_wall_lambda = 0.79
int_ceiling_lambda = 1.8

# capacity density of internal building components. (rho * c) [J/m³K]
int_wall_capacity_density = 1070.0 * 850.0
int_ceiling_capacity_density = 2400.0 * 1100.0

# thickness of layers of outside walls
wall_inside_thickness = 0.2  # thickness of inside layer of walls (brick) [m]
wall_outside_thickness = 0.1  # thickness of outside layer of walls (insulation) [m]

# thickness of layers of outside roof
roof_inside_thickness = 0.25  # thickness of inside layer of roof (concrete) [m]
roof_outside_thickness = 0.1   # thickness of outside layer of roof (insulation) [m]

# thickness of layers of floor against unheated zones or ground
floor_inside_thickness = 0.3   # thickness of inside layer of floor (concrete) [m]
floor_outside_thickness = 0.08  # thickness of outside layer of floor (insulation) [m]

# thickness of layers of internal walls
int_wall_thickness = 0.17       # thickness of internal walls (drywall) [m]
int_ceiling_thickness = 0.3654  # thickness of internal ceiling (drywall) [m]

infiltration_rate = "0.194444 * 0.001 * floor_area * 3.0"

# ventilation rate of the building (assumed to be always on)
air_ventilation_rate = "0.278 * 0.001 * floor_area * 3.0"  # [m³/s]
heat_exchanger_efficiency = 0.0  # efficiency of heat exchanger in ventilation system []

# thermal bridges
thermal_bridges = 123.4 # thermal bridges [W/K]

# difference power input [W] 
occupancy_power = "70.0 * 0.033 * floor_area * 3.0"
lighting_power = "2.7 * floor_area * 3.0"
equipment_power = "8.0 * floor_area * 3.0"

# sheduled parameters
df_schedule_occupancy = pd.DataFrame(
    columns=[f'{i:02d}:00' for i in range(24)],
    index=['Occupancy'],
    data=[[1, 1, 1, 1, 1, 1, 0.6, 0.4, 0, 0, 0, 0, 0.8, 0.4, 0, 0, 0, 0.4, 0.8, 0.8, 0.8, 1, 1, 1]],
    dtype=float
    )

df_schedule_lighting = pd.DataFrame(
    columns=[f'{i:02d}:00' for i in range(24)],
    index=['Lighting'],
    data=[[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0]],
    dtype=float
    )

df_schedule_equipment = pd.DataFrame(
    columns=[f'{i:02d}:00' for i in range(24)],
    index=['Equipment'],
    data=[[0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.8, 0.2, 0.1, 0.1, 0.1, 0.1, 0.8, 0.2, 0.1, 0.1, 0.1, 0.2, 0.8, 1.0, 0.2, 0.2, 0.2, 0.1]],
    dtype=float
    )

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
            if col is None and "colmn_index" in p:
                try:
                    # read the current column name from the grid
                    col_idx = int(p["colmn_index"])
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
        if toast:
            ui.notification_show(msg, type="error", duration=4)
            
        return accepted
    
    return last_error, error_log


df_results = sim_io_mock.load_sim_results()
df_weather = sim_io_mock.load_weather_data()

# Helper: sichere Zeitachse → Millisekunden (vermeidet ns-Probleme)
def ts_ms(series_dt):
    dt = pd.to_datetime(series_dt, errors="raise").dt.tz_localize(None)
    return (dt.view("int64") // 1_000_000).astype("int64")

# def ensure_datetime(col):
#     s = pd.Series(col)
#     if np.issubdtype(s.dtype, np.datetime64):
#         return pd.to_datetime(s)  # schon ok
#     if np.issubdtype(s.dtype, np.number):
#         m = np.nanmax(s.astype("float64"))
#         # Heuristik für Einheit
#         if m > 1e15:        # ns
#             unit = "ns"
#         elif m > 1e12:      # ms
#             unit = "ms"
#         else:               # s
#             unit = "s"
#         return pd.to_datetime(s, unit=unit)
#     # Strings etc.
#     return pd.to_datetime(s, errors="coerce")


ui.page_opts(
    title="Einfache Simulationsanwendung für ein RC-Gebäudemodell",
    page_fn=partial(page_navbar, id="page"),
)

with ui.nav_panel("home"):
    with ui.card():
        ui.input_action_button(
            id="button_start_simulation",
            label="Simulation starten",
            disabled=False,
        )
    # with ui.card():
        #     @ render.data_frame
        #     def weather_data_table():
        #         return df_weather
        # with ui.card():
                 
    with ui.card():

        @render_plotly
        def plot_temperatures():
            df_temp = sim_io_mock.make_df_temperatures().copy()


            # Zeitstempel in Millisekunden umwandeln
            df_temp["ts_ms"] = ts_ms(df_temp["datetime"])

            fig = px.line(

                df_temp,
                x="ts_ms",
                y=[
                    "Aussenlufttemperatur",
                    "Innenlufttemperatur", 
                    # 'Innentemperatur Verglasung Nord',
                    # 'Innentemperatur Verglasung Ost',
                    # 'Innentemperatur Verglasung Süd', 
                    # 'Innentemperatur Verglasung West',
                    # 'Aussentemperatur Verglasung Nord',
                    # 'Aussentemperatur Verglasung Ost',
                    # 'Aussentemperatur Verglasung Süd',
                    # 'Aussentemperatur Verglasung West',
                    # 'Inenntemperatur Fensterrahmen Nord',
                    # 'Inenntemperatur Fensterrahmen Ost',
                    # 'Inenntemperatur Fensterrahmen Süd', 
                    # 'Inenntemperatur Fensterrahmen West',
                    # 'Aussentemperatur Fensterrahmen Nord',
                    # 'Aussentemperatur Fensterrahmen Ost',
                    # 'Aussentemperatur Fensterrahmen Süd',
                    # 'Aussentemperatur Fensterrahmen West',
                    # "Temperatur 1. Knoten Aussenwand Nord",
                    # "Temperatur 1. Knoten Aussenwand Ost",
                    # "Temperatur 1. Knoten Aussenwand Süd",
                    # "Temperatur 1. Knoten Aussenwand West",
                    # "Temperatur 1. Knoten Dach",
                    # "Temperatur 1. Knoten Boden",
                    # "Temperatur 1. Knoten Innenwand",
                    # "Temperatur 1. Knoten Innendecke",
                    # "Temperatur 2. Knoten Aussenwand Nord",
                    # "Temperatur 2. Knoten Aussenwand Ost",
                    # "Temperatur 2. Knoten Aussenwand Süd",
                    # "Temperatur 2. Knoten Aussenwand West",
                    # "Temperatur 2. Knoten Dach",
                    # "Temperatur 2. Knoten Boden",
                    # "Temperatur 2. Knoten Innenwand",
                    # "Temperatur 2. Knoten Innendecke",
                    # "Temperatur 3. Knoten Aussenwand Nord",
                    # "Temperatur 3. Knoten Aussenwand Ost",
                    # "Temperatur 3. Knoten Aussenwand Süd",
                    # "Temperatur 3. Knoten Aussenwand West",
                    # "Temperatur 3. Knoten Dach",
                    # "Temperatur 3. Knoten Boden",
                    # "Temperatur 3. Knoten Innenwand",
                    # "Temperatur 3. Knoten Innendecke",
                    # "Temperatur 4. Knoten Aussenwand Nord",
                    # "Temperatur 4. Knoten Aussenwand Ost",
                    # "Temperatur 4. Knoten Aussenwand Süd",
                    # "Temperatur 4. Knoten Aussenwand West",
                    # "Temperatur 4. Knoten Dach",
                    # "Temperatur 4. Knoten Boden",
                    # "Temperatur 4. Knoten Innenwand",
                    # "Temperatur 4. Knoten Innendecke",
                   ],
                labels={
                    "datetime": "Zeit", 
                    "value": "Temperature [°C]",
                    "variable": "Legende",
                },
                ).update_xaxes(
                    type="date",
                    tickformat="%d-%m %H:%M",
                    tickangle=45,
                    showgrid=True,
                ).update_layout(
                title="Temperaturverläufe",
                hovermode="x unified",
                xaxis_title="Zeit [h]",
                yaxis_title="Temperatur [°C]",
                )
            return fig
        
        # plot with matplotlib

        # @render.plot()
        # def plot_matplotlib_example():
        #     df_temp = sim_io_mock.make_df_temperatures()

        #     fig, ax  = plt.subplots()
        #     ax.plot(
        #         df_temp["datetime"],
        #         df_temp["Innenlufttemperatur"],
        #     )
        #     ax.plot(
        #         df_temp["datetime"],
        #         df_temp["Aussenlufttemperatur"],)
        #     ax.set_title("Beispiel Matplotlib Plot")
        #     ax.set_xlabel("Innenlufttemperatur [°C]")
        #     ax.set(ylim=(-10, 35), yticks=np.arange(-10, 35, 5))

        #     # plt.show()
        #     return fig
        
        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_overheating_hours",
                value="123",
                width=4,
            ):
                "Überhitzungsstunden [h]"

    with ui.card():
        @render_widget
        def plot_cooling_heating_power():
            fig = px.line(
                df_results[['cooling_power', 'heating_power']],
                ).update_layout(
                    title="Heiz- und Kühlleistung",
                    xaxis_title="Zeit [h]",
                    yaxis_title="Leistung [W]",
                )
            return fig
        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_heating_demand",
                value="1234",
                width=4,
            ):
                "Jährlicher Heizwärmebedarf [kWh]"

            with ui.value_box(
                id="value_box_cooling_demand",
                value="567",
                width=4,
            ):
                "Jährlicher Kühlbedarf [kWh]"
            with ui.value_box(
                id="value_box_spec_heating_load",
                value="45.6",
                width=4,
            ):
                "Spezifische Heizlast [W/m²]"
            with ui.value_box(
                id="value_box_spec_cooling_load",
                value="78.9",
                width=4,
            ):
                "Spezifische Kühllast [W/m²]"
            with ui.value_box(
                id="value_box_total_energy_costs_heating",
                value="234.56",
                width=4,
            ):
                "Jährliche Stromkosten Heizung [CHF]"
            with ui.value_box(
                id="value_box_total_energy_costs_cooling",
                value="345.67",
                width=4,
            ):
                "Jährliche Stromkosten Kühlung [CHF]"


    with ui.card():

        @render_plotly
        def plot_wall_nodes_over_year():
            df = sim_io_mock.make_df_temperatures().copy()
            df["ts_ms"] = ts_ms(df["datetime"])

            node_cols = ["Temperatur 1. Knoten Aussenwand Nord", "Temperatur 2. Knoten Aussenwand Nord", "Temperatur 3. Knoten Aussenwand Nord", "Temperatur 4. Knoten Aussenwand Nord"]  # anpassen, falls nötig
            df_long = df.melt(id_vars=["ts_ms"], value_vars=node_cols,
                            var_name="Knoten", value_name="Temperatur [°C]")

            fig = (
                px.line(
                    df_long, x="ts_ms", y="Temperatur [°C]", color="Knoten",
                    labels={"ts_ms": "Zeit", "Knoten": "Knoten"}
                )
                .update_xaxes(type="date", tickformat="%d.%m.%Y %H:%M", tickangle=45, showgrid=True)
                .update_layout(
                    title="Temperaturverlauf in den 4 Wandknoten (Jahresverlauf)",
                    xaxis_title="Zeit", yaxis_title="Temperatur [°C]",
                    hovermode="x unified"
                )
            )
            return fig
        
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
        
        
        @render_plotly
        def plot_temperature_wall_over_nodes():
            df = sim_io_mock.make_df_temperatures().copy()

            # x-axis: time in ms
            df["ts_ms"] = ts_ms(df["datetime"])

            # y-axis: wall nodes
            node_cols = [
                "Temperatur 1. Knoten Aussenwand Nord",
                "Temperatur 2. Knoten Aussenwand Nord",
                "Temperatur 3. Knoten Aussenwand Nord",
                "Temperatur 4. Knoten Aussenwand Nord"
            ]

            # z-values: temperatures matrix (nodes × time)
            Z = df[node_cols].to_numpy().T
            X = df["ts_ms"].to_numpy()
            Y = node_cols

            fig = go.Figure(
                data=go.Heatmap(
                    x=X,
                    y=Y,
                    z=Z,
                    colorbar=dict(title="Temperatur [°C]"),
                    zsmooth=False, # True = smoothed, False = original values
                )
            )

            fig.update_xaxes(
                type="date",
                tickformat="%d-%m %H:%M",
                tickangle=45,
                showgrid=False,
                title_text="Zeit",
            )

            fig.update_yaxes(
                categoryorder="array",
                categoryarray=Y,
                title_text="Knoten",
            )
            fig.update_layout(
                title="Temperaturverlauf in den Wandknoten (Zeit x Knoten)",
                margin=dict(l=0, r=0, b=0, t=40),
            )
            fig.update_traces(
                hovertemplate="Zeit: %{x|%d-%m %H:%M}<br>Knoten: %{y}<br>Temperatur: %{z} °C<extra></extra>"
            )
            return fig

        @render_plotly
        def plot_wall_3d_surface():
            df = sim_io_mock.make_df_temperatures().copy()
            df["datetime"] = pd.to_datetime(df["datetime"], errors="raise").dt.tz_localize(None)
            df = df.sort_values("datetime")

            node_cols = [
                "Temperatur 1. Knoten Aussenwand Nord",
                "Temperatur 2. Knoten Aussenwand Nord",
                "Temperatur 3. Knoten Aussenwand Nord",
                "Temperatur 4. Knoten Aussenwand Nord"
            ]

            # node_cols_rev = node_cols[::-1]  # reverse for better visualization (innenseite unten)

            # x as time in ms, format ticks as datetime later
            X_num = ts_ms(df["datetime"]).to_numpy()  # Zeit in ms
            Y_idx = np.arange(len(node_cols))    # Knotenindex [0, 1, 2, 3]
            Z = df[node_cols].to_numpy()         # shape: (n_time × n_knoten)

            # make meshgrid for surface
            Xgrid, Ygrid = np.meshgrid(X_num, Y_idx, indexing="ij")  # shape: (n_time × n_knoten)
            Zgrid = Z                                     # shape: (n_time × n_knoten)

            start = pd.Timestamp(df["datetime"].dt.year.min(), 1, 1)
            end = pd.Timestamp(df["datetime"].dt.year.max(), 12, 31, 23, 59, 59)
            
            x_ticks_dt = pd.date_range(start, end, freq="MS")
            x_ticksvals =(x_ticks_dt.view("int64") // 1_000_000).astype("int64")
            x_ticktext = [d.strftime("%b") for d in x_ticks_dt]

            fig = go.Figure(data=[
                go.Surface(
                    x=Xgrid,
                    y=Ygrid,
                    z=Zgrid,
                    colorscale="RdYlBu_r",
                    colorbar=dict(title="Temperatur [°C]"),
                    showscale=True,
                )
            ])
            fig.update_layout(
                title="3D-Temperaturfeld in der Wand (Zeit × Knoten × Temperatur)",
                scene=dict(
                    xaxis=dict(
                        title="Zeit",
                        tickmode="array",
                        tickvals=x_ticksvals,
                        ticktext=x_ticktext,
                        showspikes=False,
                    ),
                    yaxis=dict(
                        title="Knoten",
                        tickmode="array",
                        tickvals=Y_idx,
                        ticktext=node_cols,
                        showspikes=False,
                    ),
                    zaxis=dict(
                        title="Temperatur [°C]",
                        showspikes=False,
                    ),
                ),
                margin=dict(l=0, r=0, b=0, t=40),
            )
            return fig
        



    with ui.card():
        @render_widget
        def plot_electricity_consumption():
            fig = px.line(
                df_results[['lighting_electricity', 'equipment_electricity']],
                color_discrete_sequence=["orange", "red"]
                ).update_layout(
                    title="Stromverbrauch",
                    xaxis_title="Zeit [h]",
                    yaxis_title="Leistung [W]",
                )
            return fig    
        
        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_total_electricity",
                value="8901",
                width=4,
            ):
                "Jährlicher Stromverbrauch [kWh]"

            with ui.value_box(
                id_="value_box_energy_costs_electricity",
                value="123.45",
                width=4,
            ):
                "Jährliche Stromkosten Beleuchtung und Geräte [CHF]"
            with ui.value_box(
                id="value_box_energy_costs_heating_cooling",
                value="67.89",
                width=4,
            ):
                "Jährliche Stromkosten Heizung und Kühlung [CHF]"
                
    with ui.card():
        ui.card_header("CO2-Emissionen")
        with ui.layout_column_wrap():
            with ui.value_box(
                id="value_box_co2_emissions_heating",
                value="234.56",
                width=6,
            ):
                "Jährliche CO2-Emissionen Heizung [kg CO2]"
            with ui.value_box(
                id="value_box_co2_emissions_cooling",
                value="345.67",
                width=6,
            ):
                "Jährliche CO2-Emissionen Kühlung [kg CO2]"
            with ui.value_box(
                id="value_box_elektricity_light_co2",
                value="456.78",
                width=6,
            ):
                "Jährliche CO2-Emissionen Stromverbrauch(Beleuchtung) [kg CO2]"
            with ui.value_box(
                id="value_box_elektricity_equip_co2",
                value="567.89",
                width=6,
            ):
                "Jährliche CO2-Emissionen Stromverbrauch(Geräte) [kg CO2]"
            with ui.value_box(
                id="value_box_total_co2_emissions",
                value="1604.90",
                width=6,
            ):
                "Gesamte jährliche CO2-Emissionen [kg CO2]"


with ui.nav_panel("Einstellungen"):
    ui.input_action_button(
        id="button_save_settings",
        label=" Speichern",
        disabled=False,
    )
    # Basic Settings tab
    with ui.navset_pill_list(id="tab"):
        with ui.nav_panel("Grundeinstellungen"):

            # Input fields for building geometry
            with ui.card():

                ui.card_header("Gebäudegeometrie")

                with ui.card():
                    ui.card_header("Unbeschattete Verglasungsflächen")
                    ui.input_text(
                        id="unshaded_glazing_area_n",
                        label="Unbeschattete Verglasungsfläche (Nord) [m²]",
                        value=unshaded_glazing_area_n,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_e",
                        label="Unbeschattete Verglasungsfläche (Ost) [m²]",
                        value=unshaded_glazing_area_e,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_s",
                        label="Unbeschattete Verglasungsfläche (Süd) [m²]",
                        value=unshaded_glazing_area_s,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_w",
                        label="Unbeschattete Verglasungsfläche (West) [m²]",
                        value=unshaded_glazing_area_w,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )

                with ui.card():
                    ui.card_header("Beschattete Verglasungsflächen")
                    ui.input_text(
                        id="shaded_glazing_area_n",
                        label="Beschattete Verglasungsfläche (Nord) [m²]",
                        value=shaded_glazing_area_n,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_e",
                        label="Beschattete Verglasungsfläche (Ost) [m²]",
                        value=shaded_glazing_area_e,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_s",
                        label="Beschattete Verglasungsfläche (Süd) [m²]",
                        value=shaded_glazing_area_s,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_w",
                        label="Beschattete Verglasungsfläche (West) [m²]",
                        value=shaded_glazing_area_w,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    
                with ui.card():
                    ui.card_header("Unbeschattete Rahmenflächen")
                    ui.input_text(
                        id="unshaded_frame_area_n",
                        label="Unbeschattete Rahmenfläche (Nord) [m²]",
                        value=unshaded_frame_area_n,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="unshaded_frame_area_e",
                        label="Unbeschattete Rahmenfläche (Ost) [m²]",
                        value=unshaded_frame_area_e,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="unshaded_frame_area_s",
                        label="Unbeschattete Rahmenfläche (Süd) [m²]",
                        value=unshaded_frame_area_s,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="unshaded_frame_area_w",
                        label="Unbeschattete Rahmenfläche (West) [m²]",
                        value=unshaded_frame_area_w,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                
                with ui.card():
                    ui.card_header("Beschattete Rahmenflächen")
                    ui.input_text(
                        id="shaded_frame_area_n",
                        label="Beschattete Rahmenfläche (Nord) [m²]",
                        value=shaded_frame_area_n,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_frame_area_e",
                        label="Beschattete Rahmenfläche (Ost) [m²]",
                        value=shaded_frame_area_e,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_frame_area_s",
                        label="Beschattete Rahmenfläche (Süd) [m²]",
                        value=shaded_frame_area_s,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="shaded_frame_area_w",
                        label="Beschattete Rahmenfläche (West) [m²]",
                        value=shaded_frame_area_w,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                
                with ui.card():
                    ui.card_header("Wandflächen (inkl. Verglasungen)")
                    ui.input_text(
                        id="wall_area_n",
                        label="Wandfläche (Nord) [m²]",
                        value=wall_area_n,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_area_e",
                        label="Wandfläche (Ost) [m²]",
                        value=wall_area_e,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_area_s",
                        label="Wandfläche (Süd) [m²]",
                        value=wall_area_s,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_area_w",
                        label="Wandfläche (West) [m²]",
                        value=wall_area_w,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                with ui.card():
                    ui.card_header("Andere Gebäudeflächen und Abmessungen")
                    ui.input_text(
                        id="roof_area",
                        label="Dachfläche [m²]",
                        value=roof_area,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="floor_area",
                        label="Bodenfläche [m²]",
                        value=floor_area,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_wall_area",
                        label="Innenwandflächen (beide seiten sollen vorhanden sein) [m²]",
                        value=int_wall_area,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="int_ceiling_area",
                        label="Innendeckenfläche (beide seiten sollen vorhanden sein) [m²]",
                        value=int_ceiling_area,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="wall_against_unheated_area",
                        label="Wandfläche gegen unbeheizte Zonen [m²]",
                        value=wall_against_unheated_area,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                    ui.input_text(
                        id="building_height",
                        label="Höhe des Gebäudes [m]",
                        value=building_height,
                        width="600px",
                        placeholder="Geben Sie eine Zahl ein",
                    )
                with ui.card():
                    with ui.layout_column_wrap():
                        with ui.value_box(
                            id="value_box_total_outerwall_area",
                            value="1234",
                            width=6,
                        ):
                            "Gesammte Aussenwandfläche (Verglasung) [m²]"
                        with ui.value_box(
                            id="value_box_total_glazing_area",
                            value="567",
                            width=6,
                        ):
                            "Gesammte Verglasungsfläche [m²]"
                        with ui.value_box(
                            id="value_box_window_to_wall_ratio",
                            value="89",
                            width=6,
                        ):
                            "Fenster-zu-Wand-Verhältnis [%]"
                        with ui.value_box(
                            id="value_box_window_shadowing_ratio",
                            value="90",
                            width=6,
                        ):
                            "Fenster-Beschattungsverhältnis [%]"

            # input fields for thermal properties
            with ui.card():
                ui.card_header("Thermische Eigenschaften")
                ui.input_numeric(
                    id="glazing_u_value",
                    label="U-Wert der Verglasung [W/m²K]",
                    value=glazing_u_value,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_numeric(
                    id="glazing_g_value",
                    label="g-Wert der Verglasung (Anteil der solaren Strahlung, welche in das Gebäude gelangt) []",
                    value=glazing_g_value,
                    width=None,
                    min=0,
                    max=1,
                    step=0.01,
                )
                ui.input_numeric(
                    id="shading_g_value_reduction_factor",
                    label="Reduktionsfaktor des g-Werts aufgrund von Beschattung (z.B. Balkone) []",
                    value=shading_g_value_reduction_factor,
                    width=None,
                    min=0,
                    max=1,
                    step=0.01,
                )
                ui.input_numeric(
                    id="frame_u_value",
                    label="U-Wert des Fensterrahmens [W/m²K]",
                    value=frame_u_value,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_text(
                    id="wall_against_unheated_u_value",
                    label="U-Wert der Wand gegen unbeheizte Zonen [W/m²K]",
                    value=wall_against_unheated_u_value,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_numeric(
                    id="wall_inside_lambda",
                    label="Wärmeleitfähigkeit der inneren Schicht der Wand [W/mK]",
                    value=wall_inside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_numeric(
                    id="roof_inside_lambda",
                    label="Wärmeleitfähigkeit der inneren Schicht des Daches [W/mK]",
                    value=roof_inside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_numeric(
                    id="floor_inside_lambda",
                    label="Wärmeleitfähigkeit der inneren Schicht des Fußbodens [W/mK]",
                    value=floor_inside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_text(
                    id="wall_inside_capacity_density",
                    label="Speicherdichte der inneren Schicht der Wand (rho * c) [J/m³K]",
                    value=wall_inside_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="roof_inside_capacity_density",
                    label="Speicherdichte der inneren Schicht des Daches (rho * c) [J/m³K]",
                    value=roof_inside_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="floor_inside_capacity_density",
                    label="Speicherdichte der inneren Schicht des Fußbodens (rho * c) [J/m³K]",
                    value=floor_inside_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_numeric(
                    id="wall_outside_lambda",
                    label="Wärmeleitfähigkeit der äusseren Schicht der Wand [W/mK]",
                    value=wall_outside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.001,
                )
                ui.input_numeric(
                    id="roof_outside_lambda",
                    label="Wärmeleitfähigkeit der äusseren Schicht des Daches [W/mK]",
                    value=roof_outside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.001,
                )
                ui.input_numeric(
                    id="floor_outside_lambda",
                    label="Wärmeleitfähigkeit der äusseren Schicht des Fußbodens [W/mK]",
                    value=floor_outside_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.001,
                )
                ui.input_text(
                    id="wall_outside_capacity_density",
                    label="Kapazitätsdichte der äusseren Schicht der Wand (rho * c) [J/m³K]",
                    value=wall_outside_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="roof_outside_capacity_density",
                    label="Kapazitätsdichte der äusseren Schicht des Daches (rho * c) [J/m³K]",
                    value=roof_outside_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="floor_outside_capacity_density",
                    label="Kapazitätsdichte der äusseren Schicht des Fussbodens (rho * c) [J/m³K]",
                    value=floor_outside_capacity_density,
                    width="600px",
                    placeholder="Enter a number",
                )
                ui.input_numeric(
                    id="int_wall_lambda",
                    label="Wärmeleitfähigkeit der Innenwand [W/mK]",
                    value=int_wall_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_numeric(
                    id="int_ceiling_lambda",
                    label="Wärmeleitfähigkeit der Innendecke [W/mK]",
                    value=int_ceiling_lambda,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_text(
                    id="int_wall_capacity_density",
                    label="Kapazitätsdichte der Innenwand (rho * c) [J/m³K]",
                    value=int_wall_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="int_ceiling_capacity_density",
                    label="Kapazitätsdichte der Innendecke (rho * c) [J/m³K]",
                    value=int_ceiling_capacity_density,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )


            # input fields for thicknesses of building components
            with ui.card():
                ui.card_header("Dicken der Bauteilschichten")
                ui.input_numeric(
                    id="wall_inside_thickness",
                    label="Dicke der inneren Schicht der Wand (Ziegel) [m]",
                    value=wall_inside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="wall_outside_thickness",
                    label="Dicke der äusseren Schicht der Wand (Dämmung) [m]",
                    value=wall_outside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="roof_inside_thickness",
                    label="Dicke der inneren Schicht des Daches (Beton) [m]",
                    value=roof_inside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="roof_outside_thickness",
                    label="Dicke der äusseren Schicht des Daches (Dämmung) [m]",
                    value=roof_outside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="floor_inside_thickness",
                    label="Dicke der inneren Schicht des Fussbodens (Beton) [m]",
                    value=floor_inside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="floor_outside_thickness",
                    label="Dicke der äusseren Schicht des Fussbodens (Dämmung) [m]",
                    value=floor_outside_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="int_wall_thickness",
                    label="Dicke der Innenwand (Gipskarton) [m]",
                    value=int_wall_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )
                ui.input_numeric(
                    id="int_ceiling_thickness",
                    label="Dicke der Innendecke (Gipskarton) [m]",
                    value=int_ceiling_thickness,
                    width=None,
                    min=0,
                    max=None,
                    step=0.01,
                )

            #input fields for building thermal parameters
            with ui.card():
                ui.card_header("Gebäude thermische Parameter")
                ui.input_text(
                    id="infiltration_rate",
                    label="Infiltrationsrate des Gebäudes [m³/s]",
                    value=infiltration_rate,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="air_ventilation_rate",
                    label="Mechanischer Luftwechselrate des Gebäudes (angenommen, immer eingeschaltet) [m³/s]",
                    value=air_ventilation_rate,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_numeric(
                    id="heat_exchanger_efficiency",
                    label="Wirkungsgrad des Wärmetauschers im Belüftungssystem []",
                    value=heat_exchanger_efficiency,
                    width=None,
                    min=0,
                    max=1,
                    step=0.01,
                )
                ui.input_text(
                    id="thermal_bridges",
                    label="Wärmebrücken [W/K]",
                    value=thermal_bridges,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="occupancy_power",
                    label="Belegungsstromverbrauch [W]",
                    value=occupancy_power,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="lighting_power",
                    label="Beleuchtungsstromverbrauch [W]",
                    value=lighting_power,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="equipment_power",
                    label="Geräte-Stromverbrauch [W]",
                    value=equipment_power,
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )

            
        # Settings for scheduled parameters
        with ui.nav_panel("Zeitpläne"):
                
            with ui.card():
                ui.card_header("Belegungszeitplan")

                @render.data_frame
                def table_occupancy():
                    return render.DataGrid(
                        df_schedule_occupancy,
                        editable=True,
                        )
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
                    return render.DataGrid(
                        df_schedule_lighting,
                        editable=True,
                        )
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
                    return render.DataGrid(
                        df_schedule_equipment,
                        editable=True,
                        )
                
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
                ui.card_header("Wetterdaten-Datei (.mat)")
                ui.input_file(
                    "weather_file",
                    "Laden Sie die .mat Wetterdatei hoch",
                    accept=".mat",
                    width="600px",
                    multiple=False
                )

        with ui.nav_panel("Erweiterte Einstellungen"):

            with ui.card():
                ui.card_header("Anfangsbedingungen")
                ui.input_text(
                    id="initial_temperature",
                    label="Anfangstemperatur [°C]",
                    value="20.0",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
            with ui.card():
                ui.card_header("Energiekosten")
                ui.input_text(
                    id="electricity_price_nt",
                    label="Strompreis Niedertarif [CHF/kWh]",
                    value="0.15",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="electricity_price_ht",
                    label="Strompreis Hochtarif [CHF/kWh]",
                    value="0.20",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
            with ui.card():
                ui.card_header("Wärmepumpe und Kühlmaschine Einstellungen")
                ui.input_text(
                    id="cop_heating",
                    label="COP der Wärmepumpe []",
                    value="3.0",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="cop_cooling",
                    label="COP der Kühlmaschine []",
                    value="3.0",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="Co2_emission_factor",
                    label="CO2-Emissionsfaktor des Strommixes [kg CO2/kWh]",
                    value="0.2",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="Co2_emission_factor_heating",
                    label="CO2-Emissionsfaktor für Heizenergie [kg CO2/kWh]",
                    value="0.2",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )
                ui.input_text(
                    id="Co2_emission_factor_cooling",
                    label="CO2-Emissionsfaktor für Kühlenergie [kg CO2/kWh]",
                    value="0.2",
                    width="600px",
                    placeholder="Geben Sie eine Zahl ein",
                )

with ui.nav_panel("über"):
    "über diese App"

