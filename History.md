# 개발 이력

## 2026-05-27 - 1단계: 프로젝트 뼈대

변경 파일:

- `main.py`
- `requirements.txt`

핵심 변경 사항:

- PyQt6 기반의 초기 애플리케이션 뼈대를 생성했다.
- `QMainWindow` 기반 `CasaSerialWindow` 클래스를 추가했다.
- 창 제목을 `CasaSerial`로 설정했다.
- 기본 창 크기를 `1024x768`로 설정했다.
- `Session`, `View`, `Help` 메뉴를 추가했다.
- 상태바를 추가하고 초기 메시지를 `Ready`로 설정했다.
- 프로젝트 의존성으로 `PyQt6`, `pyserial`을 기록했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 PyQt6 기본 창 생성 검증 통과

다음 단계 메모:

- 상단 툴바, 중앙 로그 영역, 하단 Send dialog 패널을 포함한 목표 UI 레이아웃을 구현한다.

## 2026-05-27 - 2단계: 목표 UI 레이아웃

변경 파일:

- `main.py`

핵심 변경 사항:

- 상단 툴바를 추가했다.
- 중앙 `QPlainTextEdit` 로그 영역을 추가했다.
- 하단 Send dialog 패널을 추가했다.
- Port, Baudrate, Databits, Parity, Flow control, Stopbits 설정 UI를 추가했다.
- 명령 입력창, Send 버튼, Send file 버튼, 데이터 포맷 라디오 버튼, 반복 송신 컨트롤, Start loop 버튼을 추가했다.
- 상태바에 연결 상태, 현재 포트, RX 바이트 수, TX 바이트 수 표시 영역을 추가했다.
- 해상도와 창 크기 변화에 대응하도록 Qt 레이아웃, stretch factor, size policy를 사용했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 2단계 UI 생성 및 초기 상태 검증 통과

다음 단계 메모:

- `serial.tools.list_ports.comports()`를 사용하여 시리얼 포트 스캔 기능을 구현한다.
- 포트가 없을 때와 포트가 감지되었을 때의 UI 상태 전환을 함께 처리한다.

## 2026-05-27 - 2단계 보완: 반응형 레이아웃 개선

변경 파일:

- `main.py`

핵심 변경 사항:

- 중앙 로그 영역과 하단 Send dialog 패널을 `QSplitter` 기반 구조로 변경했다.
- 하단 Send dialog 패널을 `QScrollArea` 안에 배치하여 작은 창에서도 컨트롤이 잘리지 않도록 보완했다.
- 하단 패널에 최소 크기를 설정하고, 넓은 화면에서는 가로 공간을 자연스럽게 사용하도록 size policy를 조정했다.
- 창 크기 변경 시 로그 영역이 주로 확장되고, 하단 패널은 필요한 경우 스크롤로 접근할 수 있게 했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 반응형 레이아웃 검증 통과
- `760x520`, `1024x768`, `1600x900` 크기에서 주요 UI 위젯 생성과 크기 변경 동작을 확인했다.

다음 단계 메모:

- 3단계에서 포트 스캔 기능을 추가할 때 포트 목록 갱신 후에도 반응형 레이아웃이 깨지지 않는지 함께 확인한다.

## 2026-05-27 - 실행 스크립트 추가

변경 파일:

- `run.bat`
- `History.md`

핵심 변경 사항:

- Windows에서 앱을 쉽게 실행할 수 있도록 `run.bat` 파일을 추가했다.
- 현재 폴더로 이동한 뒤 `.venv\Scripts\python.exe`가 있으면 가상환경의 Python으로 실행한다.
- 가상환경이 없으면 시스템 `python`으로 `main.py`를 실행한다.
- 실행 오류가 발생하면 `pip install -r requirements.txt` 안내를 표시한다.

검증 결과:

- 배치 파일 생성 완료

다음 단계 메모:

- 3단계 구현 전 필요한 경우 `requirements.txt` 설치 후 `run.bat`으로 GUI 실행을 확인한다.

## 2026-05-27 - 실행 스크립트 오류 수정

변경 파일:

- `run.bat`
- `History.md`

핵심 변경 사항:

- `cmd.exe`에서 배치 파일이 잘못 파싱되는 문제를 줄이기 위해 괄호 블록 구조를 제거했다.
- 배치 파일 메시지를 ASCII로 정리하여 Windows 콘솔 인코딩 문제를 피했다.
- `.venv\Scripts\python.exe`가 있으면 해당 Python을 사용하고, 없으면 시스템 `python`을 사용하도록 단순화했다.
- `run.bat --check` 옵션을 추가하여 실제 GUI를 띄우지 않고 사용할 Python 명령을 확인할 수 있게 했다.
- 배치 파일 줄바꿈을 CRLF로 변환했다.

검증 결과:

- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 실제 실행은 `.\run.bat`으로 확인한다.
- 패키지가 없으면 `pip install -r requirements.txt` 실행 후 다시 시도한다.

## 2026-05-27 - 3단계: 시리얼 포트 스캔

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- `serial.tools.list_ports.comports()`를 사용한 시리얼 포트 스캔 기능을 추가했다.
- 앱 시작 시 자동으로 포트 목록을 스캔하도록 연결했다.
- `Session > Refresh Ports` 메뉴를 추가했다.
- 상단 툴바에 `Refresh Ports` 액션을 추가하여 수동 재스캔이 가능하게 했다.
- 포트가 없으면 Port 콤보박스에 `no serial ports detected`를 표시하고 `Open` 버튼을 비활성화한다.
- 포트가 감지되면 Port 콤보박스에 장치명과 설명을 표시하고, 실제 device 값은 콤보박스 item data로 보관한다.
- 스캔 실패 시 앱이 종료되지 않고 상태바에 오류 메시지를 표시하도록 처리했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 3단계 포트 스캔 검증 통과
- 포트 없음, 포트 있음, 스캔 실패 케이스를 mock 데이터로 검증했다.

다음 단계 메모:

