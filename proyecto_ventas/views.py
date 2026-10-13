from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE ABSTRACTA
# =====================================================================

class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================

class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        self.matriculas = None

        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []

        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())

        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):

        campos_obligatorios = (
            "nombre", "apellido", "email", "carnet", "carrera"
        )

        for campo in campos_obligatorios:
            if campo in datos or id_actual is None:
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()

            if not es_email_valido(email):
                return f"Email inválido: '{email}'"

            for estudiante in self.lista:
                if estudiante.id == id_actual:
                    continue

                if estudiante.email.strip().lower() == email:
                    return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip()

            for estudiante in self.lista:
                if estudiante.id == id_actual:
                    continue

                if estudiante.carnet.strip().lower() == carnet.lower():
                    return "Ese carnet ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for estudiante in self.lista:
            if estudiante.id == id_registro:
                return estudiante

        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []

        if texto == "":
            return encontrados

        for estudiante in self.lista:
            campos = (
                str(estudiante.id),
                estudiante.nombre,
                estudiante.apellido,
                estudiante.email,
                estudiante.carnet,
                estudiante.carrera
            )

            if any(texto in campo.lower() for campo in campos):
                encontrados.append(estudiante)

        return encontrados

    def siguiente(self):
        mayor = 0

        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id

        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip(),
            str(datos["carrera"]).strip().title()
        )

        self.lista.append(estudiante)
        self.guardar()

        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_registro, datos):
        estudiante = self.obtener(id_registro)

        if estudiante is None:
            return False, f"No existe un estudiante con id {id_registro}"

        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {
            "nombre", "apellido", "email", "carnet", "carrera"
        }

        desconocidos = set(datos) - permitidos

        if desconocidos:
            return False, (
                f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            )

        error = self.validar(datos, id_registro)

        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()

            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()

            setattr(estudiante, campo, valor)

        self.guardar()

        return True, f"Estudiante {id_registro} actualizado"

    def eliminar(self, id_registro):
        estudiante = self.obtener(id_registro)

        if estudiante is None:
            return False, f"No existe un estudiante con id {id_registro}"

        # No eliminar estudiantes con matrículas registradas.
        if self.matriculas is not None:
            for matricula in self.matriculas.leer():
                if matricula.estudiante_id == id_registro:
                    return False, (
                        "No se puede eliminar el estudiante porque "
                        "tiene matrículas registradas"
                    )

        self.lista.remove(estudiante)
        self.guardar()

        return True, f"Estudiante {id_registro} eliminado"


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================

