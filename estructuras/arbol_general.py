"""
Árbol general (n-ario) para explorar el catálogo de videojuegos por categorías.

Cada nodo tiene un nombre y una lista de hijos (cualquier cantidad). Los nodos
intermedios son categorías; las hojas son videojuegos y guardan el objeto
Videojuego en 'dato'.

    Videojuegos
    ├── RPG
    │   ├── Soulslike
    │   │   └── Elden Ring
    │   └── The Witcher 3: Wild Hunt
    ├── Acción
    │   └── ...
"""
from collections import deque
from estructuras.avl import clave


class NodoGeneral:
    def __init__(self, nombre, dato=None):
        self.nombre = nombre
        self.dato = dato          # Videojuego si es hoja, None si es categoría
        self.hijos = []

    def es_hoja(self):
        return not self.hijos


class ArbolGeneral:
    def __init__(self):
        self.raiz = None

    # ------------------------------------------------------------- inserción
    def insertar_raiz(self, nombre):
        """Crea (o reemplaza) la raíz del árbol."""
        self.raiz = NodoGeneral(nombre)
        return self.raiz

    def agregar_hijo(self, nombre_padre, nombre, dato=None):
        """Agrega un hijo al nodo llamado 'nombre_padre'. Devuelve None si no existe."""
        padre = self.buscar(nombre_padre)
        if padre is None:
            return None
        nuevo = NodoGeneral(nombre, dato)
        padre.hijos.append(nuevo)
        return nuevo

    def agregar_camino(self, categorias, nombre, dato=None):
        """
        Cuelga 'nombre' al final de la cadena de categorías (desde la raíz),
        creando las categorías que falten. Solo mira los hijos directos de cada
        nivel, por eso dos categorías iguales en ramas distintas no se confunden.
        """
        if self.raiz is None:
            raise ValueError("Primero hay que insertar la raíz")
        actual = self.raiz
        for categoria in categorias:
            hijo = self._hijo_llamado(actual, categoria)
            if hijo is None:
                hijo = NodoGeneral(categoria)
                actual.hijos.append(hijo)
            actual = hijo
        nuevo = NodoGeneral(nombre, dato)
        actual.hijos.append(nuevo)
        return nuevo

    @staticmethod
    def _hijo_llamado(padre, nombre):
        k = clave(nombre)
        for h in padre.hijos:
            if clave(h.nombre) == k:
                return h
        return None

    # -------------------------------------------------------------- búsqueda
    def buscar(self, nombre):
        """Busca por nombre (sin importar mayúsculas ni acentos), en amplitud."""
        k = clave(nombre)
        cola = deque([self.raiz] if self.raiz else [])
        while cola:
            n = cola.popleft()
            if clave(n.nombre) == k:
                return n
            cola.extend(n.hijos)
        return None

    def camino_hasta(self, nombre):
        """Lista de nombres desde la raíz hasta el nodo buscado, o None."""
        k = clave(nombre)
        cola = deque([(self.raiz, [self.raiz.nombre])] if self.raiz else [])
        while cola:
            n, ruta = cola.popleft()
            if clave(n.nombre) == k:
                return ruta
            for h in n.hijos:
                cola.append((h, ruta + [h.nombre]))
        return None

    def juegos_de(self, nombre):
        """Todos los videojuegos que cuelgan de la categoría 'nombre' (o de ese juego)."""
        inicio = self.buscar(nombre)
        if inicio is None:
            return []
        juegos, pila = [], [inicio]
        while pila:
            n = pila.pop()
            if n.dato is not None:
                juegos.append(n.dato)
            pila.extend(reversed(n.hijos))
        return juegos

    # ------------------------------------------------------------ recorridos
    def amplitud(self):
        """Recorrido por niveles (usa una cola). Devuelve la lista de nombres."""
        resultado = []
        cola = deque([self.raiz] if self.raiz else [])
        while cola:
            n = cola.popleft()
            resultado.append(n.nombre)
            cola.extend(n.hijos)
        return resultado

    def profundidad(self):
        """Recorrido en profundidad, preorden (recursivo). Devuelve la lista de nombres."""
        resultado = []

        def _r(n):
            resultado.append(n.nombre)
            for h in n.hijos:
                _r(h)

        if self.raiz:
            _r(self.raiz)
        return resultado

    # ----------------------------------------------------------------- varios
    def altura(self):
        def _r(n):
            return 1 + max((_r(h) for h in n.hijos), default=0)
        return _r(self.raiz) if self.raiz else 0

    def imprimir(self, nodo=None, nivel=0):
        """Muestra la jerarquía con sangría (para la opción 'Explorar categorías')."""
        if nodo is None:
            nodo = self.raiz
        if nodo is None:
            return
        extra = f"  (rating {nodo.dato.rating})" if nodo.dato is not None else ""
        print("  " * nivel + "- " + nodo.nombre + extra)
        for h in nodo.hijos:
            self.imprimir(h, nivel + 1)


# ------------------------------------------------------------------ jerarquía
# Cada género del catálogo se ubica en una ruta de categorías (de general a específica).
RUTAS_POR_GENERO = {
    "RPG":               ["RPG"],
    "Soulslike / RPG":   ["RPG", "Soulslike"],
    "RPG / Sci-Fi":      ["RPG", "Ciencia ficción"],
    "Accion":            ["Acción"],
    "Accion / Aventura": ["Acción", "Aventura"],
    "Roguelike":         ["Acción", "Roguelike"],
    "Plataformas":       ["Plataformas"],
    "Metroidvania":      ["Plataformas", "Metroidvania"],
    "Sandbox":           ["Sandbox"],
    "Puzles":            ["Puzles"],
}


def construir_catalogo(juegos, rutas=RUTAS_POR_GENERO):
    """Arma el árbol de categorías a partir de una lista de Videojuego."""
    arbol = ArbolGeneral()
    arbol.insertar_raiz("Videojuegos")
    for j in juegos:
        ruta = rutas.get(j.genero, ["Otros"])      # género desconocido -> 'Otros'
        arbol.agregar_camino(ruta, j.titulo, j)
    return arbol
