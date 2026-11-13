import pandas as pd

# train = pd.read_csv("train.csv")
# validation = pd.read_csv("validation.csv")

from sklearn.ensemble import RandomForestRegressor

features = ["day_of_week", "is_weekend", "temperature", "rain_score", "exam_day",
            "festival_day", "sports_event", "hostel_occupancy", "competitor_discount",
            "previous_day_leftover_index", "footfall_proxy"]

items = ["tea", "poha", "sandwich", "juice", "burger"]

# #training check
# models = {}
# for item in items:
#     y = train[f"actual_demand_{item}"]
#     model = RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=6, random_state=42)
#     model.fit(train[features], y)
#     models[item] = model
# print("Done training. Models built for:", list(models.keys()))

# #validation check
# for item in items:
#     predictions = models[item].predict(validation[features])
#     actual = validation[f"actual_demand_{item}"]
#     error = (predictions - actual).abs().mean()
#     print(item, "average error:", error)

from scipy.stats import norm

PRICE = {"tea": 15, "poha": 35, "sandwich": 55, "juice": 45, "burger": 80}
COST = {"tea": 5, "poha": 14, "sandwich": 25, "juice": 20, "burger": 42}
WASTE = {"tea": 1, "poha": 6, "sandwich": 12, "juice": 18, "burger": 22}
STOCKOUT = {"tea": 3, "poha": 8, "sandwich": 12, "juice": 10, "burger": 18}
PREP_TIME = {"tea": 1, "poha": 3, "sandwich": 4, "juice": 2, "burger": 6}

#target quantile for each item
target_quantile = {}
for item in items:
    Cu = (PRICE[item] - COST[item]) + STOCKOUT[item]
    Co = COST[item] + WASTE[item]
    target_quantile[item] = Cu / (Cu + Co)

def prepare_quantity(item, predicted_mean, std):
    q = target_quantile[item]
    z = norm.ppf(q)
    quantity = predicted_mean + z * std
    return max(0, round(quantity))  # never negative, round to whole number

#marginal value of producing one more unit of an item, given the predicted mean and std of demand
def marginal_value(price, cost, waste, stockout, p, mean, std):
    prob = 1 - norm.cdf((p - mean) / std)   # chance demand ends up bigger than p
    return (price + stockout + waste) * prob - (cost + waste)

def find_best_quantity(price, cost, waste, stockout, mean, std):
    p = 0
    while True:
        mv = marginal_value(price, cost, waste, stockout, p + 1, mean, std)
        if mv <= 0:
            break   # the next unit isn't worth it anymore, stop here
        p += 1
    return p

def find_best_quantity_with_capacity(price, cost, waste, stockout, mean, std, prep_time, already_used_minutes):
    p = 0
    while True:
        mv = marginal_value(price, cost, waste, stockout, p + 1, mean, std)
        
        minutes_so_far = already_used_minutes + p * prep_time
        bar = 0 if minutes_so_far < 500 else 2.5 * prep_time
        
        if mv <= bar:
            break
        p += 1
    return p

#calculating the best quantity for each item, given the predicted mean and std of demand, and the time constraint of 500 minutes
import heapq

def solve_day(means, stds):
    heap = []
    prepared = {item: 0 for item in items}

    # every item bids for its 1st unit
    for item in items:
        mv = marginal_value(PRICE[item], COST[item], WASTE[item], STOCKOUT[item], 1, means[item], stds[item])
        heapq.heappush(heap, (-mv, item))   # negative so the heap gives us the BIGGEST bid first

    total_time = 0
    while heap:
        neg_mv, item = heapq.heappop(heap)   # take the current highest bidder
        mv = -neg_mv
        bar = 0 if total_time < 500 else 2.5 * PREP_TIME[item]

        if mv <= bar:
            continue   # this item's bid lost — drop it permanently, don't re-add it

        # accept the unit
        prepared[item] += 1
        total_time += PREP_TIME[item]

        # this item bids again, for its NEXT unit
        next_mv = marginal_value(PRICE[item], COST[item], WASTE[item], STOCKOUT[item],
                                  prepared[item] + 1, means[item], stds[item])
        heapq.heappush(heap, (-next_mv, item))

    return prepared

#required code
class CanteenSolver:
    def fit(self, train_df, validation_df=None):
        if validation_df is not None:
            train_df = pd.concat([train_df, validation_df], ignore_index=True)

        self.models = {}
        self.stds = {}
        for item in items:
            y = train_df[f"actual_demand_{item}"]
            model = RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=6, random_state=42)
            model.fit(train_df[features], y)
            self.models[item] = model
            self.stds[item] = y.std()

    def plan_day(self, row):
        row_df = pd.DataFrame([row])
        means = {item: self.models[item].predict(row_df[features])[0] for item in items}
        plan = solve_day(means, self.stds)
        return {item: int(plan[item]) for item in items}


if __name__ == "__main__":
    from scorer import score_dataset

    train = pd.read_csv("train.csv")
    validation = pd.read_csv("validation.csv")

    solver = CanteenSolver()
    solver.fit(train)
    plans = [solver.plan_day(row) for _, row in validation.iterrows()]
    score = score_dataset(plans, validation)
    print(score)

    solver_final = CanteenSolver()
    solver_final.fit(train, validation)