# SDI 논문 — From-Scratch 분석 설계서

> 작성일: 2026-05-23  
> 목적: V1~V4 분석 경험을 바탕으로 처음부터 다시 설계하는 완결형 분석 로드맵  
> 원칙: **분석 결과를 보기 전에 모든 결정을 고정한다. 이후 수정 없음.**

---

## 0. 이 설계서가 필요한 이유

V1~V4에서 반복된 문제는 하나의 패턴으로 귀결된다.

> 분석을 먼저 돌린다 → 결과가 가설과 맞지 않는다 → 변수 분류나 모형을 수정한다 → 다음 버전으로 간다

이 사이클은 **연구자 자유도(researcher degrees of freedom)** 문제를 만든다. 어떤 결과가 나오더라도 사후에 정당화할 수 있는 선택지가 많아지면, 논문의 방법론적 신뢰성이 떨어진다.

이 설계서는 분석 시작 전에 다음을 모두 고정한다:
- F/S 변수 목록과 경계 변수의 처리 방침
- 결과변수와 그 선택 이유
- 가설 지지 기준 (어떤 수치가 나와야 "지지"인가)
- 건설업 불지지 결과의 프레이밍
- 민감도 분석 방법과 판단 기준

---

## 1. 연구 가설

### 1-1. 핵심 명제

> **기업은 정부 규제·과징금을 피하려 "서류상 안전(형식)"에는 투자하지만, "실제로 사고를 줄이는 안전(실질)"은 방치한다. 이 괴리를 SDI = Substantive − Formal로 수치화한다.**

- **SDI < 0** → 형식 > 실질 → 안전 형식주의(safety decoupling)
- **SDI > 0** → 실질 > 형식 → 진짜 안전
- **SDI ≈ 0** → 균형

### 1-2. 가설 계층 (3수준)

| 수준 | 조건 | 검증 방법 | 해석 |
|------|------|----------|------|
| **수준 1 (필수)** | β_SDI > 0, p < 0.05 | 모형 A: `ra_score ~ SDI + controls` | SDI가 위험성평가 실질성을 양(+)으로 예측 |
| **수준 2 (강화)** | β_S > β_F, Wald p < 0.05 | 모형 B: `ra_score ~ F_score + S_score + controls` | 실질 효과가 형식 효과보다 통계적으로 큼 |
| **수준 3 (최강)** | 수준 1+2 유지 + 민감도 분석 방향 동일 | Q17_13 재분류 후 재실행 | 분류 선택에 결론이 의존하지 않음 |

**부분 지지 처리 기준:**
- β_SDI > 0이지만 p > 0.05 → "방향 일치, 통계적 불확실"로 기술
- β_S > β_F이지만 Wald p > 0.05 → "방향 일치, 유의하지 않음"으로 기술
- 건설업 불지지 → 사전 예측된 이질성으로 프레이밍 (아래 §2-2 참조)

---

## 2. 사전 고정 결정사항 (Pre-Analysis Plan)

분석 코드를 한 줄도 작성하기 전에 아래 결정들이 확정되어야 한다.

### 결정 1: Q17_13은 Formal에 유지

**Q17_13**: "우리 사업장은 안전 시설·장비·보호구를 **갖추고 있다**"

| 분류 기준 | 결론 |
|-----------|------|
| 이론적 정의 | 문항이 "보유(possession)"를 묻는다 → 법적 의무 비치 여부를 근로감독 시 확인받는 항목 → Formal |
| EFA 결과 | V4에서 S 요인 적재량 0.68 → 이론적 정의와 불일치 |
| **최종 결정** | **이론적 정의 우선 원칙 → F 유지** |

EFA가 S로 적재하는 이유: Q17_13은 보호구 "보유"를 묻지만 응답자(안전담당자)는 이를 "실제로 잘 갖춰져 있는가"로 해석하는 경향이 있다. 즉, 문항의 표면(형식)과 응답 패턴(실질) 사이에 괴리가 있다. 이 사실을 논문 방법론 각주에 명시한다.

### 결정 2: 결과변수는 ra_score

| 후보 변수 | 장점 | 단점 | 결정 |
|-----------|------|------|------|
| Q27 (사고 건수) | 직관적 | 역인과 + 과소보고 이중 문제 | **제외** |
| ra_score (Q14/Q15 위험성평가 실질성) | 역인과 약화 + SDI와 구성적 독립 | 자기보고 편향 존재 | **채택** |

ra_score가 역인과를 "차단"하는 게 아니라 "약화"시킨다는 사실을 논문에 솔직하게 기술한다.

**ra_score 재코딩:**

| 원값 | 의미 | ra_score |
|------|------|----------|
| 1 | 실질적으로 실시 | 2 |
| 2 | 명목적으로 실시 | 1 |
| 3 | 실시하지 않음 | 0 |

### 결정 3: 건설업은 이질성 검증 집단

건설업에서 가설이 지지되지 않는 것은 V3/V4에서 이미 확인됐다. 이를 "실패"가 아닌 "발견"으로 처리하는 방법:

- **이론 섹션**에서 건설업 구조적 특수성(다단계 하도급, 발주자-시공사 분리 책임, 건설재해예방 전문지도기관 제도)을 미리 서술
- 이 서술이 나중에 건설업 불지지를 "이미 예측한 것"처럼 읽히게 만든다
- 결과 섹션에서 세 가지 경쟁 가설(C1: 검력 부족, C2: 측정 비동등, C3: 외생 결정 요인)을 데이터로 탐색

### 결정 4: F_score·S_score 동일 범위 표준화

SDI = S_score − F_score가 의미 있는 차이가 되려면 두 점수가 같은 범위에 있어야 한다.

- **F 변수(이진+연속 혼합):** 그룹별로 각 변수를 0~1 정규화 후 그룹 평균 → 그룹 평균들의 평균 = F_score
- **S 변수(5점 리커트):** 동일 방식 (min-max 정규화 후 그룹 composite)
- 두 점수 모두 이론적 범위 0~1

---

## 3. 데이터 구성

### 3-1. 파일 목록

| 파일 | 행 × 열 | 코드북 시트 |
|------|---------|------------|
| `data/raw/제10차_...raw_data_제조업_230824.csv` | 3,255 × 162 | 제조서비스업 |
| `data/raw/제10차_...raw_data_서비스업_230824.csv` | 2,551 × 162 | 제조서비스업 |
| `data/raw/제10차_...raw_data_건설업_230824.CSV` | 1,502 × 181 | 건설업 |
| `data/raw/__제10차_...코드북_230824.xlsx` | — | — |

- 모든 CSV 인코딩: UTF-8
- 건설업 확장자 대문자 `.CSV` 주의

### 3-2. 무응답 코드 처리 기준

| 척도 유형 | 정상 값 | NaN 처리 코드 |
|-----------|--------|--------------|
| 5점 리커트 | 1~5 | `9` |
| 4점 리커트 | 1~4 | `9` |
| 이분형 (예/아니요) | 1, 2 | `9` |
| 3~4범주 | 1~3(4) | `9` |
| 인원수 (명) | 0 이상 정수 | `999`, `99999` |
| 비율 (%) | 0~100 | `999` |

---

## 4. F/S 변수 목록 (확정)

> ⚠️ 아래 변수명은 코드북 기준이다. 분석 코드 작성 전 반드시 실데이터 열명과 대조한다.  
> 확인 방법: `sorted(df.filter(like='Q17').columns.tolist())`

### 4-1. 제조·서비스업

#### Formal 변수 (10개, 8그룹)

| 그룹 ID | 변수 코드 | 개념 | 척도 | 정규화 |
|---------|-----------|------|------|--------|
| F-M1 | `Q6` | 안전보건 전담부서 유무 | 이진 (1=예, 2=아니요) | 1→1.0, 2→0.0 |
| F-M2 | `Q8_1`, `Q8_2` | 안전관리자·보건관리자 선임 인원 (명) | 연속형 | Min-Max, 99퍼센타일 윈저화 |
| F-M3 | `Q9_1`, `Q9_2` | 안전·보건관리 위탁 전문기관 유무 | 이진 (1=있음, 2=없음) | 1→1.0, 2→0.0 |
| F-M4 | `Q10` | 산업안전보건위원회 구성·운영 여부 | 3범주 | 1(운영)→1.0, 2(미운영)→0.0, 3(모름)→NaN |
| F-M5 | `Q11` | 안전보건관리담당자 선임 여부 | 이진 (1=예, 2=아니요) | 1→1.0, 2→0.0 |
| F-M6 | `Q13_1` | KOSHA-MS 인증 취득 여부 | 이진 (1=예, 2=아니요) | 1→1.0, 2→0.0 |
| F-M7 | `Q13_2` | ISO 45001 인증 취득 여부 | 이진 (1=예, 2=아니요) | 1→1.0, 2→0.0 |
| **F-M8** | **`Q17_13`** | **안전 시설·장비·보호구 보유** | **5점 리커트** | **Min-Max ← 경계 변수, F 고정** |

**F 그룹 수: 8 / 총 변수 수: 10**

#### Substantive 변수 (21개, 7그룹)

| 그룹 ID | 변수 코드 | 개념 | 척도 | 정규화 |
|---------|-----------|------|------|--------|
| S-M1 | `Q16_2_1`~`Q16_2_7` | 위험성평가 근로자 참여·노력 (7문항) | 5점 리커트 | Min-Max |
| S-M2 | `Q17_1`, `Q17_2`, `Q17_3` | 경영진 안전 강조·우선순위·중시 (3문항) | 5점 리커트 | Min-Max |
| S-M3 | `Q17_9`, `Q17_10` | 교육·훈련 기회 제공 + 실질 효과 (2문항) | 5점 리커트 | Min-Max |
| S-M4 | `Q17_12` | 규정·절차가 사고예방에 실질적으로 도움 | 5점 리커트 | Min-Max |
| S-M5 | `Q17_15`, `Q17_16`, `Q17_17` | 근로자 표준 준수·작업거부권·자발적 개선 (3문항) | 5점 리커트 | Min-Max |
| S-M6 | `Q18_1`, `Q18_2`, `Q18_3`, `Q18_4` | 관리감독자 역량 (4문항) | 5점 리커트 | Min-Max |
| S-M7 | `Q22_2` | 작업환경측정 결과 기반 유해인자 노출 최소화 노력 | 4점 리커트 | Min-Max |

**S 그룹 수: 7 / 총 변수 수: 21**

> F-S 그룹 수: 8:7 (균형). 변수 수: 10:21 (불균형) → 그룹 composite 방식으로 해소.

### 4-2. 건설업

#### Formal 변수 (9개, 7그룹)

| 그룹 ID | 변수 코드 | 개념 | 척도 | 정규화 |
|---------|-----------|------|------|--------|
| F-C1 | `Q6` | 안전보건 전담부서 유무 | 이진 | 1→1.0, 2→0.0 |
| F-C2 | `Q8_1`, `Q8_2` | 안전관리자·보건관리자 선임 인원 | 연속형 | Min-Max, 99퍼센타일 윈저화 |
| F-C3 | `Q8_3`, `Q8_4` | 산업안전·보건 전담 직원 수 | 연속형 | Min-Max |
| F-C4 | `Q9` | 건설재해예방 전문지도기관 기술지도 수혜 | 이진 (1=받음, 2=안받음) | 1→1.0, 2→0.0 |
| F-C5 | `Q10` | 산업안전보건위원회(노사협의체) 운영 여부 | 4범주 | 위원회→1.0, 협의체→0.5, 미운영→0.0, 모름→NaN |
| F-C6 | `Q12_1` | KOSHA-MS 인증 취득 여부 | 이진 | 1→1.0, 2→0.0 |
| F-C7 | `Q12_2` | ISO 45001 인증 취득 여부 | 이진 | 1→1.0, 2→0.0 |

**F 그룹 수: 7 / 총 변수 수: 9**

#### Substantive 변수 (19개, 6그룹)

