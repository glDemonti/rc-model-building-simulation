from dataclasses import dataclass


@dataclass
class RCParams:
    # building properties
    unshaded_glazing_area_n: float
    unshaded_glazing_area_e: float
    unshaded_glazing_area_s: float
    unshaded_glazing_area_w: float
    shaded_glazing_area_n: float
    shaded_glazing_area_e: float
    shaded_glazing_area_s: float
    shaded_glazing_area_w: float
    unshaded_frame_area_n: float
    unshaded_frame_area_e: float
    unshaded_frame_area_s: float
    unshaded_frame_area_w: float
    shaded_frame_area_n: float
    shaded_frame_area_e: float
    shaded_frame_area_s: float
    shaded_frame_area_w: float
    glazing_area_n: float
    glazing_area_e: float
    glazing_area_s: float
    glazing_area_w: float
    frame_area_n: float
    frame_area_e: float
    frame_area_s: float
    frame_area_w: float
    wall_area_n: float
    wall_area_e: float
    wall_area_s: float
    wall_area_w: float
    roof_area: float
    floor_area: float
    int_wall_area: float
    int_ceiling_area: float
    wall_against_unheated_area: float
    building_height: float
    wall_inside_thickness: float
    wall_outside_thickness: float
    roof_inside_thickness: float
    roof_outside_thickness: float
    floor_inside_thickness: float
    floor_outside_thickness: float
    int_wall_thickness: float
    int_ceiling_thickness: float

    # thermal properties
    glazing_u_value: float
    glazing_g_value: float
    shading_g_value_reduction_factor: float
    frame_u_value: float
    wall_against_unheated_u_value: float
    wall_inside_lambda: float
    roof_inside_lambda: float
    floor_inside_lambda: float
    wall_inside_capacity_density: float
    roof_inside_capacity_density: float
    floor_inside_capacity_density: float
    wall_outside_lambda: float
    roof_outside_lambda: float
    floor_outside_lambda: float
    wall_outside_capacity_density: float
    roof_outside_capacity_density: float
    floor_outside_capacity_density: float
    int_wall_lambda: float
    int_ceiling_lambda: float
    int_wall_capacity_density: float
    int_ceiling_capacity_density: float
    infiltration_rate_specific: float
    air_ventilation_rate_specific: float
    heat_exchanger_efficiency: float
    thermal_bridges: float
    occupancy_power_per_area: float
    lighting_power_per_area: float
    equipment_power_per_area: float
    occupancy_schedule: dict
    lighting_schedule: dict
    equipment_schedule: dict

    # simulation parameters
    time_step: float
    surf_htc_in: float
    surf_htc_out: float
    heating_setpoint: float
    cooling_setpoint: float


