# Smart Finishing AI — Apartment Finishing Cost Estimator

AI-powered graduation project for estimating apartment finishing costs in Egyptian pounds (EGP). The project combines a saved machine-learning regression pipeline, an explainable itemized cost layer, product-price data, a conversational Streamlit interface, and a FastAPI API.

> **Important:** The model target is scenario-generated/synthetic. It is built from product prices and documented quantity/labor assumptions, not historical contractor invoices. The result must be treated as an estimate, not a quotation.

## What the final application does

1. Opens a conversational chatbot in Streamlit.
2. Asks for apartment size, rooms, bathrooms, balconies, reception areas, finishing levels, quality preferences, optional upgrades, and plumbing system.
3. Validates the answers before prediction.
4. Uses the packaged `HistGradientBoostingRegressor` pipeline to predict the total finishing cost.
5. Shows an empirical prediction range based on held-out residuals.
6. Breaks the result into ceilings, doors, basic electrical, electrical finishing, flooring, paints, plumbing, sanitary ware, labor, and auxiliary costs.
7. Expands every section to show representative products, quantities, unit prices, and estimated line costs.
8. Makes the itemized estimate sum exactly to the ML predicted total by scaling representative product-cost proportions to the prediction.
9. Supports a multilingual chat/UI layer with common-language packs and optional automatic translation through `deep-translator`; if online translation is unavailable, the app falls back safely instead of failing.

## Model

- Model: `HistGradientBoostingRegressor`
- Training scenarios: 6,000
- Train/test: 4,800 / 1,200
- MAE: ~6,850 EGP
- RMSE: ~9,155 EGP
- R²: ~0.984
- Model artifact: `models/final_model_pipeline.joblib`
- Metadata: `models/model_metadata.json`

These metrics describe the packaged held-out **scenario-generated** test set and should not be presented as accuracy on real apartment invoices.

## ML inputs

The deployed model uses only information available before the final cost is known:

- Apartment area
- Rooms
- Bathrooms
- Master bathrooms
- Balconies
- Receptions
- Overall finishing level
- Quality preference for each finishing category
- Reception ceiling upgrade
- Reception chandelier
- Master bathroom upgrade
- Plumbing system

Category cost columns are excluded from the model to prevent target leakage.

## Itemized cost engine

The ML model predicts the total. The itemized layer is deliberately separate from the ML model.

It selects representative products from `data/processed/master_products_features.csv` using the requested quality level and the same quantity-rule logic used in scenario generation. The resulting category proportions are scaled to the ML total so the displayed detailed bill always reconciles to the predicted total.

This is an **explainable allocation**, not a second category-level ML prediction.

## Multilingual support

The app includes built-in labels/questions for multiple major languages and can automatically translate the remaining UI/question text when `deep-translator` has network access. Numeric answers, yes/no answers, quality levels, and PVC/PPR choices also accept common terms from multiple languages.

Because translation providers and language coverage can change, the README intentionally does not claim perfect native-language support for every language on earth. The app has an English fallback and does not fail when online translation is unavailable.

## Project structure

```text
AI_Construction_Finishing_Cost_Project/
├── app.py                         # Streamlit chatbot application
├── chatbot/
│   ├── i18n.py                    # multilingual UI + translation fallback
│   └── parser.py                  # multilingual-ish answer parsing
├── cost_engine/
│   └── engine.py                  # detailed itemized estimate
├── src/
│   ├── api/                       # FastAPI deployment
│   ├── data_processing/
│   ├── feature_engineering/
│   ├── prediction/
│   ├── scenario_generation/
│   └── training/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── previous_work/
│   └── training/
├── models/
├── notebooks/
├── reports/
├── tests/
├── All data/
├── requirements.txt
└── README.md
```

## Installation

From the project root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Streamlit application

```bash
streamlit run app.py
```

For Streamlit Community Cloud, select this repository and set the main file to:

```text
app.py
```

The repository already contains the saved model and packaged data needed for inference, so the app does not retrain the model on startup.

## Run tests

```bash
pytest -q
```

The final packaged project was tested after the application additions. The existing project suite passes, and the new cost-engine reconciliation tests verify that the itemized result adds up exactly to the ML prediction.

## Run FastAPI

```bash
uvicorn src.api.main:app --reload
```

Then open `/docs` for the interactive API documentation.

## API endpoints

### `GET /health`

Checks whether the saved model can be loaded.

### `POST /predict`

Accepts the complete 19-feature apartment scenario and returns:

- estimated total cost
- empirical prediction range
- estimated category allocation
- model version

The API category allocation remains explicitly documented as an allocation from similar scenario-generated training rows, not a separate category-cost prediction.

## Notebooks

- `01_Data_Audit.ipynb`
- `02_Data_Cleaning_and_Master_Dataset.ipynb`
- `03_EDA_and_Feature_Engineering.ipynb`
- `04_Training_Dataset_Generation.ipynb`
- `05_Model_Training_and_Comparison.ipynb`
- `06_Final_Model_Evaluation.ipynb`
- `07_Model_Inference.ipynb`

## Limitations and future work

- Training target is scenario-generated rather than historical invoice data.
- Market prices change over time.
- Product availability and contractor labor rates vary by location.
- Real invoices/quotations would materially improve validation and calibration.
- Future versions can add location, date-aware pricing, real quotations, supplier links, and a real LLM conversation layer if desired.
