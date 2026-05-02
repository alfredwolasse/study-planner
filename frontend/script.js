// Configuration Vercel par défaut (utiliser la même origine)
let API_BASE = window.location.port === '8000' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? `http://${window.location.hostname}:5000` : '';
let subjectCount = 1;
let pieChartInstance = null;
let lineChartInstance = null;

function addSubjectRow() {
    const container = document.getElementById('subjects-container');
    const rowId = subjectCount++;

    const row = document.createElement('div');
    row.className = 'subject-row';
    row.id = `row-${rowId}`;
    row.innerHTML = `
        <input type="text" placeholder="Nom de la Matière (ex: Maths)" class="subject-name" required>
        <input type="text" placeholder="Chapitre/Thème (Optionnel)" class="subject-topic">
        <select class="subject-level">
            <option value="faible">Faible (Priorité Haute)</option>
            <option value="moyen" selected>Moyen (Normal)</option>
            <option value="fort">Fort (Révision Uniquement)</option>
        </select>
        <button type="button" class="btn-remove" onclick="removeSubject(${rowId})">Supprimer</button>
    `;
    container.appendChild(row);
}

function removeSubject(id) {
    const row = document.getElementById(`row-${id}`);
    if (document.querySelectorAll('.subject-row').length > 1) {
        row.remove();
    } else {
        alert("Vous devez avoir au moins une matière.");
    }
}

async function fetchMethodology() {
    try {
        const response = await fetch(`${API_BASE}/methodology`);
        const data = await response.json();
        renderMethodology(data);
    } catch (err) {
        console.error("Échec du chargement de la méthodologie", err);
        const container = document.getElementById('methodology-content');
        if (container) container.innerText = "Erreur lors du chargement du contenu.";
    }
}

function renderMethodology(data) {
    const container = document.getElementById('methodology-content');
    if (!container) return;

    container.innerHTML = `
        <div class="methodology-content">
            <h3>Énoncé du Problème</h3>
            <p>${data.problem_statement}</p>
            
            <h3>Approche Basée sur les Données</h3>
            <p>${data.data_driven_approach}</p>
            
            <h3>Conception des Fonctionnalités</h3>
            <p>${data.feature_design}</p>
            
            <h3>Choix de l'Algorithme</h3>
            <p>${data.algorithm_choice}</p>
            
            <h3>Limites du Modèle</h3>
            <p>${data.limitations}</p>
            
            <h3>Impact dans le Monde Réel</h3>
            <p>${data.real_world_impact}</p>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('planner-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            generatePlan();
        });
    }
});

async function generatePlan() {
    const hoursPerDay = document.getElementById('hours_per_day').value;
    const daysLeft = document.getElementById('days_left').value;
    const subjectRows = document.querySelectorAll('.subject-row');

    const subjects = Array.from(subjectRows).map(row => ({
        name: row.querySelector('.subject-name').value,
        topic: row.querySelector('.subject-topic').value,
        level: row.querySelector('.subject-level').value
    }));

    const btn = document.getElementById('generate-btn');
    btn.innerText = "Génération...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/generate-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subjects,
                hours_per_day: hoursPerDay,
                days_left: daysLeft
            })
        });

        const data = await response.json();
        if (data.schedule) {
            renderSchedule(data.schedule);
            renderCharts(data.schedule, subjects.map(s => s.name));
            document.getElementById('results-section').classList.remove('hidden');
            window.scrollTo({ top: document.getElementById('results-section').offsetTop - 20, behavior: 'smooth' });
        }
    } catch (err) {
        alert("Échec de connexion au serveur. Assurez-vous qu'il est en cours d'exécution.");
    } finally {
        btn.innerText = "Générer le Plan";
        btn.disabled = false;
    }
}

function renderSchedule(schedule) {
    const container = document.getElementById('schedule-output');
    container.innerHTML = '';

    schedule.forEach(day => {
        const dayCard = document.createElement('div');
        dayCard.className = 'day-card';

        let tasksHtml = day.tasks.map(t => `
            <div class="task-item">
                <div class="task-info">
                    <span class="name">${t.subject}</span>
                    ${t.topic ? `<span class="topic">${t.topic}</span>` : ''}
                </div>
                <span class="hours">${t.hours} h</span>
            </div>
        `).join('');

        dayCard.innerHTML = `
            <h4>Jour ${day.day}</h4>
            <div class="tasks">
                ${tasksHtml || '<p style="color: var(--text-dim); font-style: italic;">Aucune tâche de prévue.</p>'}
            </div>
        `;
        container.appendChild(dayCard);
    });
}

function renderCharts(schedule, subjectNames) {
    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
        '#8b5cf6', '#06b6d4', '#ec4899', '#f97316'
    ];

    const totals = {};
    subjectNames.forEach(s => totals[s] = 0);

    schedule.forEach(day => {
        day.tasks.forEach(task => {
            if (totals[task.subject] !== undefined) {
                totals[task.subject] += task.hours;
            }
        });
    });

    const pieLabels = Object.keys(totals);
    const pieData = Object.values(totals);

    const pieCtx = document.getElementById('pieChart').getContext('2d');
    if (pieChartInstance) pieChartInstance.destroy();

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#334155';

    pieChartInstance = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: pieLabels,
            datasets: [{
                data: pieData,
                backgroundColor: colors.slice(0, pieLabels.length),
                borderWidth: 1,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    const days = schedule.map(day => `Jour ${day.day}`);
    const lineDatasets = subjectNames.map((subject, index) => {
        const data = schedule.map(day => {
            const task = day.tasks.find(t => t.subject === subject);
            return task ? task.hours : 0;
        });

        return {
            label: subject,
            data: data,
            backgroundColor: colors[index % colors.length],
            borderWidth: 1,
            borderRadius: 4
        };
    });

    const lineCtx = document.getElementById('lineChart').getContext('2d');
    if (lineChartInstance) lineChartInstance.destroy();

    lineChartInstance = new Chart(lineCtx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: lineDatasets
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: false,
                    title: { display: true, text: 'Heures' }
                },
                x: {
                    stacked: false,
                    title: { display: true, text: 'Chronologie' }
                }
            },
            plugins: {
                legend: { position: 'top' }
            }
        }
    });
}
