from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
import matplotlib.pyplot as plt

data = importData(data_options[0])
configuration = importConfiguration()
changes = calculateChanges(data["mission_profile"], False, dt = 10)
profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
airProfile = defineAirProfile(profile)

fig = plt.figure()
plt.plot(profile[:, 0], airProfile[:, 0])
plt.show()
print("a")


# define the mission fuel flows
