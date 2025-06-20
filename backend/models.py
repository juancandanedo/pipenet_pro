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
class Tuberia:
    # El constructor de la tubería ahora pide más datos.
    def __init__(self, id_tuberia, nodo_inicio, nodo_fin, longitud_m, diametro_mm, material):
        self.id = id_tuberia
        self.nodo_inicio = nodo_inicio
        self.nodo_fin = nodo_fin
        
        # Nuevas propiedades geométricas
        self.longitud = longitud_m
        self.diametro = diametro_mm / 1000 # Convertimos de mm a metros al instante!

        # Propiedades del material y del flujo
        self.material = material
        self.rugosidad_e = self.obtener_rugosidad() # Llamamos a una función para obtener 'e'

        # Propiedades que calcularemos después
        self.caudal_calculado_m3s = 0.0 # Ahora lo guardaremos en metros cúbicos/segundo
        self.velocidad = 0.0
        self.reynolds = 0.0
        self.factor_friccion = 0.0
        self.perdida_friccion_hf = 0.0

    # Nueva función para obtener la rugosidad 'e' según el material.
    # ¡Esto es como una pequeña base de datos dentro de nuestro plano!
    def obtener_rugosidad(self):
        # Diccionario de materiales y su rugosidad absoluta (e) en metros.
        rugosidades = {
            "PVC": 0.0000015,   # Muy liso
            "Acero": 0.000045,    # Un poco más rugoso
            "Hierro Fundido": 0.00026 # Bastante rugoso
        }
        # Devuelve el valor para el material de esta tubería.
        # Si el material no está en la lista, usamos Acero por defecto.
        return rugosidades.get(self.material, 0.000045)

    def __repr__(self):
        # Actualizamos la forma en que se imprime la tubería para ver más datos.
        return (f"Tubería({self.id}, D={self.diametro*1000}mm, L={self.longitud}m, "
                f"Q={self.caudal_calculado_m3s * 1000:.2f} l/s, "
                f"V={self.velocidad:.2f} m/s, hf={self.perdida_friccion_hf:.3f} m)")

# Este es el plano para cualquier TUBERÍA de nuestra red.
