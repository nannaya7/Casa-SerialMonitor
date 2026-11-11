# 패키징 가이드

작성일: 2026-05-28

이 문서는 CasaSerial 기본 기능 검증이 끝난 뒤 PyInstaller로 Windows `.exe`와 macOS `.app`을 만드는 방법을 정리한다.

## 공통 준비

```powershell
pip install -r requirements.txt
pip install pyinstaller
python -m PyInstaller --version
```

패키징 전 기본 검증:

```powershell
python -m py_compile main.py settings.py serial_worker.py
cmd /c run.bat --check
```

## Windows exe

Windows 10/11에서 실행:

```powershell
.\build_win.bat
```

생성 결과:

- `WIN\CasaSerial\CasaSerial.exe`

수동 명령이 필요할 때:

```powershell
python -m PyInstaller --noconfirm --windowed --clean --name CasaSerial --icon "%CD%\image\CasaSerial.ico" --add-data "%CD%\image\CASA_Serial_APP_ICON.png;image" --add-data "%CD%\image\buttons;image\buttons" --add-data "%CD%\Fonts;Fonts" --distpath WIN --workpath WIN\build --specpath WIN\spec main.py
```

## macOS app

macOS에서 실행:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
chmod +x build_mac.sh
./build_mac.sh
```

생성 결과:

- `MAC/CasaSerial.app`

macOS 빌드 스크립트는 `image/CASA_Serial_APP_ICON.png`에서 `image/CasaSerial.icns`를 자동 생성한 뒤 앱 아이콘으로 사용한다. spec 파일 위치와 무관하게 동작하도록 아이콘/데이터/폰트 파일은 절대 경로로 PyInstaller에 전달한다.

macOS 빌드 중간 산출물은 `MAC/build`, `MAC/spec`, `MAC/icon` 아래에 생성된다.

## 주의사항

- Windows 패키지는 Windows에서, macOS 패키지는 macOS에서 각각 생성한다.
- 실제 시리얼 장치 연결, 포트 열기 실패, USB 제거, 송신/반복 송신은 패키징 후에도 다시 확인한다.
- 코드 서명, notarization, 설치 프로그램 생성은 기본 기능 검증이 끝난 뒤 별도 단계로 진행한다.
