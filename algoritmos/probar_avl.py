"""
Script de pruebas de TP4 (AVL) y TP5 (Árbol General) + regresión de TP3 (BST).

Uso (desde la raíz del proyecto):
    python algoritmos/probar_avl.py            # pruebas + mediciones + tablas del documento
    python algoritmos/probar_avl.py --rapido   # solo pruebas (sin mediciones)

Si alguna prueba falla, NO mide ni escribe el documento (no tiene sentido
reportar números de un código que falla). Termina con código 1 si hubo fallos.
"""
import json
import math
import os
import platform
import random
import re
import statistics
import sys
import timeit
from datetime import date

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(RAIZ)
DOC = os.path.join(RAIZ, "docs", "08-analisis-tp4-tp5.md")
DATOS = os.path.join(RAIZ, "datos", "videojuegos.json")

from modelos.videojuego import Videojuego
from estructuras.arbol_binario import ArbolBinarioBusqueda
from estructuras.avl import ArbolAVL, clave
from estructuras.arbol_general import ArbolGeneral, NodoGeneral, construir_catalogo

SEMILLA = 42
RONDAS = 5          # cada medición se repite RONDAS veces y se toma la mediana
OBJETIVOS = 50      # títulos buscados por medición (elegidos al azar)

correctas, fallos = 0, []


# ----------------------------------------------------------------- utilidades
def verificar(nombre, condicion, detalle=""):
    global correctas
    if condicion:
        correctas += 1
        print(f"  OK     {nombre}")
    else:
        fallos.append(nombre)
        print(f"  FALLO  {nombre} {detalle}")


def seccion(titulo):
    print(f"\n== {titulo}")


def v(titulo, genero="accion"):
    return Videojuego(titulo, genero, 8.0, "PC")


def titulos(lista):
    return [j.titulo for j in lista]


def avl_de(ts):
    a = ArbolAVL()
    for t in ts:
        a.insertar(v(t))
    return a


def balanceado(n):
    """(¿cumple AVL en todo el subárbol?, altura real)."""
    if n is None:
        return True, 0
    ok_i, h_i = balanceado(n.izquierdo)
    ok_d, h_d = balanceado(n.derecho)
    h = 1 + max(h_i, h_d)
    return ok_i and ok_d and abs(h_i - h_d) <= 1 and n.altura == h, h


# ------------------------------------------------------------------- pruebas
def pruebas_avl():
    seccion("AVL: rotaciones")
    casos = [
        ("simple izquierda", "ABC", "simple izquierda"),
        ("simple derecha", "CBA", "simple derecha"),
        ("doble izquierda-derecha", "CAB", "doble izquierda-derecha"),
        ("doble derecha-izquierda", "ACB", "doble derecha-izquierda"),
    ]
    for nombre, orden, caso in casos:
        a = avl_de(orden)
        r = a.raiz
        forma = tuple(n.videojuego.titulo if n else None for n in (r, r.izquierdo, r.derecho))
        contadores = [k for k, n in a.casos.items() if n]
        verificar(f"rotación {nombre} ({', '.join(orden)})",
                  forma == ("B", "A", "C") and contadores == [caso],
                  f"-> forma={forma}, casos={a.casos}")

    seccion("AVL: inserción balanceada")
    for n in (100, 800):
        ts = [f"juego {i:06d}" for i in range(n)]
        a = avl_de(ts)
        ok_bal, h = balanceado(a.raiz)
        verificar(f"{n} datos ORDENADOS: balanceado y altura {h} <= 1,44*log2(n+2)",
                  ok_bal and h <= 1.44 * math.log2(n + 2))
        verificar(f"{n} datos ordenados: inorder correcto", titulos(a.inorder()) == ts)
    random.seed(SEMILLA)
    ts = [f"juego {i:06d}" for i in range(2000)]
    mezclados = ts[:]
    random.shuffle(mezclados)
    a = avl_de(mezclados)
    verificar("2000 datos ALEATORIOS: balanceado e inorder correcto",
              balanceado(a.raiz)[0] and titulos(a.inorder()) == ts)
    a = avl_de("AB")
    verificar("duplicado rechazado (insertar devuelve False) y no cambia el árbol",
              a.insertar(v("A")) is False and titulos(a.inorder()) == ["A", "B"])

    seccion("AVL: búsqueda y recorridos")
    a = avl_de("ABCDEFG")
    verificar("inorder  A..G", titulos(a.inorder()) == list("ABCDEFG"))
    verificar("preorder  D B A C F E G", titulos(a.preorder()) == list("DBACFEG"))
    verificar("postorder A C B E G F D", titulos(a.postorder()) == list("ACBEGFD"))
    verificar("altura 3 con 7 nodos", a.altura() == 3)
    h = ArbolAVL()
    h.insertar(Videojuego("Hadès", "Roguelike", 9.3, "PC"))
    h.insertar(Videojuego("Celeste", "Plataformas", 9.0, "PC"))
    verificar("buscar ignora mayúsculas y acentos ('HADES' encuentra 'Hadès')",
              h.buscar("HADES") is not None and h.buscar("celeste") is not None)
    verificar("buscar un título inexistente devuelve None", h.buscar("Zelda") is None)
    verificar("árbol vacío: buscar/inorder/altura",
              ArbolAVL().buscar("x") is None and ArbolAVL().inorder() == [] and ArbolAVL().altura() == 0)


