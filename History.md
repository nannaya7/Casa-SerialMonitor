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

## 2026-11-11 - README.md 작성 및 작업 기록 규칙 추가

변경 파일:

- `README.md`
- `CLAUDE.md`
- `History.md`

핵심 변경 사항:

- 비어 있던 `README.md`를 프로젝트 소개, 주요 기능, 설치/실행, 빌드, 파일 구조, 문서 안내 순으로 작성했다.
- `CLAUDE.md`에 `History.md` 지속 기록 규칙을 추가했다.

검증 결과:

- 문서 작업이라 코드 검증은 해당 없음.

## 2026-11-11 - run.bat 터미널 창 숨김

변경 파일:

- `run.bat`
- `History.md`

핵심 변경 사항:

- 기본 실행을 `pythonw`(`.venv`가 있으면 `.venv\Scripts\pythonw.exe`) + `start ""` 방식으로 바꿔 앱 실행 시 터미널 창이 남지 않게 했다.
- 오류 확인이 필요할 때를 위해 `run.bat --console` 옵션(기존 콘솔 실행 및 오류 시 pause)을 추가했다.
- `--check`에서 pythonw 경로도 출력하도록 했다.

검증 결과:

- `run.bat --check` 정상 출력 확인. GUI 실행은 직접 확인 필요.

## 2026-11-11 - 시작 시 New Session 창 자동 표시

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- 앱 시작 직후 `QTimer.singleShot(0, ...)`로 `new_session_action`을 실행해 New Session 다이얼로그가 자동으로 뜨게 했다.
- 다이얼로그를 취소하면 세션 없이 메인 창만 남는다.

검증 결과:

- `python -m py_compile main.py` 통과
- 오프스크린 실행 시 시작 직후 New Session 다이얼로그 `exec()` 호출 확인

## 2026-11-11 - CMD 패널 버튼 모양 개선

변경 파일:

- `main_window.py`
- `UI/mainWindow.ui`
- `History.md`

핵심 변경 사항:

- CMD00~ 버튼이 텍스트처럼 보이던 문제를 고쳤다. `_CMD_BTN_STYLE`에 배경(`#f3e7da`), 테두리(`#d9c1aa`), 둥근 모서리(8px), 중앙 정렬 텍스트를 적용했다.
- hover / pressed / disabled 상태 스타일을 추가했다.
- `.ui`의 `cmd_button_00~09`에 설정돼 있던 `flat=true`를 `false`로 변경했다.
- 동적으로 추가되는 CMD 행도 같은 스타일을 사용한다.

검증 결과:

- 오프스크린 렌더링으로 버튼 배경/테두리/둥근 모서리 적용 확인 (폰트가 없는 환경이라 글자는 박스로 표시됨).

## 2026-11-11 - CMD 패널 헤더에 "명령어 전송" 추가

변경 파일:

- `UI/mainWindow.ui`
- `History.md`

핵심 변경 사항:

- CMD 버튼 열(row 0, column 0) 위에 `cmd_header_send` 라벨("명령어 전송")을 추가했다. 다른 헤더(포트명/HEX/CR+LF)와 같은 스타일(8pt, `#7b6755`, 가운데 정렬)을 사용한다.

검증 결과:

- 오프스크린 렌더링으로 헤더 위치 확인.

## 2026-11-11 - README 스크린샷 교체

변경 파일:

- `README.md`
- `CasaSerialMonitor.png` (신규)
- `History.md`

핵심 변경 사항:

- README의 스크린샷이 참고 제품(`Target_APP.png`)이던 것을 CasaSerial 실제 화면(`CasaSerialMonitor.png`)으로 교체했다.

검증 결과:

- 문서 작업이라 코드 검증은 해당 없음.

## 2026-11-11 - 글자 선명도 개선

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- 기본 폰트에 `PreferFullHinting`과 `PreferAntialias`를 지정해 글자 윤곽이 또렷하게 렌더링되도록 했다.
- 흐림의 주 원인 후보: Windows 배율(125%/150% 등 비정수 배율), Inter 가변 폰트, 버튼 PNG 이미지의 축소 렌더링.

검증 결과:

- 오프스크린 실행 시 오류 없이 시작됨.
- 사용자 실기기 확인: 글자가 또렷해짐.

## 2026-11-11 - CMD 버튼 글자 굵기 변경

변경 파일:

- `main_window.py`
- `History.md`

핵심 변경 사항:

- `_CMD_BTN_STYLE`의 `font-weight`를 600(볼드)에서 400(일반)으로 변경해 CMD00~ 버튼 글자를 일반 굵기로 표시한다.

검증 결과:

- 스타일 값 변경 확인.
- 사용자 실기기 확인: 정상 동작.

## 2026-11-11 - 로그 형식에 따른 Dump view 출력 분기

변경 파일:

- `monitor_subwindow.py`
- `History.md`

핵심 변경 사항:

- Dump view 세션에서 로그 형식이 `String`일 때 HEX 값 없이 문자열만 출력하도록 했다. (예: `[RX] AT+BATT,4.16V,96%
`)
- 로그 형식이 `Hex`일 때만 기존처럼 `HEX  |  ASCII` 형태로 출력한다.
- Dec/Oct/Bin 형식은 해당 형식의 값만 출력한다.
- RX/TX 모두 `_format_for_view()`를 통해 같은 규칙을 적용한다.

검증 결과:

- 오프스크린 검증: Dump view + String → `AT+BATT,4.16V,96%
`, Dump view + Hex → `41 54 ... 0D 0A  |  AT+BATT,4.16V,96%..`, 일반 뷰 + Hex → HEX만 출력.

## 2026-11-11 - 포트 자동 스캔 타이머 제거

변경 파일:

- `main_window.py`
- `History.md`

핵심 변경 사항:

- 2초마다 포트를 자동 갱신하던 `port_scan_timer`(`_create_port_scan_timer`)를 제거했다.
- 포트 목록은 앱 시작 시 한 번 스캔하고, 이후에는 툴바의 포트 새로고침 버튼으로만 수동 갱신한다.
- 3단계 보완(포트 자동 갱신)의 요구사항을 대체한다.

검증 결과:

- `py_compile` 통과.
- 오프스크린 실행: `port_scan_timer`가 더 이상 없고(`loop_send_timer`만 존재), 시작 시 포트 3개 스캔됨, 새로고침 버튼 수동 갱신 정상.

## 2026-11-11 - New Session 다이얼로그 포트 더블클릭으로 바로 시작

변경 파일:

- `new_session_dialog.py`
- `History.md`

핵심 변경 사항:

- 포트 목록 항목을 더블클릭하면 `Start monitoring` 버튼을 누른 것과 같이 `_on_accept()`가 호출되어 다이얼로그가 바로 확정된다.
- 더블클릭한 항목이 선택 포트가 되고, 나머지 옵션(시각화 방식, Start monitoring now)은 현재 체크 상태를 그대로 따른다.
- 포트가 없을 때의 "No serial ports detected" 항목은 비활성이라 더블클릭해도 동작하지 않는다.

검증 결과:

- `py_compile` 통과.
- 오프스크린에서 두 번째 포트를 더블클릭 → 다이얼로그 Accepted(result=1), `selected_port=COM7`, `start_now=True` 확인. 포트가 없을 때도 오류 없이 표시됨.

## 2026-11-11 - New Session 다이얼로그 정리

변경 파일:

- `new_session_dialog.py`
- `History.md`

핵심 변경 사항:

- 오른쪽의 "Choose desired visualizers"(Dump view / Terminal view 체크박스) 영역을 제거했다.
- "Start in new window" 체크박스(비활성 상태였음)를 제거했다.
- 시각화 방식은 기존 기본값인 Dump view로 고정된다. (`selected_visualizer`는 `"Dump view"` 유지, 로그 형식이 String이면 HEX 없이 출력되는 동작은 그대로)
- 포트 목록이 다이얼로그 전체 폭을 사용한다.
- "Note: you can select multiple ports" 안내 문구도 제거했다.
- 다이얼로그 가로 폭을 520px에서 312px로 40% 줄였다. (`setMinimumWidth(312)` + 초기 `resize(312, ...)`)

검증 결과:

- `py_compile` 통과.
- 오프스크린 실행: 다이얼로그 정상 표시, 포트 더블클릭 시 `selected_port`, `selected_visualizer == "Dump view"` 확인.

## 2026-11-11 - 명령어 목록 SEND 버튼화 및 전송 데이터 저장

변경 파일:

- `UI/mainWindow.ui`
- `main_window.py`
- `History.md`

핵심 변경 사항:

- 명령어 목록의 `CMD00`~ 버튼 글자를 모두 `SEND`로 변경했다. 동적으로 추가되는 행도 동일하며, 어느 행인지 알 수 있도록 툴팁(`NN번 전송 데이터 보내기`)과 HEX 오류 메시지(`SEND NN`)에 행 번호를 표시한다.
- 열 헤더 `포트명`을 `전송데이터`로 변경했다.
- 전송 데이터를 `QSettings("CasaSerial", "CasaSerial")`에 저장한다.
  - 저장 항목: 행별 입력 텍스트, HEX 체크, CR+LF 체크, 행 개수(최대 20)
  - 저장 시점: 앱 종료 시, SEND 전송 성공 시
  - 복원 시점: 앱 시작 시 (HEX 행은 변환 없이 그대로 복원)
- 저장 위치: Windows는 레지스트리 `HKCU\Software\CasaSerial\CasaSerial`, macOS는 `~/Library/Preferences`.

검증 결과:

- `py_compile` 통과.
- 오프스크린 왕복 테스트(임시 ini 파일 사용): 행 12개로 늘려 입력 텍스트/HEX/CR+LF를 설정 → 종료 → 재시작 시 행 수와 값이 그대로 복원됨. 모든 버튼 글자 `SEND`, 헤더 `전송데이터` 확인.

## 2026-11-11 - 한글 폰트를 나눔스퀘어로 변경

변경 파일:

- `main.py`
- `History.md`

핵심 변경 사항:

