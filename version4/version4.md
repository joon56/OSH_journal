# Version 4 전용 워크플로우 지침서
> 작성일: 2026-05-23  
> 해결 과제: **고질적 문제 4 — F/S 이론적 경계의 모호성**  
> 전략: SDI = S − F 단일 지수를 분해하여 **F_score와 S_score를 독립 예측변수로 분리** 투입  
> 결과변수: Version 3와 동일 (ra_score) — 문제 1 해결 유지

---

## 0. Version 4 목적 한 줄 요약

> **"형식(F)과 실질(S)을 하나의 차이(SDI)로 압축하지 않고, 각각의 독립적 예측력을 직접 비교한다. β_S > β_F이면 '실질이 형식보다 더 중요하다'는 핵심 명제가 데이터로 직접 검증된다."**

---

## 1. CLAUDE.md와의 관계 — 변경·유지 항목 요약

| CLAUDE.md 절 | Version 4 처리 |
|---|---|
| §1 핵심 원칙 (11개) | **전부 그대로 적용** |
| §2 파일 구성 | **동일** (데이터 경로 변경 없음) |
| §3 업종별 문항 번호 차이 | **동일** (건설/제조 매핑 그대로) |
| §3-1 개념 매핑 17문항 | **동일** (F/S 분류 기준도 동일) |
| §3-2 Two-track 전략 | **단순화** — Track A(업종별)만 수행, Track B 생략 |
| §4 결측·무응답 처리 | **동일** |
| §5 워크플로우 5단계 | **⚠️ 핵심 변경** — 아래 §4 참조 |
| §6 코드 템플릿 | **⚠️ 핵심 변경** — 아래 §5 참조 |
| §7 산출물 체크리스트 | **변경** — 아래 §6 참조 |
| §7-1 환경 설정 | **동일** |
| §8 자주 하는 실수 | **동일 + Version 4 전용 주의사항 추가** |

---

## 2. 변경된 연구 가설

### 기존 가설 (V2/V3)
> β_SDI > 0: SDI가 높을수록 위험성평가가 더 실질적이다.

**문제점:** SDI = S − F로 압축하면 변수 분류 변동 시 SDI 값 전체가 흔들림.

### Version 4 가설 (직접 검증)
> **β_S > 0**: 실질 안전 점수가 높을수록 위험성평가 실질성이 높다.  
> **β_F ≈ 0 또는 유의하지 않음**: 형식 안전 점수는 위험성평가 실질성을 설명하지 못한다.  
> **β_S > β_F**: 실질의 효과가 형식의 효과보다 크다 (Wald 검정으로 확인).

### 가설 지지 기준

| 조건 | 기준 | 의미 |
|------|------|------|
| ① β_S > 0 | p < 0.05 | 실질 안전이 예방활동을 유의하게 양으로 예측 |
| ② β_F 비유의 | p > 0.1 | 형식 안전만으로는 예방활동 설명 불가 |
| ③ β_S > β_F | Wald p < 0.05 | 실질 효과가 형식 효과보다 통계적으로 큼 |
| ④ 민감도 분석 방향 일치 | 경계 변수 이동 후에도 ①② 유지 | 분류 선택에 결론이 의존하지 않음 |

①②③ 전부 충족 시 강한 가설 지지. ①③만 충족해도 방향 지지.

---

## 3. F/S 변수 목록 (Version 2/3와 동일 — 경계 변수만 따로 표시)

### 3-1. 건설업

**F_score 구성 그룹 (7그룹, 9개 변수):**
| 그룹 | 변수 | 개념 | 정규화 |
|------|------|------|--------|
| F-C1 | Q6 | 안전보건 전담부서 유무 | 이진(1→1, 2→0) |
| F-C2 | Q8_1, Q8_2 | 안전관리자·보건관리자 선임 인원 | minmax |
| F-C3 | Q8_3, Q8_4 | 안전보건 관리비 규모 | minmax |
| F-C4 | Q9 | 건설재해예방 기술지도기관 위탁 | 이진 |
| F-C5 | Q10 | 산업안전보건위원회 운영 | 3→0, 2→0.5, 1→1 |
| F-C6 | Q12_1 | KOSHA-MS 인증 | 이진 |
| F-C7 | Q12_2 | ISO 45001 인증 | 이진 |