- 4단계에서 UI 설정값을 pyserial 설정값으로 변환하는 매핑 함수를 구현한다.
- baudrate 직접 입력값 검증과 parity/stopbits/flow control 매핑을 추가한다.

## 2026-05-27 - 3단계 보완: 포트 자동 갱신

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- 앱 실행 후 USB 시리얼 장치를 연결했을 때 포트 목록이 자동으로 갱신되도록 `QTimer` 기반 주기 스캔을 추가했다.
- 포트 목록은 2초마다 확인하되, 변경이 있을 때만 콤보박스를 갱신하도록 처리했다.
- 수동 `Refresh Ports`는 항상 강제 갱신하도록 유지했다.
- 포트가 사라지면 `no serial ports detected` 상태와 `Open` 버튼 비활성화 상태로 돌아가도록 했다.
- Windows의 `COM3`, `COM10` 같은 포트가 자연스러운 순서로 정렬되도록 정렬 키를 보완했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 자동 포트 갱신 검증 통과
- 앱 실행 후 포트가 새로 생기는 상황, 포트가 사라지는 상황, `COM3`/`COM10` 정렬을 mock 데이터로 검증했다.

다음 단계 메모:

- 실제 장치 연결 테스트에서 USB 연결 후 최대 2초 안에 Port 콤보박스가 갱신되는지 확인한다.
- 4단계에서는 포트 선택값과 통신 설정값을 pyserial 설정값으로 변환하는 로직을 구현한다.

## 2026-05-27 - 가이드 문서 보완: 포트 자동 갱신 요구사항 반영

변경 파일:

- `ai_collaboration_serial_monitor_guide.md`
- `History.md`

핵심 변경 사항:

- 앱 실행 중 USB 시리얼 장치 연결/해제 시 포트 목록 자동 갱신을 MVP 요구사항에 추가했다.
- 기존에 3차 기능으로 분류했던 플러그/언플러그 자동 감지는 포트 자동 갱신과 고급 장치 필터링으로 역할을 분리했다.
- 3단계 포트 스캔 프롬프트에 `QTimer` 기반 2초 주기 자동 스캔 요구사항을 추가했다.
- 포트 목록이 바뀐 경우에만 콤보박스를 갱신해야 한다는 조건을 추가했다.
- `COM3`, `COM10` 같은 Windows 포트의 자연스러운 숫자 정렬 요구사항을 추가했다.
- 전체 검증 체크리스트에 앱 실행 후 USB 연결/제거 시 목록과 버튼 상태가 갱신되는지 확인하는 항목을 추가했다.

검증 결과:

- 가이드 문서 반영 완료

다음 단계 메모:

- 이후 단계에서도 구현 중 발견된 사용성 요구사항은 가이드 문서와 `History.md`에 함께 반영한다.

## 2026-05-27 - 4단계: 연결 설정값 매핑

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- UI에서 선택한 시리얼 통신 설정을 pyserial에서 사용할 수 있는 값으로 변환하는 `SerialSettings` 데이터 클래스를 추가했다.
- 현재 UI 상태를 읽어 `SerialSettings`를 반환하는 `current_serial_settings()` 메서드를 추가했다.
- Port, Baudrate, Databits, Parity, Stopbits, Flow control 값을 매핑하도록 구현했다.
- Baudrate 직접 입력값이 비어 있거나 정수가 아니거나 0 이하일 때 오류로 처리하도록 검증 로직을 추가했다.
- 포트가 없는 상태에서 설정을 요청하면 오류 메시지를 남기고 `None`을 반환하도록 처리했다.
- 설정 오류 메시지를 상태바에 표시하고, 테스트와 이후 로직에서 확인할 수 있도록 `last_settings_error`에도 보관한다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 4단계 설정 매핑 검증 통과
- 기본 설정값, parity 매핑, stopbits 매핑, flow control 매핑, 잘못된 baudrate, 포트 없음 케이스를 검증했다.
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 5단계에서 `QThread` 기반 `SerialWorker`를 추가한다.
- `SerialSettings`를 worker 생성 또는 연결 시작 로직에 전달할 수 있도록 활용한다.

## 2026-05-27 - 작업 재개용 메모 작성

변경 파일:

- `memory.md`
- `History.md`

핵심 변경 사항:

- 다음 작업일에 바로 이어서 시작할 수 있도록 `memory.md`를 생성했다.
- 프로젝트 개요, 완료 단계, 주요 구현 내용, 현재 파일 목록, 실행 방법, 검증 결과, 설계 규칙, 다음 작업을 정리했다.
- 다음 시작 단계가 5단계 `QThread` 기반 `SerialWorker` 구현임을 명시했다.

검증 결과:

- `memory.md` 생성 완료

다음 단계 메모:

- 다음 작업 시작 시 `memory.md`와 `History.md`를 먼저 확인한다.
- 5단계 구현 전 현재 `main.py` 구조를 다시 읽고 `SerialWorker` 추가 위치를 결정한다.

## 2026-05-28 - 5단계: QThread 기반 SerialWorker 구현

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- `QThread` 기반 `SerialWorker` 클래스를 추가했다.
- `SerialSettings`를 받아 pyserial 포트를 여는 `_open_serial()` 메서드를 구현했다.
- worker 내부 수신 루프에서 bytes 데이터를 읽고 `data_received` signal로 UI 계층에 전달할 수 있게 했다.
- 포트 열림/닫힘 상태를 전달하는 `port_opened`, `port_closed` signal을 추가했다.
- 오류 메시지를 UI 계층에 전달하는 `error_occurred` signal을 추가했다.
- `stop()` 메서드를 추가하여 수신 루프 종료를 요청하고, 가능한 경우 pyserial `cancel_read()`로 대기 중인 read를 깨우도록 했다.
- `SerialException`, `OSError`, 예상하지 못한 예외를 잡아 앱 종료 대신 signal로 전달하도록 했다.
- 포트 제거나 읽기 중 오류에 대비할 수 있도록 read loop와 close 경로를 분리했다.
- 실제 하드웨어 없이 검증할 수 있도록 `serial_factory` 주입 지점을 추가했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 가짜 시리얼 객체를 사용한 worker 수신 루프 검증 통과
- 포트 열기 실패 시 `error_occurred` signal이 발생하는지 검증 통과