- `Fonts/NanumSquareL/R/B/EB.ttf` 4종을 앱 시작 시 등록하고, 기본 폰트 패밀리를 `["Inter", "NanumSquare"]`로 지정했다. 영문/숫자는 기존대로 Inter, 한글은 Inter에 글리프가 없어 NanumSquare로 표시된다. (이전에는 시스템 기본 한글 폰트로 대체 표시)
- 로그 영역(`D2Coding`, 고정폭)은 변경하지 않았다.
- 빌드 스크립트(`build_win.bat`, `build_mac.sh`)는 `Fonts` 폴더 전체를 데이터로 포함하므로 수정이 필요 없다.

검증 결과:

- `py_compile` 통과.
- 오프스크린 확인: Inter는 한글 글리프 미지원, NanumSquare는 지원 → 한글이 NanumSquare로 대체됨. 전체 창 렌더링 정상.

## 2026-11-11 - 블루투스(BLE) 스캔 및 Nordic UART Service(NUS) 연결

변경 파일:

- `ble_worker.py` (신규)
- `ble_scan_dialog.py` (신규)
- `settings.py`
- `monitor_subwindow.py`
- `main_window.py`
- `requirements.txt`
- `build_mac.sh`
- `README.md`
- `History.md`

핵심 변경 사항:

- 툴바의 `포트 새로고침` 옆에 `블루투스 스캔` 버튼을 추가했다.
- 버튼을 누르면 `BleScanDialog`가 열린다. 열려 있는 동안 계속 스캔하며 장치 목록을 갱신한다.
  - 필터 입력창: 장치 이름 또는 주소에 포함된 글자로 목록을 거른다.
  - `연결` 버튼(또는 장치 더블클릭)으로 선택한 장치에 연결한다. 이름이 있는 장치가 위, 신호 세기 순으로 정렬한다.
- 연결하면 새 세션 서브창(Dump view)이 만들어지고, 기존 시리얼 세션과 같은 송수신 경로(하단 전송, CMD의 SEND, 반복 전송, 로그 형식)를 그대로 사용한다.
- 블루투스가 연결(연결 시도 중 포함)되면 툴바 버튼이 `블루투스 연결종료`로 바뀌고, 누르면 연결을 끊고 다시 `블루투스 스캔`으로 돌아온다. 연결이 끊긴 BLE 세션에서는 기존 `연결 열기` 버튼으로 같은 장치에 재연결할 수 있다.
- `BleWorker`(QThread + asyncio + bleak): NUS 서비스(6E400001…)의 TX 특성(6E400003, notify)으로 수신, RX 특성(6E400002)으로 송신. 송신은 MTU에 맞춰 분할 전송하고, 수신 notify는 10ms 단위로 모아서 한 번에 로그에 표시한다. `SerialWorker`와 같은 시그널/메서드를 제공한다.
- 장치에 NUS가 없거나, 연결 실패, 연결 끊김, bleak 미설치 시 오류 메시지를 세션 로그와 상태바에 표시한다.
- `BleSettings`(`settings.py`) 추가. `requirements.txt`에 `bleak>=0.22` 추가.
- `build_mac.sh`: macOS가 요구하는 블루투스 사용 목적 문구(`NSBluetoothAlwaysUsageDescription`)를 앱 `Info.plist`에 넣고 ad-hoc 재서명하도록 추가했다. (macOS 실기기에서는 검증하지 못함)

검증 결과:

- `BleWorker`를 가짜 BLE 클라이언트로 시나리오 7종 검증: 정상 송수신(수신 합치기, 20바이트 단위 분할 송신, 종료 시 disconnect), NUS 서비스 없음, 연결 실패, 연결 중 중단, 미연결 상태 송신, 원격 연결 끊김, 스캐너 스레드. 모두 통과.
- UI 흐름을 가짜 클라이언트로 검증(23항목 통과): 스캔 다이얼로그(목록, 이름/주소 필터, 선택, 더블클릭 연결, 스캐너 종료), 버튼 `블루투스 스캔` ↔ `블루투스 연결종료` 전환, SEND 전송이 NUS RX로 기록, 수신 데이터 로그 표시, 연결 종료, `연결 열기`로 재연결, 연결된 상태에서 창 닫기.
- 검증 중 발견해 수정: 스레드가 이미 끝난 뒤 `stop()`/`write_data()`를 호출하면 `RuntimeError: Event loop is closed`가 나던 문제.
- 이 PC의 실제 블루투스 어댑터로 스캔 확인(약 60개 장치 검색, 필터 동작, 다이얼로그 종료 시 스캔 스레드 종료). 임의 장치에는 연결하지 않았다.
- PyInstaller 빌드(Windows) 확인: `winrt` 및 `bleak.backends.winrt`가 자동 포함되어 빌드 옵션 변경이 필요 없었고, 빌드된 exe가 정상 기동했다.
- 실제 NUS 장치와의 연결/송수신은 아직 검증하지 못했다. 실기기 확인 필요.

## 2026-11-11 - New Session 다이얼로그에 Serial / Bluetooth 탭 추가

변경 파일:

- `new_session_dialog.py`
- `ble_scan_dialog.py`
- `main_window.py`
- `README.md`
- `History.md`

핵심 변경 사항:

- New Session 다이얼로그를 `Serial` / `Bluetooth` 두 탭으로 나눴다.
  - `Serial` 탭: 기존 포트 목록(더블클릭 시 바로 시작, `Start monitoring now` 옵션 유지).
  - `Bluetooth` 탭: 필터 입력창과 장치 목록. 탭을 열 때 스캔을 시작하고, Serial 탭으로 돌아가거나 다이얼로그를 닫으면 스캔을 멈춘다. (Serial 탭에서는 스캔하지 않는다.)
