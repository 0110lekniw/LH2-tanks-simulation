from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from fluid_properities import calculateHydrogen
from thermal_calculations import calculateConductiveHeat, calculateHeat, calculateTankChange
import numpy as np

data = importData(data_options[0])
configuration = importConfiguration()
# initiation - define the properties of the tank
tank = data["tanks_data"][2]
insulation = data["insulation_data"][0]
insulation_thickness = 0.065 # m
first = True

changes = calculateChanges(data["mission_profile"], False, dt=10)
time_steps = changes[:, 0]
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)
# ["P", "D", "T", "H", "volume", "mass", density_star, mass lh2, mass gh2, energy derivative]
totals_volume =tank[2]
tanks_changes = {}
tank_change = [0, 0, 0]
tank_pressure = configuration["pressure_tank"]
fill_level = configuration["lh2_fill_0"]
venting_pressure = configuration["pressure_vent"],
sum_volumes = data["sum_volumes"]
for tank in range(data["tanks_data"].shape[0]):
    tanks_changes[tank] = np.zeros((time_steps.shape[0], 3))
    tanks_changes[tank][0, :] = [tank_pressure,  0, fill_level]

for tank in range(data["tanks_data"].shape[0]):
    tank_data = data["tanks_data"][tank]
    for time_step in range(time_steps.shape[0]-1):
        duration = time_steps[time_step+1]
        total_volume = tank_data[2]
        pressure = tanks_changes[tank][time_step, 0]
        fill_level = tanks_changes[tank][time_step, 2]
        load = total_volume/sum_volumes
        hydrogenData = calculateHydrogen(pressure = pressure, volume_tot= total_volume, fill_level=fill_level)
        conductive_heat = calculateConductiveHeat(area=data["tanks_data"][tank][1], conductivity_coefficient=insulation[0],
                                                  thickness=insulation_thickness, hot_surface_temperature=airProfile[time_step, 0],
                                                  cold_surface_temperature=hydrogenData[2])
        heat = calculateHeat(conductive_heat=conductive_heat, time_step=duration)
        tank_change = calculateTankChange(heat=heat, energy_derivative=hydrogenData[-1], total_volume=hydrogenData[4],
                                          total_engine_flow=-changes[time_step, 2]*load,
                                          vaporization_heat=hydrogenData[3], liquid_density = hydrogenData[8],
                                          gas_density = hydrogenData[10], vented_pressure= venting_pressure,
                                          tank_pressure=pressure)
        tanks_changes[tank][time_step+1, :] = tanks_changes[tank][time_step, :] + np.multiply(tank_change, [1, 1, -1])
    print("Tank [1] finished", tank)



print(heat)


# define the mission fuel flows
