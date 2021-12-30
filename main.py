from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
import numpy as np
import matplotlib.pyplot as plt
data = importData(data_options[0])
configuration = importConfiguration()
changes = calculateChanges(data["mission_profile"], False, dt = 10)
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)

# create the data for the tank properties [pressure [Pa], temperature [K], average density [kg/m3] fill level[%]]
# create the data for the tank flows   [engine flow [kg/s], vented flow [kg/s], evaporation rate [kg/s], heat leak [W]]
fluid =
tankProperties_names = ["pressure", "temperature", "density", "fill level"]
tankProperties = np.empty([profile.shape[0], len(tankProperties_names)])
tankFlow_names = ["engine flow", "vented flow", "evaporation rate", "heat leak"]
tankFlow = np.empty([profile.shape[0], len(tankFlow_names)])
for timeStep in range(profile.shape[0]):

fig = plt.figure()
plt.plot(profile[:, 0], airProfile[:, 0])
plt.show()
print("a")


# define the mission fuel flows
