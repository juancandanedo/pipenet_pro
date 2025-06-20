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


# Este es el plano para cualquier TUBERÍA de nuestra red.
class Tuberia:
    # El constructor de la tubería.
    # Le damos un nombre, de dónde empieza y dónde termina.
    def __init__(self, id_tuberia, nodo_inicio, nodo_fin):
        self.id = id_tuberia
        self.nodo_inicio = nodo_inicio
        self.nodo_fin = nodo_fin
        
        # Al principio, no sabemos cuánta agua pasa por aquí.
        self.caudal_calculado = 0.0

    def __repr__(self):
        return f"Tubería({self.id}, Caudal={self.caudal_calculado} l/s)"