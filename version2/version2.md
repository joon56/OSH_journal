# Version 2 분석 계획서
> 작성일: 2026-05-23  
> 목적: Version 1 문제점 해소 + PDF 원본 사양 충실 구현  
> 이 문서가 내일 분석의 **유일한 기준**이다. CLAUDE.md와 함께 읽을 것.

---

## 0. Version 1 → Version 2 핵심 변경사항

| 항목 | Version 1 문제 | Version 2 방향 |
|---|---|---|
| F 변수 | Q17_1~6 (경영진 선언) → 이론적으로 형식 아님 | PDF 확정: 제도·선임·인증 변수 (Q6, Q8, Q9, Q10, Q11/Q12/Q13) |
| S 변수 | Q17_7~17 일부만 | PDF 확정: 행동·노력·효과 인식 변수 (Q13위험인식, Q15~16 스트레스관리 노력, Q16_1~3/Q17_1~3 경영·감독 강조, Q17~18 감독자역량, Q21/Q22 환경노력) |
| 회귀 변수 | SDI + 일부 통제 | PDF 확정: SDI + 경영강조점수 + 교육훈련 + 시설 + 안전관리비 + 근로자 구성 비율 |
| 회귀 모형 | GLM NegBin만 | GLM NegBin(주) + 로지스틱(any_acc)(보조) — 방향 일치 확인 |
| F/S 분류 근거 | 결과에 맞춰 사후 조정 | 분석 전 PDF+코드북으로 사전 확정, 코드 작성 후 변경 불가 |

---

## 1. 프로젝트 가설 (변경 없음)

**안전괴리지수(SDI) = Substantive score − Formal score**

- SDI < 0 (형식 > 실질): 서류·인증은 갖췄으나 실제 현장 안전 미흡 → **사고율 증가** 예상
- SDI > 0 (실질 > 형식): 실제 행동·효과가 제도를 앞섬 → **사고율 감소** 예상
- **검증 목표**: 회귀계수 β_SDI < 0 (사고 건수 또는 사고 발생 여부)

---

## 2. 확정 F/S 변수 목록 (PDF 원본 기준)

> ⚠️ **변수명은 실데이터 열 이름과 다를 수 있다. 3절의 검증 절차를 반드시 먼저 실행할 것.**

### 2-1. 건설업 (건설업 코드북 시트 기준)

#### Formal 변수 — 7그룹

| 그룹 ID | PDF 코드 | 변수 설명 | 척도 | 정규화 방법 |
|---|---|---|---|---|
| F-C1_전담부서 | Q6 | 안전보건 업무 전담 부서 유무 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |
| F-C2_선임인원 | Q8_1, Q8_2 | 안전·보건관리자 선임 신고 수 (명) | 연속형(명) | Min-Max |
| F-C3_전담직원 | Q8_3, Q8_4 | 산업안전·보건 전담 직원 수 (명) | 연속형(명) | Min-Max |
| F-C4_기술지도 | Q9 | 건설재해예방 전문지도기관 기술지도 수혜 | 이진(1=받음/2=안받음) | 1→1.0, 2→0.0 |
| F-C5_위원회 | Q10 | 산업안전보건위원회(노사협의체) 운영 여부 | 4범주 | 위원회=1.0, 협의체=0.5, 미운영=0.0, 모름=NaN |
| F-C6_KOSHA | Q12_1 | KOSHA-MS 인증 취득 여부 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |
| F-C7_ISO | Q12_2 | ISO 45001 인증 취득 여부 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |

**F 그룹 수: 7 / 총 변수 수: 8개 (Q8_1~4 각 1개, 나머지 각 1개)**

#### Substantive 변수 — 7그룹

