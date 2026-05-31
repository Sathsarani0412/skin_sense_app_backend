from flask import Flask, request, jsonify
from flask_cors import CORS

import sqlite3
import os
import cv2
import numpy as np
import tensorflow as tf
import pickle

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)
CORS(app)

# =========================================
# LOAD MODEL
# =========================================

model = tf.saved_model.load("saved_skin_model")

# GET PREDICTION FUNCTION
infer = model.signatures["serving_default"]

# =========================================
# LOAD CLASS LABELS
# =========================================

with open("class_names.pkl", "rb") as f:
    class_names = pickle.load(f)

print("Model Loaded Successfully")
print("Classes:", class_names)

# =========================================
# CREATE DATABASE
# =========================================

def create_tables():

    conn = sqlite3.connect("skinsense.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # SKIN RESULTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skin_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            blackheads REAL,
            dark_spots REAL,
            whiteheads REAL,
            wrinkles REAL,
            predicted_class TEXT,
            confidence REAL,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

create_tables()

# =========================================
# HOME ROUTE
# =========================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "SkinSense Backend Running"
    })

# =========================================
# SIGNUP
# =========================================

@app.route("/signup", methods=["POST"])
def signup():

    try:

        data = request.json

        name = data["name"]
        email = data["email"]
        password = data["password"]

        conn = sqlite3.connect("skinsense.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Email already exists"
            })

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Signup Successful",
            "name": name,
            "email": email
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.json

        email = data["email"]
        password = data["password"]

        conn = sqlite3.connect("skinsense.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            return jsonify({
                "success": True,
                "message": "Login Successful",
                "name": user[1],
                "email": user[2]
            })

        return jsonify({
            "success": False,
            "message": "Invalid Email or Password"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

# =========================================
# RESET PASSWORD
# =========================================

@app.route("/reset_password", methods=["POST"])
def reset_password():

    try:

        data = request.json

        email = data["email"]
        new_password = data["new_password"]

        conn = sqlite3.connect("skinsense.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Email not found"
            })

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (new_password, email)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Password Reset Successful"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

# =========================================
# PREDICT ROUTE
# =========================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "message": "No image uploaded"
            })

        file = request.files["image"]

        email = request.form.get("email")

        image_path = "temp.jpg"

        file.save(image_path)

        img = cv2.imread(image_path)

        if img is None:

            return jsonify({
                "success": False,
                "message": "Invalid image"
            })

        # PREPROCESS IMAGE

        img = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        img = cv2.resize(
            img,
            (224, 224)
        )

        img = img / 255.0

        img_array = np.expand_dims(
            img,
            axis=0
        )

        tensor_input = tf.convert_to_tensor(
            img_array,
            dtype=tf.float32
        )

        # PREDICT

        prediction = infer(tensor_input)

        predictions = list(
            prediction.values()
        )[0].numpy()

        predicted_index = np.argmax(predictions)

        predicted_class = class_names[predicted_index]

        confidence = float(
            np.max(predictions) * 100
        )

        # CLASS PERCENTAGES

        blackheads = round(
            float(predictions[0][0] * 100),
            2
        )

        dark_spots = round(
            float(predictions[0][1] * 100),
            2
        )

        whiteheads = round(
            float(predictions[0][2] * 100),
            2
        )

        wrinkles = round(
            float(predictions[0][3] * 100),
            2
        )

        # RECOMMENDATION

        recommendation = (
            f"Most affected issue is "
            f"{predicted_class}. "
            f"Use sunscreen daily, "
            f"drink more water, "
            f"maintain skincare routine "
            f"and consult dermatologist "
            f"if needed."
        )

        # SAVE TO DATABASE

        conn = sqlite3.connect("skinsense.db")

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO skin_results(

                email,
                blackheads,
                dark_spots,
                whiteheads,
                wrinkles,
                predicted_class,
                confidence,
                recommendation

            )

            VALUES(?,?,?,?,?,?,?,?)

        """, (

            email,
            blackheads,
            dark_spots,
            whiteheads,
            wrinkles,
            predicted_class,
            confidence,
            recommendation
        ))

        conn.commit()
        conn.close()

        # DELETE TEMP IMAGE

        if os.path.exists(image_path):
            os.remove(image_path)

        # RESPONSE

        return jsonify({

            "success": True,

            "predicted_class":
            predicted_class,

            "confidence":
            round(confidence, 2),

            "all_predictions": {

                "blackheads":
                blackheads,

                "dark_spots":
                dark_spots,

                "whiteheads":
                whiteheads,

                "wrinkles":
                wrinkles
            },

            "recommendation":
            recommendation
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        })

# =========================================
# HISTORY ROUTE
# =========================================

@app.route("/history/<email>")
def history(email):

    try:

        conn = sqlite3.connect("skinsense.db")

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
            blackheads,
            dark_spots,
            whiteheads,
            wrinkles,
            created_at

            FROM skin_results

            WHERE email=?

            ORDER BY id DESC

        """, (email,))

        rows = cursor.fetchall()

        conn.close()

        results = []

        for row in rows:

            results.append({

                "blackheads": row[0],
                "dark_spots": row[1],
                "whiteheads": row[2],
                "wrinkles": row[3],
                "created_at": row[4]
            })

        return jsonify({

            "success": True,

            "history": results
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        })

# =========================================
# UPDATE PROFILE
# =========================================

@app.route("/update_profile", methods=["POST"])
def update_profile():

    try:

        data = request.json

        old_email = data["old_email"]

        new_name = data["new_name"]

        new_email = data["new_email"]

        conn = sqlite3.connect("skinsense.db")

        cursor = conn.cursor()

        cursor.execute(

            """
            UPDATE users
            SET name=?, email=?
            WHERE email=?
            """,

            (new_name, new_email, old_email)
        )

        conn.commit()

        conn.close()

        return jsonify({

            "success": True,

            "message": "Profile Updated Successfully"
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)
        })

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )