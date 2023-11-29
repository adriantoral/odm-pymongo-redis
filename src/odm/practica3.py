import enum
from typing import Self

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_CREDENTIALS = ("neo4j", "adriantoral")
NEO4J_CONNECTION = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_CREDENTIALS)


def hacer_query(query, parameters=None):
    with NEO4J_CONNECTION.session() as session:
        result = session.run(query, parameters)
        return result.data()


class TipoConexion(enum.Enum):
    AMIGO = "Amigo"
    FAMILIAR = "Familiar"
    PAREJA = "Pareja"
    LABORAL = "Laboral"
    ESTUDIO = "Estudio"
    CONVERSACION = "Conversacion"
    MENSAJE = "Mensaje"


class Nodo:
    """
    Clase base para los nodos
    """

    tipo: str

    def datos(self):
        result = ""
        for key, value in self.__dict__.items():
            if key != "idnodo": result += f'{key}: "{value}", '
        return "{" + result[:-2] + "}"

    def crear(self): hacer_query(f'merge (nodo:{self.tipo} {self.datos()}) return id(nodo) as idnodo')

    def crear_conexion(self, nodo, tipo_conexion: TipoConexion):
        return hacer_query(f'merge (nodo1:{self.tipo} {self.datos()}) '
                           f'merge (nodo2:{nodo.tipo} {nodo.datos()}) '
                           f'merge (nodo1) - [:{tipo_conexion.value}] -> (nodo2)'
                           f'return id(nodo1) as idnodo1, id(nodo2) as idnodo2'
                           )


class Conversacion(Nodo):
    """
    Tipo de conversacion
    """

    def __init__(self):
        self.tipo = "Conversacion"
        self.id_mensaje = 0

    def crear_mensaje(self, propietario: str, texto: str, fecha: str, hora: str):
        # Crear mensaje
        mensaje = Mensaje(self.id_mensaje, propietario, texto, fecha, hora)
        self.id_mensaje += 1

        # Crear conexion de la conversacion con el mensaje
        self.crear_conexion(mensaje, TipoConexion.MENSAJE)


class Persona(Nodo):
    """
    Tipo de persona
    """

    def __init__(self, nombre: str, apellido: str, edad: int, sexo: str):
        self.tipo = "Persona"
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.sexo = sexo

    def crear_conversacion(self, persona: Self) -> Conversacion:
        # Crear conversacion
        conversacion = Conversacion()
        conversacion.crear()

        # Crear conexiones de las personas con la conversacion
        self.crear_conexion(conversacion, TipoConexion.CONVERSACION)
        persona.crear_conexion(conversacion, TipoConexion.CONVERSACION)

        return conversacion

    def crear_conversacion(self, conversacion: Conversacion, persona: Self):
        pass


class Mensaje(Nodo):
    """
    Tipo de mensaje
    """

    def __init__(self, id_mensaje: int, propietario: str, texto: str, fecha: str, hora: str):
        self.tipo = "Mensaje"
        self.id_mensaje = id_mensaje
        self.propietario = propietario
        self.texto = texto
        self.fecha = fecha
        self.hora = hora


class Empresa(Nodo):
    """
    Tipo de empresa
    """

    def __init__(self, nombre: str, direccion: str):
        self.tipo = "Empresa"
        self.nombre = nombre
        self.direccion = direccion


class CentroEducativo(Nodo):
    """
    Tipo de centro educativo
    """

    def __init__(self, nombre: str, direccion: str):
        self.tipo = "CentroEducativo"
        self.nombre = nombre
        self.direccion = direccion


if __name__ == '__main__':
    # Crear Personas
    adriantoral = Persona("Adrian", "Toral", 21, "M")
    dariollodra = Persona("Dario", "Llodra", 20, "M")

    # Guardar Personas
    adriantoral.crear()
    dariollodra.crear()

    # Crear Empresas
    utad = Empresa("UTAD", "Edificio Madrid, Complejo Europa Empresarial, C. Playa de Liencres, 2 bis, 28290 Las Rozas de Madrid, Madrid")
    utad.crear()

    # Crear Centros Educativos
    ies = CentroEducativo("IES", "Calle de la Constitución, 1, 28290 Las Rozas de Madrid, Madrid")
    ies.crear()

    # Crear Conversaciones
    conversacion1 = Conversacion()
    conversacion1.crear()

    # Crear Conexiones
    adriantoral.crear_conexion(dariollodra, TipoConexion.AMIGO)
    dariollodra.crear_conexion(adriantoral, TipoConexion.AMIGO)

    adriantoral.crear_conexion(utad, TipoConexion.LABORAL)
    dariollodra.crear_conexion(ies, TipoConexion.ESTUDIO)

    conversacion1.crear_mensaje(adriantoral.nombre, "Hola dario", "01/01/2021", "00:00:00")
    conversacion1.crear_mensaje(dariollodra.nombre, "Hola adrian", "01/01/2021", "00:00:01")

    adriantoral.crear_conexion(conversacion1, TipoConexion.CONVERSACION)
    dariollodra.crear_conexion(conversacion1, TipoConexion.CONVERSACION)

    # Cerrar conexion
    NEO4J_CONNECTION.close()
