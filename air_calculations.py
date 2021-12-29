from numpy import array
from math import e

# air International Standard Atmosphere properties
airISA = array([101325, 1.225, 288.15, 340.294, 9.80665, 36089])


def calculate_air_temperature(height):
    if height >= airISA[-1]:
        return 216.65
    else:
        return airISA[2] - 1.98 * height / 1000


def calculate_air_pressure(height, temperature):
    pressure_troposphere = airISA[0] * (1 - 0.001982 * height / temperature)
    if height >= airISA[-1]:
        pressure_tropopause = pressure_troposphere * e ** (airISA[-2] /
                                                           (287 * temperature * (
                                                                   height - airISA[-1])))
        return pressure_tropopause
    else:
        return pressure_troposphere


def calculate_air_density(temperature, pressure):
    return pressure / (287 * temperature)


def calculate_air_properities(height):
    temp = calculate_air_temperature(height)
    press = calculate_air_pressure(height, temp)
    dens = calculate_air_density(temp, press)
    return array([temp, press, dens])