- Bluetooth 탭에서는 장치를 선택해야 `Start monitoring`이 활성화되고, 장치 더블클릭으로도 바로 연결된다. Bluetooth는 항상 즉시 연결하므로 `New session options`는 비활성화된다.
- 다이얼로그 결과로 `connection_type`("serial"/"bluetooth")과 `selected_device`를 제공하고, `main_window.py`가 Bluetooth 선택 시 BLE 세션을 시작한다(툴바 `블루투스 스캔` 버튼과 같은 경로).
- 스캔 UI를 재사용할 수 있도록 `ble_scan_dialog.py`를 `BleScanPanel`(필터 + 장치 목록 + 스캔 제어)과 `BleScanDialog`(툴바 버튼용 독립 다이얼로그)로 분리했다. 장치 목록은 이름 / `주소 · 신호세기` 두 줄로 표시해 312px 폭에서도 잘리지 않게 했다.
- 툴바의 `블루투스 스캔` / `블루투스 연결종료` 버튼은 그대로 유지했다.

검증 결과:

- 오프스크린 + 가짜 스캐너/클라이언트로 검증(37항목 통과): 탭 구성, Serial 탭에서 스캔 안 함, Bluetooth 탭에서 스캔 시작, 탭 전환 시 스캔 정지/재시작, 장치 선택 전 시작 버튼 비활성, Bluetooth 더블클릭 연결, Serial 더블클릭 동작 유지, 장치 미선택 시 시작 무동작, 메인 창에서 New Session → Bluetooth 연결/툴바 버튼 `블루투스 연결종료` 전환/해제, 이전 BLE 기능 전체 회귀.
- 폰트를 로드한 상태로 Bluetooth 탭을 렌더링해 폭(312px) 안에서 목록이 잘리지 않는 것을 확인.

## 2026-11-11 - 새 세션 창 최대화 및 메뉴바 창 버튼 숨김

변경 파일:

- `main_window.py`
- `monitor_subwindow.py`
- `History.md`

핵심 변경 사항:

- 새 세션 창(New Session, 블루투스 연결, 파일 열기 모두)을 항상 최대화 상태로 열어 작업 영역을 꽉 채운다. (`_create_monitor_subwindow`에서 `showMaximized()`, 파일 열기도 같은 함수를 사용하도록 정리)
- 최대화되면 메뉴바 오른쪽에 나타나던 최소화/복원/닫기 버튼과 왼쪽 시스템 메뉴 아이콘이 나오지 않도록 `MonitorSubWindow`의 창 플래그에서 시스템 메뉴/최소화·최대화/닫기 힌트를 제거했다.
- 닫기 버튼이 없어져 세션을 닫을 방법이 필요하므로 `세션` 메뉴에 `세션 닫기`(Ctrl+W)를 추가했다. 현재 활성 세션 창을 닫으며, 연결 중이면 연결을 종료하고 닫는다.
- 세션이 여러 개일 때는 활성 세션만 화면을 채우고, 닫으면 아래 세션이 다시 최대화된다.

검증 결과:

- 오프스크린: 새 세션 생성 시 최대화됨, 메뉴바 코너 위젯(버튼/아이콘) 없음, 두 번째 세션이 작업 영역과 같은 크기, `세션 닫기`(Ctrl+W)로 활성 세션 닫힘 확인. 렌더링 화면으로 메뉴바 오른쪽 버튼이 사라진 것 확인.
- 이전 BLE/세션 흐름 회귀 테스트 전체 통과.

## 2026-11-11 - 세션이 열려 있을 때 새 세션은 별도 창으로 열기

변경 파일:

- `main_window.py`
- `History.md`

핵심 변경 사항:

- 세션이 이미 열려 있는 창에서 새 세션(NEW, 툴바 블루투스 스캔, 파일 열기)을 열면, 같은 창 안이 아니라 **운영체제의 별도 창(새 `CasaSerialWindow`)**에 세션을 연다.
  - 다이얼로그에서 확인(연결)을 눌렀을 때만 새 창을 만든다. 취소하면 아무것도 만들지 않는다.
  - 새 창은 기존 창보다 오른쪽 아래로 40px 어긋나게, 같은 크기로 열린다.
  - 각 창은 자체 툴바, 전송 패널, CMD 목록, 연결 설정, 블루투스 버튼을 가지므로 별도 창에서도 송수신이 가능하다.
  - 세션이 없는 빈 창(처음 창, 세션을 닫은 창, 새로 열린 창)에서 NEW를 누르면 새 창을 만들지 않고 그 창에 세션을 연다.
- 각 창 안의 세션은 계속 창을 꽉 채워 열린다(최대화). 앞서 넣었던 같은 창 안에서 나란히 배치(tile)하는 동작은 제거했다.
- 별도 창은 `WA_DeleteOnClose`로 닫을 때 정리되며, 창을 닫으면 그 창의 세션 연결도 함께 종료된다. 다른 창의 세션은 영향받지 않는다.
- 참고: CMD 전송 데이터는 창을 닫거나 전송할 때 저장되므로, 여러 창을 동시에 쓰면 마지막에 저장한 창의 내용이 남는다. 같은 시리얼 포트를 여러 창에서 열 수는 없다(운영체제 제한).

검증 결과:

- 오프스크린(가짜 대화상자/가짜 BLE 클라이언트): 첫 NEW는 현재 창 사용(최대화), 두 번째 NEW는 별도 최상위 창(오프셋, 세션 최대화, 기존 창 그대로), 새 창에서 NEW하면 세 번째 창, 세션을 닫은 빈 창은 재사용, 창을 닫으면 목록에서 제거, 툴바 블루투스 연결도 세션이 있으면 새 창에서 열리고 해당 창의 버튼만 `블루투스 연결종료`로 바뀌며 해제됨을 확인.
- 이전 BLE/세션 흐름 회귀 테스트 전체 통과.

## 2026-11-11 - CMD 전송 데이터를 연결 대상별로 저장

변경 파일:

- `main_window.py`
- `monitor_subwindow.py`
- `settings.py`
- `History.md`

핵심 변경 사항:

- CMD 목록(행별 입력 텍스트, HEX, CR+LF, 행 개수)을 하나로 공유하던 방식에서, **연결 대상별**로 따로 저장하도록 변경했다.
  - 시리얼: 포트 이름(예: `COM7`, macOS는 `/dev/cu...`)
  - 블루투스: 장치 이름. 이름이 없는 장치는 주소로 구분한다. (같은 이름의 장치는 같은 목록을 공유)
- 세션을 열거나 다른 세션 창으로 전환하면 CMD 패널이 그 대상의 목록으로 바뀐다. 전환 직전에 이전 대상의 내용을 저장한다. 저장 시점은 SEND 전송 성공, 대상 전환, 창 닫기이다.
- 처음 연결하는 대상은 빈 목록(10행)으로 시작한다.
- 같은 세션을 다른 포트로 다시 연결하면 그 포트의 목록으로 바뀌고, 원래 포트로 돌아오면 이전 내용이 그대로 보인다.
- 세션이 없을 때와 파일 열기 세션(연결 대상 없음)에서는 CMD 패널을 바꾸거나 저장하지 않는다. 시작 직후 세션이 없는 동안 입력한 내용은 저장되지 않는다.
- 별도 창마다 자기 세션의 대상에 맞는 목록을 보여 준다. 같은 대상을 두 창에서 쓰면 마지막에 저장한 쪽이 남는다.
- `SerialSettings.cmd_key`, `BleSettings.cmd_key`, `MonitorSubWindow.cmd_key`를 추가했다. 포트 경로의 `/` 등은 URL 인코딩해 저장 경로로 해석되지 않게 했다.
- 이전 버전이 저장하던 단일 CMD 목록(`cmd_entries`)은 자동으로 옮기지 않는다. 설정에 남아 있지만 더 이상 사용하지 않는다.

검증 결과:

- 오프스크린 + 임시 ini 설정으로 18항목 검증: 세션 없음 상태, 시리얼/이름 있는 BLE/이름 없는 BLE(주소 키)별 분리 저장, 전환 시 복원(텍스트, HEX 및 검증기, CR+LF, 행 수), 연결 대상 없는 세션은 패널 유지, 같은 세션의 포트 변경, 재시작 후 복원, 같은 이름의 다른 주소 BLE 복원, `/` 포함 포트 경로, 두 창의 독립 동작. 모두 통과.
- 이전 BLE/세션 흐름 및 워커 회귀 테스트 전체 통과.

## 2026-11-11 - 블루투스 세션에서 전송 설정 흐리게 표시 및 연결 상태 표시

변경 파일:

- `main_window.py`
- `UI/mainWindow.ui`
- `History.md`

핵심 변경 사항:

- 블루투스 세션이 활성일 때 `전송 설정` 영역의 시리얼 설정(포트, 보드레이트, 데이터 비트, 패리티, 흐름 제어, 정지 비트)의 입력창과 라벨을 모두 흐리게(비활성) 표시한다. 연결 여부와 상관없이 블루투스 세션에서는 시리얼 설정이 의미 없기 때문이다. `연결 열기/닫기` 버튼은 그대로 사용할 수 있다.
- `전송 설정` 제목 옆에 `기기명 연결됨`(이름이 없는 장치는 BD 주소)을 표시한다. 연결이 끊기면 `기기명 연결 해제됨`으로 바뀐다. 시리얼 세션이나 세션이 없을 때는 표시하지 않는다.
- 세션을 전환하면 해당 세션 종류에 맞게 다시 활성/흐림 상태와 라벨이 바뀐다. 세션이 모두 닫히면 시리얼 설정이 다시 활성화된다.
- `.ui` 스타일시트에 비활성 라벨/콤보박스 스타일(`QLabel:disabled`, `QComboBox:disabled`)을 추가했다.

검증 결과:

- 오프스크린 8항목 통과: 세션 없음 상태, BLE 연결 시 라벨(`nFor20-t01 연결됨`)과 흐림, 연결 해제 시 `연결 해제됨`과 흐림 유지, 이름 없는 장치의 주소 표시, 시리얼 세션 전환 시 복원, BLE 세션으로 복귀 시 다시 흐림, 세션 모두 닫으면 복원. 렌더링 화면으로 모양 확인.
- 이전 BLE UI / CMD 대상별 저장 / 워커 회귀 테스트 전체 통과.

