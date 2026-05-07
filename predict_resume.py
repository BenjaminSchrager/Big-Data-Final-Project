from pathlib import Path

import joblib
import pandas as pd

from resume_parser import extract_text_from_pdf, split_resume_sections
from feature_mapper import complete_feature_vector


MODEL_PATH = "resume_reviewer_model.joblib"
RESUME_PATH = "test_resumes/BenSchragerResume.pdf"


def predict_from_resume(resume_path: str, model_path: str = MODEL_PATH):
    resume_file = Path(resume_path)
    model_file = Path(model_path)

    if not resume_file.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_file)

    text = extract_text_from_pdf(str(resume_file))
    sections = split_resume_sections(text)
    features, metadata = complete_feature_vector(sections)

    required_features = [
        "EdLevel",
        "MainBranch",
        "YearsCode",
        "YearsCodePro",
        "ComputerSkills",
    ]

    missing = [col for col in required_features if features.get(col) is None]
    if missing:
        raise ValueError(f"Missing required features for prediction: {missing}")

    X_input = pd.DataFrame([{
        "EdLevel": features["EdLevel"],
        "MainBranch": features["MainBranch"],
        "YearsCode": features["YearsCode"],
        "YearsCodePro": features["YearsCodePro"],
        "ComputerSkills": features["ComputerSkills"],
    }])

    pred_class = int(model.predict(X_input)[0])
    pred_proba = float(model.predict_proba(X_input)[0, 1])

    return {
        "resume_path": str(resume_file),
        "features": X_input.iloc[0].to_dict(),
        "metadata": metadata,
        "predicted_class": pred_class,
        "predicted_probability": pred_proba,
        "raw_text_length": len(text),
        "detected_sections": list(sections.keys()),
    }


def print_prediction_report(result: dict):
    print("=== RESUME REVIEWER RESULT ===")
    print(f"Resume: {result['resume_path']}")
    print(f"Extracted text length: {result['raw_text_length']}")
    print(f"Detected sections: {', '.join(result['detected_sections'])}")

    print("\n=== EXTRACTED FEATURES USED BY MODEL ===")
    for key, value in result["features"].items():
        print(f"{key}: {value}")

    print("\n=== FEATURE EXTRACTION DETAILS ===")
    for key, value in result["metadata"].items():
        print(f"{key}: {value}")

    print("\n=== MODEL OUTPUT ===")
    print(f"Predicted class: {result['predicted_class']}")
    print(f"Estimated probability of being hired: {result['predicted_probability']:.4f}")

    if result["predicted_probability"] >= 0.5:
        interpretation = "Above the model's default hiring threshold"
    else:
        interpretation = "Below the model's default hiring threshold"

    print(f"Interpretation: {interpretation}")

    print("\n=== IMPORTANT LIMITATION ===")
    print(
        "This prediction is a prototype estimate based only on a limited set of "
        "structured features extracted or estimated from the resume. It does not "
        "capture qualitative strengths such as company prestige, project depth, "
        "school reputation, writing quality, or role-specific fit."
    )


def main():
    result = predict_from_resume(RESUME_PATH)
    print_prediction_report(result)


if __name__ == "__main__":
    main()