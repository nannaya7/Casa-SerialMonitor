# 작업 메모

작성일: 2026-05-28

## 프로젝트 개요

앱 이름은 `CasaSerial`이다.

PyQt6와 pyserial을 사용하여 Windows 10/11 및 macOS를 지원하는 크로스 플랫폼 시리얼 포트 모니터를 개발 중이다.

목표 앱은 Eltima Serial Port Monitor의 레이아웃 감각을 참고하지만, 브랜드/아이콘/문구/세부 디자인은 직접 구현하는 독자 앱으로 만든다.

## 현재 완료 상태

현재 13단계까지 구현을 완료했다.

완료 단계:

1. 프로젝트 뼈대
2. 목표 UI 레이아웃
3. 시리얼 포트 스캔
4. 연결 설정값 매핑
5. `QThread` 기반 `SerialWorker` 구현
6. `Open` 버튼과 `SerialWorker` 연결
7. 송신 기능 구현
8. 반복 송신 기능 구현
9. 수신/송신 로그 표시 옵션 개선
10. 리팩토링과 패키징 문서화
11. Send dialog CR+LF 체크박스 및 레이아웃 개선
12. New Session 다이얼로그 구현
13. MDI 멀티 세션 아키텍처

## 주요 구현 내용

### 1단계: 프로젝트 뼈대

- `main.py` 생성
- PyQt6 `QMainWindow` 기반 `CasaSerialWindow` 클래스 추가
- 창 제목: `CasaSerial`
- 기본 크기: `1024x768`
- 메뉴: `Session`, `View`, `Help`
- 상태바 초기 메시지: `Ready`
- `requirements.txt` 생성
- 의존성: `PyQt6`, `pyserial`

### 2단계: 목표 UI 레이아웃

- 상단 툴바 추가
- 중앙 `QPlainTextEdit` 로그 영역 추가
- 하단 Send dialog 패널 추가
- 포트 설정 UI 추가:
  - Port
  - Baudrate
  - Databits
  - Parity
  - Flow control
  - Stopbits
- 송신 UI 추가:
  - 명령 입력창
  - Send 버튼
  - Send file 버튼
  - String/Hex/Dec/Oct/Bin 라디오 버튼
  - Loop this command 체크박스
  - 반복 주기 SpinBox
  - Start loop 버튼
- 상태바 영구 표시 영역 추가:
  - 연결 상태
  - 현재 포트
  - RX 바이트 수
  - TX 바이트 수

### 2단계 보완: 반응형 레이아웃

- 중앙 로그 영역과 하단 Send dialog를 `QSplitter` 기반 구조로 변경
- 하단 Send dialog를 `QScrollArea` 안에 배치
- 작은 창에서는 하단 패널을 스크롤로 접근 가능
- 넓은 창에서는 로그 영역과 입력 영역이 자연스럽게 확장
- `760x520`, `1024x768`, `1600x900` 크기에서 오프스크린 검증 완료

### 3단계: 시리얼 포트 스캔

- `serial.tools.list_ports.comports()` 기반 포트 스캔 추가
- 앱 시작 시 자동 스캔
- `Session > Refresh Ports` 메뉴 추가
- 툴바에 `Refresh Ports` 액션 추가
- 포트 없음 상태:
  - `no serial ports detected` 표시
  - `Open` 버튼 비활성화
  - 상태바 `Port: -`
- 포트 있음 상태:
  - 콤보박스에 `장치명 - 설명` 표시
  - 실제 device 값은 item data로 보관
  - `Open` 버튼 활성화
- 스캔 실패 시 앱 종료 없이 상태바에 오류 표시

### 3단계 보완: 앱 실행 중 포트 자동 갱신

- `QTimer` 기반 자동 포트 스캔 추가
- 기본 주기: 2초
- 포트 목록이 바뀐 경우에만 콤보박스 갱신
- 앱 실행 후 USB 시리얼 장치 연결 시 재시작 없이 목록 반영
- USB 제거 시 포트 목록과 `Open` 버튼 상태 갱신
- Windows `COM3`, `COM10` 같은 포트는 숫자 기준으로 자연스럽게 정렬

