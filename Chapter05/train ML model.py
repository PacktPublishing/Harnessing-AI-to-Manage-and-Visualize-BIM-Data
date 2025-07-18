"""
Train, evaluate, and save comfort-index models, then plot:
  • bar charts of R² and MSE
  • scatter plots of predicted vs. actual CI for each model
"""
import pandas as pd, numpy as np, joblib, warnings, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics  import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from lightgbm         import LGBMRegressor
from xgboost          import XGBRegressor
warnings.filterwarnings("ignore")

# ── 1. LOAD ──────────────────────────────────────────────────────────────
df = pd.read_csv("union_dataset.csv")

# ── 2. QUICK TIDY-UP ─────────────────────────────────────────────────────
df = df.drop(columns=["Area", "PACKT_Nocc"], errors="ignore")        # optional
id_mask = df.columns.str.lower().str.match(r'^external[_ ]?id')
df      = df.loc[:, ~id_mask]                                         # remove IDs
if "EXT_hour" in df.columns:                                          # encode time-of-day
    df["hour_sin"] = np.sin(2*np.pi*df["EXT_hour"]/24)
    df["hour_cos"] = np.cos(2*np.pi*df["EXT_hour"]/24)
    df = df.drop(columns="EXT_hour")

TARGET = "PACKT_CI"
X = pd.get_dummies(df.drop(columns=TARGET), drop_first=True)
y = df[TARGET]

# ── 3. SPLIT ─────────────────────────────────────────────────────────────
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, random_state=42)

# ── 4. MODELS ────────────────────────────────────────────────────────────
MODELS = {
    "RandomForest": RandomForestRegressor(n_estimators=600, n_jobs=-1, random_state=42),
    "LightGBM"    : LGBMRegressor(n_estimators=1200, learning_rate=0.03,
                                  subsample=0.8, colsample_bytree=0.8, random_state=42),
    "XGBoost"     : XGBRegressor(n_estimators=1200, learning_rate=0.03, max_depth=6,
                                  subsample=0.8, colsample_bytree=0.8,
                                  objective="reg:squarederror", n_jobs=-1, random_state=42),
}

# ── 5. TRAIN / SCORE / SAVE ─────────────────────────────────────────────
score, mse, preds = {}, {}, {}
for name, mdl in MODELS.items():
    mdl.fit(X_tr, y_tr)
    y_pred      = mdl.predict(X_te)
    score[name] = r2_score(y_te, y_pred)
    mse[name]   = mean_squared_error(y_te, y_pred)
    preds[name] = y_pred
    joblib.dump(mdl, f"{name}_CI.pkl")
    print(f"{name:12}  R²={score[name]:.3f}  |  MSE={mse[name]:.4f}")

best_name  = max(score, key=score.get)
best_model = MODELS[best_name]

# ── 6. WRITE FULL-DATA PREDICTIONS ───────────────────────────────────────
df["CI_pred"] = best_model.predict(X)
df.to_csv("union_dataset_predictions.csv", index=False)
print(f"\nBest model → {best_name}  (predictions written to union_dataset_predictions.csv)")

# ── 7. BAR CHARTS (R² & MSE) ─────────────────────────────────────────────
fig, ax = plt.subplots(1, 2, figsize=(9, 4))
ax[0].bar(score.keys(), score.values()); ax[0].set_title("Hold-out R²")
ax[1].bar(mse.keys()  , mse.values()  ); ax[1].set_title("Hold-out MSE")
for a in ax: a.set_xlabel("Model"); a.grid(axis="y", alpha=.3)
plt.tight_layout(); plt.savefig("model_metrics.png", dpi=150); plt.show()
print("Metric chart saved → model_metrics.png")

# ── 8. SCATTER PLOTS (Predicted vs. Actual) ─────────────────────────────
fig, axes = plt.subplots(1, len(MODELS), figsize=(4*len(MODELS), 4), sharey=True)
if len(MODELS) == 1: axes = [axes]                                      # handle single axis

for ax, (name, y_pred) in zip(axes, preds.items()):
    ax.scatter(y_te, y_pred, alpha=.6)
    ax.plot([0,1],[0,1],'k--',lw=1)
    ax.set_title(name); ax.set_xlabel("Actual CI"); ax.grid(alpha=.3)
axes[0].set_ylabel("Predicted CI")
plt.suptitle("Predicted vs. Actual (hold-out set)")
plt.tight_layout(); plt.savefig("scatter_plots.png", dpi=150); plt.show()
print("Scatter plots saved → scatter_plots.png")
