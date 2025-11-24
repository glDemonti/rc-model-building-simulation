from dataclasses import dataclass
import numpy as np


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
    occupancy_schedule: np.ndarray
    lighting_schedule: np.ndarray
    equipment_schedule: np.ndarray

    # simulation parameters
    time_step: float
    surf_htc_in: float
    surf_htc_out: float
    heating_setpoint: float
    cooling_setpoint: float


class ModelMapper:
    def __init__(self) -> None:
        pass

    def to_model_params(self, cfg: dict) -> RCParams:

        # building poperties
        unshaded_glazing_area_n = cfg["building_geometry"]["windows"]["north"]["unshaded_glazing_area"]["value"]
        unshaded_glazing_area_e = cfg["building_geometry"]["windows"]["east"]["unshaded_glazing_area"]["value"]
        unshaded_glazing_area_s = cfg["building_geometry"]["windows"]["south"]["unshaded_glazing_area"]["value"]
        unshaded_glazing_area_w = cfg["building_geometry"]["windows"]["west"]["unshaded_glazing_area"]["value"]
        shaded_glazing_area_n = cfg["building_geometry"]["windows"]["north"]["shaded_glazing_area"]["value"]
        shaded_glazing_area_e = cfg["building_geometry"]["windows"]["east"]["shaded_glazing_area"]["value"]
        shaded_glazing_area_s = cfg["building_geometry"]["windows"]["south"]["shaded_glazing_area"]["value"]
        shaded_glazing_area_w = cfg["building_geometry"]["windows"]["west"]["shaded_glazing_area"]["value"]
        unshaded_frame_area_n = cfg["building_geometry"]["windows"]["north"]["unshaded_frame_area"]["value"]
        unshaded_frame_area_e = cfg["building_geometry"]["windows"]["east"]["unshaded_frame_area"]["value"]
        unshaded_frame_area_s = cfg["building_geometry"]["windows"]["south"]["unshaded_frame_area"]["value"]
        unshaded_frame_area_w = cfg["building_geometry"]["windows"]["west"]["unshaded_frame_area"]["value"]
        shaded_frame_area_n = cfg["building_geometry"]["windows"]["north"]["shaded_frame_area"]["value"]
        shaded_frame_area_e = cfg["building_geometry"]["windows"]["east"]["shaded_frame_area"]["value"]
        shaded_frame_area_s = cfg["building_geometry"]["windows"]["south"]["shaded_frame_area"]["value"]
        shaded_frame_area_w = cfg["building_geometry"]["windows"]["west"]["shaded_frame_area"]["value"]
        glazing_area_n = unshaded_glazing_area_n + shaded_glazing_area_n
        glazing_area_e = unshaded_glazing_area_e + shaded_glazing_area_e
        glazing_area_s = unshaded_glazing_area_s + shaded_glazing_area_s
        glazing_area_w = unshaded_glazing_area_w + shaded_glazing_area_w
        frame_area_n = unshaded_frame_area_n + shaded_frame_area_n
        frame_area_e = unshaded_frame_area_e + shaded_frame_area_e
        frame_area_s = unshaded_frame_area_s + shaded_frame_area_s
        frame_area_w = unshaded_frame_area_w + shaded_frame_area_w
        wall_area_n = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["north"]["value"] - (glazing_area_n + frame_area_n)
        wall_area_e = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["east"]["value"] - (glazing_area_e + frame_area_e)
        wall_area_s = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["south"]["value"] - (glazing_area_s + frame_area_s)
        wall_area_w = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["west"]["value"] - (glazing_area_w + frame_area_w)
        roof_area = cfg["building_geometry"]["enclosure"]["roof_area"]["value"]
        floor_area = cfg["building_geometry"]["enclosure"]["floor_area"]["value"]
        int_wall_area = cfg["building_geometry"]["enclosure"]["int_wall_area"]["value"]
        int_ceiling_area = cfg["building_geometry"]["enclosure"]["int_ceiling_area"]["value"]
        wall_against_unheated_area = cfg["building_geometry"]["enclosure"]["wall_to_unheated_area"]["value"]
        building_height = cfg["building_geometry"]["building_height"]["value"]
        wall_inside_thickness = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["thickness"]["inside_layer"]["value"]
        wall_outside_thickness = cfg["building_geometry"]["enclosure"]["outside_wall_areas"]["thickness"]["outside_layer"]["value"]
        roof_inside_thickness = cfg["building_geometry"]["enclosure"]["roof_area"]["thickness"]["inside_layer"]["value"]
        roof_outside_thickness = cfg["building_geometry"]["enclosure"]["roof_area"]["thickness"]["outside_layer"]["value"]
        floor_inside_thickness = cfg["building_geometry"]["enclosure"]["floor_area"]["thickness"]["inside_layer"]["value"]
        floor_outside_thickness = cfg["building_geometry"]["enclosure"]["floor_area"]["thickness"]["outside_layer"]["value"]
        int_wall_thickness = cfg["building_geometry"]["enclosure"]["int_wall_area"]["thickness"]["value"]
        int_ceiling_thickness = cfg["building_geometry"]["enclosure"]["int_ceiling_area"]["thickness"]["value"]

        # thermal properties
        glazing_u_value = cfg["thermal_properties"]["windows"]["u_value_glazing"]["value"]
        glazing_g_value = cfg["thermal_properties"]["windows"]["g_value_glazing"]["value"]
        shading_g_value_reduction_factor = cfg["thermal_properties"]["windows"]["shading_g_value_reduction_factor"]["value"]
        frame_u_value = cfg["thermal_properties"]["windows"]["u_value_frame"]["value"]
        wall_against_unheated_u_value = cfg["thermal_properties"]["enclosure"]["u_value_wall_against_unheated"]["value"]
        wall_inside_lambda = cfg["thermal_properties"]["enclosure"]["inside_layer"]["lambda_wall_inside"]["value"]
        roof_inside_lambda = cfg["thermal_properties"]["enclosure"]["inside_layer"]["lambda_roof_inside"]["value"]
        floor_inside_lambda = cfg["thermal_properties"]["enclosure"]["inside_layer"]["lambda_floor_inside"]["value"]
        wall_inside_capacity_density = cfg["thermal_properties"]["enclosure"]["inside_layer"]["capacity_density_wall_inside"]["value"]
        roof_inside_capacity_density = cfg["thermal_properties"]["enclosure"]["inside_layer"]["capacity_density_roof_inside"]["value"]
        floor_inside_capacity_density = cfg["thermal_properties"]["enclosure"]["inside_layer"]["capacity_density_floor_inside"]["value"]
        wall_outside_lambda = cfg["thermal_properties"]["enclosure"]["outside_layer"]["lambda_wall_outside"]["value"]
        roof_outside_lambda = cfg["thermal_properties"]["enclosure"]["outside_layer"]["lambda_roof_outside"]["value"]
        floor_outside_lambda = cfg["thermal_properties"]["enclosure"]["outside_layer"]["lambda_floor_outside"]["value"]
        wall_outside_capacity_density = cfg["thermal_properties"]["enclosure"]["outside_layer"]["capacity_density_wall_outside"]["value"]
        roof_outside_capacity_density = cfg["thermal_properties"]["enclosure"]["outside_layer"]["capacity_density_roof_outside"]["value"]
        floor_outside_capacity_density = cfg["thermal_properties"]["enclosure"]["outside_layer"]["capacity_density_floor_outside"]["value"]
        int_wall_lambda = cfg["thermal_properties"]["enclosure"]["internal_walls_ceiling"]["lambda_internal_wall"]["value"]
        int_ceiling_lambda = cfg["thermal_properties"]["enclosure"]["internal_walls_ceiling"]["lambda_internal_ceiling"]["value"]
        int_wall_capacity_density = cfg["thermal_properties"]["enclosure"]["internal_walls_ceiling"]["capacity_density_internal_wall"]["value"]
        int_ceiling_capacity_density = cfg["thermal_properties"]["enclosure"]["internal_walls_ceiling"]["capacity_density_internal_ceiling"]["value"]
        infiltration_rate_specific = cfg["thermal_properties"]["infiltration_rate_specific"]["value"]
        air_ventilation_rate_specific = cfg["thermal_properties"]["air_ventilation_rate_specific"]["value"]
        heat_exchanger_efficiency = cfg["thermal_properties"]["heat_exchanger_efficiency"]["value"]
        thermal_bridges = cfg["thermal_properties"]["thermal_bridges"]["value"]
        occupancy_power_per_area = cfg["thermal_properties"]["power_input"]["occupancy_power_per_area"]["value"]
        lighting_power_per_area = cfg["thermal_properties"]["power_input"]["lighting_power_per_area"]["value"]
        equipment_power_per_area = cfg["thermal_properties"]["power_input"]["equipment_power_per_area"]["value"]
        
        # schedules
        hours = [f"{h:02d}:00" for h in range(24)]

        occup_dict = cfg["thermal_properties"]["schedules"]["occupancy_schedule"]
        ligh_dict = cfg["thermal_properties"]["schedules"]["lighting_schedule"]
        equip_dict = cfg["thermal_properties"]["schedules"]["equipment_schedule"]

        def schedule_to_array(raw):
            if isinstance(raw, dict):
                return np.array([raw[h] for h in hours], dtype=float)
            else:
                # Liste o.ä.
                return np.array(raw, dtype=float)
        
        occupancy_schedule = schedule_to_array(occup_dict)
        lighting_schedule = schedule_to_array(ligh_dict)
        equipment_schedule = schedule_to_array(equip_dict)


        # simulation parameters

        time_step = cfg["simulation_parameters"]["time_step"]["value"]
        surf_htc_in = cfg["simulation_parameters"]["surface_heat_transfer_internal"]["value"]
        surf_htc_out = cfg["simulation_parameters"]["surface_heat_transfer_external"]["value"]
        heating_setpoint = cfg["simulation_parameters"]["heating_setpoint"]["value"]
        cooling_setpoint = cfg["simulation_parameters"]["cooling_setpoint"]["value"]

        return RCParams(
            unshaded_glazing_area_n=unshaded_glazing_area_n,
            unshaded_glazing_area_e=unshaded_glazing_area_e,
            unshaded_glazing_area_s=unshaded_glazing_area_s,
            unshaded_glazing_area_w=unshaded_glazing_area_w,
            shaded_glazing_area_n=shaded_glazing_area_n,
            shaded_glazing_area_e=shaded_glazing_area_e,
            shaded_glazing_area_s=shaded_glazing_area_s,
            shaded_glazing_area_w=shaded_glazing_area_w,
            unshaded_frame_area_n=unshaded_frame_area_n,
            unshaded_frame_area_e=unshaded_frame_area_e,
            unshaded_frame_area_s=unshaded_frame_area_s,
            unshaded_frame_area_w=unshaded_frame_area_w,
            shaded_frame_area_n=shaded_frame_area_n,
            shaded_frame_area_e=shaded_frame_area_e,
            shaded_frame_area_s=shaded_frame_area_s,
            shaded_frame_area_w=shaded_frame_area_w,
            glazing_area_n=glazing_area_n,
            glazing_area_e=glazing_area_e,
            glazing_area_s=glazing_area_s,
            glazing_area_w=glazing_area_w,
            frame_area_n=frame_area_n,
            frame_area_e=frame_area_e,
            frame_area_s=frame_area_s,
            frame_area_w=frame_area_w,
            wall_area_n=wall_area_n,
            wall_area_e=wall_area_e,
            wall_area_s=wall_area_s,
            wall_area_w=wall_area_w,
            roof_area=roof_area,
            floor_area=floor_area,
            int_wall_area=int_wall_area,
            int_ceiling_area=int_ceiling_area,
            wall_against_unheated_area=wall_against_unheated_area,
            building_height=building_height,
            wall_inside_thickness=wall_inside_thickness,
            wall_outside_thickness=wall_outside_thickness,
            roof_inside_thickness=roof_inside_thickness,
            roof_outside_thickness=roof_outside_thickness,
            floor_inside_thickness=floor_inside_thickness,
            floor_outside_thickness=floor_outside_thickness,
            int_wall_thickness=int_wall_thickness,
            int_ceiling_thickness=int_ceiling_thickness,
            glazing_u_value=glazing_u_value,
            glazing_g_value=glazing_g_value,
            shading_g_value_reduction_factor=shading_g_value_reduction_factor,
            frame_u_value=frame_u_value,
            wall_against_unheated_u_value=wall_against_unheated_u_value,
            wall_inside_lambda=wall_inside_lambda,
            roof_inside_lambda=roof_inside_lambda,
            floor_inside_lambda=floor_inside_lambda,
            wall_inside_capacity_density=wall_inside_capacity_density,
            roof_inside_capacity_density=roof_inside_capacity_density,
            floor_inside_capacity_density=floor_inside_capacity_density,
            wall_outside_lambda=wall_outside_lambda,
            roof_outside_lambda=roof_outside_lambda,
            floor_outside_lambda=floor_outside_lambda,
            wall_outside_capacity_density=wall_outside_capacity_density,
            roof_outside_capacity_density=roof_outside_capacity_density,
            floor_outside_capacity_density=floor_outside_capacity_density,
            int_wall_lambda=int_wall_lambda,
            int_ceiling_lambda=int_ceiling_lambda,
            int_wall_capacity_density=int_wall_capacity_density,
            int_ceiling_capacity_density=int_ceiling_capacity_density,
            infiltration_rate_specific=infiltration_rate_specific,
            air_ventilation_rate_specific=air_ventilation_rate_specific,
            heat_exchanger_efficiency=heat_exchanger_efficiency,
            thermal_bridges=thermal_bridges,
            occupancy_power_per_area=occupancy_power_per_area,
            lighting_power_per_area=lighting_power_per_area,
            equipment_power_per_area=equipment_power_per_area,
            occupancy_schedule=occupancy_schedule,
            lighting_schedule=lighting_schedule,
            equipment_schedule=equipment_schedule,
            time_step=time_step,
            surf_htc_in=surf_htc_in,
            surf_htc_out=surf_htc_out,
            heating_setpoint=heating_setpoint,
            cooling_setpoint=cooling_setpoint,
        )
                                                                          