다음 단계 메모:

- 6단계에서 `Open` 버튼과 `SerialWorker`를 연결한다.
- 연결 중에는 포트 설정 컨트롤을 잠그고, 닫기 동작에서 `stop()`과 `wait()`를 안전하게 호출하도록 구현한다.
- 수신 bytes를 로그 영역에 표시하고 RX 카운터를 갱신한다.

## 2026-05-28 - 6단계: Open 버튼과 SerialWorker 연결

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- `Open` 버튼 클릭 시 `current_serial_settings()`로 설정을 검증한 뒤 `SerialWorker`를 생성하고 시작하도록 연결했다.
- 연결 중에는 `Open` 버튼을 `Close`로 바꾸고 Port, Baudrate, Databits, Parity, Flow control, Stopbits, Refresh Ports 컨트롤을 잠그도록 했다.
- `Close` 클릭 시 worker의 `stop()`을 호출하고, 창 종료 시에는 `wait()`까지 수행하도록 했다.
- worker의 `data_received` signal을 로그 영역 출력과 RX 바이트 카운터 갱신에 연결했다.
- worker의 `error_occurred` signal을 상태바와 로그 영역에 표시하도록 연결했다.
- `port_opened`, `port_closed`, `finished` signal을 이용해 연결 상태 표시와 UI 복구를 처리했다.
- 연결 중 포트 목록이 비어지는 경우에도 `Close` 버튼이 비활성화되지 않도록 포트 갱신 로직을 보완했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 `Open` 버튼과 worker 연결 검증 통과
- 가짜 시리얼 데이터를 수신해 로그 영역과 RX 카운터가 갱신되는지 검증 통과
- 포트 열기 실패 시 오류 로그 표시와 UI 복구 검증 통과
- 연결 중 포트 목록이 비어져도 `Close` 버튼이 유지되는지 검증 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 7단계에서 송신 기능을 구현한다.
- `Send` 버튼 활성화, 문자열/Hex 등 포맷 변환, TX 카운터 갱신을 worker 또는 별도 thread-safe API와 연결한다.

## 2026-05-28 - 7단계: 송신 기능 구현

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- `SerialWorker`에 `write_data()` 메서드를 추가해 열린 시리얼 포트로 bytes를 송신할 수 있게 했다.
- 송신 성공 시 `bytes_written` signal을 발생시키도록 했다.
- 송신 실패 시 앱이 종료되지 않고 `error_occurred` signal로 오류를 전달하도록 했다.
- 수신 루프와 송신이 같은 serial 객체에 접근하므로 간단한 I/O lock을 추가했다.
- 연결 완료 시 `Send` 버튼을 활성화하고, 연결 해제 시 다시 비활성화하도록 했다.
- `Send` 버튼과 command 입력창 Enter 키를 송신 동작에 연결했다.
- String 포맷은 UTF-8 bytes로 송신하도록 구현했다.
- Hex, Dec, Oct, Bin 포맷은 공백/콤마/세미콜론으로 구분된 숫자 토큰을 byte 값으로 변환해 송신하도록 구현했다.
- 숫자 토큰이 잘못되었거나 0~255 범위를 벗어나면 상태바와 로그 영역에 오류를 표시하도록 했다.
- 송신 성공 시 TX 바이트 카운터를 갱신하고 로그 영역에 `[tx]` 항목을 남기도록 했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 String 송신 검증 통과
- 오프스크린 Hex 송신 검증 통과
- 잘못된 숫자 토큰과 byte 범위 초과 입력 검증 통과
- 송신 실패 시 오류 signal과 UI 표시 검증 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 8단계에서 반복 송신 기능을 구현한다.
- `Loop this command` 체크박스, interval spinbox, `Start loop` 버튼을 송신 기능과 연결한다.
- 반복 송신 중 연결 종료, 입력 오류, 송신 실패 상황을 안전하게 처리한다.

## 2026-05-28 - 8단계: 반복 송신 기능 구현

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- 반복 송신용 `QTimer`인 `loop_send_timer`를 추가했다.
- `Loop this command` 체크박스와 `Start loop` 버튼을 반복 송신 상태와 연결했다.
- `Start loop` 클릭 시 현재 명령을 즉시 한 번 송신한 뒤 설정된 주기로 반복 송신하도록 했다.
- 반복 송신 중에는 버튼 텍스트를 `Stop loop`로 변경하고, command 입력창, 포맷 라디오 버튼, 체크박스, interval spinbox를 잠가 현재 명령이 흔들리지 않도록 했다.
- `Stop loop` 클릭 시 반복 타이머를 정지하고 UI 상태를 복구하도록 했다.
- 연결 종료 시 반복 송신 타이머가 남지 않도록 `_stop_serial_connection()`과 worker 종료 처리에 정리 로직을 추가했다.
- 입력 오류 또는 송신 실패가 발생하면 반복 송신을 시작하지 않거나 즉시 중지하도록 했다.
- 반복 송신 버튼은 연결되어 있고 체크박스가 선택된 경우에만 활성화되도록 했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 반복 송신 시작/중지 검증 통과
- 반복 송신 중 command 입력과 포맷 컨트롤 잠금/복구 검증 통과
- 연결 종료 시 반복 송신 타이머 정리 검증 통과
- 잘못된 입력으로 반복 송신이 시작되지 않는지 검증 통과
- 반복 송신 중 write 실패 시 타이머가 정지되는지 검증 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 9단계에서 수신/송신 로그 표시 옵션을 개선한다.
- String/Hex/Dec/Oct/Bin 표시 방식, 줄바꿈 처리, 타임스탬프 표시 여부를 검토한다.

