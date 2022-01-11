from exporting import file_date
from input_data import data_options, importData, importConfiguration
from main_functions import calculateMaximumCruiseDuration
import pandas as pd
from numpy import array

# import data
orders = array([["Wing", "Front", "Aft"],
          ["Front", "Wing", "Aft"],
          ["Front", "Aft", "Wing"],
          ["Aft", "Front", "Wing"],
          ["Aft", "Wing", "Front"],
          ["Wing", "Aft", "Front"]])

venting_pressure = array([120000, 130000, 140000, 150000, 160000, 170000, 180000, 200000])
option = data_options[0]
for order in range(orders.shape[0]):
    data = importData(option, order = orders[order])
    configuration = importConfiguration()
    print(orders[order])
    for key in data.keys():
        df = pd.DataFrame(data = data[key])
        filepath = "Configuration " + str(option) + " Input" + key+"_O_"+str(order) +"_"+ file_date("Configuration " +
                                                                                                 str(option)) + '.xlsx'
        df.to_excel(filepath, sheet_name=key)

    results = calculateMaximumCruiseDuration(data = data, configuration = configuration, simultaneous=False,
                                             insulation_data=data["insulation_data"][0])
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
                filepath = "C_" + str(option) + " _T_" + str(data["tanks_names"][tank]) +"_O_"+str(order)+ "_" + \
                           file_date("Configuration " + str(option)) + '.xlsx'
                df.to_excel(filepath, sheet_name=data["tanks_names"][tank])
        else:
            df = pd.DataFrame(data=results[key])
            filepath = "Configuration " + str(option) + " " + key+"_O_"+str(order)+ "_" + file_date("Configuration " + str(option)) + '.xlsx'
            df.to_excel(filepath, sheet_name=key)