| 그룹 ID | PDF 코드 | 변수 설명 | 척도 | 정규화 방법 |
|---|---|---|---|---|
| S-C1_위험인식 | Q13_2, Q13_3, Q13_4, Q13_10, Q13_11, Q13_14 | 작업환경 관련 위험 요인 인식 (6문항) | 5점(1=전혀위험X~5=매우위험) | Min-Max ⚠️ 방향 주의(아래 참조) |
| S-C2_스트레스관리 | Q15_2_1 ~ Q15_2_7 | 스트레스 관리 노력 (7문항) | 5점(1=전혀노력X~5=많이노력) | Min-Max |
| S-C3_경영강조 | Q16_1, Q16_2, Q16_3 | 경영진 안전 강조·우선순위·중요성 인식 | 5점(1=전혀그렇지않다~5=매우그렇다) | Min-Max |
| S-C4_교육효과 | Q16_9, Q16_10 | 교육·훈련 기회 충분성 및 재해예방 실효성 | 5점 | Min-Max |
| S-C5_행동준수 | Q16_16, Q16_17, Q16_18 | 근로자 안전절차 준수·작업거부권·자발적 개선 | 5점 | Min-Max |
| S-C6_감독자역량 | Q17_1, Q17_2, Q17_4 | 작업반장 역할 인지·역량·재해예방 기여도 | 5점 | Min-Max |
| S-C7_환경노력 | Q21_2 | 작업환경 측정 결과 기반 유해인자 노출 최소화 노력 | 4점(1=전혀X~4=매우열심히) | Min-Max |

**S 그룹 수: 7 / 총 변수 수: 22개**

> ⚠️ **S-C1_위험인식(Q13_*) 방향 처리 결정 필요**  
> 5점 척도에서 5 = "매우 위험함" → 높을수록 위험 인식이 높다는 의미.  
> 해석 방향이 애매하다: "위험을 많이 인식 = 현실을 직시하는 실질 안전(↑좋음)" vs "위험 노출 자체가 높음(↑나쁨)".  
> **권장**: 코드북에서 해당 문항이 "위험 인식 노력/인지 수준"인지 "실제 노출 위험도"인지 확인 후 방향 결정. 확인 전까지 해당 그룹 제외 후 민감도 분석으로 처리.

---

### 2-2. 제조·서비스업 (제조서비스업 코드북 시트 기준)

#### Formal 변수 — 7그룹

| 그룹 ID | PDF 코드 | 변수 설명 | 척도 | 정규화 방법 |
|---|---|---|---|---|
| F-M1_전담부서 | Q6 | 안전보건 업무 전담 부서 유무 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |
| F-M2_선임신고 | Q8_1, Q8_2 | 안전·보건관리자 선임 신고 수 (명) | 연속형(명) | Min-Max |
| F-M3_위탁기관 | Q9_1, Q9_2 | 안전·보건관리 위탁 전문기관 유무 | 이진(1=있음/2=없음) | 1→1.0, 2→0.0 |
| F-M4_위원회 | Q10 | 산업안전보건위원회 구성·운영 여부 | 3범주(1=운영/2=미운영/3=모름) | 운영=1.0, 미운영=0.0, 모름=NaN |
| F-M5_담당자 | Q11 | 안전보건 관리 담당자 선임 여부 | 이진(1=선임/2=미선임) | 1→1.0, 2→0.0 |
| F-M6_KOSHA | Q13_1 | KOSHA-MS 인증 취득 여부 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |
| F-M7_ISO | Q13_2 | ISO 45001 인증 취득 여부 | 이진(1=예/2=아니요) | 1→1.0, 2→0.0 |

**F 그룹 수: 7 / 총 변수 수: 9개**

#### Substantive 변수 — 7그룹

| 그룹 ID | PDF 코드 | 변수 설명 | 척도 | 정규화 방법 |
|---|---|---|---|---|
| S-M1_스트레스관리 | Q16_2_1 ~ Q16_2_7 | 스트레스 관리 노력 (7문항) | 5점(1=전혀노력X~5=많이노력) | Min-Max |
| S-M2_경영강조 | Q17_1, Q17_2, Q17_3 | 경영진 안전 강조·우선순위·중요성 인식 | 5점 | Min-Max |
| S-M3_교육효과 | Q17_9, Q17_10 | 교육·훈련 기회 충분성 및 재해예방 실효성 | 5점 | Min-Max |
| S-M4_규정효과 | Q17_12, Q17_13 | 안전 규정·절차의 재해예방 실효성 (2문항) | 5점 | Min-Max |
| S-M5_행동준수 | Q17_15, Q17_16, Q17_17 | 근로자 안전절차 준수·작업거부권·자발적 개선 | 5점 | Min-Max |
| S-M6_감독자역량 | Q18_1, Q18_2, Q18_3, Q18_4 | 관리감독자 역할 인지·역량·지원·재해예방 기여도 | 5점 | Min-Max |
| S-M7_환경노력 | Q22_2 | 작업환경 측정 결과 기반 유해인자 노출 최소화 노력 | 4점(1=전혀X~4=매우열심히) | Min-Max |

**S 그룹 수: 7 / 총 변수 수: 20개**

