# Quick Start Guide

Get the project running in under 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd "/Users/owenlee/Documents/Abroad/Big Data/Big-Data-Final-Project"

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

## Step 2: Choose What to Run

### Option A: Run the Main Analysis Notebook (Recommended for first-time users)

```bash
# Start Jupyter Notebook
jupyter notebook main_notebook.ipynb
```

Then in your browser:
- Click `Cell` → `Run All` to execute the entire analysis
- Wait 2-5 minutes for completion
- Explore the visualizations and results!

### Option B: Test the Resume Reviewer

```bash
# Analyze a test resume with the pre-trained model
python3 predict_resume.py
```

You should see output like:
```
Resume reviewer
Resume: test_resumes/BenSchragerResume.pdf
Text length: XXXX
Sections: EDUCATION, EXPERIENCE, SKILLS, ...

Features
- EdLevel: Bachelor's degree
- MainBranch: I am a developer by profession
- YearsCode: X
- YearsCodePro: X
- ComputerSkills: X

Prediction
- Class: 1
- Hire probability: 0.XXXX
- Threshold: above/below default cutoff
```

## Step 3: Verify Everything Works

Run this quick check:

```bash
python3 -c "
import pandas as pd
import sklearn
import shap
import fairlearn
import pdfplumber
print('✓ All packages installed successfully!')
print('✓ Ready to run the project!')
"
```

## Troubleshooting

### If you see "command not found: jupyter"

```bash
pip install jupyter notebook --upgrade
```

### If you see "ModuleNotFoundError"

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### If Jupyter won't start

```bash
# Try Jupyter Lab instead
pip install jupyterlab
jupyter lab main_notebook.ipynb
```

## What's Next?

1. **Explore the notebook**: Read through the analysis, understand the models, and check out the visualizations
2. **Try your own resume**: Edit `predict_resume.py` to point to your resume PDF
3. **Retrain the model**: Run `python3 train_resume_model.py` to see the training process
4. **Read the full README**: Check `README.md` for detailed documentation

## Key Files

- `main_notebook.ipynb` - The main analysis (START HERE)
- `stackoverflow_full.csv` - Training data
- `resume_reviewer_model.joblib` - Pre-trained model
- `predict_resume.py` - Resume evaluation script
- `test_resumes/` - Sample resumes to test with

---

**Need help?** Check the full README.md or the troubleshooting section!
