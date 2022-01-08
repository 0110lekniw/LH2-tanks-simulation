from exporting import file_date
from input_data import data_options, importData, importConfiguration
from main_functions import calculateMaximumCruiseDuration
import pandas as pd

# import data
option = data_options[0]
data = importData(option)
configuration = importConfiguration()
insulation_thickness = 0.065  # m

results = calculateMaximumCruiseDuration()
# the results consist of four arrays:
# first is the mission profile consisting of three columns [time, altitude, engine fuel flow] and if included apu flow
# second is the air profile containing air: pressure, temperature and density
# third is the time dependent properties inside each of the tanks. If two tanks are included: for one position,
# only one array is created
# fourth is the initial data of the mission profile, or tanks data depending on used function
for keys in results.keys():
    if
for tank in results[2]:
    ## convert your array into a dataframe
    indexes = results["mission_profile"][:, 0]
    df = pd.DataFrame(data = results[2][tank][1:, :], index=indexes[1:], columns=["Tank Pressure", "Vent Flow", "Fill Level", "Engine Flow",
                                                                          "Liquid Hydrogen Mass", "Gas Hydrogen Mass"])
    ## save to xlsx file
    filepath =  "Configuration " + str(option) + " Tank " + str(data["tanks_names"][tank]) +" " + \
                file_date("Configuration " + str(option)) + '.xlsx'
    df.to_excel(filepath, sheet_name=data["tanks_names"][tank])
df = pd.DataFrame(data = results[3], columns=["Starting Altitude", "Finished Altitude", "Fuel Used", "APU Flow", "Duration"])

filepath = "Configuration " + str(option) + " Profile" + file_date("Configuration " + str(option)) + '.xlsx'
df.to_excel(filepath, sheet_name="Profile")
