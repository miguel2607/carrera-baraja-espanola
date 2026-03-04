# Carrera de Caballos con Baraja Española (Python)

## Descripción del proyecto

Este proyecto implementa una versión automatizada del juego **Carrera de Caballos con cartas**, utilizando la **baraja española** y desarrollado en **Python con interfaz gráfica (Tkinter)**.

El objetivo es simular la carrera entre diferentes caballos representados por los **palos de la baraja española** (Oros, Copas, Espadas y Bastos).
Cada vez que se voltea una carta, el caballo correspondiente avanza una posición en la pista.

El juego incluye además **checkpoints**, que al revelarse pueden provocar penalizaciones que hacen retroceder a un caballo.

El sistema permite jugar con **2, 3 o 4 jugadores**.

---

# Objetivo de la actividad

Construir un juego automatizado donde se evidencie la comprensión del concepto de:

* Modelo de datos
* Estructuras
* Operadores
* Restricciones

Aplicando una **metodología de solución de problemas**.

---

# Metodología aplicada

## 1. Análisis del problema

El juego original consiste en una carrera donde cada caballo corresponde a un palo de la baraja.

Reglas principales:

* Cada carta volteada hace avanzar al caballo del mismo palo.
* Existen **7 checkpoints**.
* Cuando todos los caballos pasan un checkpoint se revela una carta.
* Si la carta revelada coincide con un caballo activo, ese caballo **retrocede una posición**.
* Gana el caballo que llegue primero a la meta.

---

## 2. Alternativas de solución

Se consideraron dos enfoques:

1. Juego en consola
2. Juego con interfaz gráfica

Se eligió **interfaz gráfica en Python (Tkinter)** para facilitar la visualización del avance de los caballos y las cartas.

---

## 3. Modelo de datos

### Entidades principales

**Carta**

* palo
* número

**Baraja**

* lista de cartas
* método para mezclar
* método para sacar cartas

**Juego**

* caballos activos
* posiciones de los caballos
* checkpoints
* cartas reveladas

---

### Estructuras utilizadas

* **Listas** → para almacenar cartas y checkpoints
* **Diccionarios** → para posiciones de caballos
* **Clases** → para representar cartas y lógica del juego

Ejemplo:

```python
positions = {
    "Oros": 0,
    "Copas": 0,
    "Espadas": 0,
    "Bastos": 0
}
```

---

## 4. Operadores utilizados

Operadores aplicados dentro del sistema:

* **Asignación**

```python
posicion = posicion + 1
```

* **Comparación**

```python
if carta.suit in active_suits:
```

* **Lógicos**

```python
if pos >= TRACK_LEN
```

---

## 5. Restricciones del sistema

* Solo se permiten **2, 3 o 4 jugadores**
* Cada jugador corresponde a un **palo único**
* El tablero tiene **7 checkpoints**
* El caballo no puede retroceder por debajo de 0

---

## 6. Implementación

Lenguaje utilizado:

**Python 3**

Interfaz gráfica:

**Tkinter**

Conversión de cartas SVG a PNG:

* svglib
* reportlab
* pillow

---

# Estructura del proyecto

```
carrera-baraja-espanola
│
├── main.py
├── README.md
├── configuracion.txt
│
├── src
│   ├── gui.py
│   ├── game.py
│   └── model.py
│
├── assets
│   ├── svg
│   └── png_cache
```

---

# Funcionamiento del juego

1. El usuario selecciona **2, 3 o 4 caballos**.
2. Se eligen los **palos activos**.
3. Se inicia la carrera.
4. Cada turno se voltea una carta.
5. El caballo del palo correspondiente avanza.
6. Cuando todos pasan un checkpoint se revela una carta de penalización.
7. El primer caballo que llega a la meta gana.

---

# Cómo ejecutar el proyecto

1. Instalar Python 3.

2. Instalar dependencias:

```
pip install pillow
pip install svglib
pip install reportlab
```

3. Ejecutar el programa:

```
python main.py
```

---

# Tecnologías utilizadas

* Python
* Tkinter
* Pillow
* svglib
* reportlab

---

# Autor

Proyecto académico desarrollado para demostrar el uso de:

* Modelo de datos
* Estructuras
* Operadores
* Restricciones
* Metodología de solución de problemas
