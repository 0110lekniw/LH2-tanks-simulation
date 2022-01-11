import numpy as np
from define_mission import calculateChanges, defineProfile, defineAirProfile
from simulate_tank import simulateTank
from fluid_properities import calculateHydrogen


def calculateMaximumCruiseDuration(data, configuration, simultaneous=True, insulation_data=np.array([20.9, 35])):
    global profile, air_profile
    initial_fuel = 2000
    final_fuel = -100
    mission_profile = data["mission_profile"]
    tanks_changes = {}
    if simultaneous:
        while round(final_fuel / initial_fuel, 4) != configuration["reserve rate"]:
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
            # For simultaneous option this value is proportional to tanks volume to total tanks' volume ratio
            load_profile = np.zeros((time_steps.shape[0], data["tanks_data"].shape[0]))
            load = -data["tanks_data"][:, 2] / data["sum_volumes"]
            for tank in range(data["tanks_data"].shape[0]):
                final_fuel_tank = -100
                number_of_tanks = data["tanks_data"][tank][0]
                initial_fuel_tank = 1000
                insulation = np.hstack((insulation_data, data["tanks_data"][tank][-1]))
                load_profile[:, tank] = -load[tank]
                tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                   tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                                   air_data=air_profile, load_profile=load_profile[:, tank],
                                                   insulation_data=insulation)
                final_fuel_tank = tanks_changes[tank][-1, 4]
                initial_fuel_tank = tanks_changes[tank][1, 4]
                if tank == 0:
                    final_fuel = final_fuel_tank * number_of_tanks
                    initial_fuel = initial_fuel_tank * number_of_tanks
                else:
                    final_fuel += final_fuel_tank * number_of_tanks
                    initial_fuel += initial_fuel_tank * number_of_tanks
            fuel_demand = (mission_profile[6, 2] / mission_profile[6, -1])
            negative_time = round(
                (initial_fuel * configuration["reserve rate"] + configuration["reserve deviation"] - final_fuel)
                / fuel_demand, 1)
            mission_profile[6, -1] -= negative_time
            mission_profile[6, 2] = fuel_demand * mission_profile[6, -1]

            print("Iteration finished. Final Fuel is:", final_fuel, 'whats equal to:',
                  round(final_fuel / initial_fuel * 100, 2)
                  , "% of initial fuel")
    else:
        while round(final_fuel / initial_fuel, 4) != configuration["reserve rate"]:
            # initiation  - calculate fuel demand and altitude in time
            number_of_sequences = data["tanks_data"].shape[0]
            changes = calculateChanges(mission_profile, False, dt=10)
            time_steps = changes[:, 0]
            # initiation - calculate necessary amount of fuel in tanks and air properties (temperature, density and
            # pressure)
            profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"],
                                    evaporation=0)
            load_profile = np.zeros((time_steps.shape[0], number_of_sequences))
            air_profile = defineAirProfile(profile)
            # load profile indicates the percentage of demanded fuel flow from each of the tanks.
            # For sequential option this value is equal to 1/tanks number in sequence
            load = 1 / data["tanks_data"][:, 0]
            # assuming that the time for each of the tank is equal to number of tanks
            initial_time = profile[-1, 0]/number_of_sequences
            # shut_off_time defines starting and ending time of tanks in sequence defuelling
            # first and last value is constant
            shut_off_time = np.array([[0, initial_time],
                                      [initial_time, initial_time*2],
                                      [initial_time*2, initial_time*3]])
            for tank in range(data["tanks_data"].shape[0]):
                number_of_tanks = data["tanks_data"][tank, 0]
                final_fuel_tank = -100
                initial_fuel_tank = 1000
                # for each of the tank except from the last:
                if tank != data["tanks_data"].shape[0]-1:
                    while round(final_fuel_tank - initial_fuel_tank * configuration["reserve rate"], 0) != 0:
                        insulation = np.hstack((insulation_data, data["tanks_data"][tank][-1]))
                        load_profile[:, tank] = defineLoadProfile(profile, shut_off_time[tank, 0],
                                                                  shut_off_time[tank, 1], load = load[tank])
                        tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                           tank_data=data["tanks_data"][tank][:-2],
                                                           mission_data=changes,
                                                           air_data=air_profile, load_profile=load_profile[:, tank],
                                                           insulation_data=insulation)
                        final_fuel_tank = tanks_changes[tank][-1, 4]
                        initial_fuel_tank = tanks_changes[tank][1, 4]
                        if final_fuel_tank != initial_fuel_tank * configuration["reserve rate"]:
                            lacking_fuel = final_fuel_tank - initial_fuel_tank * configuration["reserve rate"]
                            bool = load_profile[:, tank] > 0
                            b_where = np.where(bool)
                            last_load_index = np.max(b_where)
                            last_fuel_flow = changes[last_load_index, 2]/changes[last_load_index, 0]
                            lacking_time = lacking_fuel/last_fuel_flow
                            shut_off_time[tank, 1] += lacking_time
                            shut_off_time[tank+1, 0] = shut_off_time[tank, 1]
                        else:
                            break
                    if tank == 0:
                        final_fuel = final_fuel_tank*number_of_tanks
                        initial_fuel = initial_fuel_tank*number_of_tanks
                    else:
                        final_fuel += final_fuel_tank*number_of_tanks
                        initial_fuel += initial_fuel_tank*number_of_tanks

                else:
                    insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
                    load_profile[:, tank] = defineLoadProfile(profile, shut_off_time[tank, 0], shut_off_time[tank, 1],
                                                              load = load[tank])
                    tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                                       tank_data=data["tanks_data"][tank][:-2],
                                                       mission_data=changes,
                                                       air_data=air_profile, load_profile=load_profile[:, tank],
                                                       insulation_data=insulation)
                    final_fuel += tanks_changes[tank][-1, 4]*number_of_tanks
                    initial_fuel += tanks_changes[tank][1, 4]*number_of_tanks
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