**S_score 구성 그룹 (6그룹, 19개 변수):**
| 그룹 | 변수 | 개념 | 정규화 |
|------|------|------|--------|
| S-C1 | Q15_2_1~7 | 위험성평가 근로자 참여·노력 | minmax |
| S-C2 | Q16_1, Q16_2, Q16_3 | 경영진 안전 강조·우선순위·중시 | minmax |
| S-C3 | Q16_9, Q16_10 | 교육 실시·교육 실질 효과 | minmax |
| S-C4 | Q16_16, Q16_17, Q16_18 | 근로자 표준 준수·작업거부·자발적 개선 | minmax |
| S-C5 | Q17_1, Q17_2, Q17_4 | 작업반장 역할인지·책임인지·조치능력 | minmax |
| S-C6 | Q21_2 | 작업환경측정 결과 개선 노력 | minmax |

> F 9개(7그룹) / S 19개(6그룹). 그룹 composite 방식으로 변수 수 불균형 해소.

### 3-2. 제조·서비스업

**F_score 구성 그룹 (8그룹, 10개 변수):**
| 그룹 | 변수 | 개념 | 정규화 |
|------|------|------|--------|
| F-M1 | Q6 | 안전보건 전담부서 유무 | 이진 |
| F-M2 | Q8_1, Q8_2 | 안전관리자·보건관리자 선임 인원 | minmax |
| F-M3 | Q9_1, Q9_2 | 기술지도기관 위탁 | 이진 |
| F-M4 | Q10 | 산업안전보건위원회 | 이진(1→1, 2→0, 3→NaN) |
| F-M5 | Q11 | 안전보건관리담당자 선임 | 이진 |
| F-M6 | Q13_1 | KOSHA-MS 인증 | 이진 |
| F-M7 | Q13_2 | ISO 45001 인증 | 이진 |
| F-M8 | Q17_13 | 안전 시설·장비·보호구 **보유** | minmax |

> ⚠️ **F-M8(Q17_13)이 경계 변수**: 코드북 기준 "보유=형식"으로 F에 분류했으나, EFA에서 S 요인(F1) 적재량 0.680. 민감도 분석 대상.

**S_score 구성 그룹 (7그룹, 21개 변수):**
| 그룹 | 변수 | 개념 | 정규화 |
|------|------|------|--------|
| S-M1 | Q16_2_1~7 | 위험성평가 근로자 참여·노력 | minmax |
| S-M2 | Q17_1, Q17_2, Q17_3 | 경영진 안전 강조·우선순위·중시 | minmax |
| S-M3 | Q17_9, Q17_10 | 교육 실시·교육 실질 효과 | minmax |
| S-M4 | Q17_12 | 규정·절차가 사고예방에 실질 도움 | minmax |
| S-M5 | Q17_15, Q17_16, Q17_17 | 표준 준수·작업거부·자발적 개선 | minmax |
| S-M6 | Q18_1~4 | 관리감독자 역량 4문항 | minmax |
| S-M7 | Q22_2 | 작업환경측정 결과 개선 노력 | minmax |

> F 10개(8그룹) / S 21개(7그룹). 그룹 composite 방식으로 변수 수 불균형 해소.

---

## 4. 변경된 워크플로우 (5단계 → 5단계, 내용 교체)

### Step 1 — 데이터 로드 및 전처리
Version 3와 동일. ra_score(Q14/Q15), env_meas(Q21_1/Q22_1) 생성.

### Step 2 — F_score / S_score 계산 (그룹 composite)
SDI를 만들지 않고 F_score, S_score만 계산한다.

```python
# 그룹 composite 방식 (Version 2/3와 동일 함수, 단 SDI는 계산하지 않음)
def compute_fs(df, f_groups, s_groups, label=''):
    f_composites = {}
    s_composites = {}
    for gname, cols in f_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            f_composites[gname] = df[avail].mean(axis=1)
    for gname, cols in s_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            s_composites[gname] = df[avail].mean(axis=1)
    F_score = pd.DataFrame(f_composites).mean(axis=1)
    S_score = pd.DataFrame(s_composites).mean(axis=1)
    print(f'  [{label}] F_score: mean={F_score.mean():.4f} / S_score: mean={S_score.mean():.4f}')
    return F_score, S_score
# SDI = S - F 계산은 하지 않음 (Version 4에서는 참고용으로만)
```

### Step 3 — 기술통계 + 단변량 패턴 확인
F_score, S_score 분포 및 ra_score와의 개별 Spearman 상관 확인.

