import os
import math
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Note: Static files are handled by Vercel directly via vercel.json


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


# --- MERGED PLANNER ---

class StudyPlanner:
    WEIGHT_MAP = {
        "faible": 3,
        "moyen": 2,
        "fort": 1
    }

    def __init__(self, subjects, hours_per_day, days_left):
        self.subjects = subjects
        self.hours_per_day = hours_per_day
        self.days_left = days_left

    def generate_plan(self):
        if not self.subjects or self.days_left <= 0:
            return []

        # 1. Calculate total weights
        total_weight = sum(self.WEIGHT_MAP.get(s['level'].lower(), 1) for s in self.subjects)
        
        # 2. Calculate total hours available
        total_available_hours = self.hours_per_day * self.days_left
        
        # 3. Calculate hours per subject based on weight
        subject_hours = {}
        for s in self.subjects:
            weight = self.WEIGHT_MAP.get(s['level'].lower(), 1)
            allocated_hours = (weight / total_weight) * total_available_hours
            subject_hours[s['name']] = round(allocated_hours * 2) / 2  # round to 0.5 hours

        # Track temporal constraints
        consecutive_days = {s['name']: 0 for s in self.subjects}
        used_previous_day = {s['name']: False for s in self.subjects}
        
        schedule = []

        # 4. Distribute across days with temporal constraints
        for day in range(1, self.days_left + 1):
            remaining_day_hours = self.hours_per_day
            used_today = {s['name']: 0.0 for s in self.subjects}
            
            # Loop until the day's hours are filled or no subjects left
            while remaining_day_hours > 0:
                available_subjects = []
                
                for s in self.subjects:
                    name = s['name']
                    rem = subject_hours[name]
                    
                    if rem <= 0:
                        continue
                        
                    # RULE 1: MAX CONSECUTIVE LIMIT (cannot appear > 2 consecutive days)
                    if consecutive_days[name] >= 2 and used_today[name] == 0:
                        continue
                        
                    # Base priority score is remaining hours
                    score = rem
                    
                    # RULE 2: REPETITION PENALTY
                    if used_previous_day[name] and used_today[name] == 0:
                        score -= 2.0  # Penalty factor to encourage rotation
                        
                    # RULE 3: DAILY DIVERSITY (Heavy penalty if already scheduled today)
                    # This forces the algorithm to pick a different subject for the second chunk
                    if used_today[name] > 0:
                        score -= 100.0 
                        
                    available_subjects.append({
                        'subject': s,
                        'name': name,
                        'score': score
                    })
                    
                if not available_subjects:
                    break  # No valid subjects can be scheduled right now
                    
                # Sort by score descending
                available_subjects.sort(key=lambda x: x['score'], reverse=True)
                best = available_subjects[0]
                
                # Determine chunk size (try to split the day into at least 2 parts for diversity)
                chunk = min(remaining_day_hours, subject_hours[best['name']], max(1.0, self.hours_per_day / 2.0))
                chunk = round(chunk * 2) / 2
                
                if chunk <= 0:
                    break
                    
                subject_hours[best['name']] -= chunk
                remaining_day_hours -= chunk
                used_today[best['name']] += chunk
                
            # Record tasks for this day
            day_tasks = []
            for s in self.subjects:
                name = s['name']
                hours = used_today[name]
                if hours > 0:
                    day_tasks.append({
                        "subject": name,
                        "topic": s.get('topic', ''),
                        "hours": hours
                    })
                    # Update trackers
                    consecutive_days[name] += 1
                    used_previous_day[name] = True
                else:
                    consecutive_days[name] = 0
                    used_previous_day[name] = False
                    
            schedule.append({
                "day": day,
                "tasks": day_tasks
            })

        return schedule


# --- MERGED METHODOLOGY ---
class Methodology:
    @staticmethod
    def get_content():
        return {
            "problem_statement": (
                "Les étudiants ont souvent du mal à gérer efficacement leur temps lors de la préparation aux examens. "
                "Le piège courant est le 'biais du temps égal', où les étudiants consacrent la même durée à chaque matière, "
                "quel que soit leur niveau de compétence, ou au contraire, évitent les matières difficiles par procrastination. "
                "Cela conduit à une préparation sous-optimale et à un stress accru."
            ),
            "data_driven_approach": (
                "Le Planificateur d'Études adopte un modèle d'allocation pondérée. En quantifiant la 'compétence' "
                "en niveaux discrets (Faible, Moyen, Fort), le système transforme l'auto-évaluation qualitative "
                "en variables quantitatives qui pilotent l'algorithme de planification."
            ),
            "feature_design": (
                "Les fonctionnalités clés incluent : (1) Des niveaux de difficulté par matière ; (2) Des contraintes temporelles "
                "(heures disponibles par jour) ; et (3) La proximité de l'échéance (jours restants). Ces entrées permettent au "
                "système de calculer le 'stock' total d'heures d'étude disponibles et de le distribuer selon les besoins."
            ),
            "algorithm_choice": (
                "Nous utilisons un algorithme de Distribution Proportionnelle Pondérée (DPP). Ce modèle déterministe "
                "attribue des poids (Faible: 3, Moyen: 2, Fort: 1) aux matières. Les heures totales sont réparties "
                "selon le ratio du poids d'une matière par rapport à la somme totale. Cela garantit que les zones les "
                "plus difficiles reçoivent la plus grande intensité d'attention."
            ),
            "limitations": (
                "Le modèle actuel suppose une relation linéaire entre le temps d'étude et les gains de compétence. "
                "Il ne tient pas compte de la fatigue cognitive ou du volume de contenu spécifique. Les futures itérations "
                "pourraient intégrer l'optimisation du rythme circadien et la méthode Pomodoro."
            ),
            "real_world_impact": (
                "En automatisant la phase de planification, l'outil réduit la charge cognitive associée à la prise de décision, "
                "permettant aux étudiants de se concentrer entièrement sur l'apprentissage. Il favorise une préparation équilibrée."
            )
        }