class ModelMapper:
    def __init__(self) -> None:
        pass

    def to_model_parms(self, cfg: dict) -> RCParams:
        sim_params = cfg.get("simulation_parameters", {})
        therm_props = (
            cfg.get("thermal_parameters")
            or cfg.get("thermal_properties", {})
        )
        build_geom = cfg.get("building_geometry", {})

        def get_nested(d, *keys, default=None):
            cur = d
            for k in keys:
                if not isinstance(cur, dict) or k not in cur:
                    return default
                cur = cur[k]
            return cur

        params_dict = {}

        # geometry - windows (north/east/south/west)
        params_dict["unshaded_glazing_area_n"] = get_nested(
            build_geom, "windows", "north", "unshaded_glazing_area", "value"
        )
        params_dict["unshaded_glazing_area_e"] = get_nested(
            build_geom, "windows", "east", "unshaded_glazing_area", "value"
        )
        params_dict["unshaded_glazing_area_s"] = get_nested(
            build_geom, "windows", "south", "unshaded_glazing_area", "value"
        )
        params_dict["unshaded_glazing_area_w"] = get_nested(
            build_geom, "windows", "west", "unshaded_glazing_area", "value"
        )

        params_dict["shaded_glazing_area_n"] = get_nested(
            build_geom, "windows", "north", "shaded_glazing_area", "value"
        )
        params_dict["shaded_glazing_area_e"] = get_nested(
            build_geom, "windows", "east", "shaded_glazing_area", "value"
        )
        params_dict["shaded_glazing_area_s"] = get_nested(
            build_geom, "windows", "south", "shaded_glazing_area", "value"
        )
        params_dict["shaded_glazing_area_w"] = get_nested(
            build_geom, "windows", "west", "shaded_glazing_area", "value"
        )

        params_dict["unshaded_frame_area_n"] = get_nested(
            build_geom, "windows", "north", "unshaded_frame_area", "value"
        )
        params_dict["unshaded_frame_area_e"] = get_nested(
            build_geom, "windows", "east", "unshaded_frame_area", "value"
        )
        params_dict["unshaded_frame_area_s"] = get_nested(
            build_geom, "windows", "south", "unshaded_frame_area", "value"
        )
        params_dict["unshaded_frame_area_w"] = get_nested(
            build_geom, "windows", "west", "unshaded_frame_area", "value"
        )

        params_dict["shaded_frame_area_n"] = get_nested(
            build_geom, "windows", "north", "shaded_frame_area", "value"
        )
        params_dict["shaded_frame_area_e"] = get_nested(
            build_geom, "windows", "east", "shaded_frame_area", "value"
        )
        params_dict["shaded_frame_area_s"] = get_nested(
            build_geom, "windows", "south", "shaded_frame_area", "value"
        )
        params_dict["shaded_frame_area_w"] = get_nested(
            build_geom, "windows", "west", "shaded_frame_area", "value"
        )

        # totals
        ug_n = params_dict.get("unshaded_glazing_area_n") or 0.0
        sg_n = params_dict.get("shaded_glazing_area_n") or 0.0
        params_dict["glazing_area_n"] = ug_n + sg_n

        ug_e = params_dict.get("unshaded_glazing_area_e") or 0.0
        sg_e = params_dict.get("shaded_glazing_area_e") or 0.0
        params_dict["glazing_area_e"] = ug_e + sg_e

        ug_s = params_dict.get("unshaded_glazing_area_s") or 0.0
        sg_s = params_dict.get("shaded_glazing_area_s") or 0.0
        params_dict["glazing_area_s"] = ug_s + sg_s

        ug_w = params_dict.get("unshaded_glazing_area_w") or 0.0
        sg_w = params_dict.get("shaded_glazing_area_w") or 0.0
        params_dict["glazing_area_w"] = ug_w + sg_w

        uf_n = params_dict.get("unshaded_frame_area_n") or 0.0
        sf_n = params_dict.get("shaded_frame_area_n") or 0.0
        params_dict["frame_area_n"] = uf_n + sf_n

        uf_e = params_dict.get("unshaded_frame_area_e") or 0.0
        sf_e = params_dict.get("shaded_frame_area_e") or 0.0
        params_dict["frame_area_e"] = uf_e + sf_e

        uf_s = params_dict.get("unshaded_frame_area_s") or 0.0
        sf_s = params_dict.get("shaded_frame_area_s") or 0.0
        params_dict["frame_area_s"] = uf_s + sf_s

        uf_w = params_dict.get("unshaded_frame_area_w") or 0.0
        sf_w = params_dict.get("shaded_frame_area_w") or 0.0
        params_dict["frame_area_w"] = uf_w + sf_w

        # enclosure areas
        params_dict["wall_area_n"] = get_nested(
            build_geom, "enclosure", "outside_wall_areas", "north", "value"
        )
        params_dict["wall_area_e"] = get_nested(
            build_geom, "enclosure", "outside_wall_areas", "east", "value"
        )
        params_dict["wall_area_s"] = get_nested(
            build_geom, "enclosure", "outside_wall_areas", "south", "value"
        )
        params_dict["wall_area_w"] = get_nested(
            build_geom, "enclosure", "outside_wall_areas", "west", "value"
        )
        params_dict["roof_area"] = get_nested(
            build_geom, "enclosure", "roof_area", "value"
        )
        params_dict["floor_area"] = get_nested(
            build_geom, "enclosure", "floor_area", "value"
        )
        params_dict["int_wall_area"] = get_nested(
            build_geom, "enclosure", "int_wall_area", "value"
        )
        params_dict["int_ceiling_area"] = get_nested(
            build_geom, "enclosure", "int_ceiling_area", "value"
        )
        params_dict["wall_against_unheated_area"] = get_nested(
            build_geom, "enclosure", "wall_to_unheated_area", "value"
        )
        params_dict["building_height"] = get_nested(
            build_geom, "building_height", "value"
        )

        # thicknesses
        params_dict["wall_inside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "outside_wall_areas",
            "thickness",
            "inside_layer",
            "value",
        )
        params_dict["wall_outside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "outside_wall_areas",
            "thickness",
            "outside_layer",
            "value",
        )
        params_dict["roof_inside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "roof_area",
            "thickness",
            "inside_layer",
            "value",
        )
        params_dict["roof_outside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "roof_area",
            "thickness",
            "outside_layer",
            "value",
        )
        params_dict["floor_inside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "floor_area",
            "thickness",
            "inside_layer",
            "value",
        )
        params_dict["floor_outside_thickness"] = get_nested(
            build_geom,
            "enclosure",
            "floor_area",
            "thickness",
            "outside_layer",
            "value",
        )
        
        # thermal properties and inputs
        params_dict["glazing_u_value"] = get_nested(
            therm_props, "windows", "u_value_glazing", "value"
        )
        params_dict["glazing_g_value"] = get_nested(
            therm_props, "windows", "g_value_glazing", "value"
        )
        params_dict["shading_g_value_reduction_factor"] = get_nested(
            therm_props,
            "windows",
            "shading_g_value_reduction_factor",
            "value",
        )
        params_dict["frame_u_value"] = get_nested(
            therm_props, "windows", "u_value_frame", "value"
        )

        params_dict["wall_against_unheated_u_value"] = get_nested(
            therm_props, "enclosure", "u_value_wall_against_unheated", "value"
        )

        params_dict["wall_inside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "lambda_wall_inside",
            "value",
        )
        params_dict["roof_inside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "lambda_roof_inside",
            "value",
        )
        params_dict["floor_inside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "lambda_floor_inside",
            "value",
        )

        params_dict["wall_inside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "capacity_density_wall_inside",
            "value",
        )
        params_dict["roof_inside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "capacity_density_roof_inside",
            "value",
        )
        params_dict["floor_inside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "inside_layer",
            "capacity_density_floor_inside",
            "value",
        )

        params_dict["wall_outside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "lambda_wall_outside",
            "value",
        )
        params_dict["roof_outside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "lambda_roof_outside",
            "value",
        )
        params_dict["floor_outside_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "lambda_floor_outside",
            "value",
        )

        params_dict["wall_outside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "capacity_density_wall_outside",
            "value",
        )
        params_dict["roof_outside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "capacity_density_roof_outside",
            "value",
        )
        params_dict["floor_outside_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "outside_layer",
            "capacity_density_floor_outside",
            "value",
        )

        params_dict["int_wall_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "internal_walls_ceiling",
            "lambda_internal_wall",
            "value",
        )
        params_dict["int_ceiling_lambda"] = get_nested(
            therm_props,
            "enclosure",
            "internal_walls_ceiling",
            "lambda_internal_ceiling",
            "value",
        )
        params_dict["int_wall_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "internal_walls_ceiling",
            "capacity_density_internal_wall",
            "value",
        )
        params_dict["int_ceiling_capacity_density"] = get_nested(
            therm_props,
            "enclosure",
            "internal_walls_ceiling",
            "capacity_density_internal_ceiling",
            "value",
        )

        params_dict["infiltration_rate_specific"] = get_nested(
            therm_props, "infiltration_rate_specific", "value"
        )
        params_dict["air_ventilation_rate_specific"] = get_nested(
            therm_props, "air_ventilation_rate_specific", "value"
        )
        params_dict["heat_exchanger_efficiency"] = get_nested(
            therm_props, "heat_exchanger_efficiency", "value"
        )
        params_dict["thermal_bridges"] = get_nested(
            therm_props, "thermal_bridges", "value"
        )

        params_dict["occupancy_power_per_area"] = get_nested(
            therm_props, "power_input", "occupancy_power_per_area", "value"
        )
        params_dict["lighting_power_per_area"] = get_nested(
            therm_props, "power_input", "lighting_power_per_area", "value"
        )
        params_dict["equipment_power_per_area"] = get_nested(
            therm_props, "power_input", "equipment_power_per_area", "value"
        )

        # schedules
        params_dict["occupancy_schedule"] = get_nested(
            therm_props, "schedules", "occupancy_schedule", default={}
        ) or {}
        params_dict["lighting_schedule"] = get_nested(
            therm_props, "schedules", "lighting_schedule", default={}
        ) or {}
        params_dict["equipment_schedule"] = get_nested(
            therm_props, "schedules", "equipment_schedule", default={}
        ) or {}

        # simulation parameters
        params_dict["time_step"] = get_nested(sim_params, "time_step", "value")
        params_dict["surf_htc_in"] = get_nested(
            sim_params, "surface_heat_transfer_internal_", "value"
        )
        params_dict["surf_htc_out"] = get_nested(
            sim_params, "surface_heat_transfer_external_", "value"
        )
        params_dict["heating_setpoint"] = get_nested(
            sim_params, "heating_setpoint", "value"
        )
        params_dict["cooling_setpoint"] = get_nested(
            sim_params, "cooling_setpoint", "value"
        )

        # ensure all dataclass fields exist in params_dict
        for fname in RCParams.__dataclass_fields__:
            if fname not in params_dict:
                if fname.endswith("_schedule"):
                    params_dict[fname] = {}
                else:
                    params_dict[fname] = 0.0

        return RCParams(**params_dict)