## 2026-11-11 - Windows 설치 파일(setup.exe) 빌드 추가

변경 파일:

- `installer/CasaSerial.iss` (신규)
- `build_setup.bat` (신규)
- `.gitignore`
- `packaging.md`
- `README.md`
- `History.md`

핵심 변경 사항:

- Inno Setup 6 스크립트(`installer/CasaSerial.iss`)와 빌드 스크립트(`build_setup.bat [버전] [--skip-build]`)를 추가했다. 앱을 PyInstaller로 빌드한 뒤 설치 파일을 만든다.
- 빌드 결과는 모두 `WIN` 폴더 아래에 생성된다: `WIN\CasaSerial`(앱), `WIN\Setup\CasaSerial_Setup_<버전>.exe`(설치 파일), `WIN\build`, `WIN\spec`.
- 설치 파일: 관리자 권한 없이 사용자 폴더에 설치(필요하면 모든 사용자용 선택 가능), 시작 메뉴 바로가기, 선택 가능한 바탕화면 아이콘, 제거 항목 등록, 설치 후 실행 옵션, 한국어/영어 지원.
- `.gitignore`에 `WIN/`, `MAC/`(빌드 결과)를 추가했다.
- `build_setup.bat`에서 `build_win.bat`를 `call "%~dp0build_win.bat"`로 호출하도록 했다. (현재 폴더 기준 호출은 이 환경에서 찾지 못함)

검증 결과:

- `build_setup.bat 0.01.202`로 앱 빌드와 설치 파일 생성 성공(`CasaSerial_Setup_0.01.202.exe`, 약 37MB).
- 설치 파일을 임시 폴더에 무음 설치해 확인: 파일 282개 설치, 제거 항목 등록(`CasaSerial 0.01.202`), 시작 메뉴 바로가기 생성, 설치된 앱이 정상 기동. 이어서 제거하자 설치 폴더, 제거 항목, 바로가기가 모두 삭제됨.
- 빌드 후 WIN 폴더 밖에 새로 생긴 산출물이 없음을 확인.

## 2026-11-12 - 앱 아이콘 바깥쪽 투명 처리

변경 파일:

- `image/CASA_Serial_APP_ICON.png`
- `image/CasaSerial.ico`
- `History.md`

핵심 변경 사항:

- 원본 아이콘은 투명도 없는 RGB 이미지였고, 둥근 사각형 바깥쪽이 흰색(약 251~254)으로 채워져 있었다. 이미지 가장자리에서 이어지는 흰색 배경만 투명하게 바꿨다. 아이콘 안쪽의 흰색 고리(하단 노트 링 구멍)는 가장자리와 이어져 있지 않으므로 그대로 불투명하게 유지된다.
- 가장자리는 1px 깎고 살짝 블러해 부드럽게 만들고, 가장자리 픽셀 색은 가장 가까운 아이콘 색으로 채워 흰 테두리(헤일로)가 남지 않게 했다.
- `CASA_Serial_APP_ICON.png`(창 아이콘, macOS 아이콘 원본)를 RGBA로 교체했다.
- `CasaSerial.ico`는 256px 하나뿐이던 것을 16/24/32/48/64/128/256 크기의 다중 크기 아이콘으로 다시 만들었다. (작업 표시줄, 탐색기, 제목 표시줄에서 알맞은 크기가 쓰이도록)
- 원본 파일은 git 이력(`V.0.01.202` 이전 커밋)에 남아 있다.

검증 결과:

- PNG 알파: 네 모서리 0(투명), 중앙 255(불투명), 투명 약 9.2%.
- 어두운 배경/파란 배경/흰 배경에 합성해 흰 테두리 없이 모서리가 깨끗한 것을 확인. 16~64px 축소본도 확인.
- 다시 빌드한 `CasaSerial.exe`와 `CasaSerial_Setup_0.01.202.exe`에서 추출한 아이콘의 모서리 알파가 0(투명)임을 확인.

## 2026-11-12 - 블루투스 아이콘 하단 잘림 복원, 색상 통일, 선 굵기 보정

변경 파일:

- `image/icons/bluetooth.png`
- `History.md`

핵심 변경 사항:

- 추가된 `bluetooth.png`(481x439)는 원이 아래쪽에서 잘려 있었다(원이 위쪽 여백 15px 기준으로 y=466까지 이어져야 하는데 이미지가 439px에서 끝남). 보이는 원 테두리의 가장자리 점들로 원을 정밀하게 맞춰(바깥 반지름 약 225px, 안쪽 약 205px, 중심 (241.5, 240.6)) 잘린 아래쪽 호를 같은 색(`#1F84CE`)으로 다시 그려 이었다. 기존 픽셀은 그대로 두고 잘린 부분만 추가했다.
- 캔버스를 481x481(정사각형)로 늘려 위쪽과 같은 여백(약 15px)을 아래에도 두었다. 투명 배경(RGBA)과 해상도는 그대로다.
- 원본(잘린 파일)은 임시 폴더에 백업해 두었다.
- 선 굵기를 약 20px에서 약 27px로 조금 더 두껍게 했다(선 양쪽으로 3.5px씩 확장, 끝과 모서리는 둥글게 유지). 다른 선 아이콘의 굵기(약 28~40px / 512px 기준)에 가까워졌다. 두꺼워진 만큼 한쪽으로 치우친 여백을 바로잡아 위/아래/좌/우 여백을 모두 11px로 맞췄다.
- 색을 `image/icons`의 다른 아이콘과 같은 단색 `#A87443`(168,116,67)으로 바꿨다. 투명도(안티앨리어싱 알파)는 그대로 두었다. 흰색 불투명 픽셀은 없었고(바깥/안쪽은 처음부터 투명), 흰색에 가까운 픽셀이 있으면 투명으로 바꾸는 처리를 함께 적용했다(해당 0개).

