# 너빼고다옴

아직 모두 모이지 않은 시간에 다음 장소와 활동을 함께 정하는 모바일 우선 웹앱 기획이다.
참가 행사: MEDILUX × 잇타 × UMC 하프해커톤.

- 일정: 2026-11-14 / 하프해커톤
- Medical: 비활성 · 관련 내용 공백 유지
- 템플릿: 1.0.0 / 준비일: 2026-10-27
- 현재 범위: 공통 지침·역할별 문서, 확정 결정 27개·기능 9개·원본 범위별 사본과 검증 기록
- 지도: 카카오지도 JavaScript API (실제 키·도메인·연동 미검증)
- 게임: 주최자가 T-Rex/물고기 점프 선택 · 20분 상한 핸디캡(물고기 최대 1.5배, 장애물 수 최대 2배)
- 채팅: MVP 후순위(여유 시) · 종료 후 24시간 조회 · 만료 조회 차단 및 매시간 DB 정리
- 와이어프레임: 사용자 요청으로 이번 작업에서 제외
- 저장소: [MEDILUX-ITTA-UMC-Half-Hackathon](https://github.com/UMC-ITTA-MEDILUX-HALF-HACKERTON/MEDILUX-ITTA-UMC-Half-Hackathon) (비공개, UMC-ITTA-MEDILUX-HALF-HACKERTON 조직)
- 기본 브랜치: main

## 처음 시작하기

1. [공통 AI 지침](AGENTS.md)을 읽는다.
2. [참여 안내](docs/start/README.md)와 [최초 질문](docs/start/ONBOARDING.md)을 확인한다.
3. 식별명·역할·세부 담당·이번 작업을 답한 뒤 개인 역할 파일을 설정한다.
4. [Plan 안내](docs/Plan/README.md)에서 필요한 원본·백업을 찾아 읽는다.

AI 도구가 AGENTS.md를 자동으로 읽는지는 도구별로 확인해야 한다.
자동으로 읽지 않는 도구에는 루트 AGENTS.md를 먼저 읽도록 명시한다.
문서상의 범위 제한은 도구의 파일 접근 권한을 기술적으로 강제하지 않는다.

## 문서 입구

- [PM 역할 지침](docs/PM/README.md)
- [Design 역할 지침](docs/Design/README.md)
- [Coding 역할 지침](docs/Coding/README.md)
- [Medical 역할 지침](docs/Medical/README.md)
- [빈 양식](docs/templates/README.md)
- [설정과 검증 기록](docs/start/VERIFICATION.md)

## 원본과 보관

기획·정책·배정·검토 기록은 Notion, 디자인은 Figma의 현재 적용본을 우선한다.
GitHub는 공통 지침·코드·기술 연결 계약의 원본이며 Plan 사본의 보관소가 된다.
온라인 원본에 접근하지 못하면 최신 원격 main의 docs와 백업 기록을 확인한다.
원격에 등록된 빈 양식도 실제 Notion·Figma 원본의 백업은 아니다. 원본 확보와 백업 상태는 별도로 확인한다.

개발 코드와 실행 설정은 기술 스택을 정한 뒤 docs 밖에 둔다.
실제로 확인하지 않은 설치·실행 명령은 이 README에 만들어 넣지 않는다.

## 현재 준비 상태

다음 장소·활동 공동 결정을 핵심으로 [팀 Notion PM](https://app.notion.com/p/418c0efa070a80c29109cd7db7143067)에 MVP 기능·흐름·게임 정책을 정리했다.
[MVP 로컬 사본](docs/Plan/MVP.md), [확정 결정](docs/Plan/DECISIONS.md), [검증 기록](docs/PM/VALIDATION-2026-11-14.md), [원본 목록](docs/start/SOURCES.yaml)을 함께 확인한다.
기획 정책은 PM-MVP-v2.2으로 확정했다. 개인별 기능 배정·기술 스택·지도와 푸시 실연동은 후속 개발 인계 사항이다.
원격 main의 적용본은 실제 커밋과 원본 개정을 함께 확인한다. 문서 검증과 제품 실행 검증을 구분한다.
개인 역할 파일은 최초 참가자의 답변 후 각자 만든다.