def defineLoadProfile(profile = np.zeros((2, 3)), start_time = 0, end_time = 1, load = 1):
    loadProfile = np.zeros((profile.shape[0]))
    starting_index = 0
    ending_index = 1
    for index in range(profile[:, 0].shape[0]):
        time = profile[index, 0]
        if time == start_time:
            starting_index = index
            loadProfile[starting_index] = load
            break
        elif time < start_time < profile[index + 1, 0]:
            starting_index = index
            loadProfile[starting_index] = (start_time - time)/(profile[index+1, 0] - time)*load
            break
    for index in range(profile[:, 0].shape[0]):
        time = profile[index, 0]
        if time == end_time:
            ending_index = index
            loadProfile[ending_index] = load
            break
        elif time < end_time < profile[index + 1, 0]:
            ending_index = index
            loadProfile[ending_index] = (end_time - time)/(profile[index+1, 0] - time)*load
            break
    loadProfile[starting_index+1:ending_index] = load
    return loadProfile



def calculateNewChanges(changes, profile, shut_off_time):
    before_changes = changes[:shut_off_time[1] - 1, :]
    to_separate = changes[shut_off_time[1], :]
    additional_time = shut_off_time[0] - profile[shut_off_time[1] - 1, 0]
    new_rows = np.array([[additional_time,
                          to_separate[1] * additional_time / to_separate[0],
                          to_separate[2] * additional_time / to_separate[0]],
                         [to_separate[0] - additional_time,
                          to_separate[1] * (to_separate[0] - additional_time) / to_separate[0],
                          to_separate[2] * (to_separate[0] - additional_time) / to_separate[0]]])
    after_changes = changes[shut_off_time[1]:, :]
    changes = np.vstack([before_changes, new_rows, after_changes])
    return changes


def calculateShutOffTime(changes, initial_index, configuration, initial_shut_off_time=0, tank_mass=100,
                         vented_gas=np.zeros([10])):
    required_reserves = tank_mass * configuration["reserve rate"] + configuration["reserve deviation"]
    shut_off_time = initial_shut_off_time
    left_mass_sum = tank_mass - np.sum(vented_gas[:initial_index])
    for index in range(initial_index, changes.shape[0]):
        required_fuel = required_reserves + (vented_gas[-1] - vented_gas[index])
        if left_mass_sum - changes[index, 2] < required_fuel:
            fuel_demand = changes[index, 2] / changes[index, 0]
            shut_off_time += (left_mass_sum - required_fuel) / fuel_demand
            break
        elif index == changes.shape[0]:
            index = changes.shape[0] - 1
            shut_off_time = np.sum(changes[:, 0])
        else:
            left_mass_sum -= (changes[index, 2] + vented_gas[index])
            shut_off_time += changes[index, 0]
            index += 1
    return [shut_off_time, index]
