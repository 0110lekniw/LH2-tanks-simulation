from sympy import nsolve, Symbol


def calculateConductiveHeat(area, conductivity_coefficient, thickness, hot_surface_temperature,
                            cold_surface_temperature):
    heat = conductivity_coefficient * 10 ** (-3) * area * abs(
        hot_surface_temperature - cold_surface_temperature) / thickness
    return heat


def calculateHeat(conductive_heat=0, radiation_heat=0, convection_heat=0, time_step=0):
    heat = 1.3 * (conductive_heat + radiation_heat + convection_heat) * time_step
    return heat


def calculateTankChange(heat=0, energy_derivative=0, total_volume=0, total_engine_flow=0, vaporization_heat=0,
                            density_star=0, vented_pressure=0, tank_pressure=101325):
    if tank_pressure == vented_pressure:
        x = Symbol('x')
        pressure_change = 0
        vented_flow = nsolve(
            heat - (total_engine_flow + x) * vaporization_heat * (x / (total_engine_flow + x) + density_star), x, 0)
    else:
        pressure_change = energy_derivative / total_volume * (
                    heat - total_engine_flow * vaporization_heat * density_star)
        if tank_pressure + pressure_change < vented_pressure:
            vented_flow = 0
        else:
            x = Symbol('x')
            vented_flow = nsolve(energy_derivative / total_volume *
                                 (heat - (total_engine_flow + x) * vaporization_heat *
                                  (x / (total_engine_flow + x) + density_star)) - pressure_change, x, 0)
    return [pressure_change, vented_flow]
