from subprocess import run
from sys import maxsize
import argparse
from random import randrange
""" Diseño de datos:
    Representaremos un laberinto como una lista de listas (una matriz) donde cada lista representa
    una fila y la posicion en esa lista, la columna. Lo que se encuentra en cada casilla del laberinto se representa
    a traves de un caracter string.

    Para representar la ubicacion, posicion, coordenadas de una casilla o nodo del laberinto usaremos una dupla (int,int)
    donde el primer elemento representa la fila-1 y el segundo la columna-1. Tambien cuando nos referimos a nodo, objetivo
    o inicio, en realidad nos referimos a sus coordenadas.

    El programa comienza generando un numero random que sera la seedrand para el programa en C, luego ejecuta el archivo
    compilado de C pasando como argumentos el archivo de entrada, el nombre del texto de salida y la seedrand.
    
    En caso que el laberinto no tenga solucion, se generan laberintos hasta que alguno tenga solucion."""

def leer_laberinto (nombreArchivo):
    with open(nombreArchivo,"r") as file:
        filas = file.readlines()
    laberinto = []
    for r, fila in enumerate(filas):
        fila = list(fila)
        laberinto.append(fila[:-1])
        for c, casilla in enumerate(fila):
            if casilla == 'I':
                inicio = (r, c)
            if casilla == 'X':
                fin = (r, c)
    return laberinto, inicio, fin, len(laberinto)

# distancia: Tupla(int) Tupla(int) -> int
# Dado un nodo del laberinto y el objetivo, devuelve la distancia entre ellos
def distancia(nodo,objetivo):
    return abs(objetivo[0]-nodo[0]) + abs(objetivo[1]-nodo[1])

# ordenar_distancia: List[Tupla(int)] Tupla(int)
# Dada una lista de nodos y el objetivo, ordena la lista en base a la distancia
# al objetivo de cada nodo de mayor a menor
def ordenar_distancia(listaNodos,objetivo):
    listaDistancia = []
    for nodo in listaNodos:
        dist = distancia(nodo,objetivo)
        listaDistancia.append((nodo, dist))
        
    listaNodos.clear()
    listaDistancia.sort(key=lambda tupla: tupla[1],reverse=True)
    for (nodo, _) in listaDistancia:
        listaNodos.append(nodo)

def limites (x, y, dimension):
    return x>=0 and y>=0 and x<dimension and y<dimension

# explorar: List[List[string]] Tupla(int) Tupla(int) int -> List[Tupla(int)]
# Dado un laberinto, un nodo, el objetivo y el tamaño del laberinto,
# devuelve una lista con los nodos adyacentes al nodo de entrada 
# que no sean una pared y no hayan sido visitados ordenados por la distancia al objetivo
def explorar(laberinto,nodo,objetivo,dimension):
    adyacentes = []
    i, j = nodo
    for x,y in ((i+1,j), (i, j+1), (i-1,j), (i,j-1)):
        if limites(x, y, dimension) and laberinto[x][y] != "1" and laberinto[x][y] != "-1":
            adyacentes.append((x,y))
    ordenar_distancia(adyacentes,objetivo)
    return adyacentes

# resolver_laberinto: List[List[string]] Tupla(int) Tupla(int) int -> List[Tupla(int)]
# Recibe un laberinto, el inicio, el objetivo, y la dimension del laberinto,
# devuelve una lista de nodos en secuencia que representan una solucion del laberinto
def resolver_laberinto(laberinto,inicio,objetivo,dimension):
    stack = []
    stack.append([inicio])
    solucion = []
    llegarObjetivo = False
    while(not llegarObjetivo and stack):
        path = stack.pop(-1)
        nodo = path[-1]
        if laberinto[nodo[0]][nodo[1]] != "-1":
            laberinto[nodo[0]][nodo[1]] = "-1"
            vecinos = explorar(laberinto,nodo,objetivo,dimension)
            for nodoVecino in vecinos:
                newPath = path + [nodoVecino]
                stack.append(newPath)
                if laberinto[nodoVecino[0]][nodoVecino[1]] == "X":
                    llegarObjetivo = True
                    solucion = newPath
    return solucion

# escrbir_solucion: List[Tupla(int)]
# Recibe una solucion del laberinto, escribe la secuencia de nodos en un archivo
def escrbir_solucion(solucion,archivoSolucion):
    with open(archivoSolucion,"w") as salida:
        for pasos in solucion:
            salida.write(f"({pasos[0]+1},{pasos[1]+1})\n")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument (
        "ejecutableC",
        help = "Archivo ejecutable para generar el laberinto"
    )
    parser.add_argument (
        "entrada",
        help = "Archivo con la informacion para crear el laberinto" 
    )
    parser.add_argument (
        "laberinto",
        help = "Archivo del laberinto"
    )
    parser.add_argument (
        "solucion",
        help = "Nombre del archivo con la solucion del laberinto"
    )
    args = parser.parse_args()

    randomSeed = str(randrange(maxsize))
    ejecutable = "./" + args.ejecutableC
    ejecutar = run([ejecutable, args.entrada, args.laberinto, randomSeed])
    #Pregunta si se genero la salida, en caso que sea False significa que la entrada no era valida
    if(ejecutar.returncode == 0):
        laberinto, inicio, objetivo, dimension = leer_laberinto (args.laberinto)
        recorrido = resolver_laberinto(laberinto, inicio, objetivo, dimension)
        while(recorrido == []):
            randomSeed = str(randrange(maxsize))
            ejecutar = run([ejecutable, args.entrada, args.laberinto, randomSeed])
            laberinto = leer_laberinto (args.laberinto)
            recorrido = resolver_laberinto(laberinto, inicio, objetivo, dimension)
        escrbir_solucion(recorrido, args.solucion)

if __name__ == "__main__":
    main()
