import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score

from imblearn.over_sampling import SMOTE


# ---------------- LOAD DATASET ----------------

df = pd.read_excel("digital_lifestyle_benchmark_dataset.xlsx")

print("Dataset Loaded Successfully")
print("Shape:", df.shape)


# ---------------- DROP ID ----------------

if 'id' in df.columns:
    df = df.drop('id', axis=1)


# ---------------- HANDLE MISSING VALUES ----------------

num_cols = df.select_dtypes(include=['int64', 'float64']).columns
cat_cols = df.select_dtypes(include=['object']).columns

df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
df[cat_cols] = df[cat_cols].fillna(df[cat_cols].mode().iloc[0])


# ---------------- LABEL ENCODING ----------------

le = LabelEncoder()

for col in cat_cols:
    df[col] = le.fit_transform(df[col])

print("Label Encoding Completed")


# ---------------- TARGET VARIABLES ----------------

y_addiction = df['digital_dependence_score']
y_health = df['high_risk_flag']

X_full = df.drop(['digital_dependence_score', 'high_risk_flag'], axis=1)


# ---------------- FEATURE IMPORTANCE (ADDICTION) ----------------

X_add_train, X_add_test, y_add_train, y_add_test = train_test_split(
    X_full, y_addiction, test_size=0.3, random_state=42
)

# SAVE TRAIN TEST DATA
train_add_df = pd.concat([X_add_train, y_add_train], axis=1)
test_add_df = pd.concat([X_add_test, y_add_test], axis=1)

train_add_df.to_csv("addiction_train_data.csv", index=False)
test_add_df.to_csv("addiction_test_data.csv", index=False)

print("Addiction Train/Test Data Saved")

scaler_add = StandardScaler()
X_add_train_scaled = scaler_add.fit_transform(X_add_train)

dt_add = DecisionTreeRegressor(random_state=42)
dt_add.fit(X_add_train_scaled, y_add_train)

add_importance = pd.DataFrame({
    'Feature': X_full.columns,
    'Importance': dt_add.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("\nAddiction Feature Importance")
print(add_importance)


# ---------------- FEATURE IMPORTANCE (HEALTH) ----------------

X_health_train, X_health_test, y_health_train, y_health_test = train_test_split(
    X_full, y_health, test_size=0.3, random_state=42, stratify=y_health
)

# SAVE TRAIN TEST DATA
train_health_df = pd.concat([X_health_train, y_health_train], axis=1)
test_health_df = pd.concat([X_health_test, y_health_test], axis=1)

train_health_df.to_csv("health_train_data.csv", index=False)
test_health_df.to_csv("health_test_data.csv", index=False)

print("Health Train/Test Data Saved")

scaler_health = StandardScaler()
X_health_train_scaled = scaler_health.fit_transform(X_health_train)

dt_health = DecisionTreeClassifier(random_state=42)
dt_health.fit(X_health_train_scaled, y_health_train)

health_importance = pd.DataFrame({
    'Feature': X_full.columns,
    'Importance': dt_health.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("\nHealth Feature Importance")
print(health_importance)


# ---------------- ADDICTION MODEL ----------------

top6_features = add_importance.head(6)['Feature'].tolist()

print("\nTop 6 Addiction Features:", top6_features)

X_add = df[top6_features]

X_train, X_test, y_train, y_test = train_test_split(
    X_add, y_addiction, test_size=0.3, random_state=42
)

scaler_add2 = StandardScaler()

X_train_scaled = scaler_add2.fit_transform(X_train)
X_test_scaled = scaler_add2.transform(X_test)

model_add = LinearRegression()
model_add.fit(X_train_scaled, y_train)

pred_add = model_add.predict(X_test_scaled)

print("\nAddiction Model Performance")
print("R2 Score:", round(r2_score(y_test, pred_add) * 100, 2), "%")
print("MAE:", round(mean_absolute_error(y_test, pred_add), 2))


# ---------------- HEALTH MODEL ----------------

top8_features = health_importance.head(8)['Feature'].tolist()

print("\nTop 8 Health Features:", top8_features)

X_health_top = df[top8_features]

X_train_h, X_test_h, y_train_h, y_test_h = train_test_split(
    X_health_top,
    y_health,
    test_size=0.3,
    random_state=42,
    stratify=y_health
)

scaler_h = StandardScaler()

X_train_scaled_h = scaler_h.fit_transform(X_train_h)
X_test_scaled_h = scaler_h.transform(X_test_h)

# Handle class imbalance
sm = SMOTE(random_state=42)
X_resampled, y_resampled = sm.fit_resample(X_train_scaled_h, y_train_h)

rf_model = RandomForestClassifier(
    n_estimators=500,        # more trees → better learning
    max_depth=12,            # slightly deeper trees
    min_samples_split=5,     # prevents overfitting
    min_samples_leaf=2,      # smoother predictions
    random_state=42,
    class_weight='balanced'
)

rf_model.fit(X_resampled, y_resampled)

pred_health = rf_model.predict(X_test_scaled_h)

accuracy = accuracy_score(y_test_h, pred_health)

print("\nHealth Model Accuracy:", round(accuracy * 100, 2), "%")


# ---------------- ADDICTION LEVEL CLASSIFICATION ----------------

def classify_addiction(score):

    q1 = df['digital_dependence_score'].quantile(0.33)
    q2 = df['digital_dependence_score'].quantile(0.66)

    if score <= q1:
        return "LOW"

    elif score <= q2:
        return "MODERATE"

    else:
        return "HIGH"


# ---------------- PREDICTION FUNCTIONS ----------------

def predict_addiction(values):

    values = np.array(values).reshape(1, -1)

    values_scaled = scaler_add2.transform(values)

    score = model_add.predict(values_scaled)[0]

    level = classify_addiction(score)

    return score, level


def predict_health(values):

    values = np.array(values).reshape(1, -1)

    values_scaled = scaler_h.transform(values)

    proba = rf_model.predict_proba(values_scaled)[0][1]

    threshold = 0.36


    if proba > threshold:
        risk = "HIGH HEALTH RISK"
    else:
        risk = "LOW HEALTH RISK"

    return risk, proba