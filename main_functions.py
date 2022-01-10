import numpy as np
from define_mission import calculateChanges, defineProfile, defineAirProfile
from simulate_tank import simulateTank


def calculateMaximumCruiseDuration(data, configuration, simultaneous = True, insulation_data = np.array([20.9, 35])):
    global profile, air_profile
    initial_fuel = 2000
    final_fuel = -100
    mission_profile = data["mission_profile"]
    negative_time = -1
    tanks_changes = {}
    while round(final_fuel/initial_fuel, 4) != configuration["reserve rate"]:
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
        length = time_steps.shape[0]
        if simultaneous:
            loads = data["tanks_data"][:, 2]/data["sum_volumes"]
        else:
            loads = 1/data["tanks_data"][:, 0]
        negative_time_tank = [length, length, length, length]
        for tank in range(data["tanks_data"].shape[0]):
            final_fuel_tank = -100
            number_of_tanks = data["tanks_data"][tank][0]
            initial_fuel_tank = 1000
            if simultaneous:
                insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
                load_profile[:, tank] = -loads[tank]
                tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                   tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                                   air_data=air_profile, load_profile=load_profile[:, tank],
                                                   insulation_data=insulation)
                final_fuel_tank = tanks_changes[tank][-1, 4]
                initial_fuel_tank = tanks_changes[tank][1, 4]
            else:
                if tank == 0 or tank == 1:
                    while round(final_fuel_tank - initial_fuel_tank*configuration["reserve rate"], 0) != 0:
                        insulation = np.hstack((insulation_data, data["tanks_data"][tank][-1]))
                        if tank == 0:
                            load_profile[:, tank] = 0
                            load_profile[:negative_time_tank[tank], tank] = -loads[tank]
                        else:
                            load_profile[:, tank] = 0
                            load_profile[negative_time_tank[tank-1]:negative_time_tank[tank], tank] = -loads[tank]
                        tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                           tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                                           air_data=air_profile, load_profile=load_profile[:, tank],
                                                           insulation_data=insulation)
                        final_fuel_tank = tanks_changes[tank][-1, 4]
                        initial_fuel_tank = tanks_changes[tank][1, 4]
                        if final_fuel_tank - initial_fuel_tank*configuration["reserve rate"] != 0:
                            for index in range(tanks_changes[tank][:, 4].shape[0]):
                                required_fuel = initial_fuel_tank*configuration["reserve rate"] + tanks_changes[tank][-1, 6] - tanks_changes[tank][index, 6]
                                mass = tanks_changes[tank][index, 4]
                                if tanks_changes[tank][index, 4] < required_fuel:
                                    fuel_demand = -changes[index, 2]/changes[index, 0]
                                    additional_time = (required_fuel - mass)/fuel_demand
                                    before_changes = changes[:index-1, :]
                                    to_separate = changes[index, :]
                                    new_rows = np.array([[to_separate[0] - additional_time,
                                                          to_separate[1]*(to_separate[0] - additional_time)/to_separate[0],
                                                          to_separate[2]*(to_separate[0] - additional_time)/to_separate[0]],
                                                         [additional_time,
                                                          to_separate[1]*additional_time/to_separate[0],
                                                          to_separate[2]*additional_time/to_separate[0]]])
                                    after_changes = changes[index:, :]
                                    changes = np.vstack([before_changes, new_rows, after_changes])
                                    negative_time_tank[tank] = index
                                    break
                                elif index == tanks_changes[tank][:, 4].shape[0]-1:
                                    mass = tanks_changes[tank][index, 4]
                                    fuel_demand = -changes[index, 2] / changes[index, 0]
                                    additional_time = abs((required_fuel - mass) / fuel_demand)
                                    too_add = 1
                                    next_time = changes[negative_time_tank[tank]+1, 0]
                                    if next_time < additional_time:
                                        while next_time < additional_time:
                                            too_add += 1
                                            next_time += changes[negative_time_tank[tank]+too_add, 0]
                                        negative_time_tank[tank] += too_add
                                    additional_time = next_time - additional_time
                                    before_changes = changes[:negative_time_tank[tank]-1, :]
                                    to_separate = changes[negative_time_tank[tank], :]
                                    new_rows = np.array([[to_separate[0] - additional_time,
                                                          to_separate[1]*(to_separate[0] - additional_time)/to_separate[0],
                                                          to_separate[2]*(to_separate[0] - additional_time)/to_separate[0]],
                                                         [additional_time,
                                                          to_separate[1]*additional_time/to_separate[0],
                                                          to_separate[2]*additional_time/to_separate[0]]])
                                    after_changes = changes[negative_time_tank[tank]:, :]
                                    changes = np.vstack([before_changes, new_rows, after_changes])
                        print(final_fuel_tank/initial_fuel_tank)
                else:
                    insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
                    if tank == 0:
                        load_profile[:, tank] = 0
                        load_profile[:negative_time_tank[tank], tank] = -loads[tank]
                    else:
                        load_profile[:, tank] = 0
                        load_profile[negative_time_tank[tank - 1]:negative_time_tank[tank], tank] = -loads[tank]
                    tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                       tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                                       air_data=air_profile, load_profile=load_profile[:, tank],
                                                       insulation_data=insulation)
                    final_fuel_tank = tanks_changes[tank][-1, 4]
                    initial_fuel_tank = tanks_changes[tank][1, 4]
            if tank == 0:
                final_fuel = final_fuel_tank* number_of_tanks
                initial_fuel = initial_fuel_tank* number_of_tanks
            else:
                final_fuel += final_fuel_tank* number_of_tanks
                initial_fuel += initial_fuel_tank* number_of_tanks
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



