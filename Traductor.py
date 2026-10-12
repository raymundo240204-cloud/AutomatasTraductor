import ast
import sys
from pathlib import Path


class Traductor:
    def __init__(self):
        self.instrucciones = []
        self.variables = {}

    def emitir(self, instruccion):
        self.instrucciones.append(f"    {instruccion}")

    def error(self, nodo, mensaje):
        linea = getattr(nodo, "lineno", "?")
        raise ValueError(f"Línea {linea}: {mensaje}")

    def expresion(self, nodo):
        """Traduce una expresión y deja su resultado en AX."""

        # Número entero
        if isinstance(nodo, ast.Constant):
            if type(nodo.value) is not int:
                self.error(nodo, "Solo se permiten números enteros.")

            if not -32768 <= nodo.value <= 32767:
                self.error(nodo, "El número debe estar entre -32768 y 32767.")

            self.emitir(f"mov ax, {nodo.value}")

        # Lectura de una variable
        elif isinstance(nodo, ast.Name):
            if nodo.id not in self.variables:
                self.error(nodo, f"La variable '{nodo.id}' no está definida.")

            self.emitir(f"mov ax, [{self.variables[nodo.id]}]")

        # Signos positivo y negativo
        elif isinstance(nodo, ast.UnaryOp):
            if not isinstance(nodo.op, (ast.UAdd, ast.USub)):
                self.error(nodo, "Operador unario no permitido.")

            # Python representa -32768 como -(32768).
            if (
                isinstance(nodo.op, ast.USub)
                and isinstance(nodo.operand, ast.Constant)
                and type(nodo.operand.value) is int
                and nodo.operand.value == 32768
            ):
                self.emitir("mov ax, -32768")
                return

            self.expresion(nodo.operand)

            if isinstance(nodo.op, ast.USub):
                self.emitir("neg ax")

        # Operación entre dos expresiones
        elif isinstance(nodo, ast.BinOp):
            operadores = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod)

            if not isinstance(nodo.op, operadores):
                self.error(nodo, "Usa únicamente +, -, *, // o %.")

            # Guardar el resultado izquierdo mientras se calcula el derecho.
            self.expresion(nodo.left)
            self.emitir("push ax")
            self.expresion(nodo.right)
            self.emitir("mov bx, ax")
            self.emitir("pop ax")

            # AX contiene el operando izquierdo; BX, el derecho.
            if isinstance(nodo.op, ast.Add):
                self.emitir("add ax, bx")
            elif isinstance(nodo.op, ast.Sub):
                self.emitir("sub ax, bx")
            elif isinstance(nodo.op, ast.Mult):
                self.emitir("imul bx")
            else:
                self.emitir("call dividir")
                if isinstance(nodo.op, ast.Mod):
                    self.emitir("mov ax, dx")

        else:
            self.error(nodo, "Esta expresión no está soportada.")

    def traducir(self, codigo):
        self.instrucciones = []
        self.variables = {}
        arbol = ast.parse(codigo)

        for sentencia in arbol.body:
            if not isinstance(sentencia, ast.Assign):
                self.error(sentencia, "Solo se permiten asignaciones.")

            if (
                len(sentencia.targets) != 1
                or not isinstance(sentencia.targets[0], ast.Name)
            ):
                self.error(sentencia, "Usa asignaciones como: variable = expresión.")

            nombre = sentencia.targets[0].id
            self.instrucciones.append(
                f"\n    ; Linea {sentencia.lineno}: asignacion"
            )

            # Primero evaluar, para detectar variables usadas antes de definirse.
            self.expresion(sentencia.value)

            # Etiquetas internas para evitar conflictos con registros como AX.
            if nombre not in self.variables:
                self.variables[nombre] = f"var_{len(self.variables)}"

            self.emitir(f"mov [{self.variables[nombre]}], ax")

        declaraciones = "\n".join(
            f"{etiqueta} dw 0" for etiqueta in self.variables.values()
        )

        return (
            "org 100h\n\n"
            + "\n".join(self.instrucciones)
            + "\n\n"
            + "    mov ax, 4C00h\n"
            + "    int 21h\n\n"
            + declaraciones
            + "\n"
            + RUTINA_DIVISION
        )


# IDIV redondea hacia cero; Python // redondea hacia abajo.
# Esta rutina ajusta cociente y residuo para coincidir con Python.
RUTINA_DIVISION = """
dividir:
    cmp bx, 0
    je error_aritmetico

    ; Evitar el desbordamiento de -32768 / -1.
    cmp ax, 8000h
    jne division_valida
    cmp bx, -1
    je error_aritmetico

division_valida:
    cwd
    idiv bx

    ; AX = cociente, DX = residuo.
    cmp dx, 0
    je division_fin

    mov cx, dx
    xor cx, bx
    jns division_fin

    dec ax
    add dx, bx

division_fin:
    ret

error_aritmetico:
    mov ax, 4C01h
    int 21h
"""


def main():
    if len(sys.argv) not in (2, 3):
        print("Uso: python traductor.py entrada.py [salida.asm]")
        return 1

    entrada = Path(sys.argv[1])
    salida = (
        Path(sys.argv[2])
        if len(sys.argv) == 3
        else entrada.with_suffix(".asm")
    )

    try:
        if entrada.resolve() == salida.resolve():
            raise ValueError("La entrada y la salida deben ser archivos distintos.")

        codigo = entrada.read_text(encoding="utf-8")
        traductor = Traductor()
        ensamblador = traductor.traducir(codigo)
        salida.write_text(ensamblador, encoding="ascii")

        print(f"Archivo generado: {salida}")
        print("Variables para inspeccionar en EMU8086:")
        for nombre, etiqueta in traductor.variables.items():
            print(f"  {nombre} -> {etiqueta}")

    except (OSError, ValueError, SyntaxError) as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())