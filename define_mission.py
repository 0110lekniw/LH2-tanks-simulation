import numpy as np
from air_calculations import calculate_air_properities


def calculateChanges(mission_data, include_apu_flow = False, dt = 10):
    # define the mission variables array[time, height, temperature, pressure, density]
    mission_properties = np.array([0, 0, 0, 0])
    for phase in mission_data:
        time = phase[-1]
        rate_of_climb = 1 / time * (phase[1] - phase[0])
        engine_fuel_flow = phase[2] / time
        apu_fuel_flow = phase[3]
        increment = np.array([1, rate_of_climb, engine_fuel_flow, apu_fuel_flow])
        steps = np.zeros((int(np.floor(time/dt)), increment.shape[0]))
        steps[:, :] = np.multiply(increment, dt)
        if time%dt>0:
            steps = np.vstack((steps, np.multiply(increment, time%dt)))
        mission_properties = np.vstack((mission_properties, steps))
    if not include_apu_flow:
        mission_properties = np.delete(mission_properties, -1, 1)
    return np.multiply(mission_properties, np.array([1, 1, -1]))


def defineProfile(changes, deviation_reserves, rate_reserve, evaporation):
    total_fuel = np.sum(changes[:, 2])
    if changes.shape[1] > 3:
        total_fuel += np.sum(changes[:, 3])
    starting_fuel = total_fuel*(1+rate_reserve/(1-rate_reserve)) + deviation_reserves + evaporation
    profile = np.empty_like(changes)
    profile[0, 2] = starting_fuel
    changes[:, 2] = np.multiply(changes[:, 2], -1)
    for row in range(changes.shape[0]):
        if row == 0:
            profile[row, :1] = changes[row, :1]
        else:
            profile[row, :] = profile[row - 1, :] + changes[row, :]
    return profile


def defineAirProfile(profile):
    air_profile = np.empty_like(profile)
    for row in range(profile.shape[0]):
        air_profile[row, :] = calculate_air_properities(profile[row, 1])
    return air_profile