| 그룹 ID | 변수 코드 | 개념 | 척도 | 정규화 |
|---------|-----------|------|------|--------|
| S-C1 | `Q15_2_1`~`Q15_2_7` | 위험성평가 근로자 참여·노력 (7문항) | 5점 리커트 | Min-Max |
| S-C2 | `Q16_1`, `Q16_2`, `Q16_3` | 경영진 안전 강조·우선순위·중시 | 5점 리커트 | Min-Max |
| S-C3 | `Q16_9`, `Q16_10` | 교육·훈련 기회 제공 + 실질 효과 | 5점 리커트 | Min-Max |
| S-C4 | `Q16_16`, `Q16_17`, `Q16_18` | 근로자 표준 준수·작업거부권·자발적 개선 | 5점 리커트 | Min-Max |
| S-C5 | `Q17_1`, `Q17_2`, `Q17_4` | 작업반장 역할 인지·역량·재해예방 기여도 | 5점 리커트 | Min-Max |
| S-C6 | `Q21_2` | 작업환경측정 결과 기반 유해인자 노출 최소화 노력 | 4점 리커트 | Min-Max |

**S 그룹 수: 6 / 총 변수 수: 19**

### 4-3. 업종별 매핑 대응표 (건설 ↔ 제조·서비스)

| 개념 | 제조·서비스 | 건설 |
|------|------------|------|
| 전담부서 | Q6 | Q6 (동일) |
| 안전관리자 선임 | Q8_1 | Q8_1 (동일) |
| 보건관리자 선임 | Q8_2 | Q8_2 (동일) |
| 위원회 | Q10 | Q10 (동일, 범주 다름 주의) |
| KOSHA-MS | Q13_1 | Q12_1 |
| ISO 45001 | Q13_2 | Q12_2 |
| 위험성평가 참여·노력 | Q16_2_1~7 | Q15_2_1~7 |
| 경영진 강조 | Q17_1~3 | Q16_1~3 |
| 교육 효과 | Q17_9, Q17_10 | Q16_9, Q16_10 |
| 표준 준수·거부·자발 | Q17_15~17 | Q16_16~18 |
| 작업환경측정 노력 | Q22_2 | Q21_2 |

---

## 5. 통제변수

| 변수 | 제조·서비스 코드 | 건설 코드 | 처리 방법 |
|------|----------------|----------|----------|
| 종사자 규모 | `log(Q1_1)` | `log(Q4_1)` | 로그 변환, 0명 → NaN |
| 업종 더미 | `ind_mfg` (제조=1, 서비스=0) | — | 이진 |
| 고령자 비율 | `Q1_2 / Q1_1` | `Q4_2 / Q4_1` | clip(0, 1) |
| 외국인 비율 | `Q1_3 / Q1_1` | `Q4_3 / Q4_1` | clip(0, 1) |
| 여성 비율 | `Q1_4 / Q1_1` | `Q4_4 / Q4_1` | clip(0, 1) |

---

## 6. 분석 파이프라인

```
Phase 1: 데이터 전처리
    └─ 변수 존재 검증 → 무응답 NaN → 이진 재코딩 → 이상치 처리

Phase 2: 측정 모형 타당성 검증
    └─ 내적 일관성 (ω) → EFA 탐색 → 판별 타당도 → VIF 사전 점검
    ※ 이 단계 통과 후에만 Phase 3 이후로 진행

Phase 3: F_score / S_score / SDI 산출
    └─ 그룹 composite → 기술통계 → 분포 시각화

Phase 4: 주 추론 모형
    └─ 모형 A (SDI 단일) → 모형 B (F+S 분리, Wald 검정)
    └─ 건설업 동일 적용 + 업종 조절 효과

Phase 5: 강건성 검증
    └─ Q17_13 재분류 → 요인점수 대체 → 표본 제한 → 결측 처리 변경

Phase 6: 건설업 이질성 분석
    └─ 경쟁 가설 C1/C2/C3 탐색 → 측정 불변성 검증
```

---

## 7. Phase별 상세 지침

### Phase 1: 데이터 전처리

**목적:** 세 파일을 분석 가능한 상태로 만들고, 품질을 문서화한다.

**작업 순서:**

```python
import pandas as pd, numpy as np

BASE = "data/raw/"

# 1) 로드
df_mfg = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_제조업_230824.csv")
df_svc = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_서비스업_230824.csv")
df_con = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_건설업_230824.CSV")

# 2) 변수 존재 검증 (코드 작성 전 반드시 실행)
print("제조업 Q17계열:", sorted(df_mfg.filter(like='Q17').columns.tolist()))
print("제조업 Q16_2계열:", sorted(df_mfg.filter(like='Q16_2').columns.tolist()))
print("건설업 Q15_2계열:", sorted(df_con.filter(like='Q15_2').columns.tolist()))
print("건설업 Q16계열:", sorted(df_con.filter(like='Q16').columns.tolist()))
# → 출력값을 §4 변수 목록과 직접 대조하여 불일치 수정

# 3) 무응답 NaN 처리
likert_ms = [c for c in df_mfg.columns
             if c.startswith(("Q14_","Q15_","Q16_","Q17_","Q18_","Q22_"))]
df_mfg[likert_ms] = df_mfg[likert_ms].replace(9, np.nan)
df_svc[likert_ms] = df_svc[likert_ms].replace(9, np.nan)

likert_con = [c for c in df_con.columns
              if c.startswith(("Q13_","Q14_","Q15_","Q16_","Q17_","Q21_"))]
df_con[likert_con] = df_con[likert_con].replace(9, np.nan)

# 이진 변수 (Q6, Q9, Q10, Q11, Q13_1, Q13_2 등) 별도 처리
binary_ms = ['Q6','Q9_1','Q9_2','Q10','Q11','Q13_1','Q13_2']
df_mfg[binary_ms] = df_mfg[binary_ms].replace(9, np.nan)

# 인원수 변수
count_cols = ['Q8_1','Q8_2','Q8_3','Q8_4']
df_mfg[count_cols] = df_mfg[count_cols].replace([999, 99999], np.nan)
df_con[count_cols] = df_con[count_cols].replace([999, 99999], np.nan)

# 4) 이진 재코딩 (아니요=2 → 0)
def binary_recode(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map({1: 1.0, 2: 0.0})
    return df

df_mfg = binary_recode(df_mfg, ['Q6','Q9_1','Q9_2','Q11','Q13_1','Q13_2'])
df_con = binary_recode(df_con, ['Q6','Q9','Q12_1','Q12_2'])

# 5) Q10 위원회 재코딩 (제조·서비스: 3범주)
df_mfg['Q10'] = df_mfg['Q10'].map({1: 1.0, 2: 0.0, 3: np.nan})
# 건설: 4범주 (코드북 확인 후)

# 6) 이상치 윈저화 (Q8_1, Q8_2 선임 인원)
for col in ['Q8_1','Q8_2']:
    for df in [df_mfg, df_svc, df_con]:
        if col in df.columns:
            p99 = df[col].quantile(0.99)
            df[col] = df[col].clip(upper=p99)

# 7) ra_score 생성
ra_map = {1: 2, 2: 1, 3: 0}
df_mfg['ra_score'] = df_mfg['Q15'].map(ra_map)
df_svc['ra_score'] = df_svc['Q15'].map(ra_map)
df_con['ra_score'] = df_con['Q14'].map(ra_map)

# 8) 통합 (제조+서비스)
df_ms = pd.concat([df_mfg.assign(industry='제조'), df_svc.assign(industry='서비스')],
                  ignore_index=True)
```