```python
# 확인 항목
r_f, p_f = stats.spearmanr(df['F_score'], df['ra_score'])  # F_score ↔ ra_score
r_s, p_s = stats.spearmanr(df['S_score'], df['ra_score'])  # S_score ↔ ra_score
# 가설 방향: r_s > r_f 여야 함
```

### Step 4 — 회귀 분석 (핵심)

**주 모형 (F/S 분리):**
```
ra_score ~ F_score + S_score + 통제변수
```

**비교 모형 (Version 3 SDI 방식, 참고용):**
```
ra_score ~ SDI + 통제변수   ← SDI = S_score - F_score
```

**Wald 검정 (β_S > β_F 직접 검정):**
```python
from scipy.stats import norm
# OLS에서 β_S - β_F의 t검정
b_s = res.params['S_score']
b_f = res.params['F_score']
se_s = res.bse['S_score']
se_f = res.bse['F_score']
cov_sf = res.cov_params().loc['S_score','F_score']
se_diff = np.sqrt(se_s**2 + se_f**2 - 2*cov_sf)
t_diff = (b_s - b_f) / se_diff
p_diff = 2 * (1 - norm.cdf(abs(t_diff)))  # 양측검정, 단측도 가능
print(f'β_S - β_F = {b_s - b_f:.4f}, t = {t_diff:.4f}, p = {p_diff:.4f}')
```

### Step 5 — 민감도 분석 (경계 변수 재분류)

**대상 변수:** 제조·서비스업 Q17_13 (안전 시설·장비·보호구 보유)
- 기본 분류: F-M8 (형식 — "보유=서류/시스템 존재")
- 대안 분류: S로 이동 (실질 — EFA에서 S 요인 적재량 높음)

```python
# 민감도 모형: Q17_13을 S로 이동
f_groups_sens = {k:v for k,v in f_groups_ms.items() if k != 'F-M8'}  # Q17_13 제거
s_groups_sens = {**s_groups_ms, 'S-M8': ['Q17_13_n']}                # Q17_13 S에 추가

F_sens, S_sens = compute_fs(df, f_groups_sens, s_groups_sens, label='민감도')
# 민감도 모형 회귀 실행 후 β_S, β_F 방향·유의성 비교
```

**판단 기준:** 기본 모형과 민감도 모형에서 ① β_S > 0 ② β_F 비유의 ③ β_S > β_F 방향이 모두 일치하면 "분류 강건성 확인".

---

## 5. 회귀 모형 설계

### 5-1. 건설업

```
[주 모형] ra_score ~ F_score + S_score + elder_rate + foreign_rate + female_rate + log(Q4_1)
[비교]    ra_score ~ SDI       + elder_rate + foreign_rate + female_rate + log(Q4_1)
[보조]    env_meas  ~ F_score + S_score + 통제변수  (로지스틱)
```

### 5-2. 제조+서비스업

```
[주 모형] ra_score ~ F_score + S_score + ind_mfg + elder_rate + foreign_rate + female_rate + log(Q1_1)
[비교]    ra_score ~ SDI       + ind_mfg + 통제변수
[보조]    env_meas  ~ F_score + S_score + ind_mfg + 통제변수  (로지스틱)
```

### 5-3. 순서형 로지스틱 병행

OLS와 동일한 공식으로 `OrderedModel` 실행. OLS와 순서형 방향 일치 시 강한 증거.

---

## 6. 결과변수 정의 (Version 3와 동일)

| 변수 | 업종 | 원코드 | 재코딩 |
|------|------|--------|--------|
| ra_score (주) | 건설 | Q14 | {1→2, 2→1, 3→0} |
| ra_score (주) | 제조·서비스 | Q15 | {1→2, 2→1, 3→0} |
| env_meas (보조) | 건설 | Q21_1 | {1→1, 2→0, 3·4→NaN} |
| env_meas (보조) | 제조·서비스 | Q22_1 | {1→1, 2→0, 3·4→NaN} |

---

## 7. 통제변수 (Version 3와 동일)

| 변수 | 코드 | 처리 |
|------|------|------|
| 종사자 규모 | log(Q4_1) 건설 / log(Q1_1) 제조서비스 | 연속형 |
| 업종 더미 | ind_mfg (제조=1/서비스=0) | 이진 |
| 고령자 비율 | Q4_2/Q4_1 (건설), Q1_2/Q1_1 (제조) | clip(0,1) |
| 외국인 비율 | Q4_3/Q4_1 (건설), Q1_3/Q1_1 (제조) | clip(0,1) |
| 여성 비율 | Q4_4/Q4_1 (건설), Q1_4/Q1_1 (제조) | clip(0,1) |

