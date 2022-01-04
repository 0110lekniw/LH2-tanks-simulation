from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from simulate_tank import simulateTank
import numpy as np

# import data
data = importData(data_options[0])
configuration = importConfiguration()
insulation_thickness = 0.065 # m
# initiation  - calculate fuel demand and altitude in time
mission_profile = data["mission_profile"]
changes = calculateChanges(mission_profile, False, dt=10)
time_steps = changes[:, 0]
# initiation - calculate necessary amount of fuel in tanks and air properties (temperature, density and pressure)
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)

# calculate evaporation of the liquid hydrogen in tanks and vented hydrogen flow for each of the tanks
tanks_changes = {}
# load profile indicates the percentage of demanded fuel flow from each of the tanks.
# For first option this value is proportional to tanks volume to total tanks' volume ratio
load_profile = np.zeros((time_steps.shape[0], data["tanks_data"].shape[0]))
for tank in range(data["tanks_data"].shape[0]):
    insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
    load_profile[:, tank] = -data["tanks_data"][tank][2]/data["sum_volumes"]
    tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                       tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                       air_data=airProfile, load_profile=load_profile[:, tank],
                                       insulation_data=insulation)
print(tanks_changes)
