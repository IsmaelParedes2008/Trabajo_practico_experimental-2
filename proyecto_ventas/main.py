from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error,
    imprimir_info, confirmar
)

from views import (
    EstudianteController,
    MateriaController,
    MatriculaController
)

from models import Materia

# =====================================================================
# CREAR Y CONECTAR LOS CONTROLADORES
# =====================================================================

estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)

# Conectar las matrículas con estudiantes y materias.
estudiantes.matriculas = matriculas
materias.matriculas = matriculas


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    if not objetos:
        imprimir_info(vacio)
        return

    for objeto in objetos:
        print(f"  {objeto}")

    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        nombre = str(clave).replace("_", " ").capitalize()
        print(f"  {nombre:<20}: {valor}")


# =====================================================================
# MENÚ DE ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("REGISTRAR ESTUDIANTE")

    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: ")
    }

    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    mostrar_lista(
        estudiantes.leer(),
        "Todavía no hay estudiantes registrados."
    )
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")

    termino = input("Nombre, apellido, email, carnet o carrera: ")

    mostrar_lista(
        estudiantes.buscar(termino),
        f"No hay estudiantes que coincidan con '{termino}'."
    )

    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")

    id_estudiante = pedir_entero("ID del estudiante: ")
    estudiante = (
        estudiantes.obtener(id_estudiante)
        if id_estudiante is not None else None
    )

    if estudiante is None:
        imprimir_error("Estudiante no encontrado.")
    else:
        mostrar_detalle(estudiante)

    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")

    id_estudiante = pedir_entero("ID del estudiante: ")
    estudiante = (
        estudiantes.obtener(id_estudiante)
        if id_estudiante is not None else None
    )

    if estudiante is None:
        imprimir_error("Estudiante no encontrado.")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco los campos que no quiera cambiar.\n")

    cambios = {}

    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()

        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(
        *estudiantes.actualizar(id_estudiante, cambios)
    )

    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")

    id_estudiante = pedir_entero("ID del estudiante: ")
    estudiante = (
        estudiantes.obtener(id_estudiante)
        if id_estudiante is not None else None
    )

    if estudiante is None:
        imprimir_error("Estudiante no encontrado.")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")

    if confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(estudiantes.eliminar(id_estudiante))
    else:
        imprimir_info("Operación cancelada.")

    pausa()


def estudiantes_por_carrera():
    imprimir_titulo("ESTUDIANTES POR CARRERA")

    agrupados = {}

    for estudiante in estudiantes.leer():
        agrupados.setdefault(estudiante.carrera, []).append(
            estudiante.nombre_completo()
        )

    if not agrupados:
        imprimir_info("No hay estudiantes registrados.")
    else:
        for carrera, nombres in agrupados.items():
            print(f"\n{carrera}:")
            for nombre in nombres:
                print(f"  - {nombre}")

    pausa()


# =====================================================================
# MENÚ DE MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("REGISTRAR MATERIA")

    datos = {
        "nombre": input("Nombre de la materia: "),
        "codigo": input("Código: "),
        "creditos": input("Créditos: "),
        "cupos": input(
            f"Cupos disponibles (máximo {Materia.CUPOS_MAXIMOS}): "
        )
    }

    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("LISTA DE MATERIAS")

    mostrar_lista(
        materias.leer(),
        "Todavía no hay materias registradas."
    )

    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")

    termino = input("Nombre o código de la materia: ")

    mostrar_lista(
        materias.buscar(termino),
        f"No hay materias que coincidan con '{termino}'."
    )

    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")

    id_materia = pedir_entero("ID de la materia: ")
    materia = (
        materias.obtener(id_materia)
        if id_materia is not None else None
    )

    if materia is None:
        imprimir_error("Materia no encontrada.")
    else:
        mostrar_detalle(materia)
        print(
            f"  Estudiantes matriculados: "
            f"{materias.cantidad_matriculados(materia.id)}"
        )

    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")

    id_materia = pedir_entero("ID de la materia: ")
    materia = (
        materias.obtener(id_materia)
        if id_materia is not None else None
    )

    if materia is None:
        imprimir_error("Materia no encontrada.")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco los campos que no quiera cambiar.\n")

    cambios = {}

    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()

        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(
        *materias.actualizar(id_materia, cambios)
    )

    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")

    id_materia = pedir_entero("ID de la materia: ")
    materia = (
        materias.obtener(id_materia)
        if id_materia is not None else None
    )

    if materia is None:
        imprimir_error("Materia no encontrada.")
        return pausa()

    imprimir_info(f"Se eliminará: {materia.etiqueta()}")

    if confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(materias.eliminar(id_materia))
    else:
        imprimir_info("Operación cancelada.")

    pausa()