### 4단계: 연결 설정값 매핑

- `SerialSettings` 데이터 클래스 추가
- `current_serial_settings()` 메서드 추가
- UI 선택값을 pyserial 설정값으로 변환:
  - Port
  - Baudrate
  - Databits
  - Parity
  - Stopbits
  - Flow control
- Baudrate 검증 추가:
  - 빈 값 오류
  - 정수가 아닌 값 오류
  - 0 이하 값 오류
- 포트가 없는 상태에서 설정 요청 시 오류 처리
- 설정 오류 메시지는 상태바와 `last_settings_error`에 기록

### 5단계: QThread 기반 SerialWorker 구현

- `SerialWorker(QThread)` 클래스 추가
- `SerialSettings`를 받아 pyserial 포트를 여는 `_open_serial()` 구현
- 별도 thread에서 수신 루프 실행
- 수신 bytes를 `data_received` signal로 전달
- 오류 메시지를 `error_occurred` signal로 전달
- 포트 열림/닫힘 상태를 `port_opened`, `port_closed` signal로 전달
- 안전 종료용 `stop()` 메서드 추가
- 가능한 경우 pyserial `cancel_read()`로 read 대기 해제
- `SerialException`, `OSError`, 예상하지 못한 예외 처리
- 실제 장치 없이 검증 가능하도록 `serial_factory` 주입 지원

### 6단계: Open 버튼과 SerialWorker 연결

- `Open` 버튼 클릭 시 `current_serial_settings()`로 설정 검증 후 `SerialWorker` 시작
- 연결 중 `Open` 버튼을 `Close`로 변경
- 연결 중 Port, Baudrate, Databits, Parity, Flow control, Stopbits, Refresh Ports 컨트롤 잠금
- `Close` 클릭 시 worker `stop()` 호출
- 창 종료 시 worker `stop()` 후 `wait()` 수행
- 수신 bytes를 로그 영역에 표시
- RX 바이트 카운터 갱신
- worker 오류 signal을 상태바와 로그 영역에 표시
- 포트 열림/닫힘/worker 종료 signal로 연결 상태 UI 복구
- 연결 중 포트 목록이 비어져도 `Close` 버튼이 유지되도록 포트 갱신 로직 보완

### 7단계: 송신 기능 구현

- `SerialWorker.write_data()` 메서드 추가
- 송신 성공 시 `bytes_written` signal 발생
- 송신 실패 시 `error_occurred` signal 발생
- 수신 루프와 송신의 serial 객체 접근 보호용 I/O lock 추가
- 연결 완료 시 `Send` 버튼 활성화, 연결 해제 시 비활성화
- `Send` 버튼 클릭과 command 입력창 Enter 키로 송신
- String 포맷은 UTF-8 bytes로 송신
- Hex/Dec/Oct/Bin 포맷은 공백/콤마/세미콜론 구분 숫자 토큰을 byte로 변환해 송신
- 잘못된 숫자 토큰 또는 0~255 범위 초과 값은 상태바와 로그 영역에 오류 표시
- 송신 성공 시 TX 바이트 카운터 갱신
- 송신 성공 시 로그 영역에 `[tx]` 항목 표시

### 8단계: 반복 송신 기능 구현

- 반복 송신용 `QTimer`인 `loop_send_timer` 추가
- `Loop this command` 체크박스와 `Start loop` 버튼 연결
- `Start loop` 클릭 시 현재 명령을 즉시 한 번 송신한 뒤 설정된 주기로 반복 송신
- 반복 송신 중 `Start loop` 버튼 텍스트를 `Stop loop`로 변경
- 반복 송신 중 command 입력창, 포맷 라디오 버튼, 체크박스, interval spinbox 잠금
- `Stop loop` 클릭 시 반복 타이머 정지와 UI 상태 복구
- 연결 종료 시 반복 송신 타이머 정리
- 입력 오류 또는 송신 실패 시 반복 송신 시작 차단 또는 즉시 중지
- 반복 송신 버튼은 연결되어 있고 체크박스가 선택된 경우에만 활성화

