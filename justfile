default:
    @just --list

update-deps:
    echo "🚧 Updating deps..."
    python scripts/update_dependencies.py