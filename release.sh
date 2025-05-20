#!/bin/bash
# This script updates the version in __init__.py, creates a git tag, and pushes changes
# Usage: ./release.sh 0.1.8

set -e  # Exit on error

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Error: Version argument is missing"
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 0.1.8"
    exit 1
fi

VERSION="$1"

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version should be in format X.Y.Z (e.g., 0.1.8)"
    exit 1
fi

echo "=========================================="
echo "Starting release process for v$VERSION"
echo "=========================================="

# Find the __init__.py file in the project
INIT_FILE=$(find . -name "__init__.py" -not -path "*/\.*" -not -path "*/venv/*" | head -n 1)

if [ -z "$INIT_FILE" ]; then
    echo "Error: __init__.py file not found"
    exit 1
fi

echo "Updating version in $INIT_FILE"

# Check if the file has a version defined
if grep -q "__version__" "$INIT_FILE"; then
    # Update existing version
    sed -i.bak "s/__version__ = \"[0-9.]*\"/__version__ = \"$VERSION\"/" "$INIT_FILE"
else
    # Add version if not present
    echo "" >> "$INIT_FILE"
    echo "__version__ = \"$VERSION\"" >> "$INIT_FILE"
fi

rm -f "$INIT_FILE.bak" 2>/dev/null || true

echo "Version updated to $VERSION"

# Stage the changes
git add "$INIT_FILE"

# Commit the changes
git commit -m "Bump version to v$VERSION"

# Create an annotated tag
echo "Creating git tag v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes and tags
echo "Pushing changes and tags to remote"
git push origin
git push origin --tags

echo "=========================================="
echo "Release v$VERSION completed successfully"
echo "=========================================="
echo "GitHub Actions will now build and release the binaries"
echo "The release will be available at:"
echo "https://github.com/Bugsterapp/bugster-cli/releases/tag/v$VERSION"
echo "==========================================" 