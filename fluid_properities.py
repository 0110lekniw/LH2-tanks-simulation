import CoolProp.CoolProp as cp
import numpy as np
from math import log, e
from numpy import array, zeros


def calculateEnergyDerivative(density, pressure_tank):
    energy_derivative = -0.053 * log(density, e) + 0.2791 - (138000 - pressure_tank) / (25 * 138000)
    return energy_derivative
# calculation of the pure liquid and pure gas properties using CoolProp library - Helmholtz Energy EoS based on pressure
def calculateFluidProperties(pressure=101325, volume=1, vapor=False, fluid="hydrogen") -> array:
    Q = 0
    if vapor:
        Q = 1
    properties_names = ["P", "D", "T", "H", "volume", "mass"]
    properties = zeros([len(properties_names)])
    for property in properties_names:
        match property:
            case "P":
                properties[properties_names.index(property)] = pressure
            case "volume":
                properties[properties_names.index(property)] = volume
            case "mass":
                density_index = properties_names.index("D")
                if properties[density_index] != 0:
                    properties[properties_names.index(property)] = volume*properties[density_index]
                else:
                    properties[density_index] = cp.PropsSI("D", "P", pressure, "Q", Q, fluid)
                    properties[properties_names.index(property)] = volume*properties[density_index]
            case _:
                properties[properties_names.index(property)] = cp.PropsSI(property, "P", pressure, "Q", Q, fluid)
    return properties

def calculateMixtureProperties(liquid_properties = zeros([5]), vapor_properties= zeros([5])) -> array:
    quality = vapor_properties[-1]/(liquid_properties[-1] + vapor_properties[-1])
    returned_properties = np.empty(liquid_properties.shape[0]+1)
    returned_properties[-3:-1] = liquid_properties[-2:] + vapor_properties[-2:]
    returned_properties[-4] = - liquid_properties[-4] + vapor_properties[-4]  # vaporization heat
    returned_properties[-1] = vapor_properties[1]/(vapor_properties[1]+liquid_properties[1])  # density star
    for element in range(returned_properties.shape[0]-4):
        returned_properties[element] = quality*vapor_properties[element] + (1-quality)*liquid_properties[element]
    return returned_properties

# calculate mass of the liquid hydrogen, gaseous hydrogen and tank properties
def calculateHydrogen(pressure, volume_tot, fill_level):
    hydrogen_liquid = calculateFluidProperties(pressure=pressure, volume=volume_tot * fill_level,
                                               vapor=False, fluid="hydrogen")
    hydrogen_gas = calculateFluidProperties(pressure=pressure,
                                            volume=volume_tot * (1 - fill_level),
                                            vapor=True, fluid="hydrogen")
    hydrogen_mixture = calculateMixtureProperties(hydrogen_liquid, hydrogen_gas)
    return np.hstack([hydrogen_mixture, hydrogen_liquid[-1], hydrogen_gas[-1],
                      calculateEnergyDerivative(hydrogen_mixture[1], hydrogen_mixture[0])])