from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from simulate_tank import simulateTank
import numpy as np

data = importData(data_options[0])
configuration = importConfiguration()
# initiation - define the properties of the tank
tank = data["tanks_data"][2]
insulation_thickness = 0.065 # m
first = True
mission_profile = data["mission_profile"],
final_fuel_mass = -100

changes = calculateChanges(mission_profile, False, dt=10)
time_steps = changes[:, 0]
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)

tanks_changes = {}
tank_pressure = configuration["pressure_tank"]
fill_level = configuration["lh2_fill_0"]
venting_pressure = configuration["pressure_vent"],
sum_volumes = data["sum_volumes"]
load_profile = np.zeros((time_steps.shape[0], data["tanks_data"].shape[0]))
load_profile[:, 0] = data["tanks_data"][0][2]
for tank in range(data["tanks_data"].shape[0]):
    insulation = np.hstack((data["insulation_data"][0], insulation_thickness))
    tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                       tank_data=data["tanks_data"][tank], mission_data=changes,
                                       air_data=airProfile, load_profile=load_profile, insulation_data=insulation)
print(tanks_changes)