## 2026-05-28 - 9단계: 수신/송신 로그 표시 옵션 개선

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- 로그 영역에 최대 라인 수 제한을 적용하기 위해 `QPlainTextEdit.document().setMaximumBlockCount(5000)`을 설정했다.
- 하단 패널에 `Log view` 콤보박스를 추가하여 로그 표시 방식을 String, Hex, Dec, Oct, Bin 중 선택할 수 있게 했다.
- 하단 패널에 `Timestamp` 체크박스를 추가하여 로그 prefix 앞에 `HH:MM:SS.mmm` 타임스탬프를 선택적으로 표시할 수 있게 했다.
- 하단 패널에 `Clear log` 버튼을 추가하여 로그를 바로 비울 수 있게 했다.
- 수신 로그는 `[RX]`, 송신 로그는 `[TX]`, 오류 로그는 `[ERR]`, 세션 로그는 `[SESSION]` prefix를 사용하도록 정리했다.
- String 표시 모드에서는 CR/LF/TAB 같은 제어 문자를 `\r`, `\n`, `\t`로 보이게 처리하여 줄바꿈으로 로그 구조가 깨지지 않도록 했다.
- Hex, Dec, Oct, Bin 표시 모드는 RX/TX 로그 양쪽에 동일하게 적용되도록 했다.
- 새 로그가 들어오면 자동으로 마지막 위치로 스크롤되도록 유지했다.

검증 결과:

- `python -m py_compile main.py` 통과
- String 로그 prefix와 CR/LF escape 표시 검증 통과
- Hex 로그 표시와 타임스탬프 표시 검증 통과
- Dec/Oct/Bin 로그 표시 포맷 검증 통과
- 최대 로그 라인 수 제한 검증 통과
- `Clear log` 버튼 검증 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 다음 단계에서는 파일 송신 기능을 구현한다.
- `Send file` 버튼을 활성화하고 `QFileDialog`로 선택한 파일을 bytes로 읽어 송신한다.
- 큰 파일 송신이 UI를 오래 멈추지 않도록 크기 제한 또는 chunk 송신 방식을 검토한다.

## 2026-05-28 - 10단계: 리팩토링과 패키징 문서화

변경 파일:

- `main.py`
- `settings.py`
- `serial_worker.py`
- `packaging.md`
- `History.md`
- `memory.md`

핵심 변경 사항:

- `SerialSettings` 데이터 클래스를 `settings.py`로 분리했다.
- `SerialWorker` 클래스를 `serial_worker.py`로 분리했다.
- `main.py`는 UI, 포트 스캔, 설정 매핑, 사용자 동작 연결을 담당하도록 정리했다.
- worker의 수신/송신/오류 signal 동작은 유지하면서 기존 UI 연결 코드를 새 모듈 import 기반으로 갱신했다.
- Windows `.exe`와 macOS `.app` 생성을 위한 PyInstaller 패키징 절차를 `packaging.md`에 작성했다.
- 패키징 전 기본 검증 명령과 OS별 생성 결과 위치를 문서화했다.

검증 결과:

- `python -m py_compile main.py settings.py serial_worker.py` 통과
- 리팩터링 후 오프스크린 Open/Receive/Send/Close 통합 검증 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 아직 `Send file` 버튼은 비활성화 상태다.
- 다음 기능 단계에서는 파일 송신을 구현한다.
- 파일 송신 구현 후 패키징 산출물에서도 실제 시리얼 장치로 연결/수신/송신/반복 송신을 다시 확인한다.

## 2026-05-28 - 앱 이름 및 아이콘 반영

변경 파일:

- `main.py`
- `build_win.bat`
- `build_mac.sh`
- `packaging.md`
- `ai_collaboration_serial_monitor_guide.md`
- `serial_monitor_ai_collaboration_review.md`
- `History.md`
- `memory.md`
- `image/CasaSerial.ico`

핵심 변경 사항:

- 앱 이름을 `CasaSerial`로 통일했다.
- Python 실행 시 창 제목과 애플리케이션 이름을 `CasaSerial`로 설정했다.
- Python 실행 시 `image/CASA_Serial_APP_ICON.png`를 창 아이콘과 앱 아이콘으로 사용하도록 했다.
- PyInstaller 패키징 실행에서도 런타임 아이콘 PNG가 포함되도록 `--add-data` 옵션을 추가했다.
- Windows 빌드 결과가 `WIN\CasaSerial\CasaSerial.exe`로 생성되도록 `build_win.bat`를 갱신했다.
- Windows 빌드 아이콘용 `image/CasaSerial.ico`를 생성하고 `--icon` 옵션에 연결했다.
- macOS 빌드 결과가 `MAC/CasaSerial.app`으로 생성되도록 `build_mac.sh`를 갱신했다.
- macOS 빌드 시 `image/CASA_Serial_APP_ICON.png`에서 `image/CasaSerial.icns`를 자동 생성하고 `--icon` 옵션에 연결하도록 했다.
- 가이드 문서와 작업 문서의 기존 앱 이름 표기를 `CasaSerial`로 반영했다.

검증 결과:

- `python -m py_compile main.py settings.py serial_worker.py` 통과
- `cmd /c build_win.bat --check` 통과
- `cmd /c run.bat --check` 통과

다음 단계 메모:

- 실제 Windows 빌드는 `build_win.bat`로 실행한다.
- 실제 macOS 빌드는 macOS에서 `chmod +x build_mac.sh` 후 `./build_mac.sh`로 실행한다.

## 2026-05-28 - Windows 빌드 폴더 경로 수정

변경 파일:

- `build_win.bat`
- `packaging.md`
- `History.md`

핵심 변경 사항:

- Windows 빌드 시 PyInstaller 작업 폴더가 프로젝트 루트의 `build`에 생기지 않도록 수정했다.
- `--workpath`를 `WIN\build`로 변경했다.
- `--specpath`를 `WIN\spec`으로 변경했다.
- Windows 빌드 관련 산출물이 `WIN` 폴더 아래에 모이도록 문서도 갱신했다.

