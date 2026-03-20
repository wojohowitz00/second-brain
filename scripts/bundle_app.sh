#!/bin/bash
set -e

APP_NAME="Second Brain"
BUILD_DIR="apps/apple/SecondBrain/.build/release"
APP_BUNDLE="dist/$APP_NAME.app"
ICON_SOURCE="resources/app_icon_source.png"
ICONSET_DIR="resources/icon.iconset"
ICNS_FILE="$APP_BUNDLE/Contents/Resources/icon.icns"

echo "Building Swift project..."
cd apps/apple/SecondBrain
swift build -c release -Xswiftc -DRELEASE
cd ../../..

echo "Creating App Bundle Structure..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

echo "Copying Executable..."
cp "$BUILD_DIR/SecondBrain" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

echo "Creating Info.plist..."
cat > "$APP_BUNDLE/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.richardyu.SecondBrain</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSUIElement</key>
    <true/> <!-- Menu Bar App -->
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

echo "Generating Icon..."
# Ensure iconset exists (assumes sips/iconutil are available or pre-generated)
if [ -d "$ICONSET_DIR" ]; then
    iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
else
    echo "Warning: Iconset not found in $ICONSET_DIR. Using generic icon."
fi

echo "Bundle created at $APP_BUNDLE"