---

## 8. 단계별 작업 순서

```
Step 1: 데이터 로드 + 전처리
         → Version 3 전처리 동일 적용
         → ra_score, env_meas 생성

Step 2: F_score / S_score 계산
         → 그룹 composite (SDI는 참고용으로만 병기)
         → F_score, S_score 기술통계 출력

Step 3: 단변량 패턴 확인
         → F_score ↔ ra_score / S_score ↔ ra_score Spearman 상관
         → r_S > r_F 여부 확인 (가설 방향 사전 점검)

Step 4: 회귀 분석
         → 주 모형: F_score + S_score (OLS + 순서형 로지스틱)
         → 비교 모형: SDI (Version 3 결과와 대조)
         → Wald 검정: β_S - β_F 유의성

Step 5: 민감도 분석
         → Q17_13 F→S 재분류 후 재실행
         → 기본 vs 민감도 결론 일치 여부 표로 정리

Step 6: 보고서 생성
         → output/SDI_report_v4.md
```

---

## 9. 산출물 체크리스트

- [ ] F_score / S_score 기술통계 (업종별)
- [ ] 단변량 Spearman: F_score↔ra_score vs S_score↔ra_score 비교
- [ ] 건설업 주 모형 (OLS + 순서형): β_F, β_S, Wald p
- [ ] 제조+서비스 주 모형 (OLS + 순서형): β_F, β_S, Wald p
- [ ] 비교 모형 (SDI 방식) vs 주 모형 결과 대조표
- [ ] 민감도 분석 결과 (Q17_13 재분류 전후 비교)
- [ ] 보조 모형 (env_meas 로지스틱)
- [ ] β_S > β_F 방향 일치 여부 종합 판정표
- [ ] SDI_report_v4.md

---

## 10. Version 4 전용 주의사항 (CLAUDE.md §8에 추가)

12. **F_score와 S_score를 동시에 투입하면 다중공선성 확인 필수.** F_score와 S_score 간 상관이 높으면 (r > 0.7) VIF를 출력해 보고한다. 상관이 높더라도 Wald 검정(β_S − β_F)은 공분산을 반영하므로 유효하다.
13. **SDI를 참고용으로만 병기하고 주 변수로 사용하지 않는다.** 주 모형에 SDI를 독립변수로 넣지 않는다. SDI = F_score + S_score를 투입한 모형과 동일한 정보이므로 완전 다중공선성 발생.
14. **Wald 검정의 방향성 명시.** β_S > β_F가 가설이므로 단측 검정(one-tailed) p/2를 보고하되, 양측 검정 결과도 병기한다.
15. **민감도 분석 결과가 역전될 경우 보고서에 명시.** 결론이 바뀐다면 해당 변수의 분류를 "경계(Review)"로 표시하고, 분류 불확실성이 결론에 미치는 영향을 정량화해 보고한다.

---

## 11. Version 2/3/4 비교표

| 항목 | Version 2 | Version 3 | Version 4 |
|------|-----------|-----------|-----------|
| 결과변수 | Q27 사고 건수 | ra_score (위험성평가) | ra_score (동일) |
| 주 독립변수 | SDI | SDI | **F_score + S_score** |
| 핵심 가설 | β_SDI < 0 | β_SDI > 0 | **β_S > 0, β_F ≈ 0, β_S > β_F** |
| F/S 경계 민감도 | 높음 (SDI 값 변동) | 높음 | **낮음 (분리 투입)** |
| 역인과 취약성 | 높음 | 낮음 (DV 교체) | 낮음 (동일) |
| 검정 방식 | t-test on β_SDI | t-test on β_SDI | **Wald test on β_S − β_F** |
| 민감도 분석 | 없음 | 없음 | **있음** |

---

## 12. 파일 구조

```
SAB_paper/version4/
├── version4.md          ← 이 문서
├── SDI_v4_main.py       ← 분석 스크립트
├── SDI_v4.ipynb         ← Jupyter 노트북
└── output/
    ├── SDI_report_v4.md
    ├── regression_fs_ols_con_v4.csv
    ├── regression_fs_ols_ms_v4.csv
    ├── regression_fs_ordinal_con_v4.csv
    ├── regression_fs_ordinal_ms_v4.csv
    ├── sensitivity_v4.csv
    └── fs_scatter_v4.png
```