검증 결과:

- `cmd /c build_win.bat --check` 통과

## 2026-05-28 - macOS 빌드 폴더 경로 수정

변경 파일:

- `build_mac.sh`
- `packaging.md`
- `History.md`

핵심 변경 사항:

- macOS 빌드 시 PyInstaller 작업 폴더가 프로젝트 루트의 `build`에 생기지 않도록 수정했다.
- `--workpath`를 `MAC/build`로 변경했다.
- `--specpath`를 `MAC/spec`으로 변경했다.
- `.icns` 생성을 위한 iconset 임시 폴더를 `MAC/icon/CasaSerial.iconset`으로 변경했다.
- macOS 빌드 관련 산출물이 `MAC` 폴더 아래에 모이도록 문서를 갱신했다.

검증 결과:

- Windows 환경이라 실제 macOS 빌드는 실행하지 못했다.
- `build_mac.sh`의 경로 설정을 확인했다.

## 2026-05-28 - PyInstaller 아이콘/데이터 경로 수정

변경 파일:

- `build_win.bat`
- `build_mac.sh`
- `packaging.md`
- `History.md`

핵심 변경 사항:

- `--specpath`를 별도 폴더로 지정하면 PyInstaller가 `--add-data` 상대 경로를 spec 파일 위치 기준으로 해석하는 문제가 있었다.
- Windows 빌드의 `--icon`, `--add-data` 입력 경로를 절대 경로로 변경했다.
- macOS 빌드의 아이콘 PNG와 `.icns` 경로도 절대 경로로 변경했다.
- 패키징 문서의 수동 Windows PyInstaller 명령도 절대 경로 방식으로 갱신했다.

검증 결과:

- `cmd /c build_win.bat --check` 통과

## 2026-05-28 - macOS 실행 스크립트 추가

변경 파일:

- `run_mac.sh`
- `History.md`

핵심 변경 사항:

- macOS에서 개발 중 앱을 바로 실행할 수 있는 `run_mac.sh`를 추가했다.
- `.venv/bin/python`이 있으면 우선 사용하고, 없으면 `python3`를 사용한다.
- `--check` 옵션으로 실제 실행 없이 사용할 Python 명령을 확인할 수 있게 했다.

검증 결과:

- Windows 환경이라 macOS에서 직접 실행하지는 못했다.
- 스크립트 줄바꿈을 Unix LF로 유지했다.

## 2026-05-28 - 현재 상태 점검 및 빌드 데이터 보강

변경 파일:

- `build_win.bat`
- `build_mac.sh`
- `packaging.md`
- `ai_collaboration_serial_monitor_guide.md`
- `History.md`

핵심 변경 사항:

- 현재 코드가 `MonitorSubWindow`, `NewSessionDialog`, `CasaSerialWindow` 기반 MDI 구조로 확장된 상태임을 확인했다.
- Python 컴파일, Windows 실행 스크립트 확인, Windows 빌드 스크립트 확인을 수행했다.
- 오프스크린 UI 스모크 테스트로 MDI 영역, Send dialog, CMD 패널, 버튼 초기 상태를 확인했다.
- 패키징 앱에서 `Fonts` 폴더가 누락될 수 있어 Windows/macOS 빌드 스크립트에 `Fonts` 데이터 포함 옵션을 추가했다.
- 패키징 문서의 수동 PyInstaller 명령에도 `Fonts` 데이터 포함 옵션을 반영했다.
- 가이드 문서에 남아 있던 이전 창 제목 `Serial Monitor` 표기를 `CasaSerial`로 정리했다.

검증 결과:

- `python -m py_compile main.py settings.py serial_worker.py` 통과
- `cmd /c run.bat --check` 통과
- `cmd /c build_win.bat --check` 통과
- 오프스크린 CasaSerial UI 스모크 테스트 통과

## 2026-05-28 - 11단계 보완: Send dialog CR+LF 및 레이아웃 개선

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- 포트 설정 행과 명령 입력 행 사이에 `addSpacing(8)`을 추가하여 시각적 구분을 개선했다.
- 명령 입력 영역의 순서를 `[명령 입력창] [Send] [CR+LF]`로 변경했다.
- `CR+LF` 체크박스를 추가했다. 체크 시 송신 payload 끝에 `\r\n`을 자동으로 붙인다.
- String/Hex/Dec/Oct/Bin 모든 포맷에서 CR+LF가 적용된다.
- 반복 송신 중에는 CR+LF 체크박스도 함께 잠금 처리한다.

검증 결과:

- `python -m py_compile main.py` 통과

다음 단계 메모:

- 12단계에서 NEW 버튼을 활성화하고 새 모니터링 세션 다이얼로그를 구현한다.

## 2026-05-28 - 12단계: New Session 다이얼로그 구현

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- 툴바 NEW(New Session) 아이콘을 활성화하고 클릭 시 `NewSessionDialog`를 여는 동작을 연결했다.
- `NewSessionDialog(QDialog)` 클래스를 추가했다.
- 다이얼로그 구성:
  - 좌측: 현재 감지된 시리얼 포트 목록 (`QListWidget`)
  - 우측: 뷰어 선택 (Terminal view만 활성, Table/Line/Dump/Modbus는 미래 기능으로 비활성)
  - New session options: "Start monitoring now" 체크박스, "Start in new window" (비활성)
  - Capture options: Create/Close, Read/Write, Device Control 체크박스
  - Start monitoring / Cancel 버튼
- "Start monitoring" 클릭 시 선택한 포트를 Send dialog의 Port 콤보에 반영하고, "Start monitoring now"가 체크되어 있으면 즉시 포트를 오픈한다.
- 필요 imports를 추가했다: `QDialog`, `QDialogButtonBox`, `QGroupBox`, `QListWidget`, `QListWidgetItem`.

검증 결과:

- `python -m py_compile main.py` 통과

다음 단계 메모:

