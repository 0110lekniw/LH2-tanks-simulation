from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from fluid_properities import calculateHydrogen
from thermal_calculations import calculateConductiveHeat, calculateHeat

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
hydrogenData = calculateHydrogen(pressure=configuration["pressure_tank"], volume_tot=tank[2],
                                 fill_level=configuration["lh2_fill_0"])
conductive_heat = calculateConductiveHeat(area=tank[1], conductivity_coefficient=insulation[0],
                                          thickness=insulation_thickness, hot_surface_temperature=airProfile[0, 0],
                                          cold_surface_temperature=hydrogenData[2])
heat = calculateHeat(conductive_heat=conductive_heat, time_step=time_steps[1])


print(heat)


# define the mission fuel flows
