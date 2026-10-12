
# AutomatasTraductor

Traductor de un subconjunto de Python a lenguaje ensamblador para arquitectura 8086. El proyecto toma expresiones matemáticas con asignaciones simples, valida su sintaxis y genera un archivo `.asm` listo para ser ejecutado en emuladores como EMU8086.

## Descripción

Este proyecto implementa un compilador muy básico para una pequeña gramática de Python, enfocada en:

- Asignaciones de variables
- Números enteros
- Variables previamente definidas
- Operadores unarios `+` y `-`
- Operadores binarios `+`, `-`, `*`, `//` y `%`
- Validación de rango para enteros de 16 bits
- Generación de código ensamblador 8086 compatible con DOS

La lógica principal está en `Traductor.py`, mientras que `entrada.py` contiene un ejemplo de entrada que demuestra el comportamiento del traductor.

## Características

- Traduce expresiones Python a instrucciones de ensamblador.
- Revisa que las variables existan antes de ser usadas.
- Detecta errores de sintaxis y de tipos.
- Genera variables en memoria con etiquetas como `var_0`, `var_1`, etc.
- Implementa una rutina de división para que `//` y `%` respeten el comportamiento de Python.
- Produce un archivo `.asm` con cabecera `org 100h` y salida para DOS.

## Requisitos

- Python 3.x
- Un emulador 8086 o entorno compatible (por ejemplo, EMU8086)

## Estructura del repositorio

- `Traductor.py`: implementación del traductor y generación del código ensamblador.
- `entrada.py`: ejemplo de programa de entrada escrito en el subconjunto soportado.

## Uso

Desde la terminal, ejecuta:

```bash
python Traductor.py entrada.py
```

```bash
python Traductor.py entrada.py salida.asm
```

## Ejemplo de entrada

El archivo `entrada.py` contiene un ejemplo como este:

```python
a = 10
b = 3
suma = a + b
resta = a - b
producto = a * b
cociente = a // b
residuo = a % b
resultado = (a + b) * 2
negativo = -7 // 3
```

## Ejemplo de salida generada

El traductor genera instrucciones del tipo:

```asm
org 100h

    ; Linea 1: asignacion
    mov ax, 10
    mov [var_0], ax

    ; Linea 2: asignacion
    mov ax, 3
    mov [var_1], ax

    ; Linea 3: asignacion
    mov ax, [var_0]
    push ax
    mov ax, [var_1]
    mov bx, ax
    pop ax
    add ax, bx
    mov [var_2], ax
```

## Limitaciones

Este traductor está pensado para un subconjunto muy pequeño de Python y no soporta:

- Condicionales
- Ciclos
- Funciones
- Listas, diccionarios u otros tipos complejos
- Operaciones con flotantes
- Asignaciones múltiples o estructuras avanzadas

## Objetivo

El proyecto sirve como ejercicio de compilación y traducción de lenguaje de alto nivel a ensamblador, mostrando cómo se pueden interpretar expresiones de Python y convertirlas en instrucciones de bajo nivel para una arquitectura 8086.

## Licencia

Este repositorio no especifica una licencia en el momento actual, por lo que se recomienda revisar el contenido del proyecto antes de reutilizarlo en producción o distribuirlo públicamente.
```

If you want, I can also produce:
- a more polished English version,
- a shorter GitHub-style README,
- or a README tailored for academic/coursework presentation.