> ⚠️ **S-M4 검증 필요**: PDF에서 Q17_12/Q17_13을 "안전 규정·절차의 재해예방 실효성 2문항"으로 묶었으나, CLAUDE.md §3-1에서 Q17_13은 "안전 시설·장비·보호구 **보유**"(Formal 성격)로 기술됨. 실데이터 코드북에서 Q17_13 문항 내용을 직접 확인 후 결정할 것.  
> → 코드북 확인 결과 Q17_12="규정효과(실질)", Q17_13="시설보유(형식)"이면: Q17_13을 F로 이동, Q17_12만 S-M4에 유지.

---

## 3. 변수명 실데이터 검증 절차 (분석 시작 전 필수 실행)

```python
import pandas as pd, numpy as np, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'data/raw/'
files = os.listdir(BASE)
df_con = pd.read_csv(BASE + [f for f in files if '건설' in f][0])
df_mfg = pd.read_csv(BASE + [f for f in files if '제조' in f][0])
df_svc = pd.read_csv(BASE + [f for f in files if '서비스' in f][0])

# 건설업 변수명 검증
print("=== 건설업 F 변수 검증 ===")
for code in ['Q6','Q8_1','Q8_2','Q8_3','Q8_4','Q9','Q10','Q12_1','Q12_2']:
    exists = code in df_con.columns
    if not exists:
        # 서브항목 형태로 존재할 수 있음 (예: Q8_1_1)
        alts = sorted(df_con.filter(like=code.split('_')[0]).columns.tolist())
        print(f'  {code}: NOT FOUND → 후보: {alts[:5]}')
    else:
        print(f'  {code}: OK, dtype={df_con[code].dtype}, nunique={df_con[code].nunique()}')

print("\n=== 건설업 S 변수 검증 ===")
for prefix in ['Q13','Q15_2','Q16_1','Q16_2','Q16_9','Q16_10',
               'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4','Q21_2']:
    candidates = sorted(df_con.filter(like=prefix.replace('_','',1) if prefix.count('_')==1 else prefix).columns.tolist())
    # 직접 검색
    direct = [c for c in df_con.columns if c == prefix]
    print(f'  {prefix}: direct={direct}, 유사={candidates[:4]}')

print("\n=== 제조업 F 변수 검증 ===")
for code in ['Q6','Q8_1','Q8_2','Q9_1','Q9_2','Q10','Q11','Q13_1','Q13_2']:
    exists = code in df_mfg.columns
    if not exists:
        alts = sorted(df_mfg.filter(like=code.rsplit('_',1)[0]).columns.tolist())
        print(f'  {code}: NOT FOUND → 후보: {alts[:5]}')
    else:
        print(f'  {code}: OK, dtype={df_mfg[code].dtype}, nunique={df_mfg[code].nunique()}')

print("\n=== 제조업 S 변수 검증 ===")
for prefix in ['Q16_2','Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
               'Q17_12','Q17_13','Q17_15','Q17_16','Q17_17',
               'Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']:
    direct = [c for c in df_mfg.columns if c == prefix]
    print(f'  {prefix}: {direct if direct else "NOT FOUND — 확인 필요"}')
```

**검증 후 실제 열 이름으로 아래 §4 변수 목록을 수정한 뒤 분석을 시작할 것.**

---

## 4. 데이터 전처리 규칙

### 4-1. 무응답 코드 처리
```python
# 리커트 5점 변수 → 9를 NaN
likert_cols = [...]   # Q13_*, Q15_2_*, Q16_*, Q17_*, Q18_*, Q21_2, Q22_2
df[likert_cols] = df[likert_cols].replace(9, np.nan)

# 이진형 변수 → 9를 NaN
binary_cols = ['Q6','Q9','Q10','Q11','Q12_1','Q12_2','Q13_1','Q13_2','Q9_1','Q9_2']
df[binary_cols] = df[binary_cols].replace(9, np.nan)

# 인원수 변수 → 999, 99999를 NaN
count_cols = ['Q8_1','Q8_2','Q8_3','Q8_4']
df[count_cols] = df[count_cols].replace([999, 99999], np.nan)

# 사고 건수 변수
acc_cols = ['Q27_1_1','Q27_1_2','Q27_1_3','Q27_3_1','Q27_3_2','Q27_3_3']
df[acc_cols] = df[acc_cols].replace([999, 99999], np.nan)
```

