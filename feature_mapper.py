import re
from datetime import datetime

from resume_feature_schema import (
    DEVELOPER_KEYWORDS,
    EDLEVEL_PATTERNS,
    SKILL_KEYWORDS,
)

CURRENT_YEAR = datetime.now().year

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


# Education

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
        best_match = max(matches, key=lambda item: priority[item[1]])[1]
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


# Main branch

def infer_main_branch(sections: dict[str, str]):
    relevant_text = "\n".join(
        [
            sections.get("EXPERIENCE", ""),
            sections.get("SKILLS", ""),
            sections.get("FULL_TEXT", ""),
        ]
    ).lower()

    matches = [word for word in DEVELOPER_KEYWORDS if word in relevant_text]

    if matches:
        return "Dev", matches

    return "NotDev", matches


# Skills

def extract_computer_skills(sections: dict[str, str]):
    skills_text = "\n".join(
        [
            sections.get("SKILLS", ""),
            sections.get("PROJECTS", ""),
            sections.get("EXPERIENCE", ""),
            sections.get("FULL_TEXT", ""),
        ]
    ).lower()

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


# Experience

def month_str_to_num(month_str: str):
    return MONTHS.get(month_str.lower())


def estimate_years_code_pro(sections: dict[str, str]):
    experience_text = sections.get("EXPERIENCE", "") or sections.get("FULL_TEXT", "")

    if not experience_text.strip():
        return None, {"method": "no_experience_section", "details": []}

    details = []
    total_years = 0.0
    seen_entries = set()

    summer_years = re.findall(
        r"\bSummer\s+(20\d{2})\b",
        experience_text,
        flags=re.IGNORECASE,
    )

    for year in sorted(set(summer_years)):
        entry = f"Summer {year}"
        if entry not in seen_entries:
            total_years += 0.25
            details.append(f"{entry} -> 0.25")
            seen_entries.add(entry)

    repeated_year_lists = re.findall(r"(20\d{2}(?:,\s*20\d{2})+)", experience_text)

    for block in repeated_year_lists:
        years = re.findall(r"20\d{2}", block)
        for year in sorted(set(years)):
            entry = f"Listed year {year}"
            if year not in summer_years and entry not in seen_entries:
                total_years += 0.25
                details.append(f"{entry} -> 0.25")
                seen_entries.add(entry)

    year_ranges = re.findall(
        r"\b(20\d{2})\s*[–-]\s*(20\d{2}|Present)\b",
        experience_text,
        flags=re.IGNORECASE,
    )

    for start, end in year_ranges:
        entry = f"Range {start}-{end}"
        if entry in seen_entries:
            continue

        start_year = int(start)
        end_year = CURRENT_YEAR if end.lower() == "present" else int(end)
        span = max(0, end_year - start_year)

        if span > 0:
            total_years += span
            details.append(f"{entry} -> {span}")
            seen_entries.add(entry)

    month_pattern = (
        r"\b("
        r"January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|"
        r"August|Aug|September|Sep|Sept|October|Oct|November|Nov|December|Dec"
        r")\s+(20\d{2})\s*[–-]\s*("
        r"January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|"
        r"August|Aug|September|Sep|Sept|October|Oct|November|Nov|December|Dec|Present"
        r")\s*(20\d{2})?\b"
    )

    month_ranges = re.findall(month_pattern, experience_text, flags=re.IGNORECASE)

    for start_month, start_year, end_month, end_year in month_ranges:
        if end_month.lower() == "present":
            entry = f"{start_month} {start_year} - Present"
        else:
            entry = f"{start_month} {start_year} - {end_month} {end_year or start_year}"

        if entry in seen_entries:
            continue

        start_month_num = month_str_to_num(start_month)
        start_year_num = int(start_year)

        if end_month.lower() == "present":
            end_month_num = datetime.now().month
            end_year_num = CURRENT_YEAR
        else:
            end_month_num = month_str_to_num(end_month)
            end_year_num = int(end_year) if end_year else start_year_num

        if start_month_num and end_month_num:
            months = (end_year_num - start_year_num) * 12 + (
                end_month_num - start_month_num
            )
            years = max(0, round(months / 12, 2))

            if years > 0:
                total_years += years
                details.append(f"{entry} -> {years}")
                seen_entries.add(entry)

    total_years = round(total_years, 2)

    if total_years == 0:
        return None, {
            "method": "no_clear_professional_duration_found",
            "details": details,
        }

    return total_years, {
        "method": "rule_based_experience_estimate",
        "details": details,
    }


def estimate_years_code(sections: dict[str, str]):
    education_text = sections.get("EDUCATION", "")
    experience_text = sections.get("EXPERIENCE", "") or sections.get("FULL_TEXT", "")

    candidate_years = []
    details = []

    experience_years = [int(year) for year in re.findall(r"\b(20\d{2})\b", experience_text)]
    if experience_years:
        earliest_experience_year = min(experience_years)
        candidate_years.append(earliest_experience_year)
        details.append(f"earliest_experience_year={earliest_experience_year}")

    class_of_matches = re.findall(
        r"\bClass of\s*(20\d{2})\b",
        education_text,
        flags=re.IGNORECASE,
    )
    if class_of_matches:
        grad_year = min(int(year) for year in class_of_matches)
        inferred_college_start = grad_year - 4
        candidate_years.append(inferred_college_start)
        details.append(
            f"inferred_college_start={inferred_college_start} from class_year={grad_year}"
        )
    else:
        grad_matches = re.findall(
            r"\b(?:Graduation:|Graduated:|Expected:?)\s*(?:[A-Za-z]+\s+)?(20\d{2})\b",
            education_text,
            flags=re.IGNORECASE,
        )
        if grad_matches:
            grad_year = min(int(year) for year in grad_matches)
            inferred_college_start = grad_year - 4
            candidate_years.append(inferred_college_start)
            details.append(
                f"inferred_college_start={inferred_college_start} from grad_year={grad_year}"
            )
        else:
            education_years = [int(year) for year in re.findall(r"\b(20\d{2})\b", education_text)]
            plausible_grad_years = [year for year in education_years if year >= CURRENT_YEAR - 1]

            if plausible_grad_years:
                grad_year = min(plausible_grad_years)
                inferred_college_start = grad_year - 4
                candidate_years.append(inferred_college_start)
                details.append(
                    f"fallback_college_start={inferred_college_start} from edu_year={grad_year}"
                )

    if not candidate_years:
        return None, {"method": "insufficient_information", "details": details}

    chosen_start_year = min(candidate_years)
    years_code = max(0, CURRENT_YEAR - chosen_start_year)

    return years_code, {
        "method": "earliest_of_experience_or_college_start",
        "details": details,
        "chosen_start_year": chosen_start_year,
    }


# Output

def complete_feature_vector(sections: dict[str, str], manual_inputs: dict | None = None):
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

    for key, value in manual_inputs.items():
        if key in features and value is not None:
            features[key] = value
            metadata[key] = {"method": "manual_input", "value": value}

    return features, metadata