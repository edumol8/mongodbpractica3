# Práctica: Escalabilidad con MongoDB, Nginx y Docker

Este proyecto implementa una arquitectura distribuida usando Docker Compose, Nginx como balanceador de carga TCP y tres instancias independientes de MongoDB. Además, incluye una aplicación web en Flask que permite interactuar con los nodos de la base de datos y visualizar cómo se distribuyen las peticiones.

La finalidad de esta práctica es comprender conceptos de escalabilidad horizontal, balanceo de carga, contenedores y conexión a múltiples bases de datos dentro de un ambiente orquestado.

--------------------------------------------------------------------
1. ARQUITECTURA GENERAL
--------------------------------------------------------------------

El proyecto incluye los siguientes servicios:

- mongo1, mongo2, mongo3:
  Tres contenedores de MongoDB funcionando como nodos independientes.
  Cada instancia tiene su propia base de datos y responde de manera aislada.

- nginx_lb:
  Contenedor de Nginx configurado como balanceador TCP.
  Acepta conexiones en el puerto 27017 y las redirige a los nodos:
      mongo1:27017
      mongo2:27017
      mongo3:27017

- flask_app:
  Aplicación web en Python (Flask).
  Proporciona endpoints para:
      • Probar la conexión vía Nginx
      • Enviar peticiones distribuidas entre los nodos de Mongo
      • Consultar estadísticas del número de peticiones atendidas por cada nodo

--------------------------------------------------------------------
2. ESTRUCTURA DEL PROYECTO
--------------------------------------------------------------------

MONGODBPRACTICA3/
│
├─ app/
│  ├─ app.py
│  ├─ dockerfile
│  └─ requirements.txt
│
├─ nginx/
│  └─ nginx.conf
│
└─ docker-compose.yml

--------------------------------------------------------------------
3. ENDPOINTS DE LA APLICACIÓN
--------------------------------------------------------------------

La aplicación se expone en:
http://localhost:5000

----- GET / -----
Muestra un mensaje indicando que la aplicación está funcionando.

----- GET /status -----
Prueba la conexión con MongoDB a través del balanceador Nginx.
La aplicación ejecuta un “ping” a MongoDB usando esta URI:
mongodb://nginx:27017/

----- GET /request -----
Genera una petición que se envía a uno de los tres nodos de MongoDB,
elegido aleatoriamente. Registra cuál nodo atendió la operación.

Sirve para simular carga distribuida.

----- GET /stats -----
Se conecta directamente a mongo1, mongo2 y mongo3.
Cuenta cuántos documentos tiene cada nodo en la colección "requests".
Permite visualizar la carga distribuida entre los tres nodos.

Ejemplo de respuesta:
/stats
{
  "stats_por_host": {
    "mongo1": 38,
    "mongo2": 39,
    "mongo3": 43
  },
  "total_peticiones": 120
}

--------------------------------------------------------------------
4. REQUISITOS PREVIOS
--------------------------------------------------------------------

- Docker Desktop instalado y ejecutándose.
- Docker Compose integrado.
- Opcional: mongosh para consultas manuales.

--------------------------------------------------------------------
5. CÓMO LEVANTAR EL PROYECTO
--------------------------------------------------------------------

1. Abrir una terminal en la raíz del proyecto:

   cd MONGODBPRACTICA3

2. Construir los contenedores:

   docker compose build

3. Levantar los servicios:

   docker compose up -d

4. Verificar que los contenedores estén en ejecución:

   docker ps

   Deberías ver:
   - mongo1
   - mongo2
   - mongo3
   - nginx_lb
   - flask_app

--------------------------------------------------------------------
6. CÓMO PROBAR EL BALANCEO DE CARGA
--------------------------------------------------------------------

----- A) Probar conexión a través del balanceador -----

Abrir en el navegador:

http://localhost:5000/status

Si todo está bien, mostrará:
"Conectado a MongoDB vía Nginx"

----- B) Generar carga distribuida -----

Puedes hacerlo manualmente con:
http://localhost:5000/request

O generar 120 peticiones automáticas desde PowerShell:

for ($i = 0; $i -lt 120; $i++) {
    curl http://localhost:5000/request > $null
}

----- C) Ver estadísticas -----

Consultar:

http://localhost:5000/stats

Verás cuántas peticiones atendió cada nodo.

--------------------------------------------------------------------
7. DETENER EL PROYECTO
--------------------------------------------------------------------

Para detener los servicios:

docker compose down

Para borrarlo todo (redes, volúmenes):

docker compose down -v

--------------------------------------------------------------------
8. RESUMEN FINAL
--------------------------------------------------------------------

Este proyecto demuestra:
- Uso de contenedores para montar múltiples nodos de base de datos.
- Uso de Nginx como balanceador TCP.
- Uso de Flask como aplicación cliente para generar carga y medir distribución.
- Cómo una arquitectura distribuida puede escalar horizontalmente.
