default:
    @just --list

update-deps:
    @echo "🚧 Updating deps..."
    python scripts/update_dependencies.py
    @echo "✅ Done!"

release-beta version:
    #!/usr/bin/env bash
    TAG="v{{version}}-beta"
    echo "🚀 Releasing... $TAG"
    git tag -a "$TAG" -m "Bugster CLI $TAG" && git push origin --tags
    echo "✅ Done!"