**산출물:**
- `df_ms` (제조+서비스, n≈5,806)
- `df_con` (건설, n≈1,502)
- 결측 패턴 표: 핵심 변수별 결측률 (F/S 변수 모두 10% 미만이어야 분석 진행)

**검증 기준:**
```python
# 핵심 F/S 변수 결측률 확인
key_vars_ms = ['Q6','Q8_1','Q8_2','Q10','Q13_1','Q13_2','Q17_13',
               'Q17_1','Q17_2','Q17_3','Q17_12','Q18_1','Q22_2']
missing_pct = df_ms[key_vars_ms].isnull().mean() * 100
print(missing_pct)
# 10% 이상인 변수는 처리 방침을 결정하고 문서화
```

---

### Phase 2: 측정 모형 타당성 검증

**목적:** F_score와 S_score가 각각 구별되는 구성 개념을 측정함을 확립한다.  
**⚠️ 이 단계가 통과되지 않으면 Phase 4 추론 모형으로 진행하지 않는다.**

#### 2-1. 내적 일관성

S 변수(5점 리커트 동질 척도)는 Cronbach α 산출.  
F 변수(이진+연속 혼합)는 α가 과소 추정되므로 해석에 주의. ω가 있으면 병기.

```python
import pingouin as pg  # 또는 scipy 직접 계산

# S 변수 전체 α
s_cols_ms = ['Q16_2_1','Q16_2_2','Q16_2_3','Q16_2_4','Q16_2_5','Q16_2_6','Q16_2_7',
             'Q17_1','Q17_2','Q17_3','Q17_9','Q17_10','Q17_12',
             'Q17_15','Q17_16','Q17_17','Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']
alpha_s = pg.cronbach_alpha(df_ms[s_cols_ms].dropna())[0]
print(f"S 변수 Cronbach α: {alpha_s:.3f}")
# 기준: α > 0.70 이상이어야 단일 복합 점수로 사용 가능
```

#### 2-2. EFA — F와 S의 요인 구조 탐색

S 변수(동질 리커트) 대상으로 EFA를 실시하여 단일 요인 또는 다요인 구조를 확인한다.  
F 변수는 혼합 척도라 EFA 결과 해석에 주의.

```python
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

# S 변수 EFA (제조·서비스)
X_s = df_ms[s_cols_ms].dropna()
kmo_val = calculate_kmo(X_s)[1]
bart_p  = calculate_bartlett_sphericity(X_s)[1]
print(f"KMO: {kmo_val:.3f}, Bartlett p: {bart_p:.4f}")
# 기준: KMO > 0.60, Bartlett p < 0.05

fa = FactorAnalyzer(n_factors=2, method='principal', rotation='varimax')
fa.fit(X_s)
loadings = pd.DataFrame(fa.loadings_, index=s_cols_ms, columns=['F1','F2'])
eigenvalues = fa.get_eigenvalues()[0]
print("고유값:", eigenvalues[:5].round(3))
print(loadings.round(3))

# Q17_13 적재 위치 확인 (중요)
print("\nQ17_13 적재량:", loadings.loc['Q17_13'])
# EFA에서 어느 요인에 적재되더라도 F 고정 결정은 유지
```

#### 2-3. 판별 타당도

```python
# F_score·S_score 임시 계산 후 상관 확인 (점수 산출은 Phase 3에서 공식 수행)
def minmax(s):
    return (s - s.min()) / (s.max() - s.min() + 1e-10)

# 간략 점수
f_temp = df_ms[['Q17_13']].apply(minmax).mean(axis=1)  # F 대표
s_temp = df_ms[['Q17_1','Q17_2','Q17_3']].apply(minmax).mean(axis=1)  # S 대표
r = f_temp.corr(s_temp)
print(f"F-S 상관: r = {r:.3f}")
# 기준: r < 0.85 → 판별 타당도 확보
# r > 0.85 → F/S 구분 자체 재검토 필요
```

#### 2-4. VIF 사전 점검

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm

# 임시 F_score, S_score로 VIF 확인
X_vif = sm.add_constant(pd.DataFrame({'F_score': f_temp, 'S_score': s_temp}).dropna())
vif = pd.Series([variance_inflation_factor(X_vif.values, i)
                 for i in range(X_vif.shape[1])], index=X_vif.columns)