### 9단계: 수신/송신 로그 표시 옵션 개선

- 로그 영역 최대 라인 수 제한 `5000` 적용
- 하단 패널에 `Log view` 콤보박스 추가
- 로그 표시 방식: String, Hex, Dec, Oct, Bin
- 하단 패널에 `Timestamp` 체크박스 추가
- 타임스탬프 형식: `HH:MM:SS.mmm`
- 하단 패널에 `Clear log` 버튼 추가
- 수신 로그 prefix: `[RX]`
- 송신 로그 prefix: `[TX]`
- 오류 로그 prefix: `[ERR]`
- 세션 로그 prefix: `[SESSION]`
- String 표시 모드에서 CR/LF/TAB 제어 문자를 `\r`, `\n`, `\t`로 escape 표시
- Hex/Dec/Oct/Bin 표시 모드는 RX/TX 로그 양쪽에 동일 적용
- 새 로그 입력 시 자동 스크롤 유지

### 10단계: 리팩토링과 패키징 문서화

- `SerialSettings` 데이터 클래스를 `settings.py`로 분리
- `SerialWorker` 클래스를 `serial_worker.py`로 분리
- `main.py`는 UI, 포트 스캔, 설정 매핑, 사용자 동작 연결 중심으로 정리
- 기존 연결/수신/송신/반복 송신 동작 유지
- PyInstaller 패키징 절차를 `packaging.md`에 문서화
- Windows `.exe` 생성 명령 정리
- macOS `.app` 생성 명령 정리
- 패키징 전 기본 검증 명령 정리

### 앱 이름 및 아이콘 반영

- 앱 이름을 `CasaSerial`로 통일
- Python 런타임 창 아이콘에 `image/CASA_Serial_APP_ICON.png` 적용
- Windows 빌드 이름을 `CasaSerial`로 변경
- Windows 빌드 아이콘에 `image/CasaSerial.ico` 적용
- Windows 빌드에 런타임 PNG 아이콘 리소스 포함
- macOS 빌드 이름을 `CasaSerial`로 변경
- macOS 빌드 시 PNG에서 `image/CasaSerial.icns` 자동 생성 후 앱 아이콘으로 적용
- macOS 빌드에 런타임 PNG 아이콘 리소스 포함
- 가이드 문서와 작업 문서의 앱 이름 표기를 `CasaSerial`로 반영

### 11단계 보완: Send dialog CR+LF 및 레이아웃 개선

- 포트 설정 행과 명령 입력 행 사이에 간격 추가
- 명령 입력 영역 순서 변경: `[명령 입력창] [Send] [CR+LF]`
- `CR+LF` 체크박스 추가: 체크 시 모든 포맷 송신 payload 끝에 `\r\n` 자동 추가
- 반복 송신 중 CR+LF 체크박스 잠금 처리 포함

### 12단계: New Session 다이얼로그 구현

- 툴바 NEW 아이콘 활성화 — 클릭 시 `NewSessionDialog(QDialog)` 팝업
- 다이얼로그: 포트 목록(QListWidget), 뷰어 선택(Terminal view만 활성), 세션 옵션, 캡처 옵션
- "Start monitoring" → 선택 포트를 Port 콤보에 반영, "Start monitoring now" 체크 시 즉시 오픈

### 13단계: MDI 멀티 세션 아키텍처

