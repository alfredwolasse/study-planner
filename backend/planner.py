import math

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