- 13단계에서 중앙 로그 영역을 `QMdiArea`로 교체하여 NEW를 여러 번 누르면 여러 개의 독립 세션 창이 MDI 영역 안에 생기도록 구현한다.

## 2026-05-28 - 13단계: MDI 멀티 세션 아키텍처

변경 파일:

- `main.py`
- `History.md`
- `memory.md`

핵심 변경 사항:

- 중앙 `QPlainTextEdit` 로그 영역을 `QMdiArea`로 교체했다. 앱 시작 시 MDI 영역은 빈 파란 배경만 표시된다.
- `MonitorSubWindow(QMdiSubWindow)` 클래스를 추가했다.
  - 자체 `QPlainTextEdit` 로그 뷰를 내부 위젯으로 보유한다.
  - 자체 `SerialWorker`를 소유하고 시리얼 연결을 독립적으로 관리한다.
  - 자체 RX/TX 바이트 카운터를 보유한다.
  - `start(settings)`, `stop(wait)`, `write_data(payload)`, `append_log(category, message)` API를 제공한다.
  - `state_changed`, `error_occurred`, `bytes_sent` signal로 메인 창 상태바에 상태를 전달한다.
  - 서브윈도우 닫기 시 열린 시리얼 연결을 안전하게 종료한다.
- NEW 버튼 클릭 → `NewSessionDialog` → 확인 시 새 `MonitorSubWindow`를 `QMdiArea`에 추가한다.
- 여러 번 NEW를 누르면 각각 독립적인 세션 창이 생성되며 동시에 여러 포트를 모니터링할 수 있다.
- Send dialog의 Open/Close 버튼은 현재 활성 서브윈도우의 연결을 제어한다.
- 서브윈도우 포커스 전환 시 상태바(연결 상태, 포트, RX/TX)가 해당 세션으로 자동 갱신된다.
- Log view 콤보박스와 Timestamp 체크박스는 활성 서브윈도우의 로그 포맷에 적용된다.
- Clear log 버튼은 활성 서브윈도우의 로그를 지운다.
- 창 종료 시 모든 서브윈도우의 연결을 안전하게 종료한다.
- 필요 imports를 추가했다: `QMdiArea`, `QMdiSubWindow`, `pyqtSignal`.

검증 결과:

- `python -m py_compile main.py` 통과

다음 단계 메모:

- 다음 단계에서는 파일 송신 기능을 구현한다.
- `send_file_button` 현재 비활성화 상태이며, `QFileDialog`로 파일을 선택한 뒤 활성 서브윈도우를 통해 bytes로 읽어 송신한다.

## 2026-05-28 - UI 개선: 폰트 적용 및 Send Dialog 레이아웃

변경 파일:

- `main.py`

핵심 변경 사항:

- `Fonts/` 폴더에 Inter, D2Coding 폰트를 추가하고 앱 시작 시 `QFontDatabase.addApplicationFont()`로 로드했다.
- 데이터 로그 뷰(`QPlainTextEdit`)에는 **D2Coding 10pt** 를 적용했다.
- 나머지 모든 UI 요소에는 `app.setFont()`로 **Inter 10pt** 를 적용했다.
- Windows에서 Python 실행 시 태스크바 아이콘이 기본 Python 아이콘으로 나오던 문제를 `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CasaSerial.App")` 호출로 수정했다.
- Send Dialog 설정 그리드 행 간격을 `setVerticalSpacing(30)`으로 조정하고 `addSpacing(20)`으로 명령 입력행과의 여백을 확보했다.
- 그리드 레이블(Port, Baudrate 등)이 콤보박스 중앙에 정렬되도록 `QLabel.setAlignment(AlignLeft | AlignVCenter)`를 적용하고, 패널 스타일시트에 `min-height: 26px`를 추가해 "Parity" 글씨가 잘리던 문제를 수정했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 실행 확인: 폰트, 태스크바 아이콘, Send Dialog 레이아웃 정상

## 2026-05-28 - UI 개선: 송신 포맷 입력 유효성 검사 및 자동 포맷

변경 파일:

- `main.py`

핵심 변경 사항:

- 포맷 라디오 버튼(Hex/Dec/Oct/Bin) 선택 시 `command_input`에 `QRegularExpressionValidator`를 적용해 해당 진수에 유효한 문자만 입력되도록 했다.
- `command_input.textChanged`에 `_auto_format_command_input()`을 연결해 입력 즉시 바이트 경계마다 공백을 자동 삽입하도록 했다 (Hex: 2자, Dec/Oct: 3자, Bin: 8자).
- `blockSignals(True/False)`로 자동 포맷 중 재귀 신호를 방지하고, 비공백 문자 수 기준으로 커서 위치를 복원했다.
- 포맷 라디오 버튼 전환 시 입력창을 초기화하지 않고 현재 값을 새 포맷으로 변환하도록 `_on_send_format_changed()`를 수정했다.
- 변환 파이프라인: `_text_to_byte_values()` → `list[int]` → `_byte_values_to_text()`. String은 UTF-8 encode/decode, 나머지는 각 진수로 파싱한다. 범위(0~255)를 벗어난 토큰은 무시한다.
- `self._send_format` 속성으로 현재 포맷을 추적한다.

검증 결과:

- `python -m py_compile main.py` 통과
- 실행 확인: 각 포맷 입력 제한, 자동 공백 삽입, 포맷 전환 시 값 변환 정상

## 2026-05-28 - CMD 사이드 패널 추가

변경 파일:

- `main.py`

핵심 변경 사항:

