import csv
import time
from pathlib import Path
import sys

BUDGET_CENTS = 50000  # Budget maximum : 500€ en centimes

FILE_PATH = "./dataset1_Python+P7.csv"

def find_csv_file():
    csv_files = list(Path(".").glob("*.csv"))
    
    if not csv_files:
        return None
    
    if len(csv_files) == 1:
        return str(csv_files[0])
    
    for csv_file in csv_files:
        if 'action' in csv_file.name.lower():
            return str(csv_file)
    
    return str(csv_files[0])

def load_actions_from_csv(file_path):
    
    actions = []
    path = Path(file_path)
    
    if not path.exists():
        return actions
    
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=',')
        
        for _, row in enumerate(reader, start=2):
            if not [v and str(v).strip() for v in row.values()]:
                continue
            
            # Extraire les données
            name = row['Actions #'].strip()
            cost_str = row['Coût par action (en euros)']
            benefit_str = row['Bénéfice (après 2 ans)']
            
            # Parser les valeurs  float(s.rstrip('%')  int(float(euros_str) * 100)
            benefit_percent = float(benefit_str.rstrip('%'))
            cost_cents =  int(float(cost_str) * 100)
            
            # Calculer le profit
            profit_cents = int(cost_cents * benefit_percent / 100)
            
            # Ajouter l'action
            actions.append({
                'name': name,
                'cost_cents': cost_cents,
                'benefit_percent': benefit_percent,
                'profit_cents': profit_cents,
            })
    return actions

def knapsack_dynamic_programming(actions, budget_cents):

    n = len(actions)
    
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
        return {
            'selected_actions': [],
            'total_cost_cents': 0,
            'total_profit_cents': 0,
            'num_actions': 0,
        }
    
    # ========================================================================
    # ÉTAPE 1: CRÉER LE TABLEAU DP
    # ========================================================================
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


def display_results(result, execution_time, num_total_actions):

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


def main():
    
    file_path = sys.argv[1]
    
    actions = load_actions_from_csv(file_path)
    start_time = time.time()
    result = knapsack_dynamic_programming(actions, BUDGET_CENTS)
    execution_time = time.time() - start_time
    
    display_results(result, execution_time, len(actions))



if __name__ == "__main__":
    main()