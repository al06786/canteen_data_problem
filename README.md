# Canteen Prep Optimizer

Demand forecasting and prep planning for a simulated canteen with a shared kitchen-capacity limit.

## Problem

Every morning, before demand is known, the canteen has to decide how many units of five items to prepare: tea, poha, sandwich, juice and burger.

- Preparing too little loses sales and incurs a stockout penalty.
- Preparing too much wastes food.
- Going over 500 minutes of total kitchen time adds a penalty of 2.5 points per extra minute.

The goal is to maximise total profit on unseen days.

## Approach

1. **Forecast demand.** One RandomForest model per item, trained on 11 daily features (weather, exam days, festivals, sports events, footfall and so on).
2. **Turn forecasts into decisions.** Each item has different price, production, waste and stockout costs, so the quantity to prepare is not simply the forecast. A newsvendor-style marginal value calculation estimates whether one more unit of an item is worth making.
3. **Share the kitchen capacity.** A priority-queue loop gives each extra unit to whichever item's next unit is worth the most. Items can go past 500 minutes only where the marginal profit still beats the 2.5 per minute overage penalty.

## Results

Scored on a held-out validation set (model trained on the training file only):

| Solver | Validation score |
|---|---|
| Baseline (average historical demand) | 1,471,712 |
| This solver | 2,225,449 |

That is about 51% above the baseline.

## How to run

The provided dataset and scoring script are not redistributed here. 

1. Place `train.csv`, `validation.csv` and `scorer.py` in the same folder as `final_solver.py`.
2. Install the requirements: `pip install -r requirements.txt`
3. Run: `python final_solver.py`

## Files

- `final_solver.py`: the solver (`CanteenSolver` class with `fit` and `plan_day`)
- `WRITEUP.md`: short write-up of the approach, experiments and findings
- `requirements.txt`: Python dependencies

## Built with

Python, pandas, scikit-learn, SciPy