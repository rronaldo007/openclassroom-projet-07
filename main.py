import csv
import sys
from pathlib import Path

from itertools import combinations

BUDGET_CENTS = 50000  # 500 en centime €
FILE_PATH = "./Liste+d'actions+-+P7+Python+-+Feuille+1.csv"


def _parse_percent(s):
    txt = s[:-1]
    return float(txt)

def _parse_euros_to_cents(s):
    euros = float(s)
    return euros * 100

def _profit_cents(cost_cents, benefit_percent):
    return cost_cents * (benefit_percent / 100)

def detect_csv_format(fieldnames):
    if 'name' in fieldnames and 'price' in fieldnames and 'profit' in fieldnames:
        return 'format_new'
    elif 'Actions #' in fieldnames:
        return 'format_original'
    else:
        raise ValueError(f"Unknown CSV format. Found columns: {fieldnames}")

def csv_file_reader(file_path):
    
    rows = []

    path = Path(file_path)
    if not path.exists():
        return

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        csv_reader = csv.DictReader(file, delimiter=',')

        print(f"# headers  : {csv_reader.fieldnames}")

        for row in csv_reader:
            if not any(v and str(v).strip() for v in row.values()):
                print("!! Skipping empty row")
                continue
            
            csv_format = detect_csv_format(csv_reader.fieldnames)
            if csv_format == 'format_new':
                action = row['name'].strip()
                cost_raw = row['price']
                benefit_raw = row['profit']
            else:
                action = row['Actions #'].strip()
                cost_raw = row['Coût par action (en euros)']
                benefit_raw = row['Bénéfice (après 2 ans)']


            benefit_percent = _parse_percent(benefit_raw)
            cost_cents = _parse_euros_to_cents(cost_raw)

            if benefit_percent is None or benefit_percent <= 0:
                print(f"!! Bad percent '{benefit_raw}' for action '{action}'. Skipping row.")
                continue
            if cost_cents is None or cost_cents <= 0:
                print(f"!! Bad cost '{cost_raw}' for action '{action}'. Skipping row.")
                continue

            profit_cents = _profit_cents(cost_cents, benefit_percent)

            rows.append({
                'action': action,
                'cost_cents': cost_cents,
                'benefit_percent': benefit_percent,
                'profit_cents': profit_cents,
            })
    return rows

def find_best_bruteforce(rows, budget_cents=BUDGET_CENTS):
    n = len(rows)

    best_rows = []
    best_profit = 0
    best_cost = 0
    combos_checked = 1 

    for k in range(1, n + 1):
        for subset in combinations(rows, k):
            combos_checked += 1
            total_cost = 0
            total_profit = 0

            for r in subset:
                total_cost += r["cost_cents"]
                total_profit += r["profit_cents"]
            if total_cost > BUDGET_CENTS:
                continue
            
            if total_profit >= best_profit:
                best_rows = list(subset)
                best_profit = total_profit
                best_cost = total_cost

    return {
        "best_rows": best_rows,
        "total_cost_cents": best_cost,
        "total_profit_cents": best_profit,
        "combos_checked": combos_checked,
    }

def main():
    file_path = sys.argv[1]
    rows = csv_file_reader(file_path)

    for row in rows:
        pretty = {
            **row,
            'cost_eur': f"{row['cost_cents']/100:.2f}€",
            'profit_eur': f"{row['profit_cents']/100:.2f}€",
        }
        print(pretty)

    result = find_best_bruteforce(rows, budget_cents=BUDGET_CENTS)

    print("\n=== Best portfolio (brute force) ===")
    print(f"Combos checked    : {result['combos_checked']}")
    print(f"Total cost        : {result['total_cost_cents']/100:.2f}€")
    print(f"Total profit      : {result['total_profit_cents']/100:.2f}€")
    print(f"Final value       : {(result['total_cost_cents'] + result['total_profit_cents'])/100:.2f}€")
    print("Actions selected  :")
    for r in result['best_rows']:
        print(f"  - {r['action']} | cost {r['cost_cents']/100:.2f}€ | profit {r['profit_cents']/100:.2f}€ ({r['benefit_percent']}%)")


if __name__ == "__main__":
    main()