- MDI 영역 오른쪽에 슬라이딩 사이드 패널(`cmd_panel_wrapper`)을 추가했다.
- MDI 영역과 CMD 패널을 수평 `QSplitter`(`h_splitter`, handleWidth=0)로 연결하고, 기존 세로 splitter의 상단 위젯을 `h_splitter`로 교체했다.
- CMD 패널 왼쪽 가장자리에 18px 너비의 토글 버튼을 배치했다. 클릭 시 패널을 접거나 펼치며 `◀`/`▶` 텍스트가 전환된다.
- 접힌 상태에서는 `h_splitter.setSizes([total - 18, 18])`로 토글 버튼만 남기고, 펼칠 때는 마지막 너비를 복원한다.
- CMD 패널 내부 그리드에 CMD0~CMD9 10개 슬롯을 구성했다: 라벨 버튼 / 입력창 / BIN 체크박스 / CR+LF 체크박스.
- CMD 라벨 버튼 클릭 시 `_send_cmd(idx)` 호출로 해당 입력창 내용을 송신한다.
- BIN 체크박스가 체크된 경우 입력값을 HEX로 해석해 바이너리 데이터로 송신한다.
- CR+LF 체크박스가 체크된 경우 송신 데이터 끝에 `\r\n`을 추가한다.

검증 결과:

- `python -m py_compile main.py` 통과

다음 단계 메모:

- 파일 송신 기능 또는 Bridge 모드 구현 중 선택한다.

## 2026-05-29 - UI 개선: New Session 다이얼로그 뷰어 정리 및 Dump view 기능 구현

변경 파일:

- `main.py`
- `serial_worker.py`

핵심 변경 사항:

- `NewSessionDialog`에서 Table view, Line view, Modbus view (Modbus RTU/ASCII 포함)를 제거했다. 뷰어 선택지는 Dump view / Terminal view만 유지한다.
- Capture options 섹션(Create/Close, Read/Write, Device Control 체크박스)을 제거했다. 기능 없이 UI에만 존재하던 항목이었다.
- Dump view 체크박스를 활성화하고, Terminal view와 상호 배타적으로 동작하도록 했다. (하나 선택 시 다른 것 자동 해제)
- `NewSessionDialog`에 `selected_visualizer` 프로퍼티를 추가했다. 기본값은 "Dump view"다.
- `serial_worker.py`에 `data_written = pyqtSignal(bytes)` 신호를 추가하고 `write_data()` 성공 시 실제 전송 bytes를 emit하도록 했다.
- `MonitorSubWindow`에 `dump_mode: bool` 파라미터를 추가했다.
  - Dump 모드에서 RX 데이터는 `61 62 63  |  abc` 형식(hex + 구분자 + ASCII)으로 표시한다.
  - Dump 모드에서 TX 데이터도 동일한 형식으로 `[TX]` 항목에 표시한다.
  - ASCII 범위(0x20~0x7E)를 벗어난 바이트는 `.`으로 표시한다.
  - `append_log("TX", ...)` 호출은 Dump 모드에서 무시되어 중복 표시를 방지한다.
- `_format_dump(data: bytes) -> str` 헬퍼 메서드를 추가했다.
- `_open_new_session_dialog()`에서 `dialog.selected_visualizer`를 읽어 `MonitorSubWindow(dump_mode=...)` 에 전달하도록 했다.

검증 결과:

- `python -m py_compile main.py serial_worker.py` 통과

## 2026-05-29 - UI 개선: 로그 카테고리 색상 표시

변경 파일:

- `main.py`

핵심 변경 사항:

- `QTextCharFormat`과 `QColor`를 import에 추가했다.
- `MonitorSubWindow._append()` 메서드를 `appendPlainText()` 기반에서 `QTextCursor` + `QTextCharFormat` 기반으로 교체했다.
- 카테고리별 색상을 `_CATEGORY_COLORS` 딕셔너리로 정의했다: RX `#0D47A1`(진한 파랑), TX `#1B5E20`(진한 초록), SESSION `#424242`(진한 회색), ERR `#B71C1C`(진한 빨강).
- 각 로그 줄이 해당 카테고리 색으로 표시된다.

검증 결과:

- `python -m py_compile main.py` 통과

## 2026-05-30 - 버튼 이미지 자산 적용 및 하단 전송 패널 정리

변경 파일:

- `main.py`
- `ai_collaboration_serial_monitor_guide.md`
- `packaging.md`
- `build_win.bat`
- `build_mac.sh`
- `WIN/spec/CasaSerial.spec`
- `image/icons/*.png`
- `image/buttons/*.png`

핵심 변경 사항:

- `image/icons` 폴더의 검정 아이콘 픽셀을 브랜드 포인트 색상 `#a87443`로 변경했다.
- `reload1.png`, `TRANSFER1.png`는 기존 색상을 유지하면서 선 굵기를 약 30% 두껍게 조정했다.
- 상단 툴바를 코드로 그린 아이콘에서 `image/buttons` PNG 이미지 버튼 기반으로 변경했다.
  - 버튼 순서: `open`, `save`, `start`, `pause`, `stop`, `erase`.
  - `reload` 포트 새로고침 버튼은 오른쪽 끝에 정렬하고 크기를 30% 줄였다.
  - 툴바 구분선을 제거했다.
- CMD 패널 제목을 "포트 목록"에서 "명령어 목록"으로 변경했다.
- CMD 패널 추가/삭제 버튼을 `plus.png`, `minus.png` 이미지 버튼으로 변경했다.
  - 버튼 크기를 40% 줄이고, 오른쪽 정렬 및 버튼 간격을 적용했다.
- 하단 전송 설정 패널의 주요 버튼을 이미지 버튼으로 변경했다.
  - 연결 열기/닫기: `connect.png`
  - 전송: `transfer.png`
  - 반복 전송 시작/정지: `start_repeat.png`
  - 연결 버튼은 20% 확대했고, 전송/반복 시작 버튼은 20% 축소했다.
  - 연결 버튼은 포트 설정 입력칸 기준 위쪽으로 배치했다.
- 하단 전송 설정 패널 레이아웃을 조정했다.
  - 포트 설정 콤보박스가 명령 입력창에 잘려 보이지 않도록 패널 높이와 행 간격을 보정했다.
  - "전송 설정" 제목 위치와 제목 아래 간격을 조정했다.
  - 미구현 `파일 전송` 버튼을 제거했다.
  - `로그 형식`, `타임스탬프`, `지우기` 컨트롤을 하단 오른쪽에 정렬하고 아래 여백을 약 10px 수준으로 줄였다.
