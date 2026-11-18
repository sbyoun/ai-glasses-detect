# AI 스마트안경 식별 데이터베이스

시험 감독관과 시험 기관을 위해, 공개 자료로 확인한 AI 안경의 카메라·화면·블루투스 식별 가능 여부·외형 단서와 시험 부정행위 적발 사례를 모은 데이터입니다.

웹에서 보기: https://glasses.foldalpha.com

## 먼저 알아 둘 것

- **블루투스 제조사 ID 로 못 잡는 안경이 있습니다.** Rokid·XREAL·Brilliant Labs 는 블루투스 SIG 제조사 ID 목록에 업체가 없습니다(2026-11-18 확인). ID 기반 탐지 앱(예: Nearby Glasses)으로는 이 안경을 알아볼 수 없습니다.
- **카메라 없는 화면 안경**(Even Realities)은 겉모습이 일반 안경과 거의 같습니다.
- **안경만의 문제가 아닙니다.** 제63회 세무사 수석 합격자는 안경 없이 개조 계산기와 초소형 카메라·모니터를 썼다고 진술했습니다.

## 데이터

| 파일 | 내용 |
|---|---|
| [`data/glasses.yaml`](data/glasses.yaml) | 모델별 카메라·화면·무게·가격·국내 판매·블루투스 ID·외형 단서·출처 |
| [`data/ble-company-ids.yaml`](data/ble-company-ids.yaml) | 안경 업체의 블루투스 SIG 제조사 ID, 목록에 없는 업체 |
| [`data/methods.yaml`](data/methods.yaml) | 탐지 방법별로 잡는 것·못 잡는 것·비용 |
| [`data/incidents.yaml`](data/incidents.yaml) | 국내외 적발 사례와 통계 |

### 원칙

- 모든 값은 `sources` 의 공개 자료에서 왔습니다. **실기기 측정값은 없습니다.**
- 모르는 값은 `null` 로 둡니다. 추정으로 채우지 않습니다.
- 블루투스 `detectable` 은 "SIG 에 ID 가 등록돼 있는가"이지, 실제로 그 ID 를 광고하는지 잡아 본 결과가 아닙니다.
- 탐지를 피하는 방법은 다루지 않습니다.

## 기여

틀린 값, 새 모델, 실기기 스캔 결과(BLE 광고 패킷 캡처 등)는 [이슈](https://github.com/sbyoun/ai-glasses-detect/issues)나 PR 로 보내 주세요. 출처 링크가 있어야 반영합니다.

## 사이트 빌드

```sh
pip install pyyaml
python3 build.py   # site/ 에 정적 HTML·JSON 생성
```

## 라이선스

- 데이터(`data/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 코드: MIT

---

**English summary.** An open dataset for exam proctors on AI smart glasses: camera/display presence, Bluetooth SIG company IDs (and which vendors such as Rokid and XREAL are *not* registered, so ID-based scanners miss them), visual tells, detection methods with their blind spots, and reported exam-cheating incidents (mostly South Korea, 2026). Public sources only; no device measurements yet. Data CC BY 4.0, code MIT.
