import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_PATH = "stackoverflow_full.csv"
MODEL_PATH = "resume_reviewer_model.joblib"


# Data

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    return df


# Model

def build_pipeline() -> Pipeline:
    categorical_features = ["EdLevel", "MainBranch"]
    numeric_features = ["YearsCode", "YearsCodePro", "ComputerSkills"]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=2000, random_state=42)),
        ]
    )

    return model


# Training

def main() -> None:
    df = load_data()

    feature_cols = [
        "EdLevel",
        "MainBranch",
        "YearsCode",
        "YearsCodePro",
        "ComputerSkills",
    ]
    target_col = "Employed"

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = build_pipeline()
    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_train_proba = model.predict_proba(X_train)[:, 1]

    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)[:, 1]

    print("Train")
    print(f"Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
    print(f"F1: {f1_score(y_train, y_train_pred):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_train, y_train_proba):.4f}")

    print("\nTest")
    print(f"Accuracy: {accuracy_score(y_test, y_test_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_test_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_test_pred):.4f}")
    print(f"F1: {f1_score(y_test, y_test_pred):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, y_test_proba):.4f}")

    print("\nConfusion matrix")
    print(confusion_matrix(y_test, y_test_pred))

    print("\nClassification report")
    print(classification_report(y_test, y_test_pred))

    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model: {MODEL_PATH}")


if __name__ == "__main__":
    main()