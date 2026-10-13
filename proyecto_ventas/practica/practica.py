""" Ejercicio 1 · Quitar duplicados conservando el orden
Dada ciudades = ["Quito","Guayaquil","Quito","Cuenca","Guayaquil"], obtén una lista sin repetidos respetando el orden de aparición (un set solo no alcanza). """
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
ciudades_sin_dup=[]
vistas = set()

for ciudad in ciudades:
    if ciudad not in vistas:
        vistas.add(ciudad)
        ciudades_sin_dup.append(ciudad)

print(ciudades_sin_dup)  # ['Quito', 'Guayaquil', 'Cuenca']

""" Ejercicio 2 · Contar con un diccionario
Con la misma lista, arma un diccionario {"Quito": 2, "Guayaquil": 2, "Cuenca": 1} """
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
conteo = {}

for ciudad in ciudades:
    conteo[ciudad] = conteo.get(ciudad, 0) + 1

mas_repetida = max(conteo, key=conteo.get)

print(conteo)  # {'Quito': 2, 'Guayaquil': 2, 'Cuenca': 1}
print(mas_repetida)  # 'Quito'

"""Ejercicio 3 · Conjuntos en acción
inscritos_matematica = {"Ana","Luis","Sol","Marco"} y 
inscritos_ingles = {"Luis","Marco","Ruth"}. 
Responde con código: ¿quiénes están en las dos?, ¿quiénes solo en matemática?, ¿cuántos estudiantes distintos hay en total?"""
inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
inscritos_ingles = {"Luis", "Marco", "Ruth"}    

ambas       = inscritos_matematica & inscritos_ingles     # {'Luis','Marco'}
solo_mate   = inscritos_matematica - inscritos_ingles     # {'Ana','Sol'}
total       = len(inscritos_matematica | inscritos_ingles)  # 5

print(sorted(ambas), sorted(solo_mate), total)


"""Ejercicio 4 · De lista de diccionarios a índice
Con clientes = [{"id":1,"nombre":"Ana"},{"id":2,"nombre":"Luis"}], crea un diccionario {id: cliente} para acceder por id sin recorrer la lista. Luego imprime el nombre del id 2."""

clientes = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]
indice_clientes = {cliente["id"]: cliente for cliente in clientes}          
print(indice_clientes[2]["nombre"])  # 'Luis'   


"""Ejercicio 5 · Tuplas como registros inmutables
Dada ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)], imprime el mes con mayor venta y el total, usando desempaquetado de tuplas."""

ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]
total = sum(monto for _mes, monto in ventas)

mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])

print(f"Total: {total}")
print(f"Mejor mes: {mejor_mes} con {mejor_monto}")

for mes, monto in ventas:              # desempaquetado en el for
    print(f"{mes:<10} {monto}")


"""Ejercicio 7 · ¿Instancia, de clase o estático?
Clasifica cada método y justifica: (a) calcular el total de una venta, (b) crear un objeto Producto a partir de un diccionario, 
(c) saber si un precio es válido, (d) saber si un producto tiene stock bajo, (e) calcular el IVA de cualquier monto."""

# (a) Calcular el total de una venta -> de instancia.
#     Necesita la cantidad y el precio unitario de esa venta en particular,
#     o sea que trabaja con self.

# (b) Crear un Producto desde un diccionario -> de clase.
#     Todavía no existe ningún objeto, justo lo va a crear, así que en vez
#     de self usa cls y devuelve cls(...). Es desde_diccionario().

# (c) Ver si un precio es válido -> estático.
#     Solo revisa que el número sea mayor a 0. No le importa qué producto
#     sea, y se usa antes de crear el producto.

# (d) Ver si hay stock bajo -> de instancia.
#     Compara el stock de ese producto (self.stock) con STOCK_MINIMO,
#     por eso necesita el objeto.

# (e) Calcular el IVA de un monto -> estático.
#     Le llega un monto cualquiera y devuelve el monto con IVA. No depende
#     de ningún producto.


"""Ejercicio 8 · Un modelo nuevo con herencia
Agrega la clase Proveedor, que hereda de Persona y suma ruc y empresa. Escribe __init__, a_diccionario() y etiqueta() reutilizando al padre."""

# La clase Proveedor está en models.py (es un modelo, igual que Cliente).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Proveedor

p = Proveedor.desde_diccionario({"id": 1, "nombre": "Luis", "apellido": "Mora",
                                 "email": "luis@x.com", "ruc": "0912345678001",
                                 "empresa": "Importadora Sur"})
print(p)


"""Ejercicio 9 · Polimorfismo sin if
Esta función tiene el olor a "falta polimorfismo". Reescríbela sin ningún if de tipo."""

# Versión original (con if):
# def describir(objeto, tipo):
#     if tipo == "cliente":
#         return f"{objeto.nombre} {objeto.apellido} de {objeto.ciudad}"
#     elif tipo == "producto":
#         return f"{objeto.nombre} a ${objeto.precio}"
#     elif tipo == "venta":
#         return f"venta de {objeto.cantidad} unidades"

# Versión nueva (polimórfica): cada clase ya sabe describirse con etiqueta().
def describir(objeto):
    return objeto.etiqueta()

print(describir(p))