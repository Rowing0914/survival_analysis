import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer

# Load data
df = pd.read_csv("echocardiogram.csv")

# Impute data
imp_mean = SimpleImputer(missing_values=np.nan, strategy="mean")
COLUMNS = ["age", "pericardialeffusion", "fractionalshortening", "epss", "lvdd", "wallmotion-score"]
df[COLUMNS] = imp_mean.fit_transform(df[COLUMNS])
df = df[COLUMNS + ["survival", "alive"]]
df = df.dropna()

# New col for dead cnt
df.loc[df.alive == 1, "dead"] = 0
df.loc[df.alive == 0, "dead"] = 1

""" Kaplan Meier Product-Limit Formula(KM)
http://pages.stat.wisc.edu/~ifischer/Intro_Stat/Lecture_Notes/8_-_Survival_Analysis/8.2_-_Kaplan-Meier_Formula.pdf
"""
# Convert the data into the KM-format as in the above material
df_survival = df["survival"].value_counts().rename_axis("survival").reset_index(name="num_casualities")
df_alive = df.groupby(by="survival").sum("alive").reset_index()
df_final = df_survival.set_index("survival").join(df_alive.set_index("survival")).reset_index()
df_final = df_final.sort_values(by="survival")

# === Apply KM estimate ===
cum_prob = 1.0
cum_prob_hist = [cum_prob]
num_remaining = df_final["num_casualities"].sum()

for row in df_final.iterrows():
    d = num_remaining - row[1]["num_casualities"]
    cum_prob *= (d/num_remaining)
    cum_prob_hist.append(cum_prob)
    num_remaining = d

# Visualise the result
plt.plot(cum_prob_hist)
plt.title("Kaplan Meier estimates")
plt.xlabel("Month after heart attack")
plt.ylabel("Survival")
plt.grid()
# plt.show()
plt.savefig("./images/result.png")