import hashlib
import time
import uuid

import redis

# Crea una conexión a la base de datos Redis
# decode_responses=True para que devuelva los datos en formato str en vez de bytes
# maxmemory=150mb para limitar el tamaño de la base de datos a 150mb
# maxmemory-policy=volatile-ttl para que elimine los datos que tengan un tiempo de vida (ttl) cuando se supere el límite de memoria
cliente_redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
cliente_redis.config_set('maxmemory', '150mb')
cliente_redis.config_set('maxmemory-policy', 'volatile-ttl')


# Encriptar un texto con md5
def encriptar_md5(texto: str) -> str:
    """
    Encripta un texto con el algoritmo md5

    Parameters
    ----------
    texto

    Returns
    -------

    """

    return hashlib.md5(texto.encode()).hexdigest()


# Función para registrar un nuevo usuario
def registrar_usuario(nombre_completo, nombre_usuario, contrasenia, privilegios) -> bool:
    """
    Registra un nuevo usuario en la base de datos
    Si el usuario no existe, lo crea y devuelve True
    Si el usuario existe, devuelve False

    Parameters
    ----------
    nombre_completo
    nombre_usuario
    contrasenia
    privilegios

    Returns
    -------

    """

    if cliente_redis.exists(f'usuario:{nombre_usuario}'): return False  # Usuario ya existe

    cliente_redis.hset(f'usuario:{nombre_usuario}', mapping={
        'nombre_completo': nombre_completo,
        'nombre_usuario': nombre_usuario,
        'contrasenia': encriptar_md5(contrasenia),
        'privilegios': privilegios
    })

    return True  # Usuario registrado correctamente


# Función para realizar el inicio de sesión
def iniciar_sesion(nombre_usuario: str = None, contrasenia: str = None, token: str = None) -> {str: str | int} or int:
    """
    Comprueba si el token de sesión es válido, si lo es devuelve el token y los privilegios
    Si no lo es, intenta iniciar sesión con el nombre de usuario y la contraseña
    Cuando verifica si la contraseña es correcta, verifica que no exista un token de sesión, si existe lo devuelve
    si no existe, genera un token de sesión y lo devuelve junto con los privilegios

    Parameters
    ----------
    nombre_usuario
    contrasenia
    token

    Returns
    -------

    """

    if token is not None and cliente_redis.exists(token):
        # Comprueba si el token de sesión es válido
        datos = cliente_redis.hgetall(f'usuario:{cliente_redis.get(token)}')

    else:
        # Comprueba si existe el usuario
        # Si no existe, devuelve -1
        if not cliente_redis.exists(f'usuario:{nombre_usuario}'): return -1  # Usuario no existe
        datos = cliente_redis.hgetall(f'usuario:{nombre_usuario}')

        # Comprueba si la contraseña es correcta
        # Si no lo es, devuelve -1
        if datos['contrasenia'] != encriptar_md5(contrasenia): return -1  # Contraseña incorrecta

        # Genera un token de sesión y lo almacena en Redis
        # El token caduca en 30 días
        if not cliente_redis.exists(f'token:{nombre_usuario}'):
            token = str(uuid.uuid4())
            cliente_redis.setex(token, 2592000, nombre_usuario)
            cliente_redis.setex(f'token:{nombre_usuario}', 2592000, token)

        else: token = cliente_redis.get(f'token:{nombre_usuario}')  # Devuelve el token de sesión

    # Devuelve los privilegios y el token de sesión
    return {
        'token': token,
        'privilegios': int(datos['privilegios'])
    }


# Función para actualizar los datos de un usuario
def actualizar_usuario(nombre_usuario: str = None, contrasenia: str = None, token: str = None, nuevos_datos: {str: str | int} = None) -> None:
    """
    Actualiza los datos de un usuario

    Parameters
    ----------
    nombre_usuario
    contrasenia
    token
    nuevos_datos

    Returns
    -------

    """

    # Comprueba si hay una contrasenia en los nuevos datos
    # Si la hay, la encripta
    if 'contrasenia' in nuevos_datos.keys(): nuevos_datos['contrasenia'] = encriptar_md5(nuevos_datos['contrasenia'])

    if (datos := iniciar_sesion(nombre_usuario, contrasenia, token)) != -1:
        cliente_redis.hset(f'usuario:{cliente_redis.get(datos["token"])}', mapping=nuevos_datos)


# Función para registrar una petición de ayuda con prioridad
def registrar_peticion(nombre_usuario, prioridad):
    """
    Guarda una petición de ayuda en la cola de peticiones de ayuda

    Parameters
    ----------
    nombre_usuario
    prioridad

    Returns
    -------

    """

    cliente_redis.zadd('peticiones', {nombre_usuario: prioridad})


# Función para atender a usuarios
def atender_usuarios():
    """
    Itera sobre la cola de peticiones de ayuda y atiende a los usuarios según su prioridad (mayor a menor)

    Returns
    -------

    """

    return cliente_redis.bzpopmax('peticiones', 0)[1]


if __name__ == '__main__':
    # Registrar usuario
    if registrar_usuario('Jacinto Venavente', 'jacintovenavente', 'pass123', 3): print('Usuario registrado correctamente')
    else: print('El usuario ya existe')

    # Iniciar sesión
    credenciales_usuario = iniciar_sesion('jacintovenavente', 'pass123')
    print(f'Credenciales de usuario: {credenciales_usuario}')

    # Actualizar usuario
    print(f'''Usuario antes cambio: {cliente_redis.hgetall(f'usuario:{cliente_redis.get(credenciales_usuario["token"])}')}''')
    actualizar_usuario(token=credenciales_usuario['token'], nuevos_datos={
        'nombre_completo': 'Jacinto Venavente nuevo',
        'nombre_usuario': 'jacintovenavente',
        'contrasenia': 'pass123',
        'privilegios': 3
    })
    print(f'''Usuario antes cambio: {cliente_redis.hgetall(f'usuario:{cliente_redis.get(credenciales_usuario["token"])}')}''')

    # Registrar peticiones
    registrar_peticion('jacinto_1', 1)
    registrar_peticion('jacinto_2', 2)
    registrar_peticion('jacinto_3', 3)
    registrar_peticion('jacinto_4', 4)

    # Atender usuarios
    print(atender_usuarios())
    print(atender_usuarios())
    print(atender_usuarios())
    print(atender_usuarios())

    # Esperar a que se registren peticiones por terminal
    print(atender_usuarios())
