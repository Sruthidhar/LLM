from flask import Flask, request, jsonify
from pymongo import MongoClient
import mysql.connector
import requests

app = Flask(__name__)

# MySQL connection configuration
mysql_config = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password',
    'database': 'mydatabase'
}

# MongoDB connection configuration
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['mydatabase']
mongo_collection = mongo_db['users']

def insert_into_mysql(user_data):
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(sql, (user_data['name'], user_data['email']))
        conn.commit()
        return True
    except Exception as e:
        print("Error inserting into MySQL:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def insert_into_mongodb(user_data):
    try:
        mongo_collection.insert_one(user_data)
        return True
    except Exception as e:
        print("Error inserting into MongoDB:", e)
        return False

@app.route('/insert-user-from-endpoint', methods=['POST'])
def insert_user_from_endpoint():
    try:
        # Assuming the endpoint returns JSON data with 'name' and 'email' fields
        endpoint_url = 'http://example.com/get-user-details'  # Replace with your actual endpoint URL

        response = requests.get(endpoint_url)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch user details from endpoint'}), 500
        
        user_data = response.json()
        if 'name' not in user_data or 'email' not in user_data:
            return jsonify({'error': 'Invalid user data received from endpoint'}), 400
        
        if insert_into_mysql(user_data) and insert_into_mongodb(user_data):
            return jsonify({'message': 'User inserted successfully into both MySQL and MongoDB'}), 200
        else:
            return jsonify({'error': 'Failed to insert user into one or both databases'}), 500
        
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