- 중앙 단일 `QPlainTextEdit`를 `QMdiArea`로 교체 (파란 배경, 시작 시 빈 상태)
- `MonitorSubWindow(QMdiSubWindow)` 추가:
  - 자체 로그뷰(`QPlainTextEdit`), `SerialWorker`, RX/TX 카운터 소유
  - `start(settings)` / `stop(wait)` / `write_data(payload)` / `append_log()` API
  - `state_changed` / `error_occurred` / `bytes_sent` signal 제공
  - 서브윈도우 닫기 시 연결 안전 종료
- NEW → NewSessionDialog → `MonitorSubWindow` 생성 및 MDI 영역 추가
- 여러 번 NEW 누르면 독립 세션 창 다중 생성 (동시 다중 포트 모니터링 가능)
- Send dialog Open/Close 버튼은 활성 서브윈도우 연결 제어
- 서브윈도우 포커스 전환 시 상태바 자동 갱신
- Log view / Timestamp / Clear log 는 활성 서브윈도우에 적용

## 현재 파일

- `main.py`: 현재 앱 구현 코드 (`MonitorSubWindow`, `NewSessionDialog`, `CasaSerialWindow` 포함)
- `settings.py`: pyserial 연결 설정 데이터 클래스
- `serial_worker.py`: QThread 기반 시리얼 I/O worker
- `requirements.txt`: Python 의존성
- `run.bat`: Windows 실행 스크립트
- `run_mac.sh`: macOS 실행 스크립트
- `build_win.bat`: Windows용 CasaSerial 빌드 스크립트
- `build_mac.sh`: macOS용 CasaSerial 빌드 스크립트
- `packaging.md`: Windows/macOS PyInstaller 패키징 가이드
- `image/CASA_Serial_APP_ICON.png`: 런타임 아이콘 원본
- `image/CasaSerial.ico`: Windows 빌드 아이콘
- `ai_collaboration_serial_monitor_guide.md`: 개선된 개발 가이드 및 단계별 프롬프트
- `serial_monitor_ai_collaboration_review.md`: 초기 리뷰/개선 의견 정리
- `History.md`: 단계별 개발 이력
- `Target_APP.png`: 목표 UI 참고 이미지
- `memory.md`: 현재 작업 재개용 메모

## 실행 방법

필요 패키지 설치:

```powershell
pip install -r requirements.txt
```

앱 실행:

```powershell
.\run.bat
```

배치 파일 확인:

```powershell
cmd /c run.bat --check
```

## 최근 검증 결과

통과한 검증:

- `python -m py_compile main.py`
- 1단계 PyQt6 기본 창 생성 검증
- 2단계 UI 생성 및 초기 상태 검증
- 반응형 레이아웃 오프스크린 검증
- 3단계 포트 스캔 검증
- 앱 실행 중 포트 자동 갱신 검증
- 4단계 설정값 매핑 검증
- 5단계 `SerialWorker` 가짜 수신 루프 검증
- 5단계 포트 열기 실패 오류 signal 검증
- 6단계 `Open` 버튼과 worker 연결 검증
- 6단계 가짜 수신 데이터 로그/RX 카운터 갱신 검증
- 6단계 포트 열기 실패 UI 복구 검증
- 6단계 연결 중 포트 목록 비어짐 상태의 `Close` 버튼 유지 검증
- 7단계 String 송신 검증
- 7단계 Hex 송신 검증
- 7단계 잘못된 숫자 토큰과 byte 범위 초과 입력 검증
- 7단계 송신 실패 오류 signal/UI 표시 검증
- 8단계 반복 송신 시작/중지 검증
- 8단계 반복 송신 중 command 입력과 포맷 컨트롤 잠금/복구 검증
- 8단계 연결 종료 시 반복 송신 타이머 정리 검증
- 8단계 잘못된 입력으로 반복 송신이 시작되지 않는지 검증
- 8단계 반복 송신 중 write 실패 시 타이머 정지 검증
- 9단계 String 로그 prefix와 CR/LF escape 표시 검증
- 9단계 Hex 로그 표시와 타임스탬프 표시 검증
- 9단계 Dec/Oct/Bin 로그 표시 포맷 검증
- 9단계 최대 로그 라인 수 제한 검증
- 9단계 `Clear log` 버튼 검증
- 10단계 `python -m py_compile main.py settings.py serial_worker.py`
- 10단계 리팩터링 후 Open/Receive/Send/Close 통합 검증
- `cmd /c run.bat --check`
- `image/buttons` 기반 상단/하단 이미지 버튼 오프스크린 로딩 검증
- CMD 패널 `plus`/`minus` 이미지 버튼 로딩 및 크기 검증
- 하단 전송 설정 패널 로그 옵션 정렬 및 아래 여백 검증
- `build_win.bat --check`에서 `image/buttons` 데이터 경로 포함 확인

