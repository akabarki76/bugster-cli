# Contributing to Bugster CLI

Thank you for your interest in contributing to Bugster CLI! We welcome contributions from developers of all skill levels. This document provides guidelines and information needed to contribute effectively to our AI-powered end-to-end testing tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

Before contributing, ensure you have the following installed:

- **Python 3.10+**: Required for the CLI core functionality
- **Node.js 18+**: Required for Playwright browser automation  
- **Git 2.0+**: For version control
- **pip**: Python package manager (usually included with Python)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bugsterapp/bugster-cli.git
   cd bugster-cli
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   # Install additional development tools
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   # Install Playwright for testing
   npx playwright install
   ```

5. **Verify installation**
   ```bash
   # Test the CLI
   bugster --help
   ```

6. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug reports**: Help us identify and fix issues
- **Feature suggestions**: Propose new functionality
- **Code contributions**: Implement bug fixes or new features
- **Documentation improvements**: Enhance README, guides, or code comments
- **Testing**: Add or improve test coverage

### Before You Start

For significant changes:

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: Discuss your proposed changes before implementing
3. **Get feedback**: Wait for maintainer feedback before starting work

For minor changes (typos, small bug fixes), you can proceed directly to a pull request.

## Reporting Bugs

When reporting bugs, please include:

### System Information
```bash
# Include output of these commands:
bugster --version
python --version
node --version
uname -a  # On Windows: systeminfo
```

### Bug Report Template
```markdown
Bug Description
A clear description of what the bug is.


Command Executed
bugster command --with --flags

Expected Behavior
What you expected to happen.

Actual Behavior
What actually happened.

Error Output
Complete error message/stack trace

Steps to Reproduce
1. Run 'bugster init'
2. Execute 'bugster generate'
3. See error

Environment
- OS: [e.g., macOS 13.0, Windows 11, Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Node.js version: [e.g., 18.17.0]
- Bugster CLI version: [e.g., 0.3.7]

Additional Context
Any other relevant information.
```

## Suggesting Features

Feature requests should include:

- **Use case**: Describe the problem you're trying to solve
- **Proposed solution**: Your idea for addressing the use case
- **Alternatives considered**: Other solutions you've thought about
- **Implementation details**: Technical considerations (if applicable)

## Pull Request Process

### Before Submitting

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow code style guidelines** (see below)

3. **Update documentation** if needed

4. **Ensure clean commit history**
   ```bash
   # Use descriptive commit messages
   git commit -m "feat: add support for Vue.js framework detection"
   ```

### Commit Message Format

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(cli): add --max-concurrent option to run command"
git commit -m "fix(sync): resolve metadata consistency issue"
git commit -m "docs(readme): update installation instructions"
```

### Pull Request Requirements

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented)

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address review feedback promptly
4. Maintain clean commit history

## Code Style Guidelines

### Python Code Style

We use several tools to maintain code quality:

- **Ruff**: For linting and formatting
- **Pre-commit hooks**: Automated style checking

```bash
# Run linting
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### General Guidelines

- Use descriptive variable and function names
- Add docstrings for public functions and classes
- Keep functions focused and small
- Follow PEP 8 conventions
- Use type hints where appropriate

### Project Structure

```
bugster/
├── __init__.py          # Version and package info
├── cli.py              # Main CLI entry point
├── commands/           # Command implementations
├── libs/               # Core libraries
├── utils/              # Utility functions
├── clients/            # API and WebSocket clients
└── types.py            # Type definitions
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Use clear and concise comments
- Update README.md for user-facing changes
- Update CHANGELOG.md for releases

### Documentation Format

```python
def generate_test_cases(self) -> List[TestCase]:
    """Generate test cases for the given codebase analysis.
    
    This method analyzes the codebase structure and creates
    comprehensive test cases using AI-powered analysis.
    
    Returns:
        List[TestCase]: Generated test cases ready for execution
        
    Raises:
        BugsterError: If analysis fails or no test cases generated
    """
```

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check [docs.bugster.dev](https://docs.bugster.dev)

### Release Process

Bugster CLI follows semantic versioning (SemVer):

- **Major version** (1.0.0): Breaking changes
- **Minor version** (0.1.0): New features, backward compatible
- **Patch version** (0.0.1): Bug fixes, backward compatible

Development releases use the format: `v0.3.7-beta.1`

### Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation

## Legal

By contributing to Bugster CLI, you agree that:

- You are the original author of 100% of the content
- You have the legal right to contribute the content
- Your contributions are provided under the project's license
- You understand that contributions may be redistributed

---

Thank you for contributing to Bugster CLI! Your efforts help make AI-powered testing accessible to developers worldwide. 🐛✨