def knapsack():
    store = [
        {'item': 'A', 'weight': 2, 'value': 3},
        {'item': 'B', 'weight': 3, 'value': 4},
        {'item': 'C', 'weight': 4, 'value': 5},
    ]
    weights = [d['weight'] for d in store]
    values  = [d['value']  for d in store]
    items   = [d['item']   for d in store]
  

    print("=======weights=========:", weights)
    print("========values=========:", values)
    n = len(weights)
    limit_weight = 5
    print("========max_weight==========:", limit_weight)


    dp = [[0]*(limit_weight+1) for _ in range(n+1)]
    for i in range(limit_weight + 1):
        dp[0][i] = i

    for i in range(1, n + 1):
        for w in range(limit_weight + 1):
            
            dont_take = dp[i-1][w]
            
            if weights[i-1] <= w:
                take = dp[i-1][w - weights[i-1]] + values[i-1]
                dp[i][w] = max(dont_take, take)
            else:
                dp[i][w] = dont_take
    
    
    for row in dp:
        print(row)


if __name__ == "__main__":
    knapsack()
