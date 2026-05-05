from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import database
import iris_processing
import matcher

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for React frontend

# Ensure database is initialized
database.init_db()

MATCH_THRESHOLD = 30

def base64_to_image(base64_string):
    """Converts a base64 encoded string to an OpenCV image."""
    try:
        # Remove header if present (e.g. "data:image/jpeg;base64,")
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    image_b64 = data.get('image')
    
    if not username or not image_b64:
        return jsonify({"success": False, "message": "Missing username or image"}), 400
        
    img = base64_to_image(image_b64)
    if img is None:
        return jsonify({"success": False, "message": "Invalid image"}), 400
        
    # Process the frame to get features
    _, left_desc, right_desc = iris_processing.process_frame(img)
    
    if left_desc is None and right_desc is None:
        return jsonify({"success": False, "message": "No eyes detected in image. Please look straight at the camera."}), 400
        
    features = (left_desc, right_desc)
    success, msg = database.register_user(username, features)
    
    if success:
        return jsonify({"success": True, "message": f"User '{username}' registered successfully."})
    else:
        return jsonify({"success": False, "message": msg}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    image_b64 = data.get('image')
    
    if not image_b64:
        return jsonify({"success": False, "message": "Missing image"}), 400
        
    img = base64_to_image(image_b64)
    if img is None:
        return jsonify({"success": False, "message": "Invalid image"}), 400
        
    # Process the frame to get features
    _, left_desc, right_desc = iris_processing.process_frame(img)
    
    if left_desc is None and right_desc is None:
        database.log_attempt("Unknown", "Failed (No eyes)")
        return jsonify({"success": False, "message": "No eyes detected. Please look straight at the camera."}), 401
        
    live_features = (left_desc, right_desc)
    users = database.get_users()
    
    if not users:
        return jsonify({"success": False, "message": "No users in database."}), 404
        
    best_match_username = None
    highest_score = 0
    
    # Compare with all registered users
    for username, stored_features in users.items():
        score = matcher.calculate_match_score(stored_features, live_features)
        if score > highest_score:
            highest_score = score
            best_match_username = username
            
    if best_match_username and highest_score >= MATCH_THRESHOLD:
        database.log_attempt(best_match_username, "Success")
        return jsonify({
            "success": True, 
            "username": best_match_username, 
            "score": highest_score,
            "message": f"Authentication successful. Welcome, {best_match_username}!"
        })
    else:
        database.log_attempt("Unknown", "Failed")
        return jsonify({
            "success": False, 
            "message": "Authentication failed. Face not recognized.", 
            "score": highest_score
        }), 401

@app.route('/api/users', methods=['GET'])
def list_users():
    """Returns a list of all registered usernames."""
    users = database.get_users()
    return jsonify({"success": True, "users": list(users.keys())})

@app.route('/api/delete', methods=['DELETE'])
def delete_user():
    """Deletes a user by username."""
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"success": False, "message": "Missing username"}), 400
    
    deleted = database.delete_user(username)
    if deleted:
        return jsonify({"success": True, "message": f"User '{username}' deleted."})
    else:
        return jsonify({"success": False, "message": f"User '{username}' not found."}), 404

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Returns all authentication logs."""
    logs = database.get_logs()
    log_list = [{"username": l[0], "timestamp": l[1], "status": l[2]} for l in logs]
    return jsonify({"success": True, "logs": log_list})

if __name__ == '__main__':
    # use_reloader=False prevents Flask from spawning a second process in debug mode,
    # which would cause both processes to lock the SQLite database simultaneously.
    app.run(port=5000, debug=True, use_reloader=False)
