"""
Árbol AVL (árbol binario de búsqueda autobalanceado) de videojuegos.

Ordena por título (sin distinguir mayúsculas ni acentos). Después de cada
inserción, el factor de balance de todo nodo queda en {-1, 0, 1}:

    factor de balance = altura(subárbol izquierdo) - altura(subárbol derecho)

Si un nodo llega a +2 o -2 se corrige con una de cuatro rotaciones:

    +2 y el hijo izquierdo pesa a la izquierda  -> simple derecha
    -2 y el hijo derecho pesa a la derecha      -> simple izquierda
    +2 y el hijo izquierdo pesa a la derecha    -> doble izquierda-derecha
    -2 y el hijo derecho pesa a la izquierda    -> doble derecha-izquierda
"""
import unicodedata


def clave(texto):
    """Clave de comparación: minúsculas y sin acentos ('Hadès' == 'hades')."""
    t = unicodedata.normalize("NFD", texto.casefold())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


class NodoAVL:
    def __init__(self, videojuego):
        self.videojuego = videojuego
        self.clave = clave(videojuego.titulo)
        self.izquierdo = None
        self.derecho = None
        self.altura = 1          # altura del subárbol que cuelga de este nodo


class ArbolAVL:
    def __init__(self):
        self.raiz = None
        self.rotaciones = 0      # rotaciones simples realizadas (una doble suma 2)
        self.casos = {           # cuántas veces ocurrió cada caso de desbalance
            "simple derecha": 0,
            "simple izquierda": 0,
            "doble izquierda-derecha": 0,
            "doble derecha-izquierda": 0,
        }
        self._insertado = False

    # ------------------------------------------------------------ utilidades
    def _altura(self, nodo):
        return nodo.altura if nodo else 0

    def _actualizar_altura(self, nodo):
        nodo.altura = 1 + max(self._altura(nodo.izquierdo), self._altura(nodo.derecho))

    def _factor_balance(self, nodo):
        return self._altura(nodo.izquierdo) - self._altura(nodo.derecho)

    # ------------------------------------------------------------ rotaciones
    def _rotacion_simple_derecha(self, y):
        """
              y                x
             / \\              / \\
            x   C    -->     A   y
           / \\                  / \\
          A   B                B   C
        """
        x = y.izquierdo
        y.izquierdo = x.derecho
        x.derecho = y
        self._actualizar_altura(y)
        self._actualizar_altura(x)
        self.rotaciones += 1
        return x

    def _rotacion_simple_izquierda(self, x):
        """
          x                    y
         / \\                  / \\
        A   y      -->       x   C
           / \\              / \\
          B   C            A   B
        """
        y = x.derecho
        x.derecho = y.izquierdo
        y.izquierdo = x
        self._actualizar_altura(x)
        self._actualizar_altura(y)
        self.rotaciones += 1
        return y

    def _rotacion_doble_izquierda_derecha(self, nodo):
        """Primero el hijo izquierdo gira a la izquierda, luego el nodo a la derecha."""
        nodo.izquierdo = self._rotacion_simple_izquierda(nodo.izquierdo)
        return self._rotacion_simple_derecha(nodo)

    def _rotacion_doble_derecha_izquierda(self, nodo):
        """Primero el hijo derecho gira a la derecha, luego el nodo a la izquierda."""
        nodo.derecho = self._rotacion_simple_derecha(nodo.derecho)
        return self._rotacion_simple_izquierda(nodo)

    def _rebalancear(self, nodo):
        self._actualizar_altura(nodo)
        fb = self._factor_balance(nodo)

        if fb > 1:                                         # pesa a la izquierda
            if self._factor_balance(nodo.izquierdo) >= 0:
                self.casos["simple derecha"] += 1
                return self._rotacion_simple_derecha(nodo)
            self.casos["doble izquierda-derecha"] += 1
            return self._rotacion_doble_izquierda_derecha(nodo)

        if fb < -1:                                        # pesa a la derecha
            if self._factor_balance(nodo.derecho) <= 0:
                self.casos["simple izquierda"] += 1
                return self._rotacion_simple_izquierda(nodo)
            self.casos["doble derecha-izquierda"] += 1
            return self._rotacion_doble_derecha_izquierda(nodo)

        return nodo

    # ------------------------------------------------------------- inserción
    def insertar(self, videojuego):
        """Inserta y rebalancea. Devuelve False si el título ya existía (se ignora)."""
        self._insertado = False
        self.raiz = self._insertar_rec(self.raiz, NodoAVL(videojuego))
        return self._insertado

    def _insertar_rec(self, actual, nuevo):
        if actual is None:
            self._insertado = True
            return nuevo
        if nuevo.clave < actual.clave:
            actual.izquierdo = self._insertar_rec(actual.izquierdo, nuevo)
        elif nuevo.clave > actual.clave:
            actual.derecho = self._insertar_rec(actual.derecho, nuevo)
        else:
            return actual                                  # duplicado
        return self._rebalancear(actual)

    # -------------------------------------------------------------- búsqueda
    def buscar(self, titulo):
        k = clave(titulo)
        nodo = self.raiz
        while nodo:
            if k == nodo.clave:
                return nodo.videojuego
            nodo = nodo.izquierdo if k < nodo.clave else nodo.derecho
        return None

    # ------------------------------------------------------------ recorridos
    def inorder(self):
        lista = []
        def _r(n):
            if n:
                _r(n.izquierdo)
                lista.append(n.videojuego)
                _r(n.derecho)
        _r(self.raiz)
        return lista

    def preorder(self):
        lista = []
        def _r(n):
            if n:
                lista.append(n.videojuego)
                _r(n.izquierdo)
                _r(n.derecho)
        _r(self.raiz)
        return lista

    def postorder(self):
        lista = []
        def _r(n):
            if n:
                _r(n.izquierdo)
                _r(n.derecho)
                lista.append(n.videojuego)
        _r(self.raiz)
        return lista

    # ----------------------------------------------------------------- varios
    def altura(self):
        return self._altura(self.raiz)

    def imprimir(self):
        """Dibuja el árbol de costado (raíz a la izquierda) con el factor de balance."""
        def _r(n, nivel):
            if n:
                _r(n.derecho, nivel + 1)
                print("    " * nivel + f"{n.videojuego.titulo} [fb={self._factor_balance(n)}]")
                _r(n.izquierdo, nivel + 1)
        _r(self.raiz, 0)
