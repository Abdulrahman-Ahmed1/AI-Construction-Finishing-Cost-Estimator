# Final Validation Report

## Validation status

- Raw source files preserved: Yes
- Processed data available: Yes
- Master dataset available: Yes
- Scenario-generated training dataset available: Yes
- Seven project notebooks included: Yes
- Saved model loads successfully: Yes
- Prediction function works: Yes
- FastAPI `/health` works: Yes
- FastAPI `/predict` works: Yes
- Test suite: **28 passed**

## Final packaged model

- Model: **HistGradientBoostingRegressor**
- Version: **1.1.0**
- MAE: **6849.82 EGP**
- RMSE: **9154.67 EGP**
- R²: **0.9838**
- Training rows: 4800
- Test rows: 1200

## Important limitation

The training dataset is scenario-generated/synthetic. The project does not contain historical apartment-level invoices with observed total finishing costs. Therefore, these metrics measure performance on held-out simulated scenarios and should not be represented as validation on real apartment invoices.

## Category breakdown

The deployed API returns an estimated category allocation. Category cost columns were intentionally excluded from model inputs to prevent leakage. The allocation is based on category-cost proportions from similar scenario-generated training rows and is normalized to the ML-predicted total. It is not a separate category-cost prediction model.
