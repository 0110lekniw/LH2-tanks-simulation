from sympy import nsolve, Symbol


def findQuadraticRoots(a, b, c):
    delta = b**2 - 4*a*c
    if delta > 0:
        first_root = (-b-delta**(1/2))/(2*a)
        second_root = (-b+delta**(1/2))/(2*a)
        return [first_root, second_root]
    elif delta == 0:
        root = first_root = (-b)/(2*a)
        return root
    else:
        print("No Real Roots")

def calculateConductiveHeat(area, conductivity_coefficient, thickness, hot_surface_temperature,
                            cold_surface_temperature):
    heat = conductivity_coefficient * 10 ** (-3) * area * abs(
        hot_surface_temperature - cold_surface_temperature) / thickness
    return heat


def calculateHeat(conductive_heat=0, radiation_heat=0, convection_heat=0, time_step=0):
    heat = 1.3 * (conductive_heat + radiation_heat + convection_heat) * time_step
    return heat


def calculateTankChange(heat=0, energy_derivative=0, total_volume=0, total_engine_flow=0, vaporization_heat=0,
                            liquid_density=71, gas_density = 1, vented_pressure=0, tank_pressure=101325):
    density_star = gas_density/(liquid_density+gas_density)
    if tank_pressure == vented_pressure:
        x = Symbol('x')
        pressure_change = 0
        if total_engine_flow == 0:
            vented_flow = heat / (vaporization_heat * (1 + density_star))
        else:
            vented_flow = nsolve(
                heat - (total_engine_flow + x) * vaporization_heat * (x / (total_engine_flow + x) + density_star), x, 0)
    else:
        pressure_change = energy_derivative / total_volume * (
                    heat - total_engine_flow * vaporization_heat * density_star)
        if tank_pressure + pressure_change < vented_pressure:
            vented_flow = 0
        else:
            pressure_change = vented_pressure - tank_pressure
            if total_engine_flow == 0:
                vented_flow = (heat - pressure_change)/(vaporization_heat*(1+density_star))
            else:
                a = 1+density_star
                b = total_engine_flow*(1+2*density_star)-(heat-pressure_change*total_volume/energy_derivative)/\
                    vaporization_heat
                c = -total_engine_flow*(-total_engine_flow*density_star+
                                        (heat-pressure_change*total_volume/energy_derivative)/vaporization_heat)
                vented_flow2 = findQuadraticRoots(a, b, c)
                vented_flow = vented_flow2[0]
                if vented_flow2[1] > 0:
                    vented_flow = vented_flow2[1]
    change_liquid_volume = (vented_flow + total_engine_flow) * (1 / (liquid_density - gas_density))/total_volume
    return [pressure_change, vented_flow, change_liquid_volume]
