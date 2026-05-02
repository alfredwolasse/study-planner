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
