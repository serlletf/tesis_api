from flask import Flask, jsonify, request
from mysql.connector import connect, Error
import os

app = Flask(__name__)

def get_db_connection():
    connection = connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_DATABASE', 'scraping_db'),
        user=os.getenv('DB_USER', 'user'),
        password=os.getenv('DB_PASSWORD', 'password')
        
    )
    print(connection)
    return connection

@app.route('/productos', methods=['GET'])
def get_productos():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(productos)
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/supermercados', methods=['GET'])
def get_supermercados():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Supermercado")
        productos = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(productos)
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/precios', methods=['GET'])
def get_precios():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Precio")
        precios = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(precios)
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/productos/<int:idSupermercado>', methods=['GET'])
def get_productos_por_supermercado(idSupermercado):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, s.nombreSupermercado 
            FROM Producto p
            JOIN Precio pr ON p.idProducto = pr.idProducto
            JOIN Supermercado s ON pr.idSupermercado = s.idSupermercado
            WHERE s.idSupermercado = %s
        """, (idSupermercado,))
        productos = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(productos)
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/producto', methods=['POST'])
def add_producto():
    data = request.json
    nombreProducto = data.get('nombreProducto')
    marcaProducto = data.get('marcaProducto')
    formatoProducto = data.get('formatoProducto')
    categoriaProducto = data.get('categoriaProducto')

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if the product already exists
        cursor.execute("SELECT * FROM Producto WHERE nombreProducto = %s", (nombreProducto,))
        existing_product = cursor.fetchone()
        
        if existing_product:
            # Update the existing product
            cursor.execute("""
                UPDATE Producto
                SET marcaProducto = %s, formatoProducto = %s, categoriaProducto = %s
                WHERE nombreProducto = %s
            """, (marcaProducto, formatoProducto, categoriaProducto, nombreProducto))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "Producto actualizado exitosamente!"}), 200
        
        # Insert the new product
        cursor.execute("INSERT INTO Producto (nombreProducto, marcaProducto, formatoProducto, categoriaProducto) VALUES (%s, %s, %s, %s)",
                       (nombreProducto, marcaProducto, formatoProducto, categoriaProducto))
        connection.commit()
        producto_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return jsonify({"message": "Producto insertado exitosamente!", "idProducto": producto_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/producto/<int:id>', methods=['PUT'])
def update_producto(id):
    data = request.json
    nombreProducto = data.get('nombreProducto')
    marcaProducto = data.get('marcaProducto')
    formatoProducto = data.get('formatoProducto')
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE Producto
            SET nombreProducto = %s, marcaProducto = %s, formatoProducto = %s
            WHERE idProducto = %s
        """, (nombreProducto, marcaProducto, formatoProducto, id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Producto actualizado exitosamente!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/producto/<int:id>', methods=['DELETE'])
def delete_producto(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Producto WHERE idProducto = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Producto eliminado exitosamente!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/precio', methods=['POST'])
def add_precio():
    data = request.json
    idProducto = data.get('idProducto')
    precio = data.get('precio')
    fecha = data.get('fecha')
    idSupermercado = data.get('idSupermercado')
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if the price entry already exists
        cursor.execute("""
            SELECT * FROM Precio WHERE idProducto = %s AND idSupermercado = %s
        """, (idProducto, idSupermercado))
        existing_price = cursor.fetchone()
        
        if existing_price:
            # Update the existing price
            cursor.execute("""
                UPDATE Precio
                SET Precio = %s, fecha = %s
                WHERE idProducto = %s AND idSupermercado = %s
            """, (precio, fecha, idProducto, idSupermercado))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "Precio actualizado exitosamente!"}), 200
        
        # Insert the new price
        cursor.execute("INSERT INTO Precio (idProducto, Precio, fecha, idSupermercado) VALUES (%s, %s, %s, %s)",
                       (idProducto, precio, fecha, idSupermercado))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Precio insertado exitosamente!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)