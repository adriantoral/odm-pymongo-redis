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
    PUBLICACIONES = "Publicaciones"


class TipoConexion(enum.Enum):
    AMIGO = "Amigo"
    FAMILIAR = "Familiar"
    PAREJA = "Pareja"
    LABORAL = "Laboral"
    ESTUDIO = "Estudio"
    CONVERSACION = "Conversacion"
    MENSAJE = "Mensaje"
    PUBLICACIONES = "Publicaciones"
    MENCION = "Mencion"


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
        hacer_query(
            f'merge (nodo1:{self.tipo} {self.datos()}) '
            f'merge (nodo2:{nodo.tipo} {nodo.datos()}) '
            f'merge (nodo1) - [:{tipo_conexion.value}] -> (nodo2)'
        )

    def tiene_conexion(self, nodo: Self, tipo_conexion: TipoConexion):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{tipo_conexion.value}] -> (nodo2:{nodo.tipo} {nodo.datos()}) return nodo2')


class EntidadPublica(Nodo):
    def crear_mensaje(self, nodo: Nodo, mensaje):
        hacer_query(
            f'merge (nodo1:{self.tipo} {self.datos()}) '
            f'merge (nodo2:{nodo.tipo} {nodo.datos()}) '
            f'merge (nodo1) - [:{mensaje.tipo} {mensaje.datos()}] -> (nodo2)'
        )

    def crear_publicacion(self, titulo: str, cuerpo: str, fecha: str):
        publicacion = Publicaciones(titulo, cuerpo, fecha)
        self.crear_conexion(publicacion, TipoConexion.PUBLICACIONES)

        return publicacion

    def get_publicaciones(self):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{TipoConexion.PUBLICACIONES.value}] -> (nodo2) return relacion, nodo2')

    def get_mensajes(self, nodo: Nodo):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{TipoConexion.MENSAJE.value}] -> (:{nodo.tipo} {nodo.datos()}) return relacion.texto, relacion.timestamp, relacion.hora')


class Mensaje(Nodo):
    """
    Tipo de mensaje
    """

    def __init__(self, texto: str, timestamp: str, hora: str, **kwargs):
        self.tipo = TipoNodos.MENSAJE.value
        self.texto = texto
        self.timestamp = timestamp
        self.hora = hora


class Publicaciones(Nodo):
    """
    Tipo de mensaje
    """

    def __init__(self, titulo: str, cuerpo: str, fecha: str, **kwargs):
        self.tipo = TipoNodos.PUBLICACIONES.value
        self.titulo = titulo
        self.cuerpo = cuerpo
        self.fecha = fecha

    def crear_menciones(self, *nodos: Nodo):
        for nodo in nodos: self.crear_conexion(nodo, TipoConexion.MENCION)

        return self

    def get_menciones(self):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{TipoConexion.MENCION.value}] -> (nodo2) return nodo2')


class Persona(EntidadPublica):
    """
    Tipo de persona
    """

    def __init__(self, nombre: str, apellido: str, edad: int, sexo: str, **kwargs):
        self.tipo = TipoNodos.PERSONA.value
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.sexo = sexo

    def get_amigos(self):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{TipoConexion.AMIGO.value}] -> (nodo2) return relacion, nodo2')

    def get_familiares(self):
        return hacer_query(f'match (nodo:{self.tipo} {self.datos()}) - [relacion:{TipoConexion.FAMILIAR.value}] -> (nodo2) return relacion, nodo2')

    def get_amigos_y_familiares(self):
        return [*self.get_amigos(), *self.get_familiares()]


class Empresa(EntidadPublica):
    """
    Tipo de empresa
    """

    def __init__(self, nombre: str, direccion: str, **kwargs):
        self.tipo = TipoNodos.EMPRESA.value
        self.nombre = nombre
        self.direccion = direccion


class CentroEducativo(EntidadPublica):
    """
    Tipo de centro educativo
    """

    def __init__(self, nombre: str, direccion: str, **kwargs):
        self.tipo = TipoNodos.CENTRO_EDUCATIVO.value
        self.nombre = nombre
        self.direccion = direccion


