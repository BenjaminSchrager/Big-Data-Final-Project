from pathlib import Path

import joblib
import pandas as pd

from feature_mapper import complete_feature_vector
from resume_parser import extract_text_from_pdf, split_resume_sections


MODEL_PATH = "resume_reviewer_model.joblib"
RESUME_PATH = "test_resumes/BenSchragerResume.pdf"


# Prediction

def predict_from_resume(resume_path: str, model_path: str = MODEL_PATH):
    resume_file = Path(resume_path)
    model_file = Path(model_path)

    if not resume_file.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_file)

    text = extract_text_from_pdf(str(resume_file))
    if not text or len(text.strip()) < 50:
        raise ValueError(
            "Resume text extraction failed or returned too little text."
        )

    sections = split_resume_sections(text)
    features, metadata = complete_feature_vector(sections)

    required_features = [
        "EdLevel",
        "MainBranch",
        "YearsCode",
        "YearsCodePro",
        "ComputerSkills",
    ]

    missing = [name for name in required_features if features.get(name) is None]
    if missing:
        raise ValueError(f"Missing required features for prediction: {missing}")

    X_input = pd.DataFrame(
        [
            {
                "EdLevel": features["EdLevel"],
                "MainBranch": features["MainBranch"],
                "YearsCode": features["YearsCode"],
                "YearsCodePro": features["YearsCodePro"],
                "ComputerSkills": features["ComputerSkills"],
            }
        ]
    )

    predicted_class = int(model.predict(X_input)[0])
    predicted_probability = float(model.predict_proba(X_input)[0, 1])

    return {
        "resume_path": str(resume_file),
        "text_length": len(text),
        "sections": [name for name in sections.keys() if name != "FULL_TEXT"],
        "features": X_input.iloc[0].to_dict(),
        "metadata": metadata,
        "predicted_class": predicted_class,
        "predicted_probability": predicted_probability,
    }


# Output

def print_prediction_report(result: dict) -> None:
    print("Resume reviewer")
    print(f"Resume: {result['resume_path']}")
    print(f"Text length: {result['text_length']}")
    print(f"Sections: {', '.join(result['sections'])}")

    print("\nFeatures")
    for key, value in result["features"].items():
        print(f"- {key}: {value}")

    print("\nFeature details")
    for key, value in result["metadata"].items():
        print(f"- {key}: {value}")

    print("\nPrediction")
    print(f"- Class: {result['predicted_class']}")
    print(f"- Hire probability: {result['predicted_probability']:.4f}")

    if result["predicted_probability"] >= 0.5:
        print("- Threshold: above default cutoff")
    else:
        print("- Threshold: below default cutoff")

    print("\nNote")
    print(
        "This is a prototype estimate based on a small set of structured features "
        "extracted or estimated from the resume."
    )


# Local test

def main() -> None:
    result = predict_from_resume(RESUME_PATH)
    print_prediction_report(result)


if __name__ == "__main__":
    main()