### 4-2. 변수 정규화 함수
```python
def minmax(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) if mx > mn else pd.Series(0.0, index=s.index)

# 이진형 변환 (NaN 유지)
def binary_norm(s, yes_val=1):
    return s.map({yes_val: 1.0, 2: 0.0})  # 9 → NaN (이미 처리됨)

# Q10 건설업 (4범주)
def q10_con_norm(s):
    return s.map({1: 1.0, 2: 0.5, 3: 0.0, 4: np.nan})

# Q10 제조·서비스업 (3범주)
def q10_ms_norm(s):
    return s.map({1: 1.0, 2: 0.0, 3: np.nan})
```

### 4-3. SDI 계산
```python
def compute_sdi(df, f_groups, s_groups, label=''):
    """
    f_groups: {'그룹ID': ['변수1','변수2',...], ...}
    s_groups: 동일 구조
    반환: Series (SDI 값), Series (F_score), Series (S_score)
    """
    # 각 그룹 composite (그룹 내 열 평균)
    f_composites = {}
    for gname, cols in f_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            f_composites[gname] = df[avail].mean(axis=1)
    
    s_composites = {}
    for gname, cols in s_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            s_composites[gname] = df[avail].mean(axis=1)
    
    F_score = pd.DataFrame(f_composites).mean(axis=1)
    S_score = pd.DataFrame(s_composites).mean(axis=1)
    SDI = S_score - F_score
    
    f_total = sum(len(v) for v in f_groups.values())
    s_total = sum(len(v) for v in s_groups.values())
    print(f'[{label}] F변수 수={f_total}, S변수 수={s_total}, F그룹={len(f_groups)}, S그룹={len(s_groups)}')
    print(f'[{label}] SDI: n={SDI.notna().sum()}, mean={SDI.mean():.4f}, std={SDI.std():.4f}')
    print(f'[{label}] SDI<0 비율: {(SDI<0).mean():.1%}')
    return SDI, F_score, S_score
```

---

## 5. 회귀 분석 설계 (PDF 원본 기준)

### 5-1. 건설업 회귀

**종속변수**: `total_acc = Q27_1_1 + Q27_1_2 + Q27_1_3 + Q27_3_1 + Q27_3_2 + Q27_3_3`  
**offset**: `log(Q4_1)` (주간 종사자 수)

| 변수 | 코드 | 처리 |
|---|---|---|
| **독립: SDI** | SDI | 연속형 |
| 위험성평가 수준 | Q14 | 더미화 (기준=실시안함) |
| 경영진 안전강조 | Q16_1, Q16_2, Q16_3 | 평균 or 개별 투입 |
| 교육·훈련 효과 | Q16_9, Q16_10, Q16_11, Q16_12 | 평균 or 개별 투입 |
| 시설·장비·보호구 | Q16_13, Q16_14, Q16_15 | 평균 or 개별 투입 |
| 교육 실시 여부 | Q18_1 | 더미 |
| 안전관리비 | Q25 또는 Q25_1 | log 변환 (0 처리: clip(1)) |
| **통제: 공사금액** | SQ2 또는 Q1_3 | 더미화 |
| **통제: 공사 종류** | Q2 | 더미화 |
| **통제: 기성공정률** | Q1_5 | 더미화 or 연속형 |
| **통제: 고령자 비율** | Q4_2/Q4_1 | 비율 |
| **통제: 외국인 비율** | Q4_3/Q4_1 | 비율 |
| **통제: 여성 비율** | Q4_4/Q4_1 | 비율 |
| **통제: 원청/하도급** | Q22 | 더미화 |

> ⚠️ **주의**: Q16_1~3, Q16_9~12, Q16_13~15는 SDI의 S 변수(S-C3, S-C4, S-C5)와 일부 겹칩니다.  
> 겹치는 변수를 회귀에 다시 투입하면 **다중공선성** 발생. 선택지:  
> - (A) SDI에 해당 그룹 제외하고 회귀에만 투입  
> - (B) SDI에 포함하고 회귀에서 제외 (SDI의 한 차원으로 흡수)  
> - (C) 포함하되 VIF 확인 후 문제시 제거  
> **권장: (B)** SDI가 포괄 지수이므로, SDI 구성 변수는 회귀 독립변수에서 제외. 회귀에는 SDI + 제도적 통제(Q14, Q18_1, Q25)만 투입.

### 5-2. 제조·서비스업 회귀

**종속변수**: `total_acc` (동일)  
**offset**: `log(Q1_1)` (전체 종사자 수)