검증 결과:

- 이음새가 보이지 않는지 흰 배경/어두운 배경에 합성해 확인했고, 하단 가장자리의 불투명 픽셀이 0개임을 확인했다. 알파가 있는 모든 픽셀의 색이 `(168,116,67)` 하나뿐임을 확인하고 `CONNECT.png`와 나란히 놓아 색을 비교했다. 이 아이콘은 아직 앱 UI에서 사용하지 않는다.

## 2026-11-12 - 툴바 버튼을 새 이미지(BT_SCAN, reload)로 교체

변경 파일:

- `main_window.py`
- `image/buttons/reload.png` (사용자가 수정한 이미지)
- `image/buttons/BT_SCAN.png` (사용자가 추가한 이미지)
- `image/buttons/BT_DISCONNECT.png` (신규, 임시)
- `History.md`

핵심 변경 사항:

- 사용자가 `포트 새로고침` 글자를 `새로고침`으로 고친 `reload.png`와 블루투스 아이콘이 있는 `BT_SCAN.png`(`스 캔`)를 툴바 버튼 이미지로 사용한다. 새 이미지는 1120x580이라 두 버튼 크기를 138x58에서 이미지 비율에 맞는 112x58로 바꿨다(`TOOLBAR_IMAGE_BUTTON_SIZE`). 비율이 달라 이미지가 늘어나 보이던 문제를 막기 위한 변경이다.
- 블루투스 버튼은 평소 `BT_SCAN.png`, 연결 중에는 `BT_DISCONNECT.png`로 바뀐다. (`BT_DISCONNECT.png`는 `BT_SCAN.png`의 카드와 아이콘을 그대로 쓰고 글자만 `연결종료`로 바꾼 임시 이미지이며, 같은 이름으로 덮어써서 교체할 수 있다. 글꼴은 사용자 이미지와 가장 비슷한 맑은 고딕 굵게.) 마우스를 올리면 툴팁으로 `블루투스 스캔` / `블루투스 연결종료`가 표시된다.
- 이전에 넣었던 텍스트+아이콘 방식(QIcon, `image/icons` 빌드 포함 설정)은 이미지 방식으로 바뀌어 제거했다. `image/icons/bluetooth.png`는 현재 앱에서 쓰지 않는다. (`image/buttons`는 이미 빌드에 포함된다.)

검증 결과:

- 오프스크린 렌더링: 두 버튼이 112x58로 이미지 비율 그대로 표시되고, 연결 상태 전환 시 `BT_DISCONNECT.png`로 바뀜. 이전 BLE UI / CMD 대상별 저장 / 전송 설정 흐림 / 워커 회귀 테스트 전체 통과.

## 2026-11-12 - 명령어 목록 SEND 버튼을 이미지 버튼으로 교체

변경 파일:

- `main_window.py`
- `image/buttons/SEND.png` (사용자가 추가한 이미지)
- `History.md`

핵심 변경 사항:

- 명령어 목록의 `SEND` 버튼(기본 10행과 `추가`로 만들어지는 행 모두)을 글자+스타일시트 버튼에서 `SEND.png` 이미지 버튼으로 바꿨다. 크기는 이미지(718x418) 비율에 맞춰 67x38로 했다(`CMD_SEND_BUTTON_SIZE`). 다른 이미지 버튼(추가/삭제 등)과 같은 방식(`_apply_image_button`)이다.
- 어느 행의 버튼인지 구분할 수 있도록 마우스를 올리면 `NN번 전송 데이터 보내기` 툴팁이 표시된다.
- 더 이상 쓰지 않는 SEND 버튼용 스타일시트(`_CMD_BTN_STYLE`)를 제거했다.
- 참고: 사용자가 `image/buttons`의 다른 버튼 이미지도 가장자리 여백을 늘린 새 버전으로 교체했다(크기가 가로세로 약 20px씩 커짐). 비율 차이가 작아 기존 버튼 크기 설정은 그대로 두었다. `reload.png`만 비율이 크게 달라져 앞선 항목에서 버튼 크기를 조정했다.

검증 결과:

- 오프스크린 렌더링: 기본 행과 동적으로 추가한 행 모두 67x38 이미지 버튼으로 표시되고 기존 행 간격/정렬 유지. 이전 BLE UI / CMD 대상별 저장(`SEND` 클릭 전송 포함) / 전송 설정 흐림 / 워커 회귀 테스트 전체 통과.

