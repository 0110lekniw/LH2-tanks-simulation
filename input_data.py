import numpy as np
from numpy import array

data_options = ["main_configuration", "alternate_configuration"]


def defineTankData(order=array(["Wing", "Front", "Aft"])):
    tanks = {
        "Front": array([2, 11.609, 2.602, 0.465, 1.170, True, 0.10]),  # Front Tank
        "Wing": array([2, 21.992, 5.236, 0.500, 1.000, False, 0.065]),  # Wing Tank
        "Aft": array([1, 20.950, 7.324, 0.392, 1.056, False, 0.06]),  # Aft Tank
    }
    returned_data = tanks[order[0]]
    if order.shape[0] > 1:
        for tank in range(order.shape[0]-1):
            returned_data = np.vstack((returned_data, tanks[order[tank+1]]))
    return returned_data


def importConfiguration():
    # Configuration of the tanks
    configuration = {"pressure_tank": 100000,  # Pa
                     "pressure_vent": 138000,  # Pa
                     "lh2_fill_0": 0.97,  # Initial ratio of liquid hydrogen volume to total volume
                     "reserve rate": 0.05,  # amount of fuel needed at the end of the flight
                     "reserve deviation": 0}
    return configuration


# define initial data

def importData(option, order):
    # Missions Definition [H0    ,H-1   ,engine  ,apu    ,time   ]
    #                     [ft    ,ft    ,kg      ,kg/s   ,s      ]

    # Tanks Definition                [No.   ,area   ,volume  ,semi_axis   ,Outer/Inner, Cargo]
    #                                 [-     ,m2     ,m3      ,m           ,-          , Bool ]
    tanks_data = defineTankData(order=order)
    match option:
        case "main_configuration":
            data = {
                "mission_profile": array([
                    [0, 0, 0, 0.0802, 1800.00],  # taxiing
                    [0, 1500, 25.433, 0.0883, 26.09],  # take-off
                    [1500, 5000, 73.750, 0.0883, 81.64],  # climb 1500->5000
                    [5000, 25000, 178.159, 0.0883, 263.02],  # climb 5000->25000
                    [25000, 35000, 192.588, 0.0883, 192.59],  # climb 25000->35000
                    [35000, 40000, 45.289, 0.0883, 142.03],  # climb 35000->40000
                    [40000, 40000, 824.000, 0.0568, 6591.64],  # cruise 40000
                    [40000, 10000, 89.472, 0.0794, 957.11],  # descent 40000 -> 10000
                    [10000, 1500, 58.262, 0.0794, 452.11],  # descent 10000 -> 1500
                    [1500, 1500, 225.000, 0.0568, 1800.00],  # descent 10000 -> 1500
                ]),  # with external tanks,
                "tanks_data": tanks_data,
                "sum_volumes": array([2 * 2.602 + 2 * 5.236 + 7.324, ]),  # m3
                "tanks_names": array(["Front", "Wing", "Aft"]),
                "insulation_data": array([[20.9, 35],  # Corafoam Pb35
                                          [11.8, 150],  # Spaceloft
                                          [18, 50],  # MLI Mylar + Polynet 20 layers
                                          [32.3, 118],  # Foamglass
                                          [22.6, 37],  # BX-265
                                          [26, 67]])  # Glass bubble type k1
            }
            return data
        case "alternate_configuration":
            data = {
                "mission_profile": array([
                    [0, 0, 0, 0.0802, 1800.00],  # taxiing
                    [0, 1500, 25.635, 0.0883, 25.63],  # take-off
                    [1500, 5000, 71.153, 0.0883, 78.77],  # climb 1500->5000
                    [5000, 25000, 165.464, 0.0883, 244.28],  # climb 5000->25000
                    [25000, 35000, 74.319, 0.0883, 167.38],  # climb 25000->35000
                    [35000, 40000, 39.902, 0.0883, 125.13],  # climb 35000->40000
                    [40000, 40000, 752.000, 0.0568, 6640.73],  # cruise 40000
                    [40000, 10000, 38.984, 0.0794, 957.11],  # descent 40000 -> 10000
                    [10000, 1500, 34.307, 0.0794, 452.11],  # descent 10000 -> 1500
                    [1500, 1500, 203.000, 0.0568, 1800.00],  # descent 10000 -> 1500
                ]),  # without external tanks
                "tanks_data": array([
                    [1, 37.620, 19.425, 0.666, 1.073, False],  # Front Tank
                    [1, 16.763, 5.167, 0.347, 1.120, False],  # Aft Tank
                ])
                ,
                "sum_volumes": 19.425 + 5.167,  # m3
                "tanks_names": array(["Front Alternate", "Aft Alternate"])
            }
            return data


# physical constants
physical_constants = array([5.68 * 10 ** (-8),  # Steffan-Boltzmann
                            0.95,  # Radiation Emittance
                            287])  # Gaseous Constant
# Options names


coefficient_material = [11314.56, -30824.32, 34964.24, -21141.43, 7187.43, -1302.708, 98.35252]  # PVC foam
density_insulation = 20.2  # kg/m3nt

conductivity_insulation = 0.020
