# SWE Resume Reviewer - Big Data Final Project

**Authors:** Owen Lee and Ben Schrager

## Overview

This project analyzes software engineering applicant data to predict hiring outcomes and provides a resume evaluation tool for aspiring software engineers. The project consists of two main components:

1. **Main Analysis Notebook** (`main_notebook.ipynb`): Comprehensive data analysis and model development
2. **Resume Reviewer Pipeline**: Automated tool to evaluate resumes and predict hiring likelihood

## Research Questions

**Primary:** Can we use applicant features to predict the likelihood that a software engineering applicant is hired?

**Supporting Questions:**
1. Which applicant features matter most in predicting hiring outcomes?
2. Can we turn the prediction into a simple resume-style evaluator for users?

## Key Findings

- **Best Model**: Logistic Regression outperforms Random Forest with better generalization
- **Most Important Features**: Years of coding experience (YearsCode, YearsCodePro) and previous salary
- **Fairness**: Including sensitive demographic attributes (gender, age) provides minimal accuracy gains but introduces measurable bias
- **Recommendation**: Use the baseline model without sensitive features for ethical deployment

## Project Structure

```
.
├── main_notebook.ipynb              # Main analysis notebook (START HERE)
├── stackoverflow_full.csv           # Training dataset
├── requirements.txt                 # Python dependencies
│
├── Resume Reviewer Pipeline:
├── train_resume_model.py            # Train the resume reviewer model
├── predict_resume.py                # Predict from PDF resumes
├── resume_parser.py                 # Extract text from PDFs
├── feature_mapper.py                # Map resume text to features
├── resume_feature_schema.py         # Feature definitions
├── resume_reviewer_model.joblib     # Pre-trained model
├── test_resumes/                    # Sample PDF resumes
│
└── Additional Files:
    ├── notebook.ipynb               # Earlier prototype notebook
    ├── NLP_Feature_Analysis_Data_Leakage_Report.txt
    └── data_leakage_visualization.png
```

## Requirements

- **Python**: 3.8 or higher (tested on Python 3.14.0)
- **Dependencies**: See `requirements.txt`

### Required Python Packages
- pandas, numpy (data manipulation)
- scikit-learn (machine learning)
- matplotlib, seaborn (visualization)
- shap (SHAP analysis for model interpretability)
- fairlearn (fairness metrics)
- pdfplumber (PDF text extraction)
- jupyter, notebook (for running notebooks)

## Installation

### 1. Clone or Navigate to the Project Directory

```bash
cd /path/to/Big-Data-Final-Project
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including Jupyter notebook support.

## Usage

### Running the Main Analysis Notebook

The main analysis is in `main_notebook.ipynb`. This is the primary deliverable and contains:

- Exploratory Data Analysis (EDA)
- Random Forest model development
- Logistic Regression model development
- SHAP analysis for interpretability
- Fairness analysis across demographic groups
- Conclusions and recommendations

**To run the notebook:**

```bash
# Start Jupyter Notebook
jupyter notebook main_notebook.ipynb
```

OR

```bash
# Start Jupyter Lab (alternative interface)
jupyter lab main_notebook.ipynb
```

Your browser should open automatically. If not, copy the URL from the terminal (usually `http://localhost:8888/...`).

**In the Jupyter interface:**
1. Click on `Cell` → `Run All` to execute all cells
2. Or run cells individually by pressing `Shift + Enter`

**Expected Runtime:** 2-5 minutes depending on your machine

**Requirements:**
- The notebook requires `stackoverflow_full.csv` to be in the same directory
- All visualizations will appear inline in the notebook

### Using the Resume Reviewer Pipeline

The resume reviewer allows you to evaluate PDF resumes and get hiring predictions.

#### Option 1: Quick Test with Pre-trained Model

```bash
# Predict on the default test resume
python3 predict_resume.py
```

This will analyze `test_resumes/BenSchragerResume.pdf` and output:
- Extracted features (education level, years of experience, skills)
- Predicted hiring probability
- Feature details

#### Option 2: Analyze Your Own Resume

Edit `predict_resume.py` and change the `RESUME_PATH` variable:

```python
RESUME_PATH = "path/to/your/resume.pdf"
```

Then run:

```bash
python3 predict_resume.py
```

#### Option 3: Retrain the Model

If you want to retrain the model with updated data:

```bash
# This will retrain and save the model as resume_reviewer_model.joblib
python3 train_resume_model.py
```

#### Resume Format Requirements

For best results, your resume PDF should include:
- **Education section** with degree information
- **Experience section** with dates (to calculate years of experience)
- **Skills section** with technical skills/programming languages

The parser looks for common section headers like:
- EDUCATION, EXPERIENCE, PROFESSIONAL EXPERIENCE, WORK EXPERIENCE
- SKILLS, TECHNICAL SKILLS
- PROJECTS, ACTIVITIES, LEADERSHIP

## Can This Project Be Run?

**YES** ✓ - This project is fully runnable with the following setup:

### Prerequisites Checklist

- [ ] Python 3.8+ installed (check with `python3 --version`)
- [ ] All dependencies installed (run `pip install -r requirements.txt`)
- [ ] `stackoverflow_full.csv` present in project directory
- [ ] Jupyter notebook installed for running `main_notebook.ipynb`

### What Works

1. **Main Notebook** (`main_notebook.ipynb`):
   - ✓ Fully self-contained analysis
   - ✓ All models train and evaluate successfully
   - ✓ Visualizations render correctly
   - ✓ SHAP and Fairlearn analyses work

2. **Resume Reviewer**:
   - ✓ Pre-trained model ready to use (`resume_reviewer_model.joblib`)
   - ✓ Can analyze any PDF resume
   - ✓ Can retrain model with updated data
   - ✓ Test resumes included in `test_resumes/` directory

### Known Limitations

1. **Resume Parsing**: Works best with well-structured resumes that follow standard formatting
2. **Feature Extraction**: Uses regex-based parsing; may not capture all resume variations
3. **Model Accuracy**: Model is trained on StackOverflow survey data, which may not perfectly represent all hiring scenarios
4. **PDF Format**: Requires text-based PDFs (not scanned images)

## Troubleshooting

### Jupyter Not Found

```bash
# Install Jupyter
pip install jupyter notebook
```

### Import Errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade
```

### PDF Parsing Errors

If you get errors about PDF parsing:
```bash
# Reinstall pdfplumber
pip install pdfplumber --upgrade
```

### SHAP Visualization Issues

If SHAP plots don't render:
```bash
# Install latest SHAP version
pip install shap --upgrade
```

## Model Performance

### Logistic Regression (Recommended Model)
- **Accuracy**: ~0.74
- **F1 Score**: ~0.80
- **ROC-AUC**: ~0.80

### Feature Importance (Top 5)
1. YearsCodePro (Professional coding years)
2. YearsCode (Total coding years)
3. PreviousSalary
4. EdLevel (Education level)
5. MainBranch (Professional developer status)

## Ethical Considerations

This project demonstrates the importance of fairness in hiring algorithms:

- Adding demographic features (gender, age) introduces bias without improving accuracy
- The baseline model (without sensitive attributes) is recommended for deployment
- This tool should be used as **decision support**, not automated screening
- Human review and judgment remain essential in hiring decisions

## Citation

Data Source: StackOverflow Developer Survey
Contributors: Code & Read-Me Generation Assisted with Anthropic Claude

## License

This project is for educational purposes as part of a Big Data course final project.

## Contact

- Owen Lee
- Ben Schrager

---

**Last Updated:** May 2025