def pruebas_bst_regresion():
    seccion("BST (TP3) sigue funcionando")
    b = ArbolBinarioBusqueda()
    for t in "BAC":
        b.insertar(v(t))
    verificar("inorder / preorder / postorder",
              titulos(b.inorder()) == list("ABC") and titulos(b.preorder()) == list("BAC")
              and titulos(b.postorder()) == list("ACB"))
    verificar("buscar y altura",
              b.buscar("a") is not None and b.buscar("Z") is None and b.altura() == 2)


def pruebas_comparacion():
    seccion("Desbalance con datos ordenados: BST vs AVL")
    for n in (100, 400, 800):          # el insertar recursivo del BST falla cerca de 1000
        bst, avl = ArbolBinarioBusqueda(), ArbolAVL()
        for i in range(n):
            j = v(f"juego {i:06d}")
            bst.insertar(j)
            avl.insertar(j)
        verificar(f"N={n}: BST degenera (altura {bst.altura()}), AVL altura {avl.altura()}",
                  bst.altura() == n and avl.altura() <= 1.44 * math.log2(n + 2))
        verificar(f"N={n}: ambos devuelven el mismo inorder",
                  titulos(bst.inorder()) == titulos(avl.inorder()))


def pruebas_general():
    seccion("Árbol general")
    g = ArbolGeneral()
    verificar("árbol vacío: recorridos y búsqueda",
              g.amplitud() == [] and g.profundidad() == [] and g.buscar("x") is None)
    g.insertar_raiz("Videojuegos")
    g.agregar_hijo("Videojuegos", "RPG")
    g.agregar_hijo("Videojuegos", "Plataformas")
    g.agregar_hijo("RPG", "Soulslike")
    g.agregar_hijo("Soulslike", "Elden Ring", v("Elden Ring"))
    verificar("amplitud (por niveles)",
              g.amplitud() == ["Videojuegos", "RPG", "Plataformas", "Soulslike", "Elden Ring"])
    verificar("profundidad (preorden)",
              g.profundidad() == ["Videojuegos", "RPG", "Soulslike", "Elden Ring", "Plataformas"])
    verificar("buscar ignora mayúsculas y acentos", g.buscar("ELDEN ring") is not None)
    verificar("buscar inexistente devuelve None", g.buscar("Zelda") is None)
    verificar("agregar_hijo a un padre inexistente devuelve None",
              g.agregar_hijo("NoExiste", "X") is None)
    verificar("camino_hasta", g.camino_hasta("elden ring") ==
              ["Videojuegos", "RPG", "Soulslike", "Elden Ring"])
    verificar("juegos_de una categoría", titulos(g.juegos_de("rpg")) == ["Elden Ring"])
    verificar("altura 4", g.altura() == 4)


def pruebas_datos_reales():
    seccion("Integración con datos/videojuegos.json")
    if not os.path.exists(DATOS):
        print("  (no existe datos/videojuegos.json: se omite)")
        return
    with open(DATOS, encoding="utf-8") as f:
        juegos = [Videojuego(d["titulo"], d["genero"], d["rating"], d["plataforma"])
                  for d in json.load(f)]
    bst, avl = ArbolBinarioBusqueda(), ArbolAVL()
    for j in juegos:
        bst.insertar(j)
        avl.insertar(j)
    catalogo = construir_catalogo(juegos)
    unicos = len({clave(j.titulo) for j in juegos})

    verificar(f"{len(juegos)} juegos cargados; el AVL guarda {len(avl.inorder())} títulos únicos",
              len(avl.inorder()) == unicos)
    verificar("todos los títulos se encuentran en el AVL y en el BST",
              all(avl.buscar(j.titulo) is not None and bst.buscar(j.titulo) is not None
                  for j in juegos))
    verificar("el AVL está balanceado", balanceado(avl.raiz)[0])
    verificar("todos los juegos aparecen en el árbol de categorías",
              len(catalogo.juegos_de("Videojuegos")) == len(juegos))
    otros = catalogo.juegos_de("Otros")
    if otros:
        print(f"  AVISO  {len(otros)} juego(s) cayeron en 'Otros' (género sin ruta en "
              f"RUTAS_POR_GENERO):
