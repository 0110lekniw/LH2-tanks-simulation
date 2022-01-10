from exporting import file_date
from input_data import data_options, importData, importConfiguration
from main_functions import calculateMaximumCruiseDuration
import pandas as pd
from numpy import array

# import data
orders = {1: array(["Wing", "Front", "Aft"]),
          2: array(["Front", "Wing", "Aft"]),
          3: array(["Front", "Aft", "Wing"]),
          4: array(["Aft", "Front", "Wing"]),
          5: array(["Aft", "Wing", "Front"]),
          6: array(["Wing", "Aft", "Front"])
          }
option = data_options[0]
data = importData(option, order = orders[4])
configuration = importConfiguration()
for key in data.keys():
    df = pd.DataFrame(data = data[key])
    filepath = "Configuration " + str(option) + " Input" + key + file_date("Configuration " + str(option)) + '.xlsx'
    df.to_excel(filepath, sheet_name=key)
for insulation in data["insulation_data"]:
    results = calculateMaximumCruiseDuration(data = data, configuration = configuration, simultaneous=False,
                                             insulation_data=insulation)
    # the results consist of four arrays:
    # first is the mission profile consisting of three columns [time, altitude, engine fuel flow] and if included apu flow
    # second is the air profile containing air: pressure, temperature and density
    # third is the time dependent properties inside each of the tanks. If two tanks are included: for one position,
    # only one array is created
    # fourth is the initial data of the mission profile, or tanks data depending on used function
    for key in results.keys():
        if type(results[key]) is dict:
            for tank in results[key]:
                ## convert your array into a dataframe
                df = pd.DataFrame(data=results[key][tank], columns=["Tank Pressure", "Vent Flow", "Fill Level",
                                                                    "Engine Flow", "Liquid Hydrogen Mass",
                                                                    "Gas Hydrogen Mass", "Evaporated Hydrogen"])
                ## save to xlsx file
                filepath = "C_" + str(option) + " _T_" + str(data["tanks_names"][tank]) +"_I_"+insulation[0]+ " " + \
                           file_date("Configuration " + str(option)) + '.xlsx'
                df.to_excel(filepath, sheet_name=data["tanks_names"][tank])
        else:
            df = pd.DataFrame(data=results[key])
            filepath = "Configuration " + str(option) + " " + key+"_I_"+insulation[0] + file_date("Configuration " + str(option)) + '.xlsx'
            df.to_excel(filepath, sheet_name=key)