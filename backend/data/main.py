# Le decimos a Python: "Oye, trae los planos que están en models.py"
from models import Nodo, Tuberia
import networkx as nx # Importamos la herramienta para hacer mapas

# --- 1. CREAMOS NUESTRAS PIEZAS (Nodos y Tuberías) ---
print("Paso 1: Creando las piezas de nuestra red...")

# Creamos los nodos. El rociador 1 pide 15 litros por segundo.
# El rociador 2 pide 20. La bomba no pide nada.
nodo_bomba = Nodo(id_nodo="Bomba", elevacion=100)
nodo_union = Nodo(id_nodo="Union", elevacion=102)
nodo_rociador1 = Nodo(id_nodo="Rociador1", elevacion=105, demanda=15.0)
nodo_rociador2 = Nodo(id_nodo="Rociador2", elevacion=104, demanda=20.0)

# Creamos las tuberías, diciendo qué nodos conectan.
tuberia1 = Tuberia(id_tuberia="T1", nodo_inicio=nodo_bomba, nodo_fin=nodo_union)
tuberia2 = Tuberia(id_tuberia="T2", nodo_inicio=nodo_union, nodo_fin=nodo_rociador1)
tuberia3 = Tuberia(id_tuberia="T3", nodo_inicio=nodo_union, nodo_fin=nodo_rociador2)

# Guardamos todas nuestras piezas en listas para tenerlas ordenadas.
nodos = [nodo_bomba, nodo_union, nodo_rociador1, nodo_rociador2]
tuberias = [tuberia1, tuberia2, tuberia3]

# --- 2. CREAMOS EL MAPA DE LA RED ---
# Usamos la herramienta 'networkx' para entender las conexiones
G = nx.DiGraph() # DiGraph significa "Grafo Dirigido" (el agua va en una dirección)

# Añadimos las tuberías como las "calles" de nuestro mapa.
# Los nodos se añaden automáticamente.
for t in tuberias:
    G.add_edge(t.nodo_inicio.id, t.nodo_fin.id, data=t) # Guardamos el objeto tubería

# --- 3. LA RECETA PARA CALCULAR CAUDALES ---
print("Paso 2: Calculando los caudales...")

# Un diccionario para guardar el caudal de cada tubería
caudales = {t.id: 0.0 for t in tuberias}
# Un diccionario para guardar la demanda de cada nodo
demandas = {n.id: n.demanda for n in nodos}

# La herramienta 'networkx' nos da los nodos en orden, desde el final hasta el principio.
# Esto es perfecto para sumar caudales hacia atrás.
nodos_en_orden_inverso = reversed(list(nx.topological_sort(G)))

for nodo_id in nodos_en_orden_inverso:
    # El caudal que sale de este nodo es su propia demanda
    # más el caudal de todas las tuberías que ya hemos calculado que salen de él.
    caudal_saliente_total = demandas[nodo_id]
    for tuberia_saliente in G.successors(nodo_id):
        # Buscamos la tubería que conecta nodo_id con tuberia_saliente
        tuberia_obj = G.edges[nodo_id, tuberia_saliente]['data']
        caudal_saliente_total += caudales[tuberia_obj.id]
    
    # Ahora, buscamos la tubería que LLEGA a este nodo
    # Su caudal debe ser igual a todo lo que sale del nodo.
    predecesores = list(G.predecessors(nodo_id))
    if predecesores:
        nodo_anterior_id = predecesores[0]
        tuberia_entrante = G.edges[nodo_anterior_id, nodo_id]['data']
        caudales[tuberia_entrante.id] = caudal_saliente_total

# --- 4. ACTUALIZAMOS NUESTRAS PIEZAS Y MOSTRAMOS RESULTADOS ---
print("¡Cálculo terminado! Actualizando piezas...")

# Ponemos los resultados del cálculo en nuestros objetos de tubería
for t in tuberias:
    t.caudal_calculado = caudales[t.id]

print("\n--- RESULTADOS FINALES ---")
print(tuberias)

print("\nAnálisis:")
print(f"El agua que necesita el Rociador 1 es: {nodo_rociador1.demanda} l/s.")
print(f"Por lo tanto, la Tubería 2 debe llevar: {tuberia2.caudal_calculado} l/s.")
print(f"El agua que necesita el Rociador 2 es: {nodo_rociador2.demanda} l/s.")
print(f"Por lo tanto, la Tubería 3 debe llevar: {tuberia3.caudal_calculado} l/s.")
print(f"La Tubería 1 debe llevar el agua para AMBAS, así que su caudal es {tuberia2.caudal_calculado} + {tuberia3.caudal_calculado} = {tuberia1.caudal_calculado} l/s.")
print(f"¡El caudal total que la bomba debe impulsar es {tuberia1.caudal_calculado} l/s!")