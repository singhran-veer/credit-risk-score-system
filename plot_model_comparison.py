"""Plot the supplied 1,500-row test results for all three classifiers."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parent / "metrics_output"
OUT.mkdir(exist_ok=True)

models = ["Logistic Regression", "Random Forest", "XGBoost"]
metrics = {
    "Accuracy": [0.8466667, 0.872, 0.872],
    "Class 0 precision": [0.82, 0.87, 0.87],
    "Class 0 recall": [0.81, 0.81, 0.81],
    "Class 0 F1": [0.81, 0.84, 0.84],
    "Class 1 precision": [0.87, 0.88, 0.87],
    "Class 1 recall": [0.87, 0.91, 0.92],
    "Class 1 F1": [0.87, 0.89, 0.89],
}

fig, ax = plt.subplots(figsize=(13, 6.5))
x = np.arange(len(metrics))
width = 0.25
colors = ["#6c8ebf", "#ed9b40", "#3678a8"]
for i, model in enumerate(models):
    values = [metrics[m][i] for m in metrics]
    bars = ax.bar(x + (i - 0.5) * width, values, width, label=model, color=colors[i])
    ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)

ax.set_title("Model Performance Comparison", fontsize=16, weight="bold", pad=14)
ax.set_ylabel("Score")
ax.set_ylim(0, 1.08)
ax.set_xticks(x, metrics.keys(), rotation=12, ha="right")
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False, ncols=3, loc="upper center")
fig.text(
    0.5, 0.01,
    "Test set: 1,500 customers. Class 1 = high risk; values rounded as reported.",
    ha="center", fontsize=9, color="#555555",
)
fig.tight_layout(rect=[0, 0.05, 1, 1])
path = OUT / "model_comparison.png"
fig.savefig(path, dpi=180, bbox_inches="tight")
plt.close(fig)
print(f"Saved {path}")