## 현재 UI 메모

- 상단 툴바는 `image/buttons` PNG 이미지 버튼을 사용한다.
  - 왼쪽: `open`, `save`, `start`, `pause`, `stop`, `erase`
  - 오른쪽 끝: `reload` 포트 새로고침
  - 툴바 구분선은 사용하지 않는다.
- 우측 CMD 패널 제목은 "명령어 목록"이다.
- CMD 패널 행 추가/삭제는 `plus.png`, `minus.png` 이미지 버튼을 사용한다.
  - 버튼은 오른쪽 정렬이며 버튼 사이 간격을 둔다.
- 하단 전송 설정 패널의 주요 버튼은 이미지 버튼이다.
  - 연결 열기/닫기: `connect.png`
  - 전송: `transfer.png`
  - 반복 전송 시작/정지: `start_repeat.png`
- 하단 `파일 전송` 버튼은 현재 UI에서 제거되어 있다.
- `로그 형식`, `타임스탬프`, `지우기`는 하단 오른쪽에 정렬되어 있다.
- `로그 형식`과 `타임스탬프` 기능은 동작한다.
  - 로그 형식은 활성 `MonitorSubWindow.log_format`에 반영된다.
  - 타임스탬프는 활성 `MonitorSubWindow.timestamp_enabled`에 반영된다.

## 중요한 설계 규칙

- 지원 OS는 Windows 10/11 및 macOS
- UI는 해상도와 창 크기에 따라 자동으로 맞춰지는 반응형 레이아웃으로 구성
- 고정 좌표 배치 대신 Qt layout, size policy, stretch factor, splitter, scroll area 사용
- 단계가 완료될 때마다 `History.md`를 한국어로 갱신
- 문서, 작업 이력, 사용자 확인용 설명은 한국어로 작성
- 포트가 없거나 열기 실패해도 앱이 종료되지 않아야 함
- 앱 실행 중 USB 시리얼 장치 연결/해제 시 포트 목록이 자동 갱신되어야 함

## 다음 작업

다음에 시작할 단계 후보는 파일 송신 단계다.

다음 단계 목표:

- 파일 송신 UI 재추가
- 파일 송신 버튼 활성화
- `QFileDialog`로 송신할 파일 선택
- 선택한 파일을 bytes로 읽어 활성 `MonitorSubWindow`를 통해 송신
- 파일 선택 취소/읽기 실패/송신 실패 처리
- 큰 파일 송신이 UI를 오래 멈추지 않도록 크기 제한 또는 chunk 송신 방식 검토

다음 단계 시작 시 참고:

- 현재 `send_file_button`은 UI에서 제거되어 있으므로, 파일 송신 기능을 구현할 때 버튼/배치부터 다시 추가해야 한다.
- `MonitorSubWindow.write_data(payload)`가 내부적으로 `SerialWorker.write_data()`를 호출한다.
- 활성 서브윈도우를 `self._active_subwindow()`로 가져온 뒤 `write_data()`를 호출하면 된다.
- 작은 파일은 `write_data()` 한 번 호출로 송신할 수 있고, 큰 파일은 chunk 단위 송신 설계가 필요하다.
- worker는 `serial_worker.py`, 설정 데이터는 `settings.py`에 있다.
