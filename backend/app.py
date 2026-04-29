import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from planner import StudyPlanner
from methodology import Methodology

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for frontend communication

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    
    # Basic Validation
    if not data:
        return jsonify({"error": "Aucune donnée fournie"}), 400
    
    subjects = data.get('subjects')
    hours_per_day = data.get('hours_per_day')
    days_left = data.get('days_left')
    
    if not all([subjects, hours_per_day, days_left]):
        return jsonify({"error": "Champs requis manquants"}), 400
    
    try:
        hours_per_day = float(hours_per_day)
        days_left = int(days_left)
    except ValueError:
        return jsonify({"error": "Valeurs numériques invalides"}), 400

    planner = StudyPlanner(subjects, hours_per_day, days_left)
    schedule = planner.generate_plan()
    
    return jsonify({"schedule": schedule})

@app.route('/methodology', methods=['GET'])
def get_methodology():
    content = Methodology.get_content()
    return jsonify(content)

if __name__ == '__main__':
    # Listen on 0.0.0.0 and dynamically assign port for Railway
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
