from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from fluid_properities import calculateHydrogen
from thermal_calculations import calculateConductiveHeat, calculateHeat, calculateTankChange

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
hydrogenData = calculateHydrogen(pressure=configuration["pressure_tank"], volume_tot=tank[2],
                                 fill_level=configuration["lh2_fill_0"])
conductive_heat = calculateConductiveHeat(area=tank[1], conductivity_coefficient=insulation[0],
                                          thickness=insulation_thickness, hot_surface_temperature=airProfile[0, 0],
                                          cold_surface_temperature=hydrogenData[2])
heat = calculateHeat(conductive_heat=conductive_heat, time_step=time_steps[1])
tank_change = calculateTankChange(heat=heat, energy_derivative=hydrogenData[-1], total_volume=hydrogenData[4],
                                  total_engine_flow=changes[1, 2], vaporization_heat=hydrogenData[3],
                                  density_star=hydrogenData[-4], vented_pressure=configuration["pressure_vent"],
                                  tank_pressure=configuration["pressure_tank"])


print(heat)


# define the mission fuel flows
