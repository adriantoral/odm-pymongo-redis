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


class TipoNodos(enum.Enum):
    PERSONA = "Persona"
    EMPRESA = "Empresa"
    CENTRO_EDUCATIVO = "CentroEducativo"
    MENSAJE = "Mensaje"


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
        for key, value in self.__dict__.items(): result += f'{key}: "{value}", '
        return "{" + result[:-2] + "}"

    def crear(self): hacer_query(f'merge (nodo:{self.tipo} {self.datos()})')

    def crear_conexion(self, nodo, tipo_conexion: TipoConexion):
        hacer_query(f'merge (nodo1:{self.tipo} {self.datos()}) '
                    f'merge (nodo2:{nodo.tipo} {nodo.datos()}) '
                    f'merge (nodo1) - [:{tipo_conexion.value}] -> (nodo2)'
                    )


class Mensaje(Nodo):
    """
    Tipo de mensaje
    """

    def __init__(self, texto: str, timestamp: str, hora: str):
        self.tipo = TipoNodos.MENSAJE.value
        self.texto = texto
        self.timestamp = timestamp
        self.hora = hora


class Persona(Nodo):
    """
    Tipo de persona
    """

    def __init__(self, nombre: str, apellido: str, edad: int, sexo: str):
        self.tipo = TipoNodos.PERSONA.value
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.sexo = sexo

    def crear_mensaje(self, persona: Self, mensaje: Mensaje):
        hacer_query(f'merge (nodo1:{self.tipo} {self.datos()}) '
                    f'merge (nodo2:{persona.tipo} {persona.datos()}) '
                    f'merge (nodo1) - [:{mensaje.tipo} {mensaje.datos()}] -> (nodo2)'
                    )


class Empresa(Nodo):
    """
    Tipo de empresa
    """

    def __init__(self, nombre: str, direccion: str):
        self.tipo = TipoNodos.EMPRESA.value
        self.nombre = nombre
        self.direccion = direccion


class CentroEducativo(Nodo):
    """
    Tipo de centro educativo
    """

    def __init__(self, nombre: str, direccion: str):
        self.tipo = TipoNodos.CENTRO_EDUCATIVO.value
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

    # Crear Conexiones
    adriantoral.crear_conexion(dariollodra, TipoConexion.AMIGO)
    dariollodra.crear_conexion(adriantoral, TipoConexion.AMIGO)

    adriantoral.crear_conexion(utad, TipoConexion.LABORAL)
    dariollodra.crear_conexion(ies, TipoConexion.ESTUDIO)

    adriantoral.crear_mensaje(dariollodra, Mensaje("Hola", "1701263134", "12:00"))
    dariollodra.crear_mensaje(adriantoral, Mensaje("Hola", "1701263135", "12:00"))
    adriantoral.crear_mensaje(dariollodra, Mensaje("Que tal?", "1701263136", "12:01"))
    dariollodra.crear_mensaje(adriantoral, Mensaje("Bien", "1701263137", "12:01"))
    adriantoral.crear_mensaje(dariollodra, Mensaje("Y tu?", "1701263138", "12:02"))
    dariollodra.crear_mensaje(adriantoral, Mensaje("Bien", "1701263139", "12:02"))
    adriantoral.crear_mensaje(dariollodra, Mensaje("Me alegro", "1701263140", "12:03"))
    dariollodra.crear_mensaje(adriantoral, Mensaje("Gracias", "1701263141", "12:03"))
    adriantoral.crear_mensaje(dariollodra, Mensaje("Adios", "1701263142", "12:04"))
    dariollodra.crear_mensaje(adriantoral, Mensaje("Adios", "1701263143", "12:04"))

    # Cerrar conexion
    NEO4J_CONNECTION.close()