# =====================================================================
# MENÚ DE MATRÍCULAS
# =====================================================================

def registrar_matricula():
    imprimir_titulo("REGISTRAR MATRÍCULA")

    imprimir_info("Estudiantes registrados:")
    mostrar_lista(estudiantes.leer())

    imprimir_info("Materias disponibles:")
    mostrar_lista(materias.leer())

    if not estudiantes.leer():
        imprimir_error("Primero debe registrar un estudiante.")
        return pausa()

    if not materias.leer():
        imprimir_error("Primero debe registrar una materia.")
        return pausa()

    estudiante_id = pedir_entero("\nID del estudiante: ")
    materia_id = pedir_entero("ID de la materia: ")

    if estudiante_id is None or materia_id is None:
        imprimir_error("Los IDs deben ser números enteros.")
        return pausa()

    periodo = input("Período académico (ej. 2026-2): ").strip()
    nota = input("Nota inicial (0 a 20, Enter para 0): ").strip()

    if nota == "":
        nota = "0"

    datos = {
        "estudiante_id": estudiante_id,
        "materia_id": materia_id,
        "periodo": periodo,
        "nota": nota
    }

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("LISTA DE MATRÍCULAS")

    mostrar_lista(
        matriculas.leer(),
        "Todavía no hay matrículas registradas."
    )

    pausa()


def buscar_matricula():
    imprimir_titulo("BUSCAR MATRÍCULA")

    termino = input(
        "ID, estudiante, materia, período, nota o estado: "
    )

    mostrar_lista(
        matriculas.buscar(termino),
        "No se encontraron matrículas."
    )

    pausa()
    
def ver_matricula():
    imprimir_titulo("VER MATRÍCULA POR ID")

    id_matricula = pedir_entero("ID de la matrícula: ")
    matricula = (
        matriculas.obtener(id_matricula)
        if id_matricula is not None else None
    )

    if matricula is None:
        imprimir_error("Matrícula no encontrada.")
    else:
        estudiante = estudiantes.obtener(matricula.estudiante_id)
        materia = materias.obtener(matricula.materia_id)

        print(f"\nID                  : {matricula.id}")
        print(f"Fecha               : {matricula.fecha}")
        print(f"Estudiante ID       : {matricula.estudiante_id}")
        print(f"Materia ID          : {matricula.materia_id}")
        print(f"Periodo             : {matricula.periodo}")
        print(f"Nota                : {matricula.nota:g}")
        print(f"Estado              : {matricula.estado()}")

        print(
            f"Estudiante          : "
            f"{estudiante.nombre_completo() if estudiante else 'No encontrado'}"
        )
        print(
            f"Materia             : "
            f"{materia.nombre if materia else 'No encontrada'}"
        )

    pausa()

def actualizar_matricula():
    imprimir_titulo("ACTUALIZAR MATRÍCULA")

    id_matricula = pedir_entero("ID de la matrícula: ")
    matricula = (
        matriculas.obtener(id_matricula)
        if id_matricula is not None else None
    )

    if matricula is None:
        imprimir_error("Matrícula no encontrada.")
        return pausa()

    mostrar_detalle(matricula)
    print("\nDeje en blanco los campos que no quiera cambiar.")

    cambios = {}

    nuevo_periodo = input(
        f"Período [{matricula.periodo}]: "
    ).strip()

    if nuevo_periodo:
        cambios["periodo"] = nuevo_periodo

    nueva_nota = input(
        f"Nota (0 a 20) [{matricula.nota:g}]: "
    ).strip()

    if nueva_nota:
        cambios["nota"] = nueva_nota

    mostrar_resultado(
        *matriculas.actualizar(id_matricula, cambios)
    )

    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")

    id_matricula = pedir_entero("ID de la matrícula: ")
    matricula = (
        matriculas.obtener(id_matricula)
        if id_matricula is not None else None
    )

    if matricula is None:
        imprimir_error("Matrícula no encontrada.")
        return pausa()

    imprimir_info(f"Se retirará: {matricula.etiqueta()}")

    if confirmar("¿Confirma el retiro? Se liberará un cupo."):
        mostrar_resultado(matriculas.eliminar(id_matricula))
    else:
        imprimir_info("Operación cancelada.")

    pausa()


# =====================================================================
# CONSULTAS ACADÉMICAS
# =====================================================================

