# Este es el plano para cualquier NODO de nuestra red.
class Nodo:
    # El "constructor" se ejecuta cuando creamos un nuevo nodo.
    # Le damos un nombre (id), una altura (elevacion) y cuánta agua pide (demanda).
    def __init__(self, id_nodo, elevacion, demanda=0.0):
        self.id = id_nodo
        self.elevacion = elevacion
        self.demanda = demanda # Por defecto, un nodo no pide agua.

    # Esto es para que cuando imprimamos un nodo, se vea bonito.
    def __repr__(self):
        return f"Nodo({self.id}, Demanda={self.demanda} l/s)"

# --- ESTA ES LA CLASE QUE VAMOS A MEJORAR ---
# Este es el plano para cualquier TUBERÍA de nuestra red.
# ==============================================================================
#           CONTENIDO ACTUALIZADO PARA: backend/models.py (con accesorios)
# ==============================================================================

# La clase Nodo no cambia.

class Tuberia:
    # El constructor ahora acepta una lista de accesorios
    def __init__(self, id_tuberia, nodo_inicio, nodo_fin, longitud_m, diametro_mm, material, accesorios=[]):
        self.id = id_tuberia
        self.nodo_inicio = nodo_inicio
        self.nodo_fin = nodo_fin
        
        self.longitud = longitud_m
        self.diametro = diametro_mm / 1000

        self.material = material
        self.rugosidad_e = self.obtener_rugosidad()
        
        # ¡NUEVO! Guardamos la lista de accesorios que nos pasan.
        self.accesorios = accesorios

        # Propiedades calculadas
        self.caudal_calculado_m3s = 0.0
        self.velocidad = 0.0
        self.reynolds = 0.0
        self.factor_friccion = 0.0
        self.perdida_friccion_hf = 0.0
        
        # ¡NUEVO! Propiedades para pérdidas locales
        self.perdida_locales_hl = 0.0
        self.perdida_total = 0.0 # hf + hl

    def obtener_rugosidad(self):
        rugosidades = {
            "PVC": 0.0000015,
            "Acero": 0.000045,
            "Hierro Fundido": 0.00026
        }
        return rugosidades.get(self.material, 0.000045)

    def __repr__(self):
        return (f"Tubería({self.id}, D={self.diametro*1000}mm, L={self.longitud}m, "
                f"Q={self.caudal_calculado_m3s * 1000:.2f} l/s, "
                f"V={self.velocidad:.2f} m/s, h_total={self.perdida_total:.3f} m)")