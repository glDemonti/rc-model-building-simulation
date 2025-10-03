from functools import partial

from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import page_navbar, nav_panel, navset_pill_list

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

ui.page_opts(
    title="Simple simulation app",
    page_fn=partial(page_navbar, id="page"),
)

with ui.nav_panel("home"):
    "page 1"

with ui.nav_panel("settings"):
    with ui.navset_pill_list(id="tab"):
        with ui.nav_panel("basic settings"):

            # Input fields for building geometry
            with ui.card():

                ui.card_header("Building geometry")

                with ui.card():
                    ui.card_header("Unshaded glazing areas")
                    ui.input_text(
                        id="unshaded_glazing_area_n",
                        label="Unshaded glazing area (north) [m²]",
                        value=unshaded_glazing_area_n,
                        width="600px",
                        placeholder="Enter a number",   
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_e",
                        label="Unshaded glazing area (east) [m²]",
                        value=unshaded_glazing_area_e,
                        width="600px",
                        placeholder="Enter a number",   
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_s",
                        label="Unshaded glazing area (south) [m²]",
                        value=unshaded_glazing_area_s,
                        width="600px",
                        placeholder="Enter a number",
                    )

                    ui.input_text(
                        id="unshaded_glazing_area_w",
                        label="Unshaded glazing area (west) [m²]",
                        value=unshaded_glazing_area_w,
                        width="600px",
                        placeholder="Enter a number",
                    )

                with ui.card():
                    ui.card_header("Shaded glazing areas")
                    ui.input_text(
                        id="shaded_glazing_area_n",
                        label="Shaded glazing area (north) [m²]",
                        value=shaded_glazing_area_n,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_e",
                        label="Shaded glazing area (east) [m²]",
                        value=shaded_glazing_area_e,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_s",
                        label="Shaded glazing area (south) [m²]",
                        value=shaded_glazing_area_s,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_glazing_area_w",
                        label="Shaded glazing area (west) [m²]",
                        value=shaded_glazing_area_w,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    
                with ui.card():
                    ui.card_header("unshaded frame areas")
                    ui.input_text(
                        id="unshaded_frame_area_n",
                        label="Unshaded frame area (north) [m²]",
                        value=unshaded_frame_area_n,
                        width="600px",
                        placeholder="Enter a number",   
                    )
                    ui.input_text(
                        id="unshaded_frame_area_e",
                        label="Unshaded frame area (east) [m²]",
                        value=unshaded_frame_area_e,
                        width="600px",
                        placeholder="Enter a number",   
                    )
                    ui.input_text(
                        id="unshaded_frame_area_s",
                        label="Unshaded frame area (south) [m²]",
                        value=unshaded_frame_area_s,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="unshaded_frame_area_w",
                        label="Unshaded frame area (west) [m²]",
                        value=unshaded_frame_area_w,
                        width="600px",
                        placeholder="Enter a number",
                    )
                
                with ui.card():
                    ui.card_header("shaded frame areas")
                    ui.input_text(
                        id="shaded_frame_area_n",
                        label="Shaded frame area (north) [m²]",
                        value=shaded_frame_area_n,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_frame_area_e",
                        label="Shaded frame area (east) [m²]",
                        value=shaded_frame_area_e,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_frame_area_s",
                        label="Shaded frame area (south) [m²]",
                        value=shaded_frame_area_s,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="shaded_frame_area_w",
                        label="Shaded frame area (west) [m²]",
                        value=shaded_frame_area_w,
                        width="600px",
                        placeholder="Enter a number",
                    )
                
                with ui.card():
                    ui.card_header("Wall areas (including glazings)")
                    ui.input_text(
                        id="wall_area_n",
                        label="Wall area (north) [m²]",
                        value=wall_area_n,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="wall_area_e",
                        label="Wall area (east) [m²]",
                        value=wall_area_e,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="wall_area_s",
                        label="Wall area (south) [m²]",
                        value=wall_area_s,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="wall_area_w",
                        label="Wall area (west) [m²]",
                        value=wall_area_w,
                        width="600px",
                        placeholder="Enter a number",
                    )
                with ui.card():
                    ui.card_header("Other areas")
                    ui.input_text(
                        id="roof_area",
                        label="Roof area [m²]",
                        value=roof_area,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="floor_area",
                        label="Floor area [m²]",
                        value=floor_area,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="int_wall_area",
                        label="Internal wall area (both sides should be present) [m²]",
                        value=int_wall_area,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="int_ceiling_area",
                        label="Internal ceiling area (both sides should be present) [m²]",
                        value=int_ceiling_area,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="wall_against_unheated_area",
                        label="Wall area against unheated zones [m²]",
                        value=wall_against_unheated_area,
                        width="600px",
                        placeholder="Enter a number",
                    )
                    ui.input_text(
                        id="building_height",
                        label="Height of the building [m]",
                        value=building_height,
                        width="600px",
                        placeholder="Enter a number",
                    )
     

            # input fields for thermal properties
            with ui.card():
                ui.card_header("Thermal_properties")
                ui.input_numeric(
                    id="glazing_u_value",
                    label="U-value of glazing [W/m²K]",
                    value=glazing_u_value,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )
                ui.input_numeric(
                    id="glazing_g_value",
                    label="g-value of glazing (fraction of solar radiation transmitted into the building) []",
                    value=glazing_g_value,
                    width=None,
                    min=0,
                    max=1,
                    step=0.01,
                )
                ui.input_numeric(
                    id="shading_g_value_reduction_factor",
                    label="Reduction factor of g-value due to shading (e.g. balconies) []",
                    value=shading_g_value_reduction_factor,
                    width=None,
                    min=0,
                    max=1,
                    step=0.01,
                )
                ui.input_numeric(
                    id="frame_u_value",
                    label="U-value of window frame [W/m²K]",
                    value=frame_u_value,
                    width=None,
                    min=0,
                    max=None,
                    step=0.1,
                )

            # input fields for internal gains

        with ui.nav_panel("advanced settings"):
            "Advanced settings"

with ui.nav_panel("about"):
    "About this app"



