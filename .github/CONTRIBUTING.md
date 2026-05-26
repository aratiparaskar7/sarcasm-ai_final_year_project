# Contributing to SarcasmAI

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and constructive
- Avoid offensive language
- Help each other learn and improve
- Give credit to others' ideas and work

## Getting Started

### 1. Fork the Repository

Click the **Fork** button on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai
```

### 3. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cd sarcasm_detect
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
```

### 4. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-toxicity-detection`
- `fix/improve-model-accuracy`
- `docs/update-api-reference`
- `test/add-audio-tests`

## Making Changes

### Code Style

- **Python**: Follow [PEP 8](https://pep8.org/)
- **Naming**: Use descriptive names (no single letters except i, j, k in loops)
- **Comments**: Only when non-obvious
- **Imports**: Group (standard library, third-party, local)

### Example

```python
# Good
def analyze_sentiment(text, threshold=0.5):
    """Analyze text sentiment using transformer model."""
    scores = model.predict(text)
    return scores > threshold

# Bad
def a(t):  # unclear variable names
    s = model.predict(t)  # no docstring
    return s > 0.5
```

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR

```bash
python manage.py test analyzer
```

### Documentation

- Update docstrings for functions/classes
- Update README if adding features
- Update API.md if modifying endpoints

## Commit Guidelines

### Commit Message Format

```
[type] Brief description (under 50 chars)

Longer explanation of what changed and why.
Keep lines under 72 characters.

Related issues: Closes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Build, dependencies

### Examples

```bash
git commit -m "feat: Add support for PDF text extraction"
git commit -m "fix: Correct CLIP image preprocessing"
git commit -m "docs: Update installation guide for M1 Macs"
```

## Submitting a Pull Request

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request

- Go to https://github.com/sarcasm-ai/sarcasm-ai
- Click **New Pull Request**
- Select your branch
- Fill in the template:

```markdown
## Description
Brief explanation of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update

## How to Test
Steps to verify the changes work

## Screenshots (if applicable)
Add relevant screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass (`python manage.py test`)
- [ ] Documentation updated
- [ ] No new warnings generated
```

### 3. Address Review Feedback

Make requested changes and push again:

```bash
# Make changes
git add .
git commit -m "Address review feedback"
git push origin feature/your-feature-name
```

## Areas for Contribution

### High Priority
- [ ] Improve model accuracy
- [ ] Add more test coverage
- [ ] Optimize inference speed
- [ ] Improve documentation
- [ ] Fix reported bugs

### Medium Priority
- [ ] Add new ML models
- [ ] Improve UI/UX
- [ ] Add more languages
- [ ] Performance optimization
- [ ] Security improvements

### Low Priority
- [ ] Code refactoring
- [ ] Add comments
- [ ] Update examples
- [ ] Typo fixes

## Development Tips

### Running Specific Tests

```bash
# Run all analyzer tests
python manage.py test analyzer

# Run specific test class
python manage.py test analyzer.tests.TextAnalyzerTest

# Run specific test method
python manage.py test analyzer.tests.TextAnalyzerTest.test_irony_detection

# Verbose output
python manage.py test analyzer -v 2
```

### Debugging

```bash
# Django shell
python manage.py shell

>>> from analyzer.ml.text_analyzer import TextAnalyzer
>>> analyzer = TextAnalyzer()
>>> analyzer.predict("Oh great, another meeting")

# Run with print debugging
python manage.py runserver --pdb
```

### Performance Testing

```bash
import time
from analyzer.ml.text_analyzer import TextAnalyzer

analyzer = TextAnalyzer()
start = time.time()
result = analyzer.predict("Test text")
print(f"Inference time: {time.time() - start:.2f}s")
```

## Common Issues

### Tests Fail Locally

```bash
# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +
python manage.py test analyzer
```

### Import Errors

```bash
# Ensure you're in correct directory
cd sarcasm_detect

# Verify virtual environment
source venv/bin/activate
which python  # Should show venv path
```

### Model Download Issues

```bash
# Delete cache and re-download
rm -rf ~/.cache/huggingface/
python manage.py shell
>>> from analyzer.ml.text_analyzer import TextAnalyzer
>>> TextAnalyzer().predict("test")
```

## Review Process

1. **Automated Checks**: Tests must pass
2. **Code Review**: Maintainers review changes
3. **Feedback**: Requests for modifications
4. **Approval**: Ready to merge
5. **Merge**: Changes integrated

## License

By contributing, you agree your code is licensed under MIT license (same as project).

## Questions?

- Check existing [GitHub Issues](https://github.com/sarcasm-ai/sarcasm-ai/issues)
- Start a [Discussion](https://github.com/sarcasm-ai/sarcasm-ai/discussions)
- Open a new Issue for bugs/features

---

**Thank you for contributing!** ❤️

---

**Last Updated**: 2026-05-26