- PyInstaller 패키징 시 `image/buttons` 폴더가 포함되도록 Windows/macOS 빌드 스크립트와 spec, 패키징 문서를 갱신했다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 UI 확인으로 상단 툴바 버튼 7개와 하단 이미지 버튼 로딩 확인
- 오프스크린 UI 확인으로 `plus`/`minus` 버튼, 하단 로그 옵션 정렬, 하단 패널 여백 확인
- `build_win.bat --check`에서 `image/buttons` 데이터 경로 포함 확인

## 2026-05-29 - CMD 패널 동적 행 추가/삭제 기능

변경 파일:

- `main.py`

핵심 변경 사항:

- CMD 버튼 레이블을 `CMD0` → `CMD00` 형식(2자리)으로 변경했다.
- `self._cmd_grid`를 인스턴스 변수로 저장하여 동적 행 추가/삭제에 사용한다.
- `self._cmd_buttons`를 별도 리스트로 관리하여 삭제 시 참조가 가능하게 했다.
- `_append_cmd_row(i)` 헬퍼 메서드를 추가했다.
- `_add_cmd_row()`, `_remove_cmd_row()`, `_update_cmd_pm_buttons()` 메서드를 추가했다.
  - 최대 20개(CMD00~CMD19), 최소 1개(CMD00) 제한을 적용한다.
  - 한계 도달 시 해당 버튼 자동 비활성화.
- CMD 패널 하단에 `＋ 추가` / `－ 삭제` 버튼을 나란히 배치했다. 버튼 사이 구분선은 없애고 양쪽으로 동일하게 1:1 비율로 배치했다.

검증 결과:

- `python -m py_compile main.py` 통과

## 2026-05-29 - 전체 UI 한국어 및 웜 베이지 테마 개선

변경 파일:

- `main.py`

핵심 변경 사항:

- 앱 이름을 `CasaSerial` → `CasaSerialMonitor`로 변경했다.
- 메뉴를 한국어로 변경했다: Session → 세션, View → 보기, Help → 도움말, Refresh Ports → 포트 새로고침.
- 툴바를 아이콘+텍스트(`ToolButtonTextUnderIcon`) 방식으로 변경했다.
  - 아이콘 크기를 32px로 확대했다.
  - 버튼 레이블을 한국어로 변경했다: 열기, 저장, 시작, 일시정지, 정지, 지우기, 도움말, 포트 새로고침.
  - 툴바와 버튼에 웜 베이지 스타일시트를 적용했다.
- CMD 패널에 "포트 목록" 제목 레이블을 추가했다.
- CMD 패널 그리드에 "포트명" 컬럼 헤더를 추가했다.
- `＋ 추가` / `－ 삭제` 버튼을 웜 베이지 스타일로 변경했다.
- Send 패널 제목을 "Send dialog" → "전송 설정"으로 변경했다.
- Send 패널 레이블을 한국어로 변경했다: 포트, 보드레이트, 데이터 비트, 패리티, 흐름 제어, 정지 비트.
- 버튼 레이블을 한국어로 변경했다: 연결 열기/연결 닫기, 전송, 파일 전송, 반복 전송, 시작, 지우기, 로그 형식, 타임스탬프.
- 명령 입력창 placeholder를 "명령어 입력"으로 변경했다.
- 연결 버튼(`open_button`)에 골든 계열 강조 스타일을 적용했다.
- Send 패널 배경을 웜 크림 계열(`#faf6f0`)로 변경했다.
- MDI 영역 배경을 짙은 파랑(`#3a5898`) → 웜 베이지(`#e8ddd0`)로 변경했다.
- 상태바 메시지를 한국어로 변경했다: 준비, 연결됨, 연결 해제됨, 연결 중, 닫는 중.
- SESSION 로그 메시지를 한국어로 변경했다.

검증 결과:

- `python -m py_compile main.py` 통과

---

## 나중에 할 일

### 파일 송신 기능

- `send_file_button` 활성화
- `QFileDialog`로 파일 선택
- 큰 파일은 chunk 단위 송신으로 UI 프리징 방지

### Bridge 모드 (소프트웨어 시리얼 프록시)

**목적:**
하드웨어 탭(USB-UART 어댑터 배선) 없이 내 프로그램과 내 보드 사이의 통신을 CasaSerial로 모니터링한다.

**배경:**
Windows의 시리얼 포트는 독점 접근 구조라 다른 프로그램이 포트를 점유 중이면 Python에서 같은 포트를 열 수 없다. Portmon(Sysinternals) 같은 커널 드라이버 기반 패시브 모니터 도구가 있으나 Windows 10/11 64비트에서는 드라이버 서명 문제로 사실상 동작하지 않는다.

**동작 구조:**

```text
[내 프로그램] ── 가상 포트 ── [CasaSerial Bridge] ── 실제 포트 ── [내 보드]
                                   TX→ / ←RX 로그
```

**구현 내용:**

- Send dialog에 Bridge 모드 UI 추가 (포트 A + 포트 B 동시 선택)
- `BridgeWorker`: 두 SerialWorker를 동시에 관리하며 A↔B 데이터를 중계
- 로그에 방향 구분 표시 (`[PC→보드]` / `[보드→PC]`)
- 가상 포트 생성 플랫폼별 처리:
  - **Windows**: com0com 1회 설치 필요 — SourceForge에서 signed 버전 받아야 Windows 10/11에서 정상 동작
  - **macOS**: Python 내장 `pty` 모듈로 앱 내부에서 자동 생성 (외부 도구 불필요)
  - **Linux**: `pty` 모듈 또는 `socat`

**장점:**

- 최초 설정 1회 후, 이후에는 CasaSerial 실행만으로 즉시 양방향 모니터링 가능
- 하드웨어 배선 불필요, TX/RX 방향 동시 확인
