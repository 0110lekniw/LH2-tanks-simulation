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

venting_pressure = array([120000, 130000, 138000, 150000, 160000, 170000, 180000, 200000])
option = data_options[1]
order = 0
pressure = 138000
if order == 0:
    Simultaneous = True
    data = importData(option, order=orders[0])
    print("Simultaneous")
else:
    Simultaneous = False
    data = importData(option, order = orders[order-1])
    print(orders[order-1])
configuration = importConfiguration()
configuration["pressure_vent"] = pressure

for pressure in venting_pressure:
    for key in data.keys():
        df = pd.DataFrame(data = data[key])
        filepath = str(data["insulation_data"][0]) +"_I_ " +str(pressure/100000)+"_P_"+str(order)+"_S_"+ " Input_" + key+"_"+ file_date("C_" + str(option)) + '.xlsx'
        df.to_excel(filepath, sheet_name=key)

    results = calculateMaximumCruiseDuration(data = data, configuration = configuration, simultaneous=Simultaneous,
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
                filepath = str(data["insulation_data"][0]) +"_I_ " +str(pressure/100000)+"_P_"+str(order)+"_S_"+"C_" + str(option) + " _T_" + str(data["tanks_names"][tank]) +"_" + \
                           file_date("C_ " + str(option)) + '.xlsx'
                df.to_excel(filepath, sheet_name=data["tanks_names"][tank])
        else:
            df = pd.DataFrame(data=results[key])
            filepath = str(data["insulation_data"][0]) +"_I_ " +str(pressure/100000)+"_P_"+str(order)+"_S_"+"C_ " + str(option) + " " + key+"_" + file_date("C_" + str(option)) + '.xlsx'
            df.to_excel(filepath, sheet_name=key)