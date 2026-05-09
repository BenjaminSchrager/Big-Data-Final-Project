from pathlib import Path

from predict_resume import predict_from_resume, print_prediction_report


RESUME_PATH = "test_resumes/BenSchragerResume.pdf"
MODEL_PATH = "resume_reviewer_model.joblib"


def run_system_test(resume_path: str, model_path: str):
    resume_file = Path(resume_path)
    model_file = Path(model_path)

    print("=== SYSTEM TEST START ===")

    assert resume_file.exists(), f"Resume file not found: {resume_path}"
    print("PASS: resume file exists")

    assert model_file.exists(), f"Model file not found: {model_path}"
    print("PASS: model file exists")

    result = predict_from_resume(resume_path, model_path)

    assert isinstance(result, dict), "Prediction result should be a dictionary."
    print("PASS: prediction result is a dictionary")

    required_top_keys = [
        "resume_path",
        "features",
        "metadata",
        "predicted_class",
        "predicted_probability",
        "raw_text_length",
        "detected_sections",
    ]

    for key in required_top_keys:
        assert key in result, f"Missing key in prediction result: {key}"
    print("PASS: prediction result contains required keys")

    required_feature_keys = [
        "EdLevel",
        "MainBranch",
        "YearsCode",
        "YearsCodePro",
        "ComputerSkills",
    ]

    for key in required_feature_keys:
        assert key in result["features"], f"Missing extracted feature: {key}"
        assert result["features"][key] is not None, f"Feature {key} is None"
    print("PASS: all required model features were extracted")

    assert result["predicted_class"] in [0, 1], "Predicted class must be 0 or 1"
    print("PASS: predicted class is valid")

    assert 0.0 <= result["predicted_probability"] <= 1.0, "Predicted probability must be between 0 and 1"
    print("PASS: predicted probability is valid")

    assert result["raw_text_length"] > 0, "Extracted text length must be positive"
    print("PASS: extracted text length is positive")

    print("\n=== FULL PREDICTION REPORT ===")
    print_prediction_report(result)

    print("\n=== SYSTEM TEST COMPLETE ===")


def main():
    run_system_test(RESUME_PATH, MODEL_PATH)


if __name__ == "__main__":
    main()