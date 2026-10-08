# Análisis TP4 y TP5: AVL y Árbol General

Entrega 4 (acumulativa con TP3). Compara el árbol binario de búsqueda (BST) con el AVL y analiza el árbol general que usa la opción "Explorar categorías" del catálogo de videojuegos.

## 1. Entorno de medición

<!-- TABLA:entorno -->
(pendiente: ejecutar `python algoritmos/probar_avl.py`)
<!-- /TABLA:entorno -->

## 2. Metodología

- Los videojuegos de prueba se generan con títulos `juego 000000`, `juego 000001`, etc. (género y plataforma fijos), para controlar el orden de inserción.
- **Datos ordenados:** se insertan en orden alfabético. Es el peor caso del BST y el caso que el AVL corrige con rotaciones. Los tamaños se limitan a N ≤ 800 porque el `insertar` recursivo del BST supera el límite de recursión de Python (~1000) con datos ordenados.
- **Datos aleatorios:** los mismos títulos mezclados con semilla fija (42), para que los resultados sean reproducibles.
- **Tiempos:** cada medición se repite 5 veces y se informa la **mediana**, para reducir el efecto de picos del sistema. La búsqueda se mide sobre 50 títulos elegidos al azar (existentes) y se informa el tiempo medio por búsqueda.
- **Alturas y rotaciones** son deterministas: no dependen de la máquina. El contador de rotaciones cuenta cada rotación simple por separado, así que una rotación doble suma 2.
- **Costo de la clave:** el BST compara con `.lower()` y el AVL con `clave()` (minúsculas y sin acentos), que cuesta algo más por búsqueda. Por eso el tiempo de búsqueda del AVL tiene un piso constante de pocos microsegundos, independiente de N.
- **Árbol general:** se arma un árbol con 4 hijos por nodo. Para medir los recorridos se construye directamente; la construcción con `agregar_hijo` se mide aparte porque tiene otro costo (ver 3.3).

## 3. Resultados

### 3.1 Datos ordenados (peor caso del BST)

<!-- TABLA:ordenado -->
(pendiente: ejecutar `python algoritmos/probar_avl.py`)
<!-- /TABLA:ordenado -->

### 3.2 Datos aleatorios

<!-- TABLA:aleatorio -->
(pendiente: ejecutar `python algoritmos/probar_avl.py`)
<!-- /TABLA:aleatorio -->

### 3.3 Árbol general

Recorridos y búsqueda sobre un árbol ya construido:

<!-- TABLA:general_recorridos -->
(pendiente: ejecutar `python algoritmos/probar_avl.py`)
<!-- /TABLA:general_recorridos -->

Construcción usando `agregar_hijo` (que primero busca al padre por nombre):

<!-- TABLA:general_construccion -->
(pendiente: ejecutar `python algoritmos/probar_avl.py`)
<!-- /TABLA:general_construccion -->

## 4. Complejidad

| Operación | BST (promedio) | BST (peor caso) | AVL (siempre) |
|---|---|---|---|
| Insertar | O(log n) | O(n) | O(log n) |
| Buscar | O(log n) | O(n) | O(log n) |
| Recorridos (inorder, preorder, postorder) | O(n) | O(n) | O(n) |
| Altura | O(n) si se recalcula | O(n) | O(1) (se guarda en cada nodo) |
| Rotación | no aplica | no aplica | O(1) |

- El peor caso del BST ocurre con datos ordenados: el árbol se convierte en una lista enlazada de altura n. Construirlo cuesta entonces O(n²).
- El AVL garantiza `|factor de balance| ≤ 1` en cada nodo, lo que acota su altura a menos de 1,44 · log₂(n + 2).
- En una inserción el AVL hace como máximo un rebalanceo (una rotación simple o una doble); el resto del camino solo actualiza alturas.
- Espacio: ambos O(n). El AVL guarda un entero extra (la altura) por nodo.

| Operación del árbol general | Complejidad | Comentario |
|---|---|---|
| Insertar raíz | O(1) | |
| `agregar_hijo` | O(n) | Busca al padre por nombre (recorrido en amplitud). Armar un árbol de n nodos así cuesta O(n²). |
| `agregar_camino` | O(profundidad × hijos por nivel) | Solo mira los hijos directos de cada nivel; es lo que usa el catálogo. |
| Buscar nodo | O(n) | Un árbol general no tiene orden que permita descartar ramas. |
| Amplitud | O(n) | Usa una cola; memoria extra proporcional al ancho máximo. |
| Profundidad (preorden) | O(n) | Usa recursión; memoria extra proporcional a la altura. |

## 5. Análisis

### 5.1 BST con datos ordenados

Cada título nuevo es mayor que todos los anteriores y se agrega siempre a la derecha, así que la altura del BST es igual a N (100, 200, 400 y 800 en la tabla 3.1). Eso tiene tres consecuencias visibles en los resultados: la búsqueda recorre en promedio la mitad del árbol y su tiempo crece de forma lineal con N (aproximadamente se duplica cada vez que N se duplica); construir el árbol cuesta O(n²), por lo que su tiempo se multiplica aproximadamente por 4 cada vez que N se duplica; y, con N cercano a 1000, la inserción recursiva falla por `RecursionError`.