class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        self.matriculas = None

        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []

        for materia in self.lista:
            datos.append(materia.a_diccionario())

        self.gestor.guardar(datos)

    def cantidad_matriculados(self, materia_id):
        cantidad = 0

        if self.matriculas is not None:
            for matricula in self.matriculas.leer():
                if matricula.materia_id == materia_id:
                    cantidad += 1

        return cantidad

    def validar(self, datos, id_actual=None):

        campos_obligatorios = ("nombre", "codigo", "creditos", "cupos")

        for campo in campos_obligatorios:
            if campo in datos or id_actual is None:
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "creditos" in datos:
            try:
                creditos = int(datos["creditos"])

                if creditos <= 0:
                    return "Los créditos deben ser mayores que 0"

            except (TypeError, ValueError):
                return "Los créditos deben ser un número entero"

        if "cupos" in datos:
            try:
                cupos = int(datos["cupos"])

                if cupos < 0 or cupos > Materia.CUPOS_MAXIMOS:
                    return (
                        f"Los cupos deben estar entre 0 y "
                        f"{Materia.CUPOS_MAXIMOS}"
                    )

                # Considerar los estudiantes ya matriculados.
                if id_actual is not None:
                    matriculados = self.cantidad_matriculados(id_actual)

                    if cupos + matriculados > Materia.CUPOS_MAXIMOS:
                        return (
                            "Los cupos disponibles más los matriculados "
                            f"no pueden superar {Materia.CUPOS_MAXIMOS}"
                        )

            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()

            if codigo == "":
                return "El código de la materia es obligatorio"

            for materia in self.lista:
                if materia.id == id_actual:
                    continue

                if materia.codigo.upper() == codigo:
                    return "Ese código de materia ya está registrado"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().lower()

            for materia in self.lista:
                if materia.id == id_actual:
                    continue

                if materia.nombre.strip().lower() == nombre:
                    return f"Ya existe una materia llamada {datos['nombre']}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for materia in self.lista:
            if materia.id == id_registro:
                return materia

        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []

        if texto == "":
            return encontrados

        for materia in self.lista:
            campos = (
                str(materia.id),
                materia.nombre,
                materia.codigo
            )

            if any(texto in campo.lower() for campo in campos):
                encontrados.append(materia)

        return encontrados

    def siguiente(self):
        mayor = 0

        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id

        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            int(datos["cupos"])
        )

        self.lista.append(materia)
        self.guardar()

        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_registro, datos):
        materia = self.obtener(id_registro)

        if materia is None:
            return False, f"No existe una materia con id {id_registro}"

        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos

        if desconocidos:
            return False, (
                f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            )

        error = self.validar(datos, id_registro)

        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()

        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()

        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])

        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()

        return True, f"Materia {id_registro} actualizada"

    def eliminar(self, id_registro):
        materia = self.obtener(id_registro)

        if materia is None:
            return False, f"No existe una materia con id {id_registro}"

        # No eliminar materias que tengan matrículas.
        if self.matriculas is not None:
            for matricula in self.matriculas.leer():
                if matricula.materia_id == id_registro:
                    return False, (
                        "No se puede eliminar la materia porque "
                        "tiene matrículas registradas"
                    )

        self.lista.remove(materia)
        self.guardar()

        return True, f"Materia {id_registro} eliminada"


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================