if __name__ == '__main__':
    # Borrar todos los nodos
    hacer_query("match (n) detach delete n")

    # Crear 5 usuarios
    adriantoral = Persona("Adrian", "Toral", 21, "M")
    dariollodra = Persona("Dario", "Llodra", 20, "M")
    ikerlizarraga = Persona("Iker", "Lizarraga", 21, "M")
    sergiorodriguez = Persona("Sergio", "Rodriguez", 12, "M")
    davidcuadrado = Persona("David", "Cuadrado", 27, "M")

    # Crear relaciones de los usuarios
    adriantoral.crear_conexion(dariollodra, TipoConexion.AMIGO)
    adriantoral.crear_conexion(ikerlizarraga, TipoConexion.AMIGO)
    adriantoral.crear_conexion(sergiorodriguez, TipoConexion.FAMILIAR)
    adriantoral.crear_conexion(davidcuadrado, TipoConexion.FAMILIAR)

    # Crear 4 familiares
    pedroparedes = Persona("Pedro", "Paredes", 21, "M")
    josecacicedo = Persona("Jose", "Cacicedo", 21, "M")
    mariajimenez = Persona("Maria", "Jimenez", 21, "M")
    lauraperez = Persona("Laura", "Perez", 21, "M")

    # Crear relaciones de los familiares
    sergiorodriguez.crear_conexion(pedroparedes, TipoConexion.FAMILIAR)
    sergiorodriguez.crear_conexion(josecacicedo, TipoConexion.FAMILIAR)
    davidcuadrado.crear_conexion(mariajimenez, TipoConexion.FAMILIAR)
    davidcuadrado.crear_conexion(lauraperez, TipoConexion.FAMILIAR)

    # Crear mensajes
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

    # Crear 2 empresas y 1 centro educativo
    utad = CentroEducativo("UTAD", "Edificio Madrid, Complejo Europa Empresarial, C. Playa de Liencres, 2 bis, 28290 Las Rozas de Madrid, Madrid")
    google = Empresa("Google", "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA")
    microsoft = Empresa("Microsoft", "One Microsoft Way, Redmond, WA 98052-6399, USA")

    # Crear relacion laboral
    adriantoral.crear_conexion(utad, TipoConexion.ESTUDIO)
    adriantoral.crear_conexion(google, TipoConexion.LABORAL)
    adriantoral.crear_conexion(microsoft, TipoConexion.LABORAL)

    # Crear publicaciones y menciones
    (
        adriantoral
        .crear_publicacion("Publicacion 1", "Cuerpo de la publicacion 1", "11-12-2023")
        .crear_menciones(dariollodra)
        .crear_menciones(utad)
        .crear_menciones(google)
        .crear_menciones(microsoft)
    )

    # Consulta 1 - Obtener los amigos y familiares de un usuario
    print("\nConsulta 1 - Obtener los amigos y familiares de un usuario")
    for x in adriantoral.get_amigos_y_familiares():
        print(x['relacion'])

    # Consulta 2 - Obtener los familiares de los familiares de un usuario
    print("\nConsulta 2 - Obtener los familiares de los familiares de un usuario")
    for x in adriantoral.get_familiares():
        for y in Persona(**x['nodo2']).get_familiares():
            print(y['relacion'])

    # Consulta 3 - Obtener los mensajes de un usuario
    print("\nConsulta 3 - Obtener los mensajes de un usuario")
    for x in [mensaje for mensaje in adriantoral.get_mensajes(dariollodra) if int(mensaje['relacion.timestamp']) >= 1701263138]:
        print(x)

    # Consulta 4 - Obtener todos los mensajes entre dos usuarios
    print("\nConsulta 4 - Obtener todos los mensajes entre dos usuarios")
    for x in [
        *[{'adrian': k} for k in adriantoral.get_mensajes(dariollodra)],
        *[{'dario': k} for k in dariollodra.get_mensajes(adriantoral)]
    ]:
        print(x)

    # Consulta 5 - Obtener todos los usuarios mencionados por un usuario los cuales tengan una relación laboral con el usuario
    print("\nConsulta 5 - Obtener todos los usuarios mencionados por un usuario los cuales tengan una relación laboral con el usuario")
    for x in adriantoral.get_publicaciones():
        for y in Publicaciones(**x['nodo2']).get_menciones():
            if k := adriantoral.tiene_conexion(globals()[y['nodo2']['tipo']](**y['nodo2']), TipoConexion.LABORAL):
                print(k)

    # Cerrar conexion
    NEO4J_CONNECTION.close()
