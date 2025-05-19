# Bugster CLI

A command-line interface tool for managing test cases.

## Installation

```bash
pip install bugster
```

## Usage

Initialize Bugster configuration:

```bash
bugster init
```

This will:

1. Create a `.bugster` directory in your current working directory
2. Set up configuration (base URL and optional credentials)
3. Create an example test case

## Development

To set up the development environment:

```bash
# Clone the repository
git clone <repository-url>
cd bugster-cli

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```