print("VIF:", vif)
# VIF < 10 → 모형 B(F+S 분리) 안전
# VIF > 10 → 모형 A(SDI 단일)에 의존
```

---

### Phase 3: F_score / S_score / SDI 산출

**목적:** 그룹 composite 방식으로 점수를 산출하고 기술통계를 생성한다.

```python
def minmax_col(series):
    """단일 열 min-max 정규화 (0~1)."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return series * 0.0
    return (series - mn) / (mx - mn)

def compute_group_composite(df, group_dict, label=''):
    """
    group_dict: {그룹명: [변수코드, ...]}
    각 그룹의 변수를 min-max 후 평균 → 그룹 점수
    그룹 점수들의 평균 → 최종 composite 점수
    """
    group_scores = {}
    for gname, cols in group_dict.items():
        avail = [c for c in cols if c in df.columns]
        if not avail:
            print(f"  ⚠️  [{label}] 그룹 {gname}: 변수 없음 ({cols})")
            continue
        normed = df[avail].apply(minmax_col)
        group_scores[gname] = normed.mean(axis=1)
    score = pd.DataFrame(group_scores).mean(axis=1)
    print(f"  [{label}] 그룹 수: {len(group_scores)}, 점수 범위: {score.min():.3f}~{score.max():.3f}, 평균: {score.mean():.3f}")
    return score

# ── 제조·서비스업 F/S 그룹 정의 ──
# (§4-1의 확정 목록 — 실데이터 열명 검증 후 수정)
formal_groups_ms = {
    'F-M1': ['Q6'],
    'F-M2': ['Q8_1', 'Q8_2'],
    'F-M3': ['Q9_1', 'Q9_2'],
    'F-M4': ['Q10'],
    'F-M5': ['Q11'],
    'F-M6': ['Q13_1'],
    'F-M7': ['Q13_2'],
    'F-M8': ['Q17_13'],   # 경계 변수, F 고정
}
subst_groups_ms = {
    'S-M1': ['Q16_2_1','Q16_2_2','Q16_2_3','Q16_2_4','Q16_2_5','Q16_2_6','Q16_2_7'],
    'S-M2': ['Q17_1','Q17_2','Q17_3'],
    'S-M3': ['Q17_9','Q17_10'],
    'S-M4': ['Q17_12'],
    'S-M5': ['Q17_15','Q17_16','Q17_17'],
    'S-M6': ['Q18_1','Q18_2','Q18_3','Q18_4'],
    'S-M7': ['Q22_2'],
}

print(f"F 그룹 수: {len(formal_groups_ms)}, S 그룹 수: {len(subst_groups_ms)}")

df_ms['F_score'] = compute_group_composite(df_ms, formal_groups_ms, '제조서비스 F')
df_ms['S_score'] = compute_group_composite(df_ms, subst_groups_ms, '제조서비스 S')
df_ms['SDI']     = df_ms['S_score'] - df_ms['F_score']

# ── 건설업 ──
formal_groups_con = {
    'F-C1': ['Q6'],
    'F-C2': ['Q8_1', 'Q8_2'],
    'F-C3': ['Q8_3', 'Q8_4'],
    'F-C4': ['Q9'],
    'F-C5': ['Q10'],
    'F-C6': ['Q12_1'],
    'F-C7': ['Q12_2'],
}
subst_groups_con = {
    'S-C1': ['Q15_2_1','Q15_2_2','Q15_2_3','Q15_2_4','Q15_2_5','Q15_2_6','Q15_2_7'],
    'S-C2': ['Q16_1','Q16_2','Q16_3'],
    'S-C3': ['Q16_9','Q16_10'],
    'S-C4': ['Q16_16','Q16_17','Q16_18'],
    'S-C5': ['Q17_1','Q17_2','Q17_4'],
    'S-C6': ['Q21_2'],
}

df_con['F_score'] = compute_group_composite(df_con, formal_groups_con, '건설 F')
df_con['S_score'] = compute_group_composite(df_con, subst_groups_con, '건설 S')
df_con['SDI']     = df_con['S_score'] - df_con['F_score']

# ── 기술통계 ──
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    print(f"\n[{name}] n={len(df)}")
    print(df[['F_score','S_score','SDI']].describe().round(4))
    sdi_neg = (df['SDI'] < 0).mean() * 100
    print(f"SDI < 0 (형식주의) 비율: {sdi_neg:.1f}%")

# 가중 평균 병기 (WT2)
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    w = df['WT2']
    for col in ['F_score','S_score','SDI']:
        valid = df[col].dropna()
        ww = w.loc[valid.index]
        wmean = np.average(valid, weights=ww)
        print(f"[{name}] 가중 {col} 평균: {wmean:.4f}")
```

**시각화 — F vs S 산포도 (핵심 그림):**

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, (name, df, color) in zip(axes, [
    ('제조+서비스', df_ms, {'제조':'#2196F3','서비스':'#FF9800'}),
    ('건설', df_con, {'건설':'#4CAF50'})
]):
    if '제조' in color:
        for ind, c in color.items():
            mask = df['industry'] == ind
            ax.scatter(df.loc[mask,'F_score'], df.loc[mask,'S_score'],
                       alpha=0.3, s=10, color=c, label=ind)
    else:
        ax.scatter(df['F_score'], df['S_score'], alpha=0.3, s=10, color=list(color.values())[0])
    
    # 등치선 (F = S → SDI = 0)
    ax.plot([0, 1], [0, 1], 'k--', lw=1, label='F = S (SDI=0)')
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.05, color='blue', label='SDI>0 영역')
    ax.fill_between([0, 1], [0, 1], [1, 1], alpha=0.05, color='red', label='SDI<0 영역(형식주의)')
    
    ax.set_xlabel('F_score (형식)')
    ax.set_ylabel('S_score (실질)')
    ax.set_title(f'{name}\n(n={len(df)})')
    ax.legend(fontsize=8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('output/fs_scatter_v5.png', dpi=150, bbox_inches='tight')
```

---

### Phase 4: 주 추론 모형

**목적:** SDI가 ra_score를 유의하게 예측하는지 검증한다.

#### 4-0. 통제변수 준비

```python
# 제조·서비스업
df_ms['log_workers'] = np.log1p(df_ms['Q1_1'].replace([999,99999], np.nan))
df_ms['ind_mfg']     = (df_ms['industry'] == '제조').astype(float)
df_ms['elder_rate']  = (df_ms['Q1_2'] / df_ms['Q1_1']).clip(0, 1)
df_ms['foreign_rate']= (df_ms['Q1_3'] / df_ms['Q1_1']).clip(0, 1)
df_ms['female_rate'] = (df_ms['Q1_4'] / df_ms['Q1_1']).clip(0, 1)

# 건설업
df_con['log_workers'] = np.log1p(df_con['Q4_1'].replace([999,99999], np.nan))
df_con['elder_rate']  = (df_con['Q4_2'] / df_con['Q4_1']).clip(0, 1)
df_con['foreign_rate']= (df_con['Q4_3'] / df_con['Q4_1']).clip(0, 1)
df_con['female_rate'] = (df_con['Q4_4'] / df_con['Q4_1']).clip(0, 1)
```

#### 4-1. 모형 A — SDI 단일 지수

```python
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel
import scipy.stats as stats

controls_ms  = 'ind_mfg + log_workers + elder_rate + foreign_rate + female_rate'
controls_con = 'log_workers + elder_rate + foreign_rate + female_rate'

# OLS (제조+서비스)
res_A_ms_ols = smf.ols(f'ra_score ~ SDI + {controls_ms}', data=df_ms).fit()
print(res_A_ms_ols.summary())

# OLS (건설)
res_A_con_ols = smf.ols(f'ra_score ~ SDI + {controls_con}', data=df_con).fit()

# 순서형 로지스틱 (강건성)
ordered_data_ms = df_ms[['ra_score','SDI','ind_mfg','log_workers','elder_rate',
                          'foreign_rate','female_rate']].dropna()
ordered_data_ms['ra_score'] = ordered_data_ms['ra_score'].astype(int)
res_A_ms_ord = OrderedModel(ordered_data_ms['ra_score'],
                             ordered_data_ms[['SDI','ind_mfg','log_workers','elder_rate',
                                              'foreign_rate','female_rate']],
                             distr='logit').fit(method='bfgs', disp=False)
print(res_A_ms_ord.summary())
```

#### 4-2. 모형 B — F_score + S_score 분리 투입 + Wald 검정

```python
# OLS (제조+서비스)
res_B_ms_ols = smf.ols(f'ra_score ~ F_score + S_score + {controls_ms}', data=df_ms).fit()

# Wald 검정: H0: β_S = β_F
b_s  = res_B_ms_ols.params['S_score']
b_f  = res_B_ms_ols.params['F_score']
se_s = res_B_ms_ols.bse['S_score']
se_f = res_B_ms_ols.bse['F_score']
cov_sf = res_B_ms_ols.cov_params().loc['S_score','F_score']
se_diff = np.sqrt(se_s**2 + se_f**2 - 2*cov_sf)
t_diff  = (b_s - b_f) / se_diff
p_both  = 2 * (1 - stats.norm.cdf(abs(t_diff)))  # 양측
p_one   = p_both / 2                              # 단측 (β_S > β_F 방향)

print(f"β_S = {b_s:.4f}, β_F = {b_f:.4f}")
print(f"β_S - β_F = {b_s - b_f:.4f}, t = {t_diff:.4f}, p(양측) = {p_both:.4f}, p(단측) = {p_one:.4f}")

# 건설업 동일 적용
res_B_con_ols = smf.ols(f'ra_score ~ F_score + S_score + {controls_con}', data=df_con).fit()
```

#### 4-3. 가설 판정 자동화

```python
def judge_hypothesis(res_A, res_B, label=''):
    beta_sdi = res_A.params.get('SDI', np.nan)
    p_sdi    = res_A.pvalues.get('SDI', np.nan)
    b_s = res_B.params.get('S_score', np.nan)
    b_f = res_B.params.get('F_score', np.nan)
    # (Wald p는 별도 계산 필요)
    
    h1 = (beta_sdi > 0) and (p_sdi < 0.05)
    h2_dir = (b_s > b_f)
    
    print(f"\n[{label}]")
    print(f"  수준 1: β_SDI={beta_sdi:.4f}, p={p_sdi:.4f} → {'지지' if h1 else '불지지'}")
    print(f"  수준 2 방향: β_S({b_s:.4f}) {'>' if h2_dir else '<='} β_F({b_f:.4f}) → {'지지 방향' if h2_dir else '불지지 방향'}")

judge_hypothesis(res_A_ms_ols, res_B_ms_ols, '제조+서비스')
judge_hypothesis(res_A_con_ols, res_B_con_ols, '건설')
```

#### 4-4. 업종 조절 효과 (탐색적)

```python
# 제조+서비스+건설 통합 데이터
df_all = pd.concat([df_ms.assign(is_con=0), df_con.assign(is_con=1, ind_mfg=np.nan)],
                   ignore_index=True)

# 상호작용 모형: SDI × 건설더미
res_inter = smf.ols('ra_score ~ SDI * is_con + log_workers + elder_rate + foreign_rate + female_rate',
                    data=df_all).fit()
print(res_inter.summary())
# SDI:is_con 상호작용항이 유의하면 건설업 이질성 통계적 지지
```

---

### Phase 5: 강건성 검증

| 검증 | 변경 내용 | 판단 기준 |
|------|-----------|----------|
| 경계 변수 민감도 | Q17_13을 S로 이동 후 재실행 | β_S > β_F 방향 유지 여부 확인 |
| 점수 산출 방식 | 단순 평균 → EFA 요인점수 | 방향·유의성 일치 여부 |
| 표본 제한 | 50인 이상 사업장만 | 방향 일치 여부 |
| 결측 처리 | listwise 삭제 → 문항 평균 대치 | 방향·표준오차 변화 확인 |

```python
# ── 민감도 1: Q17_13 → S로 이동 ──
formal_groups_ms_sens = {k: v for k, v in formal_groups_ms.items() if k != 'F-M8'}
subst_groups_ms_sens  = {**subst_groups_ms, 'S-M8': ['Q17_13']}

df_ms['F_score_sens'] = compute_group_composite(df_ms, formal_groups_ms_sens, '민감도 F')
df_ms['S_score_sens'] = compute_group_composite(df_ms, subst_groups_ms_sens, '민감도 S')
df_ms['SDI_sens']     = df_ms['S_score_sens'] - df_ms['F_score_sens']

res_sens = smf.ols(f'ra_score ~ F_score_sens + S_score_sens + {controls_ms}', data=df_ms).fit()
b_s_s = res_sens.params['S_score_sens']
b_f_s = res_sens.params['F_score_sens']
print(f"[민감도] β_S={b_s_s:.4f}, β_F={b_f_s:.4f}, 방향유지: {b_s_s > b_f_s}")

# ── 민감도 2: 50인 이상 표본 ──
df_ms_50 = df_ms[df_ms['Q1_1'] >= 50].copy()
res_50 = smf.ols(f'ra_score ~ SDI + {controls_ms}', data=df_ms_50).fit()
print(f"[50인 이상] β_SDI={res_50.params['SDI']:.4f}, p={res_50.pvalues['SDI']:.4f}")
```

**민감도 분석 결과 처리 원칙:**
- Q17_13 재분류 시 결론이 바뀌면: "Q17_13의 분류가 결론에 영향을 주며, 이 변수는 F/S 경계상에 위치한다"고 명시
- 방향(β 부호)이 유지되는 경우 이를 방향 강건성 근거로 서술
- 유의성이 사라지는 경우 이를 솔직하게 보고하고 한계 섹션에 기술

---

### Phase 6: 건설업 이질성 분석

**목적:** 건설업의 불지지 결과를 이론적으로 설명 가능한 발견으로 전환한다.

#### 경쟁 가설 데이터 탐색

**C1: SDI 분산이 작아 통계적 검력 부족**
```python
print("건설업 SDI 표준편차:", df_con['SDI'].std().round(4))
print("제조+서비스 SDI 표준편차:", df_ms['SDI'].std().round(4))
# 건설업 σ < 0.15 이면 검력 문제일 가능성
```

**C2: ra_score 분포가 제조업과 다름 (측정 비동등)**
```python
print("건설업 ra_score 분포:")
print(df_con['ra_score'].value_counts(normalize=True))
print("\n제조+서비스 ra_score 분포:")
print(df_ms['ra_score'].value_counts(normalize=True))
# 건설업 73% = 0이면 바닥 효과(floor effect)로 회귀 계수 추정이 불안정
```

**C3: 외생 결정 요인(원청-하청 관계) 탐색**
```python
# 건설업 전용 변수: 협력업체 관련 Q23_*, Q24_*
# 이 변수들을 공변량으로 추가했을 때 SDI 효과가 변하는지 확인
if 'Q23_1' in df_con.columns:
    res_c3 = smf.ols(f'ra_score ~ SDI + Q23_1 + {controls_con}', data=df_con).fit()
    print(f"[C3 탐색] β_SDI={res_c3.params['SDI']:.4f}, p={res_c3.pvalues['SDI']:.4f}")
```

---

## 8. 통제변수 로직 및 공변량 선택 근거

| 통제변수 | 포함 이유 | 예상 부호 |
|---------|-----------|----------|
| log(종사자 수) | 규모 클수록 전담부서·인증 보유 용이하지만 위험성평가 형식화 경향 | 음(−) |
| 업종 더미 (제조=1) | 제조업이 서비스업보다 법적 의무 강해 형식 준수 높음 | 음(−) |
| 고령자 비율 | 고령자 다수 = 위험 노출 높아 안전 필요성 실질화 가능 | 양(+) 또는 불확실 |
| 외국인 비율 | 의사소통 장벽 = 안전 형식화 위험 | 음(−) |
| 여성 비율 | 업종 특성 통제 | 불확실 |

---

## 9. 논문 서술 구조

### 섹션 배치

```
1. 서론
   - 안전 형식주의 문제의 실무적 중요성
   - 기존 연구의 한계: 형식-실질 괴리를 측정한 연구가 없음
   - SDI 개념 도입
   - 연구 목적: ① SDI의 결과 예측력 검증 ② 업종별 이질성 탐색

2. 이론적 배경
   2.1 안전 관리의 형식-실질 이분법 (신제도주의, 탈동조화 이론)
   2.2 건설업의 구조적 특수성 (다단계 하도급, 발주자-시공사 분리) ← 불지지 예측
   2.3 연구 가설 (제조·서비스업 H1, 건설업 탐색적 질문 RQ1로 구분)

3. 연구 방법
   3.1 데이터 (표본 기술, WT2 가중치 처리 여부 명시)
   3.2 변수 구성
       - F/S 분류 기준 (코드북 + 이론적 정의)
       - Q17_13 F 유지 결정 이유 (각주)
       - 그룹 composite 방식 및 SDI 계산
   3.3 측정 타당성 검증 방법
   3.4 회귀 모형 설계 (모형 A, B, 통제변수 선택 근거)

4. 결과
   4.1 측정 타당성 (EFA 적재량 표, α/ω, 판별 타당도)
   4.2 기술통계
       - F_score, S_score, SDI 분포 표 (업종별)
       - F vs S 산포도
       - SDI < 0 기업 특성
   4.3 제조·서비스업 주 분석
       - 기저 모형 → 모형 A → 모형 B 순서
       - Wald 검정 (β_S − β_F)
       - OLS + 순서형 로지스틱 방향 일치 확인
   4.4 강건성 검증 (표로 정리)
   4.5 건설업 이질성 분석
       - 결과 제시 + 즉시 이론적 해석
       - 경쟁 가설 C1/C2/C3 검토

5. 토론
   5.1 가설 지지 결과의 이론적 의미
   5.2 건설업 불지지의 해석 (C1/C2/C3 중 가장 지지받는 설명)
   5.3 안전 형식주의 기업 특성과 정책 함의
       (형식 지표보다 실질 지표 중심의 근로감독 설계)
   5.4 한계 (횡단 설계, 자기보고 편향, Q17_13 분류 불확실성)

6. 결론
```

### 결과 제시 테이블 양식

| 변수 | 기저 모형 β (SE) | 모형 A β (SE) | 모형 B β (SE) |
|------|----------------|--------------|--------------|
| SDI | — | **β_SDI** | — |
| F_score | — | — | **β_F** |
| S_score | — | — | **β_S** |
| log(종사자) | β | β | β |
| 업종(제조) | β | β | β |
| R² | R² | R² | R² |
| n | n | n | n |
| **Wald(β_S>β_F)** | — | — | **t, p** |

---

## 10. 주의사항 — 흔히 빠지는 함정

### 절대 하지 말 것

1. **Q27(사고 건수)를 결과변수로 다시 쓰는 것** — 역인과 + 과소보고 이중 문제. 민감도 분석에서도 사용하지 않는다.

2. **GLM 음이항 IRR을 그대로 해석하는 것** — V2에서 IRR=0.094(90.6% 감소)는 변수 스케일 차이에서 비롯된 산물. IRR을 보고한다면 변수 1단위 변화의 실질적 의미를 먼저 확인한다.

3. **결과를 보고 F/S 분류를 수정하는 것** — 이 설계서가 존재하는 이유다. 분류는 §2에서 고정됐다.

4. **업종별 SDI를 Track A(업종 전용) 결과로 직접 비교하는 것** — 척도가 다르면 절대 수준 비교 불가. 통합 Track B로만 비교한다.

5. **단측 검정을 선택적으로 적용하는 것** — 양측 검정을 기본으로, 단측을 적용할 때는 이론적 방향 예측 근거를 사전에 명시한다.

### 빠뜨리기 쉬운 것

1. **변수 존재 검증** — `df.filter(like='Q17').columns` 없이 코드북 표기를 그대로 쓰면 NaN 열 생성 (에러 없이 분석 오염).

2. **가중치(WT2) 처리** — 기술통계에서 가중/비가중 병기. 회귀 분석은 비가중으로 수행하되 이를 명시.

3. **F/S 그룹 수 출력** — 코드 첫 줄에 `print(f"F 그룹: {len(formal_groups_ms)}, S 그룹: {len(subst_groups_ms)}")`.

4. **효과 크기 보고** — p값만으로 부족. 표준화 β, 부분 R², ΔR²를 함께 보고.

5. **보고서·테이블에 영어 alias 금지** — `mgmt_emphasis`, `rule_have` 등은 원본 코드(Q17_1, Q17_11 등)로만 표기.

---

## 11. 환경 설정

```bash
pip install factor_analyzer "scikit-learn<1.6" --break-system-packages
```

> scikit-learn ≥ 1.6은 factor_analyzer와 충돌한다 (`check_array()` 오류).  
> 이 충돌은 V1~V4 공통 트러블슈팅으로 이미 검증됨.

**추가 패키지:**
```bash
pip install pingouin statsmodels scipy matplotlib seaborn --break-system-packages
```

---

## 12. 파일 구조 제안

```
SAB_paper/
├── DESIGN.md               ← 이 문서 (설계서)
├── CLAUDE.md               ← 워크플로우 지침
├── known_issues.md         ← 고질적 한계
├── 변수_설정.pdf             ← F/S 분류 원본 PDF
├── data/raw/               ← 원본 데이터 (읽기 전용)
└── version5/               ← 이번 분석
    ├── SDI_v5.ipynb        ← 주 분석 노트북 (Phase 1~6)
    ├── output/
    │   ├── descriptive_v5.csv       ← Phase 3 기술통계
    │   ├── measurement_v5.csv       ← Phase 2 타당성 검증
    │   ├── regression_ms_v5.csv     ← Phase 4 제조+서비스 결과
    │   ├── regression_con_v5.csv    ← Phase 4 건설 결과
    │   ├── robustness_v5.csv        ← Phase 5 강건성
    │   ├── construction_v5.csv      ← Phase 6 건설 이질성
    │   ├── fs_scatter_v5.png        ← F vs S 산포도
    │   └── SDI_report_v5.md        ← 최종 보고서
    └── version5.md         ← 이번 분석 전용 추가 지침
```

---

## 13. 체크리스트

### Phase 1: 데이터 전처리
- [ ] 제조·서비스·건설 3개 파일 로드 완료
- [ ] 핵심 변수 존재 검증 (`df.filter(like=...).columns`) 실행 및 코드북 대조
- [ ] 무응답 코드 NaN 처리 완료 (리커트→9, 인원수→999/99999)
- [ ] 이진 재코딩 완료 (2→0)
- [ ] Q8_1, Q8_2 이상치 윈저화 완료
- [ ] ra_score 생성 완료 ({1→2, 2→1, 3→0})
- [ ] 결측률 표 출력 (F/S 핵심 변수 모두 10% 미만 확인)

### Phase 2: 측정 타당성
- [ ] S 변수 Cronbach α 산출 (기준: α > 0.70)
- [ ] EFA 실행 및 Q17_13 적재 위치 확인·문서화
- [ ] F_score ↔ S_score 상관 확인 (기준: r < 0.85)
- [ ] VIF 점검 (기준: VIF < 10)

### Phase 3: 점수 산출
- [ ] F 그룹 수 / S 그룹 수 출력 확인
- [ ] F_score, S_score, SDI 산출 완료
- [ ] 가중(WT2) / 비가중 기술통계 병기
- [ ] F vs S 산포도 저장

### Phase 4: 주 추론 모형
- [ ] 모형 A OLS: β_SDI 부호·유의성 확인
- [ ] 모형 A 순서형: OLS와 방향 일치 여부 확인
- [ ] 모형 B OLS: β_S, β_F 산출
- [ ] Wald 검정: β_S − β_F, t, p (양측·단측 모두)
- [ ] 모형 B 순서형: OLS와 방향 일치 여부 확인
- [ ] 건설업 동일 적용
- [ ] 업종 조절 효과(탐색) 실행

### Phase 5: 강건성
- [ ] Q17_13 F→S 재분류 민감도 분석
- [ ] 결론 역전 여부 확인 및 처리 방침 문서화
- [ ] 50인 이상 표본 제한 분석
- [ ] 결과 비교표 작성

### Phase 6: 건설업 이질성
- [ ] SDI 분산 비교 (경쟁 가설 C1)
- [ ] ra_score 분포 비교 (경쟁 가설 C2)
- [ ] 협력업체 변수 탐색 (경쟁 가설 C3)
- [ ] 3가지 경쟁 가설 중 가장 지지받는 설명 결론

### 보고서
- [ ] 모든 테이블에 영어 alias 없이 원본 변수 코드 사용
- [ ] 가중/비가중 결과 병기
- [ ] ΔR², 표준화 β 포함
- [ ] 한계 섹션 (횡단 설계, 자기보고, Q17_13 불확실성) 기술
