# Copilot Instructions for Projeto Integrador - Aprendizado Supervisionado

## Repository Overview

This repository contains a supervised learning (Aprendizado Supervisionado) project focused on implementing machine learning algorithms and models. The project is part of an integrated course project (Projeto Integrador).

## Technology Stack

- **Primary Language**: Python
- **Domain**: Machine Learning / Supervised Learning
- **Package Management**: pip (Python package manager)

## Project Structure

```
.
├── .github/              # GitHub configuration and workflows
├── .gitignore           # Git ignore patterns (Python-specific)
└── README.md            # Project documentation
```

## Development Guidelines

### Code Style and Conventions

- Follow PEP 8 style guidelines for Python code
- Use descriptive variable and function names in English or Portuguese (match existing codebase convention)
- Add docstrings to functions and classes following the existing pattern
- Keep functions focused and modular

### Python Best Practices

- Use virtual environments for dependency isolation
- Keep dependencies up to date and documented
- Write type hints where appropriate
- Handle exceptions appropriately
- Add comments for complex logic

### Machine Learning Specific Guidelines

- Document model architectures and hyperparameters clearly
- Include data preprocessing steps in code comments
- Save trained models with versioning
- Document evaluation metrics and results
- Include data validation checks

### Testing

- Write unit tests for utility functions
- Test data preprocessing pipelines
- Validate model inputs and outputs
- Include edge case testing

### Git Workflow

- Write clear, descriptive commit messages
- Keep commits atomic and focused
- Reference issue numbers in commits when applicable

## File Organization

### Python Files
- Keep machine learning models in dedicated modules
- Separate data processing from model training
- Use clear naming conventions for scripts (e.g., `train_model.py`, `preprocess_data.py`)

### Notebooks
- If using Jupyter notebooks, keep them well-documented
- Clear all outputs before committing to avoid large diffs
- Use markdown cells to explain steps

### Data Files
- Do not commit large datasets
- Document data sources and how to obtain them
- Include sample data if needed for testing

## Dependencies

- Always update `requirements.txt` when adding new packages
- Pin versions for reproducibility
- Check for security vulnerabilities in dependencies

## Documentation

- Keep README.md up to date with project changes
- Document API interfaces
- Include setup and installation instructions
- Provide usage examples

## Common Tasks

### Setting Up the Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Code
- Execute Python scripts from the repository root
- Use consistent paths for data and model files

## Notes for Copilot

- Prioritize code clarity and maintainability
- Follow existing patterns in the repository
- Ask for clarification if the task is ambiguous
- Consider edge cases and error handling
- Ensure changes are minimal and focused on the task at hand
