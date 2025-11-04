"""
AlgoInvest&Trade - Algorithme Optimisé
Programmation Dynamique (Knapsack 0/1)

Trouve la meilleure combinaison d'actions pour maximiser le profit
sans dépasser le budget, en utilisant l'algorithme du sac à dos.

Complexité: O(n × W) où n = nombre d'actions, W = budget en centimes
Auteur: AlgoInvest&Trade
Date: Novembre 2025
"""

import csv
import time
from pathlib import Path

# ============================================================================
# CONSTANTES
# ============================================================================

BUDGET_CENTS = 50000  # Budget maximum : 500€ en centimes


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def parse_percent(s):
    """
    Convertit un pourcentage en string vers float.
    Exemple: '5%' → 5.0
    """
    return float(s.rstrip('%'))


def euros_to_cents(euros_str):
    """
    Convertit des euros en centimes (entiers).
    Utilise des entiers pour éviter les problèmes de précision avec les floats.
    Exemple: '20.5' → 2050
    """
    return int(float(euros_str) * 100)


def calculate_profit(cost_cents, benefit_percent):
    """
    Calcule le profit en centimes.
    profit = coût × (bénéfice% / 100)
    """
    return int(cost_cents * benefit_percent / 100)


def find_csv_file():
    """
    Trouve automatiquement le fichier CSV dans le répertoire courant.
    Cherche les fichiers contenant 'action' dans leur nom.
    """
    csv_files = list(Path(".").glob("*.csv"))
    
    if not csv_files:
        return None
    
    # Si un seul fichier CSV, le retourner
    if len(csv_files) == 1:
        return str(csv_files[0])
    
    # Chercher un fichier contenant 'action'
    for csv_file in csv_files:
        if 'action' in csv_file.name.lower():
            return str(csv_file)
    
    # Sinon retourner le premier
    return str(csv_files[0])


# ============================================================================
# LECTURE DES DONNÉES
# ============================================================================