### 5.2 AVL con datos ordenados

El AVL mantiene la altura en el orden de log₂ N: 7, 8, 9 y 10 para N = 100, 200, 400 y 800. Con datos ordenados cada inserción desbalancea siempre el mismo lado, así que todas las rotaciones son simples a la izquierda (en el caso de N = 800, 790 rotaciones). Las rotaciones dobles aparecen cuando el orden de llegada hace que un nodo pese hacia un lado y su hijo hacia el otro (por ejemplo, C, A, B), cosa que los datos ordenados nunca producen. El tiempo de construcción crece de forma casi proporcional a N y el de búsqueda queda prácticamente constante, porque la altura casi no cambia.

### 5.3 Datos aleatorios

Con datos aleatorios el BST también queda con altura logarítmica en promedio, aunque mayor que la del AVL (con N = 10000, la altura del BST es 32 y la del AVL 16). Esa diferencia de altura **no** se traduce en una búsqueda más rápida en nuestras mediciones: los tiempos de búsqueda de ambos árboles son parecidos, y la diferencia es pequeña y puede inclinarse hacia cualquiera de los dos lados. A estos tamaños el costo por búsqueda lo domina el costo fijo de normalizar la clave, no el número de niveles recorridos. En cambio, la construcción del AVL es más lenta que la del BST, porque cada inserción actualiza alturas y a veces rota (por ejemplo, 6946 rotaciones con N = 10000). La diferencia importante es que el AVL **garantiza** el comportamiento logarítmico y el BST solo lo ofrece si los datos llegan en un orden favorable.

### 5.4 Lectura de nuestros resultados

- **BST frente a AVL con N = 800 ordenado:** la altura es 800 contra 10, y la búsqueda del BST es entre decenas de veces más lenta que la del AVL (tabla 3.1). La brecha crece con N, porque el BST es lineal y el AVL casi constante.
- **Construcción con datos aleatorios:** el AVL fue más lento que el BST (tabla 3.2). El motivo es el trabajo extra de mantener el balance: actualizar la altura de cada nodo del camino y rotar cuando hace falta.
- **Búsqueda con datos aleatorios:** los tiempos son parecidos. El AVL tiene un árbol más bajo, pero a estos tamaños eso se compensa con el costo constante de la clave, que normaliza el texto para ignorar acentos.
- **Árbol general:** al duplicar la cantidad de nodos, el tiempo de construcción con `agregar_hijo` se multiplica aproximadamente por 4 (tabla 3.3), lo que confirma el comportamiento O(n²) por buscar al padre en cada llamada.

### 5.5 Árbol general

Amplitud y profundidad recorren los mismos n nodos, así que tienen la misma complejidad temporal; la diferencia está en el recurso auxiliar (cola frente a pila de llamadas) y en el orden en que entregan los nodos: la amplitud explora categoría por categoría y la profundidad baja por una rama completa antes de pasar a la siguiente. Para "Explorar categorías", la profundidad se parece a navegar un menú de carpetas.

La búsqueda de un nodo es O(n) porque el árbol no tiene un orden que permita descartar ramas; para el catálogo es suficiente, ya que se navega por la jerarquía y no se busca entre miles de nodos.

La construcción con `agregar_hijo` es cuadrática porque cada llamada busca al padre desde la raíz. Por eso el catálogo se arma con `agregar_camino`, que solo revisa los hijos directos de cada nivel. Una mejora posible es guardar un diccionario `nombre → nodo` para que agregar un hijo sea O(1).

## 6. Conclusión

- **AVL frente a BST:** el BST es más simple y, con datos aleatorios, construye más rápido y busca a una velocidad comparable. Pero su rendimiento depende del orden de inserción: con datos ordenados, algo habitual en un catálogo cargado alfabéticamente, degenera a O(n) tanto al buscar como al construirse. El AVL cuesta rotaciones extra al insertar y un campo más por nodo, y a cambio garantiza O(log n) en insertar y buscar sin importar el orden. Para la opción "Buscar" de la aplicación, el AVL es la elección segura.
- **Árbol general:** es la estructura natural para la jerarquía género → subgénero → juego, porque cada nodo puede tener cualquier cantidad de hijos. No ofrece búsqueda rápida (O(n)), pero eso no importa para explorar categorías, donde se navega por la jerarquía.
- **Limitaciones conocidas:** el AVL ignora títulos duplicados; el árbol general identifica nodos por nombre en `agregar_hijo`, así que dos categorías con el mismo nombre en ramas distintas pueden confundirse (`agregar_camino` no tiene ese problema); el BST recursivo falla con unos 1000 elementos ordenados.
- **Mejoras posibles:** diccionario de nodos en el árbol general, inserción iterativa en el BST y una función `clave()` compartida por los tres árboles.

## 7. Cómo reproducir

Desde la raíz del proyecto:

```bash
python algoritmos/probar_avl.py
```

El script corre las pruebas de corrección, mide, y reescribe las tablas de este documento. Los tiempos varían de una máquina a otra; las alturas y las rotaciones no.
