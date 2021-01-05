""" Echocardiogram data set - UCI
- Data Set Information
  All the patients suffered heart attacks at some point in the past. Some are still alive and some are not.
  The survival and still-alive variables, when taken together, indicate whether a patient survived for at least one year
  following the heart attack.

- Columns
  - survival: the number of months patient survived (has survived, if patient is still alive). Because all the patients
    had their heart attacks at different times, it is possible that some patients have survived less than one year but
    they are still alive. Check the second variable to confirm this. Such patients cannot be used for the prediction
    task mentioned above.
  - still-alive: a binary variable. 0=dead at end of survival period, 1 means still alive
  - age-at-heart-attack: age in years when heart attack occurred
  - pericardial-effusion: binary. Pericardial effusion is fluid around the heart. 0=no fluid, 1=fluid
  - fractional-shortening: a measure of contracility around the heart lower numbers are increasingly abnormal
  - epss: E-point septal separation, another measure of contractility. Larger numbers are increasingly abnormal.
  - lvdd: left ventricular end-diastolic dimension. This is a measure of the size of the heart at end-diastole. Large
    hearts tend to be sick hearts.
  - wall-motion-score: a measure of how the segments of the left ventricle are moving
  - wall-motion-index: equals wall-motion-score divided by number of segments seen
  - alive-at-1: Boolean-valued. Derived from the first two attributes. 0 means patient was either dead after 1 year or
    had been followed for less than 1 year. 1 means patient was alive at 1 year.
    - variable alive-at-1 is highly imbalanced

- Reference
  - https://www.kaggle.com/loganalive/echocardiogram-dataset-uci
"""

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
plt.show()