def load_actions_from_csv(file_path):
    """
    Lit le fichier CSV et retourne une liste d'actions valides.
    
    Filtre automatiquement:
    - Les lignes vides
    - Les actions avec coût <= 0
    - Les actions avec bénéfice <= 0
    
    Args:
        file_path: Chemin vers le fichier CSV
        
    Returns:
        Liste de dictionnaires contenant les actions valides
    """
    actions = []
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Erreur: Le fichier '{file_path}' n'existe pas.")
        return actions
    
    print(f"📄 Lecture du fichier: {path.name}")
    
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=',')
            
            for row_num, row in enumerate(reader, start=2):
                # Ignorer les lignes vides
                if not any(v and str(v).strip() for v in row.values()):
                    continue
                
                try:
                    # Extraire les données
                    name = row['Actions #'].strip()
                    cost_str = row['Coût par action (en euros)']
                    benefit_str = row['Bénéfice (après 2 ans)']
                    
                    # Parser les valeurs
                    benefit_percent = parse_percent(benefit_str)
                    cost_cents = euros_to_cents(cost_str)
                    
                    # Validation
                    if benefit_percent <= 0:
                        print(f"⚠️  Ligne {row_num}: Bénéfice invalide pour '{name}' ({benefit_str})")
                        continue
                    
                    if cost_cents <= 0:
                        print(f"⚠️  Ligne {row_num}: Coût invalide pour '{name}' ({cost_str}€)")
                        continue
                    
                    # Calculer le profit
                    profit_cents = calculate_profit(cost_cents, benefit_percent)
                    
                    # Ajouter l'action
                    actions.append({
                        'name': name,
                        'cost_cents': cost_cents,
                        'benefit_percent': benefit_percent,
                        'profit_cents': profit_cents,
                    })
                    
                except (KeyError, ValueError) as e:
                    print(f"⚠️  Ligne {row_num}: Erreur de parsing - {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return []
    
    return actions


# ============================================================================
# ALGORITHME KNAPSACK (PROGRAMMATION DYNAMIQUE)
# ============================================================================

def knapsack_dynamic_programming(actions, budget_cents):
    """
    Résout le problème du sac à dos 0/1 avec la programmation dynamique.
    
    Principe:
    - Construit un tableau dp[i][w] où:
      dp[i][w] = profit maximal avec les i premières actions et budget w
    
    - Pour chaque case, on choisit le maximum entre:
      1. Ne pas prendre l'action: dp[i-1][w]
      2. Prendre l'action: dp[i-1][w-coût] + profit
    
    Complexité: O(n × W) où n = nombre d'actions, W = budget
    
    Args:
        actions: Liste des actions disponibles
        budget_cents: Budget maximum en centimes
        
    Returns:
        Dictionnaire avec les actions sélectionnées et les statistiques
    """
    n = len(actions)
    
    # Cas particulier: aucune action
    if n == 0:
        return {
            'selected_actions': [],
            'total_cost_cents': 0,
            'total_profit_cents': 0,
            'num_actions': 0,
        }
    
    # Filtrer les actions trop chères
    valid_actions = [a for a in actions if a['cost_cents'] <= budget_cents]
    n = len(valid_actions)
    
    if n == 0:
        print("⚠️  Aucune action ne rentre dans le budget!")
        return {
            'selected_actions': [],
            'total_cost_cents': 0,
            'total_profit_cents': 0,
            'num_actions': 0,
        }
    
    print(f"\n🔧 Construction du tableau DP...")
    print(f"   Taille: {n} actions × {budget_cents:,} centimes")
    print(f"   Cases à remplir: {n * budget_cents:,}")
    
    # ========================================================================
    # ÉTAPE 1: CRÉER LE TABLEAU DP
    # ========================================================================
    # dp[i][w] = profit maximal avec les i premières actions et budget w
    dp = [[0] * (budget_cents + 1) for _ in range(n + 1)]
    
    # ========================================================================
    # ÉTAPE 2: REMPLIR LE TABLEAU
    # ========================================================================
    for i in range(1, n + 1):
        action = valid_actions[i - 1]
        cost = action['cost_cents']
        profit = action['profit_cents']
        
        for w in range(budget_cents + 1):
            # Option 1: Ne pas prendre cette action
            dont_take = dp[i - 1][w]
            
            # Option 2: Prendre cette action (si elle rentre)
            if cost <= w:
                take = dp[i - 1][w - cost] + profit
                dp[i][w] = max(dont_take, take)
            else:
                # L'action est trop chère pour ce budget
                dp[i][w] = dont_take
    
    # Le profit maximal est dans la dernière case
    max_profit = dp[n][budget_cents]
    
    # ========================================================================
    # ÉTAPE 3: RECONSTRUCTION DE LA SOLUTION (BACKTRACKING)
    # ========================================================================
    # On remonte le tableau pour trouver quelles actions ont été prises
    selected_actions = []
    w = budget_cents
    
    for i in range(n, 0, -1):
        # Si la valeur a changé par rapport à la ligne précédente,
        # c'est que cette action a été prise
        if dp[i][w] != dp[i - 1][w]:
            action = valid_actions[i - 1]
            selected_actions.append(action)
            w -= action['cost_cents']
    
    # Inverser la liste pour avoir l'ordre d'origine
    selected_actions.reverse()
    
    # Calculer le coût total
    total_cost = sum(a['cost_cents'] for a in selected_actions)
    
    return {
        'selected_actions': selected_actions,
        'total_cost_cents': total_cost,
        'total_profit_cents': max_profit,
        'num_actions': len(selected_actions),
    }


# ============================================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================================

def display_results(result, execution_time, num_total_actions):
    """
    Affiche les résultats de manière claire et professionnelle.
    """
    print("\n" + "=" * 70)
    print(f"{'RÉSULTAT - MEILLEUR PORTEFEUILLE':^70}")
    print("=" * 70)
    
    # Statistiques principales
    print(f"\n💼 Actions disponibles    : {num_total_actions}")
    print(f"📦 Actions sélectionnées  : {result['num_actions']}")
    print(f"💰 Coût total             : {result['total_cost_cents'] / 100:.2f}€")
    print(f"📈 Profit après 2 ans     : {result['total_profit_cents'] / 100:.2f}€")
    print(f"💵 Valeur finale          : {(result['total_cost_cents'] + result['total_profit_cents']) / 100:.2f}€")
    
    # ROI (Return On Investment)
    if result['total_cost_cents'] > 0:
        roi = (result['total_profit_cents'] / result['total_cost_cents']) * 100
        print(f"📊 ROI                    : {roi:.2f}%")
    
    print(f"⏱️  Temps d'exécution      : {execution_time:.6f}s")
    
    # Liste détaillée des actions
    if result['selected_actions']:
        print("\n" + "-" * 70)
        print(f"{'ACTION':<20} {'COÛT':>12} {'PROFIT':>12} {'BÉNÉFICE':>12}")
        print("-" * 70)
        
        for action in result['selected_actions']:
            print(f"{action['name']:<20} "
                  f"{action['cost_cents'] / 100:>11.2f}€ "
                  f"{action['profit_cents'] / 100:>11.2f}€ "
                  f"{action['benefit_percent']:>11.2f}%")
        
        print("-" * 70)
        print(f"{'TOTAL':<20} "
              f"{result['total_cost_cents'] / 100:>11.2f}€ "
              f"{result['total_profit_cents'] / 100:>11.2f}€")
    
    print("=" * 70)


def display_performance_metrics(num_actions, budget_cents, execution_time):
    """
    Affiche les métriques de performance de l'algorithme.
    """
    print("\n📊 MÉTRIQUES DE PERFORMANCE")
    print("-" * 70)
    print(f"Algorithme           : Programmation Dynamique (Knapsack 0/1)")
    print(f"Complexité théorique : O(n × W)")
    print(f"Opérations réalisées : {num_actions} × {budget_cents:,} = {num_actions * budget_cents:,}")
    
    if execution_time > 0:
        ops_per_second = (num_actions * budget_cents) / execution_time
        print(f"Opérations/seconde   : {ops_per_second:,.0f}")
    
    print("-" * 70)


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """
    Fonction principale du programme.
    """
    print("=" * 70)
    print(f"{'AlgoInvest&Trade':^70}")
    print(f"{'Optimisation de portefeuille - Programmation Dynamique':^70}")
    print("=" * 70)
    print(f"\n💼 Budget maximum: {BUDGET_CENTS / 100:.2f}€ ({BUDGET_CENTS:,} centimes)\n")
    
    # ========================================================================
    # 1. TROUVER ET LIRE LE FICHIER CSV
    # ========================================================================
    file_path = find_csv_file()
    
    if not file_path:
        print("❌ Aucun fichier CSV trouvé dans le répertoire.")
        print("   Assurez-vous qu'un fichier CSV contenant les actions est présent.")
        return
    
    actions = load_actions_from_csv(file_path)
    
    if not actions:
        print("\n❌ Aucune action valide trouvée dans le fichier.")
        return
    
    print(f"\n✅ {len(actions)} actions valides chargées")
    
    # ========================================================================
    # 2. EXÉCUTER L'ALGORITHME KNAPSACK
    # ========================================================================
    print("\n🚀 Lancement de l'algorithme...")
    
    start_time = time.time()
    result = knapsack_dynamic_programming(actions, BUDGET_CENTS)
    execution_time = time.time() - start_time
    
    # ========================================================================
    # 3. AFFICHER LES RÉSULTATS
    # ========================================================================
    display_results(result, execution_time, len(actions))
    display_performance_metrics(len(actions), BUDGET_CENTS, execution_time)
    
    print("\n✅ Calcul terminé avec succès!\n")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()