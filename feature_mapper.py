import re
from datetime import datetime

from resume_feature_schema import EDLEVEL_PATTERNS, DEVELOPER_KEYWORDS, SKILL_KEYWORDS


CURRENT_YEAR = datetime.now().year


def extract_edlevel(sections: dict[str, str]):
    education_text = sections.get("EDUCATION", "")
    education_lower = education_text.lower()

    matches = []
    for pattern, mapped_value in EDLEVEL_PATTERNS:
        if pattern.search(education_text):
            matches.append((pattern.pattern, mapped_value))

    if matches:
        priority = {
            "NoHigherEd": 0,
            "Other": 1,
            "Undergraduate": 2,
            "Master": 3,
            "PhD": 4,
        }
        best_match = max(matches, key=lambda x: priority[x[1]])[1]
        return best_match, matches

    undergraduate_signals = [
        "university",
        "college",
        "school of engineering",
        "class of",
        "major",
        "majors:",
    ]

    if any(signal in education_lower for signal in undergraduate_signals):
        return "Undergraduate", [("fallback_undergraduate_inference", "Undergraduate")]

    return None, []


def infer_main_branch(sections: dict[str, str]):
    relevant_text = "\n".join([
        sections.get("PROFESSIONAL EXPERIENCE", ""),
        sections.get("EXPERIENCE", ""),
        sections.get("WORK EXPERIENCE", ""),
        sections.get("SKILLS", ""),
        sections.get("TECHNICAL SKILLS", ""),
    ]).lower()

    matches = [word for word in DEVELOPER_KEYWORDS if word in relevant_text]

    if matches:
        return "Dev", matches
    return "NotDev", matches


def extract_computer_skills(sections: dict[str, str]):
    skills_text = "\n".join([
        sections.get("SKILLS", ""),
        sections.get("TECHNICAL SKILLS", ""),
        sections.get("PROJECTS", ""),
        sections.get("PROFESSIONAL EXPERIENCE", ""),
        sections.get("EXPERIENCE", ""),
    ]).lower()

    found_skills = []

    for skill in SKILL_KEYWORDS:
        if skill == "r":
            pattern = r"(?<![a-zA-Z])r(?![a-zA-Z])"
        elif skill in {"c++", "c#"}:
            pattern = re.escape(skill)
        else:
            pattern = rf"\b{re.escape(skill)}\b"

        if re.search(pattern, skills_text, flags=re.IGNORECASE):
            found_skills.append(skill)

    found_skills = sorted(set(found_skills))
    return len(found_skills), found_skills


def estimate_years_code_pro(sections: dict[str, str]):
    """
    Roughly estimate YearsCodePro from experience section year mentions.

    Assumptions:
    - 'Summer YYYY' counts as about 0.25 years
    - a listed standalone year counts as about 0.25 years if it appears in a repeated summer pattern
    - a range like 2018 - 2022 counts as full-year span
    """
    exp_text = "\n".join([
        sections.get("PROFESSIONAL EXPERIENCE", ""),
        sections.get("EXPERIENCE", ""),
        sections.get("WORK EXPERIENCE", ""),
    ])

    if not exp_text.strip():
        return None, {"method": "no_experience_section", "details": []}

    details = []
    total_years = 0.0

    # Count "Summer YYYY"
    summer_years = re.findall(r"\bSummer\s+(20\d{2})\b", exp_text, flags=re.IGNORECASE)
    for year in set(summer_years):
        total_years += 0.25
        details.append(f"Summer {year} -> 0.25")

    # Count explicit repeated standalone years in lists like "2021, 2022, 2023"
    repeated_year_lists = re.findall(r"(20\d{2}(?:,\s*20\d{2})+)", exp_text)
    for block in repeated_year_lists:
        years = re.findall(r"20\d{2}", block)
        for year in set(years):
            if year not in summer_years:
                total_years += 0.25
                details.append(f"Listed year {year} -> 0.25")

    # Count ranges like 2018 - 2022
    ranges = re.findall(r"\b(20\d{2})\s*[–-]\s*(20\d{2}|Present)\b", exp_text, flags=re.IGNORECASE)
    for start, end in ranges:
        start_year = int(start)
        end_year = CURRENT_YEAR if end.lower() == "present" else int(end)
        span = max(0, end_year - start_year)
        total_years += span
        details.append(f"Range {start}-{end} -> {span}")

    total_years = round(total_years, 2)

    if total_years == 0:
        return None, {"method": "no_clear_professional_duration_found", "details": details}

    return total_years, {"method": "rule_based_experience_estimate", "details": details}


