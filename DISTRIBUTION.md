# Distributing Bugster CLI

This document explains how to build and distribute the Bugster CLI executable using PyInstaller.

## Prerequisites

- Python 3.7 or higher
- PyInstaller (`pip install pyinstaller`)

## Building the Executable

### Option 1: Using the build script

1. Run the build script:
   ```
   ./build.py
   ```
   
2. The executable will be created in the `dist/bugster` directory.

### Option 2: Manual build with PyInstaller

1. Run PyInstaller with the spec file:
   ```
   pyinstaller bugster.spec --clean
   ```

2. The executable will be created in the `dist/bugster` directory.

## Distribution Options

### Option 1: Standalone Executable

For simple distribution, you can share just the executable file:
- macOS/Linux: `dist/bugster/bugster`
- Windows: `dist\bugster\bugster.exe`

### Option 2: Bundled Distribution

For more reliable distribution, share the entire `dist/bugster` directory, which includes all dependencies.

### Option 3: Installer Package (Advanced)

For a more professional distribution:

- **Windows**: Use tools like NSIS or Inno Setup to create an installer.
- **macOS**: Create a DMG file or use tools like `pkgbuild` to create a package installer.
- **Linux**: Create a `.deb` or `.rpm` package for different distributions.

## Platform-specific Notes

### macOS

On macOS, you might need to sign the application for distribution outside the App Store:

```bash
codesign --sign "Developer ID Application: Your Name" dist/bugster/bugster
```

### Windows

On Windows, consider using UPX (included with PyInstaller) to compress the executable:

```
pyinstaller bugster.spec --clean --upx-dir=path\to\upx
```

### Linux

For Linux, make sure the executable has proper permissions:

```bash
chmod +x dist/bugster/bugster
``` 