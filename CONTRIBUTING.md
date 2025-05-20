# Contributing to Bugster CLI

This document outlines the development workflow for Bugster CLI.

## Development Workflow

### 1. Making Changes

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bugster-cli.git
   cd bugster-cli
   ```

2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Set up the development environment:
   ```bash
   ./dev.py setup
   ```

4. Make your changes to the codebase.

### 2. Testing Locally

1. Test your changes locally:
   ```bash
   ./dev.py test
   ```

2. Build a local executable to test the full distribution:
   ```bash
   ./dev.py build
   ```

3. Run the executable to make sure it works:
   ```bash
   ./dist/bugster --help
   ```

4. Alternatively, run all steps at once:
   ```bash
   ./dev.py all
   ```

### 3. Making a Release

1. Update the version number in `bugster/__init__.py`.

2. Commit your changes:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

3. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request on GitHub.

5. Once the PR is merged to main, create and push a tag to trigger the release workflow:
   ```bash
   git checkout main
   git pull
   git tag -a v0.1.1 -m "Release v0.1.1"
   git push origin v0.1.1
   ```

The GitHub Actions release workflow will automatically:
- Build executables for Windows, macOS, and Linux
- Create a GitHub release with these executables

### 4. Installing the Released Version

1. Install the latest released version:
   ```bash
   ./install_release.py
   ```

2. Install a specific version:
   ```bash
   ./install_release.py --version v0.1.0
   ```

## Continuous Integration

GitHub Actions automatically runs tests on:
- All pull requests to main
- All pushes to main

The CI workflow:
- Runs on multiple Python versions
- Confirms the CLI is operational 
- Will be expanded to include more comprehensive tests in the future

## Release Process

Releases are automated through GitHub Actions:

1. Pushing a tag with format `v*` (e.g., `v0.1.0`) triggers the release workflow
2. The workflow builds executables for all platforms
3. A GitHub Release is created with the executables attached
4. Users can download these executables directly or use the `install_release.py` script 