def estimate_years_code(sections: dict[str, str]):

    """

    Estimate total years coding as:

    current year - earlier of

    (a) earliest professional experience year

    (b) inferred college start year = graduation/class year - 4

    If neither is available, return None.

    """

    education_text = sections.get("EDUCATION", "")

    experience_text = "\n".join([

        sections.get("PROFESSIONAL EXPERIENCE", ""),

        sections.get("EXPERIENCE", ""),

        sections.get("WORK EXPERIENCE", ""),

    ])

    candidate_years = []

    details = []

    # Earliest year from experience

    exp_years = [int(y) for y in re.findall(r"\b(20\d{2})\b", experience_text)]

    if exp_years:

        earliest_exp_year = min(exp_years)

        candidate_years.append(earliest_exp_year)

        details.append(f"earliest_experience_year={earliest_exp_year}")

    # Graduation/class year from education, then subtract 4

    grad_matches = re.findall(r"\b(?:Class of|Graduated:?)\s*(20\d{2})\b", education_text, flags=re.IGNORECASE)

    if grad_matches:

        grad_year = min(int(y) for y in grad_matches)

        inferred_college_start = grad_year - 4

        candidate_years.append(inferred_college_start)

        details.append(f"inferred_college_start={inferred_college_start} from grad_year={grad_year}")

    else:

        # fallback: any year in education section that looks like a future class year

        edu_years = [int(y) for y in re.findall(r"\b(20\d{2})\b", education_text)]

        plausible_grad_years = [y for y in edu_years if y >= CURRENT_YEAR - 1]

        if plausible_grad_years:

            grad_year = min(plausible_grad_years)

            inferred_college_start = grad_year - 4

            candidate_years.append(inferred_college_start)

            details.append(f"fallback_college_start={inferred_college_start} from edu_year={grad_year}")

    if not candidate_years:

        return None, {"method": "insufficient_information", "details": details}

    earliest_start = min(candidate_years)

    years_code = max(0, CURRENT_YEAR - earliest_start)

    return years_code, {

        "method": "earliest_of_experience_or_college_start",

        "details": details,

        "chosen_start_year": earliest_start,

    }


def complete_feature_vector(sections: dict[str, str], manual_inputs: dict | None = None):
    """
    Build a complete feature vector for the model.
    manual_inputs can override or fill missing values.
    """
    manual_inputs = manual_inputs or {}

    edlevel, edlevel_meta = extract_edlevel(sections)
    main_branch, main_branch_meta = infer_main_branch(sections)
    computer_skills, skills_meta = extract_computer_skills(sections)
    years_code_pro, years_code_pro_meta = estimate_years_code_pro(sections)
    years_code, years_code_meta = estimate_years_code(sections)
    
    features = {
        "EdLevel": edlevel,
        "MainBranch": main_branch,
        "YearsCode": years_code,
        "YearsCodePro": years_code_pro,
        "ComputerSkills": computer_skills,
    }

    metadata = {
        "EdLevel": edlevel_meta,
        "MainBranch": main_branch_meta,
        "YearsCode": years_code_meta,
        "YearsCodePro": years_code_pro_meta,
        "ComputerSkills": skills_meta,
    }

    # Fill from manual inputs when provided
    for key, value in manual_inputs.items():
        if key in features and value is not None:
            features[key] = value
            metadata[key] = {"method": "manual_input", "value": value}

    return features, metadata