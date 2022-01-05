from define_mission import calculateChanges, defineProfile, defineAirProfile
from input_data import data_options, importData, importConfiguration
from simulate_tank import simulateTank
import numpy as np
import pandas as pd
import os
import datetime
def file_date(filename):
    with open(filename, 'w') as file1:
        pass

    path = os.path.abspath(filename)

    timestamp = os.path.getctime(path)

    date_created = datetime.date.today()

    str_DT = date_created.strftime('%Y-%m-%d')

    return str_DT

# import data
option = data_options[0]
data = importData(option)
configuration = importConfiguration()
insulation_thickness = 0.065  # m
initialFuel = 2000
finalFuel = -100
mission_profile = data["mission_profile"]
negative_time = -1
tanks_changes = {}
while negative_time != 0:
    # initiation  - calculate fuel demand and altitude in time
    changes = calculateChanges(mission_profile, False, dt=10)
    time_steps = changes[:, 0]
    # initiation - calculate necessary amount of fuel in tanks and air properties (temperature, density and pressure)
    profile = defineProfile(changes, configuration["reserve deviation"], configuration["reserve rate"], evaporation=0)
    airProfile = defineAirProfile(profile)

    # calculate evaporation of the liquid hydrogen in tanks and vented hydrogen flow for each of the tanks

    # load profile indicates the percentage of demanded fuel flow from each of the tanks.
    # For first option this value is proportional to tanks volume to total tanks' volume ratio
    load_profile = np.zeros((time_steps.shape[0], data["tanks_data"].shape[0]))
    for tank in range(data["tanks_data"].shape[0]):
        insulation = np.hstack((data["insulation_data"][0], data["tanks_data"][tank][-1]))
        load_profile[:, tank] = -data["tanks_data"][tank][2] / data["sum_volumes"]
        tanks_changes[tank] = simulateTank(time_steps=time_steps, configuration=configuration,
                                           tank_data=data["tanks_data"][tank][:-2], mission_data=changes,
                                           air_data=airProfile, load_profile=load_profile[:, tank],
                                           insulation_data=insulation)
        if tank == 0:
            finalFuel = tanks_changes[tank][-1, 4] * data["tanks_data"][tank][0]
            initialFuel = tanks_changes[tank][1, 4] * data["tanks_data"][tank][0]
        else:
            finalFuel += tanks_changes[tank][-1, 4] * data["tanks_data"][tank][0]
            initialFuel += tanks_changes[tank][1, 4] * data["tanks_data"][tank][0]
    fuel_demand = (mission_profile[6, 2] / mission_profile[6, -1])
    negative_time = round((initialFuel * configuration["reserve rate"] + configuration["reserve deviation"] - finalFuel)
                          / fuel_demand, 1)
    mission_profile[6, -1] -= negative_time
    mission_profile[6, 2] = fuel_demand*mission_profile[6, -1]
    print("Iteration finished. Final Fuel is:", finalFuel, "whats equal to:", round(finalFuel/initialFuel*100, 2)
          , "% of initial fuel")
for tank in tanks_changes:
    ## convert your array into a dataframe
    indexes = profile[:, 0]
    df = pd.DataFrame(data = tanks_changes[tank][1:, :], index=indexes[1:], columns=["Tank Pressure", "Vetn Flow", "Fill Level", "Engine Flow",
                                                                          "Liquid Hydrogen Mass", "Gas Hydrogen Mass"])
    ## save to xlsx file
    filepath =  "Configuration " + str(option) + " Tank " + str(data["tanks_names"][tank]) +" "+\
                                                            file_date("Configuration "+str(option)) + '.xlsx'
    df.to_excel(filepath, sheet_name=data["tanks_names"][tank])
df = pd.DataFrame(data = mission_profile, columns=["Starting Altitude", "Finished Altitude", "Fuel Used", "APU Flow", "Duration"])

filepath = "Configuration " + str(option) + " Profile"+file_date("Configuration "+str(option)) + '.xlsx'
df.to_excel(filepath, sheet_name="Profile")
