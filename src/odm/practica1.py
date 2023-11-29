__author__ = 'Adrian Toral / Dario Llodra'

import json
import time
from typing import Generator, Any, Self

import bson
import pymongo
import redis
import yaml
from geojson import Point
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim


def getLocationPoint(address: str) -> Point:
    """ 
    Obtiene las coordenadas de una dirección en formato geojson.Point
    Utilizar la API de geopy para obtener las coordenadas de la direccion
    Cuidado, la API es publica tiene limite de peticiones, utilizar sleeps.

    Parameters
    ----------
        address : str
            direccion completa de la que obtener las coordenadas
    Returns
    -------
        geojson.Point
            coordenadas del punto de la direccion
    """

    location = None
    while location is None:
        try:
            time.sleep(1)
            location = Nominatim(user_agent='adtodallo').geocode(address)
        except GeocoderTimedOut:
            # Puede lanzar una excepcion si se supera el tiempo de espera
            # Volver a intentarlo
            continue

    return Point((location.latitude, location.longitude))


class Model:
    """ 
    Clase de modelo abstracta
    Crear tantas clases que hereden de esta clase como  
    colecciones/modelos se deseen tener en la base de datos.

    Attributes
    ----------
        required_vars : set[str]
            conjunto de variables requeridas por el modelo
        admissible_vars : set[str]
            conjunto de variables admitidas por el modelo
        db : pymongo.collection.Collection
            conexion a la coleccion de la base de datos

    Methods
    -------
        __setattr__(name: str, value: str | dict) -> None
            Sobreescribe el metodo de asignacion de valores a las
            variables del objeto con el fin de controlar las variables
            que se asignan al modelo y cuando son modificadas.
        save()  -> None
            Guarda el modelo en la base de datos
        delete() -> None
            Elimina el modelo de la base de datos
        find(filter: dict[str, str | dict]) -> ModelCursor
            Realiza una consulta de lectura en la BBDD.
            Devuelve un cursor de modelos ModelCursor
        aggregate(pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor
            Devuelve el resultado de una consulta aggregate.
        find_by_id(id: str) -> dict | None
            Busca un documento por su id utilizando la cache y lo devuelve.
            Si no se encuentra el documento, devuelve None.
        init_class(db_collection: pymongo.collection.Collection, requiered_vars: set[str], admissible_vars: set[str]) -> None
            Inicializa las variables de clase en la inicializacion del sistema.

    """

    required_vars: set[str]
    admissible_vars: set[str]
    db: pymongo.collection.Collection
    redis: redis.Redis

    def __init__(self, **kwargs: dict[str, str | dict]):
        """
        Inicializa el modelo con los valores proporcionados en kwargs
        Comprueba que los valores proporcionados en kwargs son admitidos
        por el modelo y que las variables requeridas son proporcionadas.

        Parameters
        ----------
            kwargs : dict[str, str | dict]
                diccionario con los valores de las variables del modelo
        """

        self.__changed__: set[str] = set()

        for required in self.required_vars:
            if required not in kwargs.keys():
                raise Exception(f'[2] Variable "{required}" requerida no especificada.')

        for name, value in kwargs.items(): self.__setattr__(name, value)

    def __setattr__(self, name: str, value: str | dict) -> None:
        """ Sobreescribe el metodo de asignacion de valores a las
        variables del objeto con el fin de controlar las variables
        que se asignan al modelo y cuando son modificadas.
        """

        if name not in {*self.required_vars, *self.admissible_vars, *{'__changed__'}}:
            raise Exception(f'[1] Variable "{name}" no admitida por el modelo.')

        # Si ya existe la variable, la agrega como cambiada
        if name in self.__dict__.keys():
            self.__changed__.add(name)

        self.__dict__[name] = value

    def save(self) -> None:
        """
        Guarda el modelo en la base de datos
        Si el modelo no existe en la base de datos, se crea un nuevo
        documento con los valores del modelo. En caso contrario, se
        actualiza el documento existente con los nuevos valores del
        modelo.
        """

        # Si tiene datos cambiados, los actualiza basado en los otros datos no cambiados
        if hasattr(self, '_id'):
            self.db.update_one({'_id': getattr(self, '_id')}, {'$set': {changed: getattr(self, changed) for changed in self.__changed__}})
            self.__changed__.clear()

        # Si no tiene datos cambiados, inserta los datos
        else:
            # Copia los datos en una variable nueva
            # Elimina las variables cambiadas para evitar errores en la busqueda
            # Elimina las variables de control
            datos: dict[str, str | dict] = self.__dict__.copy()
            datos.pop('__changed__')
            setattr(self, '_id', self.db.insert_one(datos).inserted_id)

        datos: dict[str, str | dict] = self.__dict__.copy()
        datos.pop('__changed__')
        datos.pop('_id')
        self.redis.setex(str(getattr(self, '_id')), 60 * 60 * 24, json.dumps(datos))

    def delete(self) -> None:
        """
        Elimina el modelo de la base de datos
        """

        if not hasattr(self, '_id'):
            raise Exception('[3] El modelo no esta guardado, imposible eliminarlo.')

        self.db.delete_one({'_id': getattr(self, '_id')})
        self.redis.delete(getattr(self, '_id'))

    @classmethod
    def find(cls, filter: dict[str, str | dict]) -> Any:
        """
        Utiliza el metodo find de pymongo para realizar una consulta
        de lectura en la BBDD.
        find debe devolver un cursor de modelos ModelCurso

        Parameters
        ----------
            filter : dict[str, str | dict]
                diccionario con el criterio de busqueda de la consulta
        Returns
        -------
            ModelCursor
                cursor de modelos
        """

        return iter(ModelCursor(cls, cls.db.find(filter), cls.redis))

    @classmethod
    def aggregate(cls, pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor:
        """
        Devuelve el resultado de una consulta aggregate.
        No hay nada que hacer en esta funcion.
        Se utilizara para las consultas solicitadas
        en el segundo apartado de la practica.

        Parameters
        ----------
            pipeline : list[dict]
                lista de etapas de la consulta aggregate
        Returns
        -------
            pymongo.command_cursor.CommandCursor
                cursor de pymongo con el resultado de la consulta
        """

        return cls.db.aggregate(pipeline)

    @classmethod
    def find_by_id(cls, identificador: str) -> Self | None:
        """
        NO IMPLEMENTAR HASTA LA SEGUNDA PRACTICA
        Busca un documento por su id utilizando la cache y lo devuelve.
        Si no se encuentra el documento, devuelve None.

        Parameters
        ----------
            id : str
                id del documento a buscar
        Returns
        -------
            dict | None
                documento encontrado o None si no se encuentra
        """

        if cls.redis.exists(identificador):
            documento = json.loads(cls.redis.get(identificador))
            documento.update({'_id': bson.ObjectId(identificador)})
            cls.redis.expire(identificador, 60 * 60 * 24)

        else:
            documento = cls.db.find_one({'_id': bson.ObjectId(identificador)})
            documento_copia = documento.copy()
            documento_copia.pop('_id')
            cls.redis.setex(identificador, 60 * 60 * 24, json.dumps(documento_copia))

        return cls(**documento) if documento else None

    @classmethod
    def init_class(cls, db_collection: pymongo.collection.Collection, redis_connection: redis.Redis, required_vars: set[str], admissible_vars: set[str]) -> None:
        """
        Inicializa las variables de clase en la inicializacion del sistema.
        En principio nada que hacer aqui salvo que se quieran realizar
        comprobaciones o cambios adicionales.

        Parameters
        ----------
            db_collection : pymongo.collection.Collection
                Conexion a la collecion de la base de datos.
            required_vars : set[str]
                Set de variables requeridas por el modelo
            admissible_vars : set[str]
                Set de variables admitidas por el modelo
        """

        cls.db = db_collection
        cls.redis = redis_connection
        cls.required_vars = required_vars
        cls.admissible_vars = admissible_vars


class ModelCursor:
    """
    Cursor para iterar sobre los documentos del resultado de una
    consulta. Los documentos deben ser devueltos en forma de objetos
    modelo.

    Attributes
    ----------
        model_class : Model
            Clase para crear los modelos de los documentos que se iteran.
        command_cursor : pymongo.command_cursor.CommandCursor
            Cursor de pymongo a iterar

    Methods
    -------
        __iter__() -> Generator
            Devuelve un iterador que recorre los elementos del cursor
            y devuelve los documentos en forma de objetos modelo.
    """

    def __init__(self, model_class: Model, command_cursor: pymongo.cursor.Cursor):
        """
        Inicializa el cursor con la clase de modelo y el cursor de pymongo

        Parameters
        ----------
            model_class : Model
                Clase para crear los modelos de los documentos que se iteran.
            command_cursor: pymongo.command_cursor.CommandCursor
                Cursor de pymongo a iterar
        """

        self.model = model_class
        self.cursor = command_cursor

    def __iter__(self) -> Generator:
        """
        Devuelve un iterador que recorre los elementos del cursor
        y devuelve los documentos en forma de objetos modelo.
        Utilizar yield para generar el iterador
        Utilizar la funcion next para obtener el siguiente documento del cursor
        Utilizar alive para comprobar si existen mas documentos.
        """

        while self.cursor.alive:
            # Comprobar si el documento existe en la cache
            # Si existe, devolver el documento de la cache
            # Si no existe, devolver el documento de la base de datos
            documento = next(self.cursor)
            if not self.model.redis.exists(str(documento['_id'])):
                documento_copia = documento.copy()
                documento_copia.pop('_id')
                self.model.redis.setex(str(documento['_id']), 60 * 60 * 24, json.dumps(documento_copia))

            else:
                self.model.redis.expire(str(documento['_id']), 60 * 60 * 24)

            yield self.model(**documento)


def initApp(definitions_path: str = '/home/adriantoral/utad/ampliacion-bases-de-datos/p1_g11_adrian_toral_dario_llodra/models.yml', mongodb_uri='mongodb://localhost:27017/', db_name='proyecto1') -> None:
    """
    Declara las clases que heredan de Model para cada uno de los
    modelos de las colecciones definidas en definitions_path.
    Inicializa las clases de los modelos proporcionando las variables
    admitidas y requeridas para cada una de ellas y la conexión a la
    collecion de la base de datos.

    Parameters
    ----------
        definitions_path : str
            ruta al fichero de definiciones de modelos
        mongodb_uri : str
            uri de conexion a la base de datos
        db_name : str
            nombre de la base de datos
    """

    cliente_mongodb = pymongo.MongoClient(mongodb_uri)
    base_datos = cliente_mongodb[db_name]

    cliente_redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cliente_redis.config_set('maxmemory', '150mb')
    cliente_redis.config_set('maxmemory-policy', 'volatile-ttl')

    with open(definitions_path, 'r') as modelos:
        colecciones = yaml.safe_load(modelos)

    for modelo, atributos in colecciones.items():
        globals()[modelo] = type(modelo, (Model,), {})
        globals()[modelo].init_class(getattr(base_datos, modelo), cliente_redis, atributos['required_vars'], atributos['admissible_vars'])


# Q1
Q1 = [
    {'$match': {'centro_educativo': {'$in': ['UPM', 'UAM']}}}
]

# Q2
Q2 = [
    {'$match': {'direccion': 'Madrid'}},
    {'$group': {'_id': '$centro_educativo'}}
]

# Q3
Q3 = [
    {'$match': {'descripcion': {'$in': ['Big Data', 'Inteligencia Artificial']}}}
]

# Q4
Q4 = [
    {'$match': {'anio_estudios_terminados': {'$gte': 2017}}},
    {'$out': 'PersonasConEstudios2017yDespues'}
]

# Q5
Q5 = [
    {'$match': {'empresa': 'Microsoft'}},
    {'$group': {'_id': '$empresa', 'promedio_estudios': {'$avg': '$promedio_estudios'}}}
]

# Q6
Q6 = [
    {
        "$match": {
            "empresa": "Google"
        }
    },
    {
        "$project": {
            "nombre": 1,
            "apellido": 1,
            "coordenadas": 1
        }
    },
    {
        "$addFields": {
            "distancia_al_trabajo": {
                "$sqrt": {
                    "$sum": [
                        {
                            "$pow": [
                                {"$subtract": ["$coordenadas", "$latitud"]},
                                2
                            ]
                        },
                        {
                            "$pow": [
                                {"$subtract": ["$coordenadas", "$longitud"]},
                                2
                            ]
                        }
                    ]
                }
            }
        }
    }
]

# Q7
Q7 = [
    {'$group': {'_id': '$centro_educativo', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}},
    {'$limit': 3}
]

if __name__ == '__main__':
    # Inicializar base de datos y modelos con initApp
    initApp()

    # Hacer pruebas para comprobar que funciona correctamente el modelo
    # Crear modelo
    modelo_1 = globals()['Persona'](nombre="Felipe",
                                    apellido="Goncalez",
                                    dni="987654321",
                                    edad=20,
                                    genero="Masculino",
                                    direccion="Cuenca",
                                    centro_educativo="UPM",
                                    empresa="Google",
                                    telefono="555-431-4567",
                                    descripcion="Big Data",
                                    anio_estudios_terminados=2015,
                                    promedio_estudios=5,
                                    coordenadas={"latitud": 38.345996, "longitud": -0.56123}
                                    )

    # Asignar nuevo valor a variable admitida del objeto
    modelo_1.nombre = 'Quijote'

    # Asignar nuevo valor a variable no admitida del objeto
    try: modelo_1.peso = 100
    except Exception as error: print(error)

    # Guardar
    modelo_1.save()

    # Asignar nuevo valor a variable admitida del objeto
    modelo_1.apellido = 'Pastor'

    # Guardar
    modelo_1.save()

    # Buscar nuevo documento con find
    documento = globals()['Persona'].find({'nombre': 'Quijote'})

    # Obtener primer documento
    modelo_2 = next(documento)

    # Modificar valor de variable admitida
    modelo_2.edad = 30

    # Guardar
    modelo_2.save()

    # Ejecutar consultas Q1, Q2, etc. y mostrarlo
    for i in range(1, 8):
        print(f'Q{i}:')
        [print(resultado) for resultado in globals()['Persona'].aggregate(globals()[f'Q{i}'])]
        print()
