#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
ROOT_DIR="$(pwd)"

PYTHON_EXE="python3"
if [ -x ".venv/bin/python" ]; then
  PYTHON_EXE=".venv/bin/python"
fi

APP_NAME="CasaSerial"
DIST_DIR="MAC"
WORK_DIR="MAC/build"
SPEC_DIR="MAC/spec"
ICON_PNG="$ROOT_DIR/image/CASA_Serial_APP_ICON.png"
BUTTON_DATA="$ROOT_DIR/image/buttons"
FONT_DATA="$ROOT_DIR/Fonts"
UI_DATA="$ROOT_DIR/UI"
ICONSET_DIR="MAC/icon/CasaSerial.iconset"
ICON_ICNS="$ROOT_DIR/image/CasaSerial.icns"

if [ "${1:-}" = "--check" ]; then
  echo "Python command: \"$PYTHON_EXE\""
  echo "Build output: \"$DIST_DIR/$APP_NAME.app\""
  echo "Icon file: \"$ICON_ICNS\""
  echo "Runtime icon data: \"$ICON_PNG\""
  echo "Runtime button data: \"$BUTTON_DATA\""
  echo "Runtime font data: \"$FONT_DATA\""
  echo "Runtime UI data: \"$UI_DATA\""
  echo "Work path: \"$WORK_DIR\""
  echo "Spec path: \"$SPEC_DIR\""
  exit 0
fi

mkdir -p "$DIST_DIR" "$WORK_DIR" "$SPEC_DIR" "$ICONSET_DIR"

sips -z 16 16 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
sips -z 64 64 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"

"$PYTHON_EXE" -m PyInstaller \
  --noconfirm \
  --windowed \
  --clean \
  --name "$APP_NAME" \
  --icon "$ICON_ICNS" \
  --add-data "$ICON_PNG:image" \
  --add-data "$BUTTON_DATA:image/buttons" \
  --add-data "$FONT_DATA:Fonts" \
  --add-data "$UI_DATA:UI" \
  --distpath "$DIST_DIR" \
  --workpath "$WORK_DIR" \
  --specpath "$SPEC_DIR" \
  main.py

# macOS는 블루투스를 쓰는 앱에 사용 목적 문구(Info.plist)를 요구한다. 없으면 BLE 접근 시 앱이 종료된다.
INFO_PLIST="$DIST_DIR/$APP_NAME.app/Contents/Info.plist"
BT_TEXT="CasaSerial은 블루투스 장치(Nordic UART Service)에 연결하기 위해 블루투스를 사용합니다."
/usr/libexec/PlistBuddy -c "Delete :NSBluetoothAlwaysUsageDescription" "$INFO_PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :NSBluetoothAlwaysUsageDescription string $BT_TEXT" "$INFO_PLIST"
# Info.plist를 수정하면 서명이 깨지므로 ad-hoc 재서명한다.
codesign --force --deep --sign - "$DIST_DIR/$APP_NAME.app"

echo
echo "Build complete: $DIST_DIR/$APP_NAME.app"
