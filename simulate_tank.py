import numpy as np

from fluid_properities import calculateHydrogen
from thermal_calculations import calculateConductiveHeat, calculateHeat, calculateTankChange


def simulateTank(time_steps = np.zeros((3)), configuration = np.zeros((3)), tank_data = np.zeros((3)),
                 mission_data = np.zeros((3, 3)), air_data = np.zeros((3, 3)), load_profile = np.zeros((5)),
                 insulation_data = np.zeros(3)):
    results = np.zeros(time_steps.shape[0], 3)
    results[0, :] = [configuration["pressure_tank"], 0 , configuration["lh2_fill_0"]]
    # values constant during the iterations:
    # geometrical tank data
    total_volume = tank_data[2]
    total_area = tank_data[1]
    venting_pressure = configuration["pressure_vent"]
    for time_step in range(time_steps.shape[0] - 1):
        duration = time_steps[time_step + 1]
        pressure = results[time_step, 0]
        fill_level = results[time_step, 2]
        fuel_flow = load_profile[time_step]*mission_data[time_step, 2]
        hydrogenData = calculateHydrogen(pressure=pressure, volume_tot=total_volume, fill_level=fill_level)
        conductive_heat = calculateConductiveHeat(area=total_area, conductivity_coefficient=insulation_data[0],
                                                  thickness=insulation_data[2],
                                                  hot_surface_temperature=air_data[time_step, 0],
                                                  cold_surface_temperature=hydrogenData[2])
        heat = calculateHeat(conductive_heat=conductive_heat, time_step=duration)
        tank_change = calculateTankChange(heat=heat, energy_derivative=hydrogenData[-1], total_volume=hydrogenData[4],
                                          total_engine_flow=fuel_flow,
                                          vaporization_heat=hydrogenData[3], liquid_density=hydrogenData[8],
                                          gas_density=hydrogenData[10], vented_pressure=venting_pressure,
                                          tank_pressure=pressure)
        results[time_step + 1, :] = results[time_step, :] + np.multiply(tank_change, [1, 1, -1])
    return results