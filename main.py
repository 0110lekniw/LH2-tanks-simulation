from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from fluid_properities import calculateHydrogen
import numpy as np
import matplotlib.pyplot as plt

data = importData(data_options[0])
configuration = importConfiguration()
# initiation - define the properties of the tank
tank = data["tanks_data"][2]
insulation = data["insulation_data"][0]
first = True

changes = calculateChanges(data["mission_profile"], False, dt=10)
time_steps = changes[:, 0]
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)
hydrogenData = calculateHydrogen(pressure=configuration["pressure_tank"], volume_tot=tank[2],
                                 fill_level=configuration["lh2_fill_0"])

# define the mission fuel flows