| 변수 | 코드 | 처리 |
|---|---|---|
| **독립: SDI** | SDI | 연속형 |
| 위험성평가 수준 | Q15 | 더미화 |
| 경영진 안전강조 | Q17_1, Q17_2, Q17_3 | 평균 |
| 교육·훈련 | Q17_9, Q17_10, Q17_11, Q17_12 | 평균 |
| 시설·장비 | Q17_13, Q17_14 | 평균 |
| 교육 실시 여부 | Q19_1 | 더미 |
| 작업환경 측정 여부 | Q22_1 | 더미 (1=예, 2=아니요, 3=해당없음→NaN, 4=모름→NaN) |
| 건강진단 여부 | Q20_1 | 더미 |
| **통제: 종사자 규모** | SQ3 | 더미화 |
| **통제: 업종** | SQ4 | 더미 (제조/서비스) |
| **통제: 교대근무** | Q2 | 더미 |
| **통제: 고령자 비율** | Q1_2/Q1_1 | 비율 |
| **통제: 외국인 비율** | Q1_3/Q1_1 | 비율 |
| **통제: 여성 비율** | Q1_4/Q1_1 | 비율 |
| **통제: 야간 비율** | Q3_1_1/Q1_1 | 비율 |
| **통제: 노조** | Q5 | 더미 |

> 동일한 다중공선성 주의 적용 (위 5-1 참고).

### 5-3. 모형 선택

```
주 모형: sm.GLM(y, X, family=sm.families.NegativeBinomial(), offset=log_workers)
보조 모형: sm.Logit(any_acc, X)  # any_acc = (total_acc > 0).astype(int)
```

- 두 모형의 β_SDI **부호가 일치**하면 강한 증거
- GLM NegBin이 수렴 실패 시: `res = model.fit(method='bfgs', maxiter=500)`
- 건설업 GLM NegBin 실패 시: Poisson with offset 또는 로지스틱만 보고
- **절대로 ZIP은 사용하지 않음** (Version 1에서 Inflation 방정식이 역인과 artifact 유발)

---

## 6. 단계별 작업 순서

```
Step 1: 변수명 검증 (§3 스크립트 실행)
         → 결과 출력 확인 후 §2의 변수 코드 수정
         → S-C1 위험인식 방향, S-M4 Q17_13 처리 방향 결정

Step 2: 데이터 로드 및 전처리
         → 무응답 NaN 처리
         → 이진형·인원수·리커트 각각 정규화 함수 적용
         → 비율 변수 계산 (고령자/외국인/여성/야간 비율)

Step 3: SDI 계산
         → F_score, S_score, SDI 산출
         → 기술통계 출력 (n, mean, std, SDI<0 비율, 가중평균)
         → 업종별 분포 비교 (박스플롯)

Step 4: EFA (구성타당도 검증)
         → S 변수 중 Likert 문항만 대상 (이진·연속형 제외)
         → KMO, Bartlett, 고유값, 요인적재량 확인
         → "S 변수들이 1~2요인으로 수렴하는가" 확인

Step 5: 회귀 분석
         → 건설업: GLM NegBin + 로지스틱
         → 제조·서비스업: GLM NegBin + 로지스틱
         → β_SDI 부호, IRR/OR, 95% CI, p값 출력

Step 6: 보고서 생성
         → SDI_report_v2.md 로 저장 (v1과 구분)
         → output/v2/ 폴더에 CSV 산출물 저장
```

---

## 7. 주의사항 및 잠재 문제

### 7-1. 반드시 확인해야 할 사항

| 번호 | 확인 항목 | 확인 방법 |
|---|---|---|
| 1 | Q8_1~Q8_4 실데이터 열 이름 (선임 인원수) | `df_con.filter(like='Q8').columns` |
| 2 | Q15_2_1~7 (건설 스트레스 관리) 실존 여부 | `df_con.filter(like='Q15').columns` |
| 3 | Q16_2_1~7 (제조 스트레스 관리) 실존 여부 | `df_mfg.filter(like='Q16').columns` |
| 4 | Q17_13 문항 내용 (시설보유 vs 규정효과) | 코드북 `제조서비스업` 시트 Q17_13 확인 |
| 5 | Q13_2~Q13_14 건설 위험인식 방향 | 코드북 `건설업` 시트 Q13_2 등 확인 |
| 6 | Q21_2 건설 / Q22_2 제조 실존 여부 | `df_con.filter(like='Q21').columns` 등 |
| 7 | Q8_3, Q8_4 (전담직원 수) 건설업 존재 여부 | `df_con.filter(like='Q8').columns` |
| 8 | 종사자 수 변수: 건설=Q4_1, 제조=Q1_1 맞는지 | value_counts, describe로 범위 확인 |

