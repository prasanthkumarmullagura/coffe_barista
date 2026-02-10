# Contributing to Barista Queue System

## 🤝 Collaboration Workflow

This project follows a standard Feature Branch Workflow. Please follow these steps to contribute.

### 1. Structure
- **`main`**: Production-ready code. NEVER push directly to main.
- **`feature/*`**: New features (e.g., `feature/dashboard`, `feature/analytics`).
- **`bugfix/*`**: Bug fixes (e.g., `bugfix/simulation-crash`).

### 2. Step-by-Step Cycle

#### Step 1: Get Latest Code
Always start by syncing with the remote repository:
```bash
git checkout main
git pull origin main
```

#### Step 2: Create a Branch
Create a branch for your specific task:
```bash
# Sudo-code: git checkout -b <type>/<short-description>
git checkout -b feature/streamlit-dashboard
```

#### Step 3: Work & Commit
Make your changes. Keep commits small and descriptive.
```bash
git add .
git commit -m "Add initial Streamlit layout"
```

#### Step 4: Push to GitHub
Push your branch to the remote repository:
```bash
git push -u origin feature/streamlit-dashboard
```

#### Step 5: Create Pull Request (PR)
1. Go to GitHub repo.
2. Click "Compare & pull request".
3. Assign a reviewer (e.g., Team Lead).
4. Description should include "What changed" and "Why".

#### Step 6: Code Review & Merge
- Reviewer checks code.
- Once approved, merge into `main`.
- Delete the feature branch.

### 3. Code Style Guidelines
- **Python**: Follow PEP 8.
- **Comments**: Document complex logic (like priority weights).
- **Tests**: Run `python -m unittest discover tests` before pushing.

---
**"We are not just writing code; we are building a product together."**
