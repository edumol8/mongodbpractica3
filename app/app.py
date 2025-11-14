from flask import Flask, jsonify
from pymongo import MongoClient
import os
import random

app = Flask(__name__)

# Conexión principal (para mostrar que Nginx funciona)
MONGO_URI_BALANCER = os.getenv("MONGO_URI", "mongodb://nginx:27017/")
DB_NAME = "test_database"
COLLECTION_NAME = "requests"

# URIs directas a cada Mongo para balanceo explícito y estadísticas
MONGO_NODES = {
    "mongo1": "mongodb://mongo1:27017/",
    "mongo2": "mongodb://mongo2:27017/",
    "mongo3": "mongodb://mongo3:27017/"
}


def get_db_via_balancer():
    """Conexión que pasa por Nginx (para /status)."""
    client = MongoClient(MONGO_URI_BALANCER)
    db = client[DB_NAME]
    return client, db


def get_db_to_node(node_name: str):
    """Conexión directa a un nodo específico (para /request y /stats)."""
    uri = MONGO_NODES[node_name]
    client = MongoClient(uri)
    db = client[DB_NAME]
    return client, db


@app.route("/")
def index():
    return "Aplicación Escalable con MongoDB y Nginx (demo de balanceo de carga)"


@app.route("/status")
def status():
    """
    Verifica que la aplicación pueda conectarse a MongoDB a través de Nginx.
    Demuestra el uso del balanceador TCP.
    """
    client, db = get_db_via_balancer()
    try:
        db.command("ping")
        return jsonify({
            "status": "Conectado a MongoDB vía Nginx",
            "mongo_uri": MONGO_URI_BALANCER
        })
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        client.close()


@app.route("/request")
def make_request():
    """
    Inserta un documento en UNO de los tres nodos de MongoDB,
    elegido aleatoriamente (balanceo explícito a nivel de aplicación).
    Así podemos ver cuántas peticiones atiende cada nodo.
    """
    # Elegimos aleatoriamente el nodo destino
    node = random.choice(list(MONGO_NODES.keys()))
    client, db = get_db_to_node(node)

    try:
        # Usamos serverStatus solo para registrar info del nodo
        info = db.command("serverStatus")
        host = info.get("host", node)
        pid = info.get("pid", None)

        result = db[COLLECTION_NAME].insert_one({
            "host": host,
            "pid": pid,
            "node": node
        })

        return jsonify({
            "message": "Petición registrada",
            "mongo_node": node,
            "mongo_host": host,
            "mongo_pid": pid,
            "inserted_id": str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        client.close()


@app.route("/stats")
def stats():
    """
    Pregunta DIRECTAMENTE a cada contenedor mongo1, mongo2 y mongo3
    cuántos documentos tiene en la colección 'requests'.
    """
    stats_por_host = {}
    total = 0

    for nombre, uri in MONGO_NODES.items():
        client = MongoClient(uri)
        db = client[DB_NAME]
        try:
            count = db[COLLECTION_NAME].count_documents({})
            stats_por_host[nombre] = count
            total += count
        except Exception as e:
            stats_por_host[nombre] = f"Error: {str(e)}"
        finally:
            client.close()

    return jsonify({
        "stats_por_host": stats_por_host,
        "total_peticiones": total
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