class MatriculaController(CrudBase):

    def __init__(
        self,
        estudiantes,
        materias,
        archivo="data/matriculas.json"
    ):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = []

        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []

        for matricula in self.lista:
            datos.append(matricula.a_diccionario())

        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))

        except (TypeError, ValueError):
            return (
                "Los IDs del estudiante y la materia "
                "deben ser números enteros"
            )

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)

        if materia is None:
            return f"No existe una materia con id {materia_id}"

        periodo = str(datos.get("periodo", "")).strip()

        if periodo == "":
            return "El período es obligatorio"

        if "nota" in datos:
            if not Materia.es_nota_valida(datos["nota"]):
                return "La nota debe ser un número entre 0 y 20"

        # Evitar duplicar estudiante, materia y período.
        for otra in self.lista:
            if otra.id == id_actual:
                continue

            if (
                otra.estudiante_id == estudiante_id
                and otra.materia_id == materia_id
                and otra.periodo.strip().lower() == periodo.lower()
            ):
                return (
                    "El estudiante ya está matriculado en esa "
                    "materia durante ese período"
                )

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for matricula in self.lista:
            if matricula.id == id_registro:
                return matricula

        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []

        if texto == "":
            return encontradas

        for matricula in self.lista:
            campos = (
                str(matricula.id),
                str(matricula.estudiante_id),
                str(matricula.materia_id),
                matricula.periodo,
                str(matricula.nota),
                matricula.fecha,
                matricula.estado()
            )

            if any(texto in str(campo).lower() for campo in campos):
                encontradas.append(matricula)

        return encontradas

    def siguiente(self):
        mayor = 0

        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id

        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))

        if not materia.hay_cupo():
            return False, f"No hay cupos disponibles en {materia.nombre}"

        nota = float(datos.get("nota", 0))

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            int(datos["materia_id"]),
            str(datos["periodo"]).strip(),
            nota
        )

        # Registrar la matrícula y descontar un cupo.
        materia.ocupar_cupo()
        self.lista.append(matricula)

        try:
            self.materias.guardar()
            self.guardar()

        except Exception as error_guardado:
            # Revertir los cambios en memoria si ocurre un error.
            self.lista.remove(matricula)
            materia.liberar_cupo()

            return False, f"No se pudo guardar la matrícula: {error_guardado}"

        return True, f"Matrícula creada: {matricula.etiqueta()}"

    def actualizar(self, id_registro, datos):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, f"No existe una matrícula con id {id_registro}"

        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"periodo", "nota"}
        desconocidos = set(datos) - permitidos

        if desconocidos:
            return False, (
                f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            )

        nuevo_periodo = str(
            datos.get("periodo", matricula.periodo)
        ).strip()

        if nuevo_periodo == "":
            return False, "El período es obligatorio"

        if "nota" in datos:
            if not Materia.es_nota_valida(datos["nota"]):
                return False, "La nota debe ser un número entre 0 y 20"

        # Comprobar que no exista otra matrícula duplicada.
        for otra in self.lista:
            if otra.id == matricula.id:
                continue

            if (
                otra.estudiante_id == matricula.estudiante_id
                and otra.materia_id == matricula.materia_id
                and otra.periodo.strip().lower() == nuevo_periodo.lower()
            ):
                return False, (
                    "Ya existe otra matrícula para esa materia y período"
                )

        periodo_anterior = matricula.periodo
        nota_anterior = matricula.nota

        matricula.periodo = nuevo_periodo

        if "nota" in datos:
            matricula.nota = float(datos["nota"])

        try:
            self.guardar()

        except Exception as error_guardado:
            matricula.periodo = periodo_anterior
            matricula.nota = nota_anterior

            return False, f"No se pudo actualizar la matrícula: {error_guardado}"

        return True, f"Matrícula {id_registro} actualizada"

    def eliminar(self, id_registro):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, f"No existe una matrícula con id {id_registro}"

        materia = self.materias.obtener(matricula.materia_id)

        # Conservar los datos anteriores para poder revertir un fallo.
        if materia is not None:
            cupos_anteriores = materia.cupos
            materia.liberar_cupo()

        self.lista.remove(matricula)

        try:
            if materia is not None:
                self.materias.guardar()

            self.guardar()

        except Exception as error_guardado:
            self.lista.append(matricula)

            if materia is not None:
                materia.cupos = cupos_anteriores

            return False, f"No se pudo retirar la matrícula: {error_guardado}"

        return True, f"Matrícula {id_registro} retirada y cupo liberado"

    # ---------------------------------------------------------------
    # AGRUPAR MATRÍCULAS POR ESTUDIANTE
    # ---------------------------------------------------------------

    def matriculas_por_estudiante(self):
        agrupadas = {}

        for matricula in self.lista:
            agrupadas.setdefault(
                matricula.estudiante_id, []
            ).append(matricula)

        return agrupadas

    # ---------------------------------------------------------------
    # GENERAR CERTIFICADO ACADÉMICO
    # ---------------------------------------------------------------

    def certificado(self, estudiante_id):
        estudiante = self.estudiantes.obtener(estudiante_id)

        if estudiante is None:
            return None

        materias_por_id = {
            materia.id: materia
            for materia in self.materias.leer()
        }

        agrupadas = self.matriculas_por_estudiante()
        matriculas = agrupadas.get(estudiante_id, [])

        texto = "CERTIFICADO ACADÉMICO\n"
        texto += f"Estudiante: {estudiante.nombre_completo()}\n"
        texto += f"Carnet: {estudiante.carnet}\n"
        texto += f"Carrera: {estudiante.carrera}\n"
        texto += "-" * 50 + "\n"

        if not matriculas:
            texto += "El estudiante no registra matrículas."
            return texto

        for matricula in matriculas:
            materia = materias_por_id.get(matricula.materia_id)

            if materia is None:
                nombre_materia = "Materia eliminada"
            else:
                nombre_materia = materia.nombre

            texto += (
                f"Materia: {nombre_materia} | "
                f"Período: {matricula.periodo} | "
                f"Nota: {matricula.nota:g} | "
                f"Estado: {matricula.estado()}\n"
            )

        return texto