def consultar_matriculas_estudiante():
    imprimir_titulo("MATRÍCULAS POR ESTUDIANTE")

    id_estudiante = pedir_entero("ID del estudiante: ")

    if id_estudiante is None:
        imprimir_error("El ID debe ser un número entero.")
        return pausa()

    estudiante = estudiantes.obtener(id_estudiante)

    if estudiante is None:
        imprimir_error("Estudiante no encontrado.")
        return pausa()

    agrupadas = matriculas.matriculas_por_estudiante()
    registros = agrupadas.get(id_estudiante, [])

    imprimir_info(f"Estudiante: {estudiante.nombre_completo()}")

    if not registros:
        imprimir_info("El estudiante no registra matrículas.")
    else:
        materias_por_id = {
            materia.id: materia
            for materia in materias.leer()
        }

        for registro in registros:
            materia = materias_por_id.get(registro.materia_id)
            nombre = materia.nombre if materia else "Materia eliminada"

            print(
                f"  {nombre} | "
                f"Período: {registro.periodo} | "
                f"Nota: {registro.nota:g} | "
                f"Estado: {registro.estado()}"
            )

        imprimir_info(f"Total de matrículas: {len(registros)}")

    pausa()


def generar_certificado():
    imprimir_titulo("CERTIFICADO ACADÉMICO")

    id_estudiante = pedir_entero("ID del estudiante: ")

    if id_estudiante is None:
        imprimir_error("El ID debe ser un número entero.")
        return pausa()

    texto = matriculas.certificado(id_estudiante)

    if texto is None:
        imprimir_error("Estudiante no encontrado.")
    else:
        print()
        print(texto)

    pausa()


def resumen_academico():
    imprimir_titulo("RESUMEN ACADÉMICO")

    lista_estudiantes = estudiantes.leer()
    lista_materias = materias.leer()
    lista_matriculas = matriculas.leer()

    aprobadas = 0
    reprobadas = 0

    for matricula in lista_matriculas:
        if matricula.esta_aprobada():
            aprobadas += 1
        else:
            reprobadas += 1

    cupos_disponibles = 0

    for materia in lista_materias:
        cupos_disponibles += materia.cupos

    print(f"  Estudiantes registrados : {len(lista_estudiantes)}")
    print(f"  Materias registradas    : {len(lista_materias)}")
    print(f"  Matrículas registradas  : {len(lista_matriculas)}")
    print(f"  Matrículas aprobadas    : {aprobadas}")
    print(f"  Matrículas reprobadas   : {reprobadas}")
    print(f"  Cupos disponibles       : {cupos_disponibles}")
    print(f"  Nota mínima para aprobar: {Materia.NOTA_APROBACION}/20")

    pausa()


# =====================================================================
# DICCIONARIOS DE LOS SUBMENÚS
# =====================================================================

MENU_ESTUDIANTES = {
    "1": ("Registrar estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por ID", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "7": ("Estudiantes por carrera", estudiantes_por_carrera),
    "0": ("Volver", None)
}

MENU_MATERIAS = {
    "1": ("Registrar materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por ID", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None)
}

MENU_MATRICULAS = {
    "1": ("Registrar matrícula", registrar_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Buscar", buscar_matricula),
    "4": ("Ver por ID", ver_matricula),
    "5": ("Actualizar período o nota", actualizar_matricula),
    "6": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None)
}

MENU_CONSULTAS = {
    "1": ("Matrículas por estudiante", consultar_matriculas_estudiante),
    "2": ("Generar certificado académico", generar_certificado),
    "3": ("Resumen académico", resumen_academico),
    "0": ("Volver", None)
}


# =====================================================================
# EJECUTAR SUBMENÚS
# =====================================================================

def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)

        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")

        print()
        tecla = input("Opción: ").strip()

        if tecla not in opciones:
            imprimir_error("Opción no válida.")
            pausa()
            continue

        _texto, funcion = opciones[tecla]

        if funcion is None:
            break

        funcion()


# =====================================================================
# MENÚ PRINCIPAL
# =====================================================================

def main():
    while True:
        imprimir_titulo("SISTEMA DE GESTIÓN ACADÉMICA")

        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Consultas académicas")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()

        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)

        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)

        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)

        elif tecla == "4":
            ejecutar_menu("CONSULTAS ACADÉMICAS", MENU_CONSULTAS)

        elif tecla == "0":
            imprimir_info("Programa finalizado.")
            break

        else:
            imprimir_error("Opción no válida.")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")