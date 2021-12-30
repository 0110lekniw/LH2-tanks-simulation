def calculateConductiveHeat(area, conductivity_coefficient, thickness, hot_surface_temperature, cold_surface_temperature):
    heat = conductivity_coefficient*10**(-3)*area*abs(hot_surface_temperature -cold_surface_temperature)/thickness
    return heat


def calculateHeat(conductive_heat = 0, radiation_heat = 0, convection_heat = 0, time_step = 0):
    heat = 1.3*(conductive_heat + radiation_heat + convection_heat)*time_step
    return heat