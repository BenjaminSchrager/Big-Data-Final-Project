from dataclasses import dataclass
import re


MODEL_FEATURE_ORDER = [
    "EdLevel",
    "MainBranch",
    "YearsCode",
    "YearsCodePro",
    "ComputerSkills",
]


@dataclass
class FeatureRule:
    feature_name: str
    source: str
    extraction_method: str
    required_for_model: bool
    allow_manual_input: bool
    notes: str


FEATURE_SCHEMA = {
    "EdLevel": FeatureRule(
        feature_name="EdLevel",
        source="resume",
        extraction_method="extract_from_education_section",
        required_for_model=True,
        allow_manual_input=True,
        notes=(
            "Map the highest education signal on the resume into one of the model's "
            "education categories."
        ),
    ),
    "MainBranch": FeatureRule(
        feature_name="MainBranch",
        source="resume",
        extraction_method="infer_from_experience_and_skills",
        required_for_model=True,
        allow_manual_input=True,
        notes=(
            "Infer whether the applicant is primarily a developer based on role titles, "
            "project language, and skills."
        ),
    ),
    "YearsCode": FeatureRule(
        feature_name="YearsCode",
        source="resume_or_user",
        extraction_method="estimate_from_dates_or_manual",
        required_for_model=True,
        allow_manual_input=True,
        notes=(
            "Estimate coding experience using education and experience dates when possible, "
            "otherwise allow manual entry."
        ),
    ),
    "YearsCodePro": FeatureRule(
        feature_name="YearsCodePro",
        source="resume_or_user",
        extraction_method="estimate_from_experience_dates",
        required_for_model=True,
        allow_manual_input=True,
        notes=(
            "Estimate professional coding experience from dated experience entries, with "
            "manual input as a fallback."
        ),
    ),
    "ComputerSkills": FeatureRule(
        feature_name="ComputerSkills",
        source="resume",
        extraction_method="count_recognized_skills",
        required_for_model=True,
        allow_manual_input=True,
        notes=(
            "Count recognized programming languages, frameworks, databases, tools, and "
            "platforms from the resume."
        ),
    ),
}


EDLEVEL_PATTERNS = [
    (
        re.compile(r"\bph\.?d\b|\bdoctorate\b", re.IGNORECASE),
        "PhD",
    ),
    (
        re.compile(
            r"\bmaster'?s\b|\bmaster of science\b|\bm\.?s\.?\b|\bmba\b",
            re.IGNORECASE,
        ),
        "Master",
    ),
    (
        re.compile(
            r"\bbachelor'?s\b|\bbachelor of science\b|\bbachelor of arts\b|"
            r"\bb\.?s\.?\b|\bb\.?a\.?\b",
            re.IGNORECASE,
        ),
        "Undergraduate",
    ),
    (
        re.compile(r"\bassociate'?s\b", re.IGNORECASE),
        "Other",
    ),
    (
        re.compile(r"\bhigh school\b", re.IGNORECASE),
        "NoHigherEd",
    ),
]


DEVELOPER_KEYWORDS = [
    "software engineer",
    "software developer",
    "developer",
    "full stack",
    "backend",
    "front end",
    "frontend",
    "web developer",
    "application developer",
    "programmer",
    "engineer",
]


SKILL_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "go",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "r",
    "sql",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node",
    "django",
    "flask",
    "spring",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "mongodb",
    "postgresql",
    "mysql",
    "redis",
    "spark",
    "hadoop",
    "tableau",
    "excel",
]


def print_feature_schema() -> None:
    for feature in MODEL_FEATURE_ORDER:
        rule = FEATURE_SCHEMA[feature]
        print(f"\n{rule.feature_name}")
        print(f"  source: {rule.source}")
        print(f"  extraction: {rule.extraction_method}")
        print(f"  required: {rule.required_for_model}")
        print(f"  manual input: {rule.allow_manual_input}")
        print(f"  notes: {rule.notes}")