## 2026-11-12 - 상단 메뉴 정리 (`보기` 제거, 도움말에 `이 앱에 관하여` 추가)

변경 파일:

- `UI/mainWindow.ui`
- `main_window.py`
- `app_resources.py`
- `README.md`
- `History.md`

핵심 변경 사항:

- 상단 메뉴에서 비어 있던 `보기` 메뉴를 제거했다. 메뉴는 `세션`, `도움말` 두 개가 남는다.
- `도움말` 메뉴에 `이 앱에 관하여`를 추가했다. 선택하면 앱 이름, 버전, 간단한 설명, 사용 기술(PyQt6 · pyserial · bleak)을 보여 주는 대화상자가 열린다.
- 버전은 `app_resources.APP_VERSION`(현재 `0.01.202`)에서 가져온다. 버전을 올릴 때 이 값과 `installer/CasaSerial.iss`의 기본 버전을 함께 바꿔야 한다.
- `README.md`에 남아 있던 "2초 간격 자동 갱신" 설명을 현재 동작(시작 시 검색, `새로고침` 버튼으로 다시 검색)에 맞게 고쳤다.

검증 결과:

- 오프스크린: 메뉴 막대가 `세션`, `도움말`뿐이고 `도움말` 아래에 `이 앱에 관하여`가 있으며, 실행하면 앱 이름/버전/설명이 담긴 대화상자 내용이 만들어짐을 확인. 이전 BLE UI / CMD 대상별 저장 회귀 테스트 통과.

## 2026-11-12 - README.md 전면 재작성

변경 파일:

- `README.md`
- `CasaSerialMonitor.png` (사용자가 갱신한 스크린샷)
- `app_resources.py`, `installer/CasaSerial.iss` (버전 `0.01.211`)
- `History.md`

핵심 변경 사항:

- README를 현재 기능과 화면에 맞춰 처음부터 다시 썼다. 목차, 주요 기능(연결 / 송신 / 수신 로그 / 화면), 화면 구성 표, 사용 방법(시리얼 / 블루투스 / 여러 세션과 별도 창 / 명령어 목록), 단축키, 저장되는 설정, 요구 사항, 설치 및 실행, 빌드와 설치 파일 만들기, 블루투스 동작 방식(NUS UUID 표 포함), 알려진 제한 사항, 프로젝트 구조, 문서, 로드맵 순서다.
- 오래된 정보를 갱신했다: 자동 포트 갱신(제거됨), 버튼 이름(`새로고침`, `스캔`, `SEND`), 블루투스 지원, 별도 창 동작, 설치 파일 빌드, 파일 구조(`ble_*`, `installer/`, `build_setup.bat` 등), `run.bat`의 터미널 창 숨김과 `--console` 옵션.
- 코드로 확인한 사실만 적었다. 툴바의 `시작`/`일시정지`/`정지` 버튼은 비활성 자리표시자라 "알려진 제한 사항"에 명시했고, macOS 빌드/블루투스와 설치 파일 코드 서명 없음도 제한 사항에 적었다.
- 앱 버전을 `0.01.211`로 올렸다(`APP_VERSION`, 설치 스크립트 기본 버전).

검증 결과:

- README의 목차 링크(앵커)와 명시한 값(보드레이트 목록, 반복 전송 간격 범위 1 ~ 3,600,000 ms, 행 수 1 ~ 20, 단축키, 로그 최대 5,000줄, NUS UUID)을 코드/UI 파일과 대조해 확인했다.

## 2026-11-12 - 전송 설정 콤보박스에 아래쪽 화살표 표시

변경 파일:

- `main_window.py`
- `image/buttons/arrow_down.png` (신규)
- `image/buttons/arrow_down_disabled.png` (신규)
- `History.md`

핵심 변경 사항:

- 전송 설정의 콤보박스(포트, 보드레이트, 데이터 비트, 패리티, 흐름 제어, 정지 비트)에 드롭다운 화살표(▼)가 보이지 않던 문제를 고쳤다.
- 원인: `UI/mainWindow.ui`의 스타일시트가 `QComboBox::drop-down`(테두리 없음, 폭 24px)을 직접 꾸미고 있었다. Qt 스타일시트에서 이 부분을 꾸미면 기본 화살표를 더 이상 그리지 않기 때문에, `::down-arrow` 이미지를 따로 지정해야 한다. (이 규칙을 빼면 화살표가 다시 보이는 것을 확인했다.)
- `_apply_combo_arrow_style()`에서 `::down-arrow`에 작은 삼각형 이미지(10x6px, 테마 갈색 `#A87443`)를 지정했고, 비활성 상태(연결 중이거나 블루투스 세션일 때 흐리게 표시되는 경우)에는 옅은 색 이미지를 쓴다. 이미지는 이미 빌드에 포함되는 `image/buttons`에 두었다.
- 수신 데이터 영역의 로그 형식 콤보박스는 원래 화살표가 보여서 바꾸지 않았다.

검증 결과:

- 오프스크린 렌더링: 6개 콤보박스 모두 화살표 표시, 비활성 상태에서는 옅은 화살표로 표시됨. 이전 BLE UI / CMD 대상별 저장 / 전송 설정 흐림 회귀 테스트 전체 통과.

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
