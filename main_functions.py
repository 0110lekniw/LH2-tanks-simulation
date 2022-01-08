import numpy as np

from define_mission import calculateChanges, defineProfile, defineAirProfile
from main import data, configuration
from simulate_tank import simulateTank


def calculateMaximumCruiseDuration():
    global profile, air_profile
    initial_fuel = 2000
    final_fuel = -100
    mission_profile = data["mission_profile"]
    negative_time = -1
    tanks_changes = {}
    while negative_time != 0:
        # initiation  - calculate fuel demand and altitude in time
        changes = calculateChanges(mission_profile, False, dt=10)
        time_steps = changes[:, 0]
        # initiation - calculate necessary amount of fuel in tanks and air properties (temperature, density and
        # pressure)
        profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"],
                                evaporation=0)
        air_profile = defineAirProfile(profile)

        # calculate evaporation of the liquid hydrogen in tanks and vented hydrogen flow for each of the tanks

        # load profile indicates the percentage of demanded fuel flow from each of the tanks.
        # For first option this value is proportional to tanks volume to total tanks' volume ratio
        load_profile = np.zeros((time_steps.shape[0], data["tanks_data"].shape[0]))
        for tank in range(data["tanks_data"].shape[0]):
            insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
            load_profile[:, tank] = -data["tanks_data"][tank][2] / data["sum_volumes"]
            tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                               tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                               air_data=air_profile, load_profile=load_profile[:, tank],
                                               insulation_data=insulation)
            if tank == 0:
                final_fuel = tanks_changes[tank][-1, 4] * data["tanks_data"][tank][0]
                initial_fuel = tanks_changes[tank][1, 4] * data["tanks_data"][tank][0]
            else:
                final_fuel += tanks_changes[tank][-1, 4] * data["tanks_data"][tank][0]
                initial_fuel += tanks_changes[tank][1, 4] * data["tanks_data"][tank][0]
        fuel_demand = (mission_profile[6, 2] / mission_profile[6, -1])
        negative_time = round(
            (initial_fuel * configuration["reserve rate"] + configuration["reserve deviation"] - final_fuel)
            / fuel_demand, 1)
        mission_profile[6, -1] -= negative_time
        mission_profile[6, 2] = fuel_demand * mission_profile[6, -1]

        print("Iteration finished. Final Fuel is:", final_fuel, 'whats equal to:',
              round(final_fuel / initial_fuel * 100, 2)
              , "% of initial fuel")

    results = {"mission_profile": profile, "air_profile": air_profile, "tank_properties": tanks_changes,
               "mission_data": mission_profile}
    return results
