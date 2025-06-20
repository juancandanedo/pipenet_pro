# En este archivo guardaremos todas nuestras fórmulas de ingeniería.
import numpy as np # Importamos numpy para usar logaritmo y pi

# Constante de la gravedad
G = 9.81 # m/s^2

# Fórmula 1: Calcular la velocidad del agua dentro de la tubería.
def calcular_velocidad(caudal_m3s, diametro_m):
    if diametro_m == 0: return 0
    area = (np.pi * diametro_m**2) / 4
    return caudal_m3s / area

# Fórmula 2: Calcular el Número de Reynolds.
# Este número nos dice si el flujo es tranquilo (laminar) o caótico (turbulento).
def calcular_reynolds(velocidad_ms, diametro_m):
    # Viscosidad cinemática del agua a 20°C (un valor estándar)
    viscosidad_nu = 1.004e-6 # m^2/s
    if diametro_m == 0: return 0
    return (velocidad_ms * diametro_m) / viscosidad_nu

# Fórmula 3: Calcular el factor de fricción 'f'.
# Esta es la ecuación de Swamee-Jain, una versión directa de la famosa ecuación de Colebrook.
def calcular_factor_friccion(reynolds, rugosidad_e, diametro_m):
    # Si el flujo es laminar, la fórmula es muy simple.
    if reynolds < 2300:
        return 64 / reynolds
    
    # Si el flujo es turbulento, usamos la fórmula compleja.
    # No te preocupes por entenderla, ¡solo confía en que funciona!
    if diametro_m == 0: return 0
    parte1 = rugosidad_e / (3.7 * diametro_m)
    parte2 = 5.74 / (reynolds**0.9)
    
    # El np.log10 es el logaritmo base 10 que nos da numpy.
    denominador = (np.log10(parte1 + parte2))**2
    return 0.25 / denominador

# Fórmula 4: Calcular la pérdida de energía por fricción (hf).
# Esta es la famosa ecuación de Darcy-Weisbach.
def calcular_perdida_friccion_hf(factor_friccion_f, longitud_m, diametro_m, velocidad_ms):
    if diametro_m == 0: return 0
    return factor_friccion_f * (longitud_m / diametro_m) * (velocidad_ms**2) / (2 * G)