### 7-2. F/S 변수 수 불균형

현재 설계: F 7그룹 (8~9변수) vs S 7그룹 (20~22변수)  
→ 그룹 composite 방식(그룹 내 평균 → 그룹 간 평균)으로 불균형 해소  
→ **변수 수 불균형이 아닌 그룹 수 균형**으로 SDI 안정성 확보

### 7-3. 이진형 F 변수의 낮은 분산

KOSHA-MS, ISO45001 인증 보유율이 매우 낮을 경우 (<5%) 해당 변수가 F_score에 미치는 영향 미미.  
→ 빈도 확인 후 "희소 변수" 메모, 필요시 해당 그룹 제외 민감도 분석.

### 7-4. 건설업 회귀에서 β_SDI 방향

Version 1에서 건설업 β_SDI > 0 (가설 불지지)이었음.  
Version 2에서 F 변수를 제도적 변수로 교체하면 결과가 달라질 수 있으나,  
건설업 구조적 특성(현장 상주 감독자, 현장별 구성 변동) 때문에 여전히 불지지 가능.  
→ **건설업 결과가 불지지로 나오더라도 논문에서 "업종 특수 한계"로 명시하고 보고**. 결과에 맞춰 F/S 재정의는 Version 2에서 절대 금지.

### 7-5. 회귀 다중공선성

SDI = f(Q16/Q17 S변수들)이고 회귀에 Q16_1~3 같은 변수를 다시 투입하면 VIF 폭발.  
→ **§5 권장(B): SDI 구성에 포함된 변수는 회귀 독립변수에서 제외**.  
회귀 독립변수는 SDI에 포함되지 않은 변수만 사용 (Q14/Q15 위험성평가, Q18_1/Q19_1 교육실시, Q25 안전관리비, 근로자 구성 비율, 통제변수).

---

## 8. 파일 구조 (Version 2 신규 생성)

```
SAB_paper/
├── version1/          ← Version 1 모든 산출물 보관
├── version2.md        ← 이 문서
├── SDI_v2.ipynb       ← Version 2 분석 노트북 (새로 작성)
├── output/
│   └── v2/            ← Version 2 출력물 전용 폴더
│       ├── SDI_report_v2.md
│       ├── regression_results_con_v2.csv
│       ├── regression_results_ms_v2.csv
│       ├── sdi_descriptive_v2.csv
│       └── efa_loadings_v2.csv
├── data/raw/          ← 원본 데이터 (변경 불가)
└── CLAUDE.md
```

---

## 9. 예상 산출물 체크리스트

- [ ] 변수명 검증 출력 (실제 열 이름 확인표)
- [ ] F/S 변수 최종 확정 목록 (검증 후 수정본)
- [ ] 업종별 SDI 기술통계 (n, mean, std, SDI<0 비율, 가중평균)
- [ ] SDI 업종별 분포 박스플롯
- [ ] EFA 결과 (KMO, Bartlett, 고유값, 적재량)
- [ ] 회귀 결과: 건설업 (GLM NegBin + 로지스틱)
- [ ] 회귀 결과: 제조·서비스업 (GLM NegBin + 로지스틱)
- [ ] β_SDI 부호 일치 여부 확인 (두 모형 간)
- [ ] SDI_report_v2.md (최종 보고서)

---

## 10. Version 1 결과 참고용 요약

| 항목 | Version 1 결과 |
|---|---|
| F 변수 | Q17_1~6 (경영선언) / Q16_1~6 (건설) |
| S 변수 | Q17_7~17 / Q16_7~18 |
| 제조·서비스 β_SDI | -1.8174 (IRR=0.163, p<0.001***) → 가설 강하게 지지 |
| 건설 β_SDI | +0.838 (p=0.055) → 미유의, 가설 불지지 |
| SDI<0 비율 | 건설 63.2%, 제조 59.5%, 서비스 60.2% |
| 회귀 모형 | GLM NegBin, offset=log(workers) |

Version 2에서 제도적 F 변수로 교체하면 SDI의 이론적 정당성은 높아지나, 제조업 β_SDI 부호가 유지될지는 데이터 확인 후 판단.
