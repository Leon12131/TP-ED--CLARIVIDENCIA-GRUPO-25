import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelos.videojuego import Videojuego
from estructuras.arbol_binario import ArbolBinarioBusqueda
from estructuras.avl import ArbolAVL
from estructuras.arbol_general import construir_catalogo

def cargar_datos():
    with open("datos/videojuegos.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    juegos = []
    for d in datos:
        juegos.append(Videojuego(d["titulo"], d["genero"], d["rating"], d["plataforma"]))
    return juegos

def mostrar_menu():
    print("\n" + "=" * 40)
    print("      CLARIVIDENCIA - GAME ADVISOR")
    print("=" * 40)
    print("1. Buscar videojuego")
    print("2. Listar todos los videojuegos")
    print("3. Filtrar por genero")
    print("4. Explorar categorias")
    print("5. Comparar BST vs AVL")
    print("0. Salir")
    print("-" * 40)

def buscar(avl):
    # TP4: la busqueda usa el arbol AVL
    titulo = input("\nTitulo a buscar: ")
    juego = avl.buscar(titulo.strip())
    if juego:
        print(f"- {juego}")
    else:
        print("No se encontraron coincidencias.")
    print("Fin de resultados.")

def listar(juegos):
    print("\n--- Catálogo de Videojuegos ---")
    for i, j in enumerate(juegos, 1):
        print(f"{i}. {j}")

def filtrar(juegos):
    genero = input("\nGenero a filtrar: ")
    encontrado = False
    for j in juegos:
        if genero.lower() in j.genero.lower():
            print(f"- {j}")
            encontrado = True
    if not encontrado:
        print("No se encontraron juegos en ese género.")

def explorar_categorias(categorias):
    # TP5: navegacion por la jerarquia con el arbol general
    while True:
        print("\n--- Explorar categorias ---")
        print("1. Ver la jerarquia completa")
        print("2. Ver los juegos de una categoria")
        print("3. Recorrido en amplitud (por niveles)")
        print("4. Recorrido en profundidad (rama por rama)")
        print("0. Volver")
        opcion = input("Opcion: ")

        if opcion == "1":
            print()
            categorias.imprimir()
        elif opcion == "2":
            print("Categorias principales:", ", ".join(h.nombre for h in categorias.raiz.hijos))
            nombre = input("Categoria: ").strip()
            nodo = categorias.buscar(nombre) if nombre else None
            if nodo is None:
                print("No existe esa categoria.")
                continue
            juegos = categorias.juegos_de(nodo.nombre)
            print(f"\n{' > '.join(categorias.camino_hasta(nodo.nombre))}: {len(juegos)} juego(s)")
            for j in sorted(juegos, key=lambda j: j.rating, reverse=True):
                print(f"- {j}")
        elif opcion == "3":
            print("\n" + " | ".join(categorias.amplitud()))
        elif opcion == "4":
            print("\n" + " | ".join(categorias.profundidad()))
        elif opcion == "0":
            break
        else:
            print("Opción no válida. Intente de nuevo.")

def comparar(arbol, avl):
    print("\n--- Comparacion BST vs AVL ---")
    print("Altura BST     :", arbol.altura())
    print("Altura AVL     :", avl.altura())
    print("Rotaciones AVL :", avl.rotaciones)
    print("Casos AVL      :", avl.casos)

def main():
    juegos = cargar_datos()

    arbol = ArbolBinarioBusqueda()      # TP3
    avl = ArbolAVL()                    # TP4
    for j in juegos:
        arbol.insertar(j)
        avl.insertar(j)
    categorias = construir_catalogo(juegos)     # TP5

    while True:
        mostrar_menu()
        opcion = input("Opcion: ")
        if opcion == "1":
            buscar(avl)
        elif opcion == "2":
            listar(juegos)
        elif opcion == "3":
            filtrar(juegos)
        elif opcion == "4":
            explorar_categorias(categorias)
        elif opcion == "5":
            comparar(arbol, avl)
        elif opcion == "0":
            print("¡Hasta luego! Gracias por usar Clarividencia.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
