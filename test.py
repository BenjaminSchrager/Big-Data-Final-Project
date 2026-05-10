from pathlib import Path

from predict_resume import predict_from_resume, print_prediction_report


RESUME_PATH = "test_resumes/example1.pdf"
MODEL_PATH = "resume_reviewer_model.joblib"


# System test

def run_system_test(resume_path: str, model_path: str) -> None:
    resume_file = Path(resume_path)
    model_file = Path(model_path)

    print("System test")

    assert resume_file.exists(), f"Resume file not found: {resume_path}"
    print("- resume file found")

    assert model_file.exists(), f"Model file not found: {model_path}"
    print("- model file found")

    try:
        result = predict_from_resume(resume_path, model_path)
    except Exception as e:
        print(f"- prediction failed: {e}")
        raise

    assert isinstance(result, dict), "Prediction result should be a dictionary."
    print("- prediction returned")

    required_top_keys = [
        "resume_path",
        "text_length",
        "sections",
        "features",
        "metadata",
        "predicted_class",
        "predicted_probability",
    ]

    for key in required_top_keys:
        assert key in result, f"Missing key in prediction result: {key}"
    print("- result keys present")

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
    print("- model features present")

    assert result["predicted_class"] in [0, 1], "Predicted class must be 0 or 1"
    print("- predicted class valid")

    assert 0.0 <= result["predicted_probability"] <= 1.0, (
        "Predicted probability must be between 0 and 1"
    )
    print("- predicted probability valid")

    assert result["text_length"] > 0, "Extracted text length must be positive"
    print("- text extracted")

    print("\nReport")
    print_prediction_report(result)


# Entry point

def main() -> None:
    run_system_test(RESUME_PATH, MODEL_PATH)


if __name__ == "__main__":
    main()