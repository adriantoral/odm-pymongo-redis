# MongoDB ODM

Se desea desarrollar una red social de ámbito educativo y laboral para el mercado español quepermita poner en contacto a personas conocidas o con intereses o aptitudes similares.
Nosotrosparticiparemos en este proyecto dentro del equipo de ‘Data’.
Este equipo será el encargado dediseñar e implementar el sistema de bases de datos que tenga la capacidad de gestionar lainformación necesaria para el correcto funcionamiento de la plataforma, así como el diseño eimplementación de los modelos y la interfaz de mapeo que permita la comunicación con las basesde datos.

Esta plataforma se desarrollará en cuatro fases diferenciadas.

- 1ª fase: Base de datos general (Práctica 1).
- 2ª fase: Cache y sesiones (Práctica 2).
- 3ª fase: Búsqueda de conexiones (Práctica 3).
- 4ª fase: análisis de datos e informes (Práctica 4).

La primera fase del desarrollo de la plataforma se centrará en el modelado de las entidadespersona, empresa y centro educativo.
Se pide diseñar e implementar una base de datos quealbergue la información asociada a dichas entidades, así como el diseño e implementación de unODM (clases Model y ModelCursor) específico que administre la información asociada a cadaentidad y la comunicación con la base de datos.
Se prevé que el listado de atributos pueda aumentar a lo largo del tiempo y sea necesarioincluirlos en la base de datos.
Adicionalmente, se ha de tener en cuenta que es posible que algunode estos atributos no sea común a todos los contactos y por tanto no tenga valor para alguno deellos.
Se proporcionará un archivo de configuración YAML del ODM que permita definir de formadinámica los modelos y especificar aquellos atributos obligatorios (que tienen que estar para cadadocumento) y admitidos (atributos válidos/aceptados que no tienen por qué estar en cadadocumento) de cada modelo.
Para los atributos de tipo dirección, se ha de incluir en el atributo dirección del modelo unatributo que almacene la geolocalización en formato punto de GeoJSON.
Se utilizará y terminaráde implementar la función getLocationPoint que debe devolver un punto GeoJson a partir de ladirección proporcionada.
Esta función utiliza una API pública con acceso limitado y por tanto nose pueden realizar consultas de forma masiva.
Consultar haciendo uso de sleeps y guardar losresultados.

Autores:

- Adrian Toral
- Dario Llodra
