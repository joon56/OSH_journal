# SDI_v3 분석 스크립트 (version3.md 기준)
# 해결 과제: 고질적 문제 1 — 횡단 설계 인과관계 문제
# 전략: 결과변수를 Q27 사고율 → 위험성평가 실질성(Q14/Q15) + 예방활동으로 교체
#
# 결과변수:
#   주  : Q14(건설)/Q15(제조서비스) 위험성평가 수준 → ra_score (0~2, 높을수록 실질적)
#   보조: Q21_1(건설)/Q22_1(제조서비스) 작업환경측정 실시 여부 (이진)
#         Q19_1(건설)/Q20_1(제조서비스) 건강진단 실시 여부 (이진, 참고용)
# 가설: β_SDI > 0 (SDI 높을수록 위험성평가가 더 실질적)
# SDI 계산: Version 2와 동일

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep
RAW  = ROOT + 'data' + os.sep + 'raw' + os.sep
OUT  = BASE + 'output' + os.sep
os.makedirs(OUT, exist_ok=True)

plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

files = os.listdir(RAW)
F_CON = RAW + [f for f in files if '건설' in f and f.lower().endswith('.csv')][0]
F_MFG = RAW + [f for f in files if '제조' in f and f.lower().endswith('.csv')][0]
F_SVC = RAW + [f for f in files if '서비스' in f and f.lower().endswith('.csv')][0]

print("=" * 60)
print("SDI Version 3 분석")
print("목표: 결과변수를 위험성평가 실질성으로 교체 (문제 1 해결)")
print("=" * 60)

# ============================================================
# 공통 함수 (Version 2와 동일)
# ============================================================
def minmax(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) if mx > mn else pd.Series(0.0, index=s.index)

def binary_norm(s):
    return s.map({1: 1.0, 2: 0.0})

def q10_con_norm(s):
    return s.map({1: 1.0, 2: 0.5, 3: 0.0, 4: np.nan, 9: np.nan})

def q10_ms_norm(s):
    return s.map({1: 1.0, 2: 0.0, 3: np.nan})

def compute_sdi(df, f_groups, s_groups, label=''):
    f_composites, s_composites = {}, {}
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
    SDI = S_score - F_score
    f_total = sum(len(v) for v in f_groups.values())
    s_total = sum(len(v) for v in s_groups.values())
    print(f"  [{label}] F={f_total}개({len(f_groups)}그룹) / S={s_total}개({len(s_groups)}그룹)")
    print(f"  [{label}] SDI: n={SDI.notna().sum()}, mean={SDI.mean():.4f}, std={SDI.std():.4f}")
    return SDI, F_score, S_score

# ============================================================
# STEP 2: 데이터 로드 및 전처리
# ============================================================
print("\n[Step 2] 데이터 로드 및 전처리")

# ── 건설업 ──────────────────────────────────────────────────
df_con = pd.read_csv(F_CON)
# SDI 변수 무응답 처리 (Version 2 동일)
likert_con = ([f'Q15_2_{i}' for i in range(1,8)] +
              ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
               'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4'])
df_con[likert_con] = df_con[likert_con].replace(9, np.nan)
df_con['Q21_2'] = df_con['Q21_2'].replace(9, np.nan)
df_con['Q6']    = df_con['Q6'].replace(9, np.nan)
df_con['Q9']    = df_con['Q9'].replace(9, np.nan)
for c in ['Q8_1','Q8_2','Q8_3','Q8_4']:
    df_con[c] = df_con[c].replace(999, np.nan)
for c in ['Q4_1','Q4_2','Q4_3','Q4_4']:
    df_con[c] = df_con[c].replace(99999, np.nan)

# 위험성평가 수준: Q14 건설 (코드북 확인 후 3범주 확정)
# 실제 값: 1(실질적), 2(명목적), 3(미실시/형식적) — 코드북 기준 적용
# version2.md mapping {1:1.0, 2:0.75, 3:0.5, 4:0.0, 9:NaN}에서 실제 데이터 값이 1,2,3만 존재
# → 3 = 미실시(4와 합산)로 처리 (건설 특성상 3=형식적 실시가 포함될 수 있음)
# ra_score: 높을수록 실질적
df_con['ra_score'] = df_con['Q14'].map({1: 2, 2: 1, 3: 0})  # 0~2

# 작업환경측정: Q21_1 (1=실시, 2=안함, 3=해당없음→NaN, 4=모름→NaN)
df_con['env_meas'] = df_con['Q21_1'].map({1: 1.0, 2: 0.0, 3: np.nan, 4: np.nan})

# 건강진단: Q19_1 (1=실시, 2=미실시)
df_con['health_exam'] = df_con['Q19_1'].map({1: 1.0, 2: 0.0})

# 통제변수
df_con['elder_rate']   = (df_con['Q4_2'] / df_con['Q4_1']).clip(0, 1)
df_con['foreign_rate'] = (df_con['Q4_3'] / df_con['Q4_1']).clip(0, 1)
df_con['female_rate']  = (df_con['Q4_4'] / df_con['Q4_1']).clip(0, 1)
df_con['log_workers']  = np.log(df_con['Q4_1'].clip(lower=1))

print(f"\n  건설 ra_score: {df_con['ra_score'].value_counts(dropna=False).sort_index().to_dict()}")
print(f"  건설 env_meas: {df_con['env_meas'].value_counts(dropna=False).to_dict()}")
print(f"  건설 health_exam: {df_con['health_exam'].value_counts(dropna=False).to_dict()}")

# ── 제조·서비스업 공통 전처리 ───────────────────────────────
likert_ms = ([f'Q16_2_{i}' for i in range(1,8)] +
             ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
              'Q17_12','Q17_13','Q17_15','Q17_16','Q17_17',
              'Q18_1','Q18_2','Q18_3','Q18_4'])

def preprocess_ms(path, label):
    df = pd.read_csv(path)
    df[likert_ms] = df[likert_ms].replace(9, np.nan)
    df['Q22_2'] = df['Q22_2'].replace(9, np.nan)
    df['Q6']    = df['Q6'].replace(9, np.nan)
    for c in ['Q9_1','Q9_2','Q11']:
        df[c] = df[c].replace(9, np.nan)
    df['Q10_norm'] = q10_ms_norm(df['Q10'])
    for c in ['Q8_1','Q8_2']:
        df[c] = df[c].replace(999, np.nan)
    for c in ['Q1_1','Q1_2','Q1_3','Q1_4']:
        df[c] = df[c].replace(99999, np.nan)

    # 위험성평가 수준: Q15 (1=실질, 2=명목, 3=미실시)
    df['ra_score'] = df['Q15'].map({1: 2, 2: 1, 3: 0})

    # 작업환경측정: Q22_1 (1=실시, 2=안함, 3=해당없음→NaN, 4=모름→NaN)
    df['env_meas'] = df['Q22_1'].map({1: 1.0, 2: 0.0, 3: np.nan, 4: np.nan})

    # 건강진단: Q20_1 (1=실시, 2=미실시)
    df['health_exam'] = df['Q20_1'].map({1: 1.0, 2: 0.0})

    df['elder_rate']   = (df['Q1_2'] / df['Q1_1']).clip(0, 1)
    df['foreign_rate'] = (df['Q1_3'] / df['Q1_1']).clip(0, 1)
    df['female_rate']  = (df['Q1_4'] / df['Q1_1']).clip(0, 1)
    df['log_workers']  = np.log(df['Q1_1'].clip(lower=1))
    df['industry']     = label

    print(f"\n  {label} ra_score: {df['ra_score'].value_counts(dropna=False).sort_index().to_dict()}")
    print(f"  {label} env_meas 실시율: {df['env_meas'].mean():.1%} (n={df['env_meas'].notna().sum()})")
    print(f"  {label} health_exam 실시율: {df['health_exam'].mean():.1%} (n={df['health_exam'].notna().sum()})")
    return df

df_mfg = preprocess_ms(F_MFG, '제조')
df_svc = preprocess_ms(F_SVC, '서비스')

# ============================================================
# STEP 3: SDI 계산 (Version 2 동일)
# ============================================================
print("\n" + "=" * 60)
print("[Step 3] SDI 계산 (Version 2 동일)")
print("=" * 60)

# 건설 정규화
df_con['Q6_n']    = binary_norm(df_con['Q6'])
df_con['Q8_1_n']  = minmax(df_con['Q8_1'])
df_con['Q8_2_n']  = minmax(df_con['Q8_2'])
df_con['Q8_3_n']  = minmax(df_con['Q8_3'])
df_con['Q8_4_n']  = minmax(df_con['Q8_4'])
df_con['Q9_n']    = binary_norm(df_con['Q9'])
df_con['Q10_norm'] = q10_con_norm(df_con['Q10'])
df_con['Q12_1_n'] = binary_norm(df_con['Q12_1'])
df_con['Q12_2_n'] = binary_norm(df_con['Q12_2'])
for c in ([f'Q15_2_{i}' for i in range(1,8)] +
          ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
           'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4','Q21_2']):
    df_con[c + '_n'] = minmax(df_con[c])

f_groups_con = {
    'F-C1': ['Q6_n'], 'F-C2': ['Q8_1_n','Q8_2_n'], 'F-C3': ['Q8_3_n','Q8_4_n'],
    'F-C4': ['Q9_n'], 'F-C5': ['Q10_norm'], 'F-C6': ['Q12_1_n'], 'F-C7': ['Q12_2_n'],
}
s_groups_con = {
    'S-C2': [f'Q15_2_{i}_n' for i in range(1,8)],
    'S-C3': ['Q16_1_n','Q16_2_n','Q16_3_n'],
    'S-C4': ['Q16_9_n','Q16_10_n'],
    'S-C5': ['Q16_16_n','Q16_17_n','Q16_18_n'],
    'S-C6': ['Q17_1_n','Q17_2_n','Q17_4_n'],
    'S-C7': ['Q21_2_n'],
}
df_con['SDI'], df_con['F_score'], df_con['S_score'] = compute_sdi(
    df_con, f_groups_con, s_groups_con, label='건설')

# 제조·서비스 정규화
for df_ in [df_mfg, df_svc]:
    df_['Q6_n']    = binary_norm(df_['Q6'])
    df_['Q8_1_n']  = minmax(df_['Q8_1'])
    df_['Q8_2_n']  = minmax(df_['Q8_2'])
    df_['Q9_1_n']  = binary_norm(df_['Q9_1'])
    df_['Q9_2_n']  = binary_norm(df_['Q9_2'])
    df_['Q11_n']   = binary_norm(df_['Q11'])
    df_['Q13_1_n'] = binary_norm(df_['Q13_1'])
    df_['Q13_2_n'] = binary_norm(df_['Q13_2'])
    df_['Q17_13_n'] = minmax(df_['Q17_13'])
    for c in ([f'Q16_2_{i}' for i in range(1,8)] +
              ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
               'Q17_12','Q17_15','Q17_16','Q17_17',
               'Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']):
        df_[c + '_n'] = minmax(df_[c])

f_groups_ms = {
    'F-M1': ['Q6_n'], 'F-M2': ['Q8_1_n','Q8_2_n'],
    'F-M3': ['Q9_1_n','Q9_2_n'], 'F-M4': ['Q10_norm'],
    'F-M5': ['Q11_n'], 'F-M6': ['Q13_1_n'],
    'F-M7': ['Q13_2_n'], 'F-M8': ['Q17_13_n'],
}
s_groups_ms = {
    'S-M1': [f'Q16_2_{i}_n' for i in range(1,8)],
    'S-M2': ['Q17_1_n','Q17_2_n','Q17_3_n'],
    'S-M3': ['Q17_9_n','Q17_10_n'],
    'S-M4': ['Q17_12_n'],
    'S-M5': ['Q17_15_n','Q17_16_n','Q17_17_n'],
    'S-M6': ['Q18_1_n','Q18_2_n','Q18_3_n','Q18_4_n'],
    'S-M7': ['Q22_2_n'],
}
df_mfg['SDI'], df_mfg['F_score'], df_mfg['S_score'] = compute_sdi(
    df_mfg, f_groups_ms, s_groups_ms, label='제조')
df_svc['SDI'], df_svc['F_score'], df_svc['S_score'] = compute_sdi(
    df_svc, f_groups_ms, s_groups_ms, label='서비스')

# ============================================================
# STEP 4: 결과변수 기술통계 + SDI 분위별 ra_score 비교
# ============================================================
print("\n" + "=" * 60)
print("[Step 4] 결과변수 기술통계")
print("=" * 60)

print("\n  [위험성평가 실질성 점수(ra_score) 분포]")
for label, df_ in [('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)]:
    vc = df_['ra_score'].value_counts(dropna=False).sort_index()
    n  = df_['ra_score'].notna().sum()
    m  = df_['ra_score'].mean()
    pct_top = (df_['ra_score'] == 2).mean()
    print(f"  {label}: n={n}, mean={m:.3f}, 실질적(2) 비율={pct_top:.1%}")
    print(f"    {vc.to_dict()}")

print("\n  [작업환경측정 실시율]")
for label, df_ in [('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)]:
    n_valid = df_['env_meas'].notna().sum()
    rate = df_['env_meas'].mean()
    print(f"  {label}: 실시율={rate:.1%}, n={n_valid}")

# SDI 분위별 ra_score 평균 비교
print("\n  [SDI 분위별 ra_score 평균 (가설 방향 확인)]")
for label, df_ in [('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)]:
    d = df_[['SDI','ra_score']].dropna()
    d['sdi_q'] = pd.qcut(d['SDI'], q=4, labels=['Q1(최저)','Q2','Q3','Q4(최고)'])
    means = d.groupby('sdi_q', observed=True)['ra_score'].mean()
    r, p = stats.spearmanr(d['SDI'], d['ra_score'])
    print(f"  {label}: Spearman r={r:.3f}, p={p:.4f}")
    print(f"    SDI 분위별 ra_score 평균: {means.round(3).to_dict()}")

# 시각화: SDI 분위별 ra_score
fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
colors = ['#4e79a7','#f28e2b','#59a14f']
for ax, (label, df_), col in zip(axes, [('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)], colors):
    d = df_[['SDI','ra_score']].dropna()
    d['sdi_q'] = pd.qcut(d['SDI'], q=4, labels=['Q1','Q2','Q3','Q4'])
    means = d.groupby('sdi_q', observed=True)['ra_score'].mean()
    ax.bar(means.index, means.values, color=col, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.set_title(f'{label}업')
    ax.set_xlabel('SDI 분위')
    ax.set_ylabel('ra_score 평균')
    ax.set_ylim(0, 2)
    for i, v in enumerate(means.values):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=9)

fig.suptitle('SDI 분위별 위험성평가 실질성 점수 (Version 3)', fontsize=11)
plt.tight_layout()
fig.savefig(OUT + 'sdi_ra_quartile_v3.png', dpi=150)
plt.close()
print(f"\n  시각화 저장: {OUT}sdi_ra_quartile_v3.png")

# ============================================================
# STEP 5: 회귀 분석
# ============================================================
print("\n" + "=" * 60)
print("[Step 5] 회귀 분석")
print("=" * 60)

# ── 5-1. 건설업 ────────────────────────────────────────────
print("\n  [5-1] 건설업")
reg_cols_con = ['SDI', 'elder_rate', 'foreign_rate', 'female_rate', 'log_workers']
df_rc = df_con[reg_cols_con + ['ra_score', 'env_meas', 'health_exam']].dropna(
    subset=reg_cols_con + ['ra_score'])
print(f"  ra_score 회귀 샘플: n={len(df_rc)}")
X_rc = sm.add_constant(df_rc[reg_cols_con])

# OLS (ra_score 연속형)
res_ols_con = sm.OLS(df_rc['ra_score'], X_rc).fit()
coef_ols_con = pd.DataFrame({
    'coef': res_ols_con.params, 'std': res_ols_con.bse,
    't': res_ols_con.tvalues, 'p': res_ols_con.pvalues,
    'CI_lo': res_ols_con.conf_int()[0], 'CI_hi': res_ols_con.conf_int()[1]
})
print("\n  --- 건설업 OLS (ra_score) ---")
print(coef_ols_con.round(4).to_string())
print(f"  R²={res_ols_con.rsquared:.4f}")
coef_ols_con.to_csv(OUT + 'regression_ra_ols_con_v3.csv', encoding='utf-8-sig')
sdi_ols_con = (res_ols_con.params['SDI'], res_ols_con.pvalues['SDI'])

# 순서형 로지스틱 (ra_score 범주형)
try:
    from statsmodels.miscmodels.ordinal_model import OrderedModel
    mod_ord_con = OrderedModel(df_rc['ra_score'].astype(int), df_rc[reg_cols_con],
                               distr='logit')
    res_ord_con = mod_ord_con.fit(method='bfgs', maxiter=300, disp=False)
    coef_ord_con = pd.DataFrame({
        'coef': res_ord_con.params, 'p': res_ord_con.pvalues
    })
    print("\n  --- 건설업 순서형 로지스틱 ---")
    print(coef_ord_con.round(4).to_string())
    sdi_ord_con = (res_ord_con.params.get('SDI', np.nan),
                   res_ord_con.pvalues.get('SDI', np.nan))
    coef_ord_con.to_csv(OUT + 'regression_ra_ordinal_con_v3.csv', encoding='utf-8-sig')
except Exception as e:
    print(f"  순서형 로지스틱 실패: {e}")
    sdi_ord_con = (np.nan, np.nan)

# 보조: 작업환경측정 로지스틱
df_env_con = df_con[reg_cols_con + ['env_meas']].dropna()
if len(df_env_con) > 50:
    X_env = sm.add_constant(df_env_con[reg_cols_con])
    res_env_con = sm.Logit(df_env_con['env_meas'], X_env).fit(maxiter=200, disp=False)
    print(f"\n  --- 건설업 작업환경측정 로지스틱 (n={len(df_env_con)}) ---")
    env_row = pd.DataFrame({'coef': res_env_con.params, 'OR': np.exp(res_env_con.params),
                             'p': res_env_con.pvalues})
    print(env_row.round(4).to_string())
    sdi_env_con = (res_env_con.params['SDI'], res_env_con.pvalues['SDI'])
else:
    sdi_env_con = (np.nan, np.nan)

# ── 5-2. 제조+서비스 합산 ──────────────────────────────────
print("\n  [5-2] 제조+서비스업")
df_mfg['ind_mfg'] = 1
df_svc['ind_mfg'] = 0
merge_cols = ['SDI','F_score','S_score','ra_score','env_meas','health_exam',
              'elder_rate','foreign_rate','female_rate','log_workers','ind_mfg','WT2']
df_ms = pd.concat([df_mfg[merge_cols], df_svc[merge_cols]], ignore_index=True)

reg_cols_ms = ['SDI','ind_mfg','elder_rate','foreign_rate','female_rate','log_workers']
df_rm = df_ms[reg_cols_ms + ['ra_score']].dropna()
print(f"  ra_score 회귀 샘플: n={len(df_rm)}")
X_rm = sm.add_constant(df_rm[reg_cols_ms])

# OLS
res_ols_ms = sm.OLS(df_rm['ra_score'], X_rm).fit()
coef_ols_ms = pd.DataFrame({
    'coef': res_ols_ms.params, 'std': res_ols_ms.bse,
    't': res_ols_ms.tvalues, 'p': res_ols_ms.pvalues,
    'CI_lo': res_ols_ms.conf_int()[0], 'CI_hi': res_ols_ms.conf_int()[1]
})
print("\n  --- 제조+서비스 OLS (ra_score) ---")
print(coef_ols_ms.round(4).to_string())
print(f"  R²={res_ols_ms.rsquared:.4f}")
coef_ols_ms.to_csv(OUT + 'regression_ra_ols_ms_v3.csv', encoding='utf-8-sig')
sdi_ols_ms = (res_ols_ms.params['SDI'], res_ols_ms.pvalues['SDI'])

# 순서형 로지스틱
try:
    mod_ord_ms = OrderedModel(df_rm['ra_score'].astype(int), df_rm[reg_cols_ms],
                              distr='logit')
    res_ord_ms = mod_ord_ms.fit(method='bfgs', maxiter=300, disp=False)
    coef_ord_ms = pd.DataFrame({
        'coef': res_ord_ms.params, 'p': res_ord_ms.pvalues
    })
    print("\n  --- 제조+서비스 순서형 로지스틱 ---")
    print(coef_ord_ms.round(4).to_string())
    sdi_ord_ms = (res_ord_ms.params.get('SDI', np.nan),
                  res_ord_ms.pvalues.get('SDI', np.nan))
    coef_ord_ms.to_csv(OUT + 'regression_ra_ordinal_ms_v3.csv', encoding='utf-8-sig')
except Exception as e:
    print(f"  순서형 로지스틱 실패: {e}")
    sdi_ord_ms = (np.nan, np.nan)

# 보조: 작업환경측정
df_env_ms = df_ms[reg_cols_ms + ['env_meas']].dropna()
if len(df_env_ms) > 50:
    X_env_ms = sm.add_constant(df_env_ms[reg_cols_ms])
    res_env_ms = sm.Logit(df_env_ms['env_meas'], X_env_ms).fit(maxiter=200, disp=False)
    print(f"\n  --- 제조+서비스 작업환경측정 로지스틱 (n={len(df_env_ms)}) ---")
    env_ms_row = pd.DataFrame({'coef': res_env_ms.params,
                                'OR': np.exp(res_env_ms.params),
                                'p': res_env_ms.pvalues})
    print(env_ms_row.round(4).to_string())
    sdi_env_ms = (res_env_ms.params['SDI'], res_env_ms.pvalues['SDI'])
    env_ms_row.to_csv(OUT + 'regression_env_ms_v3.csv', encoding='utf-8-sig')
else:
    sdi_env_ms = (np.nan, np.nan)

# ============================================================
# 최종 요약
# ============================================================
print("\n" + "=" * 60)
print("최종 요약: β_SDI 결과 (가설: β > 0)")
print("=" * 60)

results = [
    ('건설   OLS(ra_score)',        *sdi_ols_con),
    ('건설   순서형로지스틱',        *sdi_ord_con),
    ('건설   작업환경측정로지스틱',   *sdi_env_con),
    ('제조+서비스 OLS(ra_score)',    *sdi_ols_ms),
    ('제조+서비스 순서형로지스틱',   *sdi_ord_ms),
    ('제조+서비스 작업환경측정로지스틱', *sdi_env_ms),
]
for name, coef, p in results:
    if np.isnan(coef):
        print(f"  {name:38s}: 결과없음")
        continue
    sig  = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ('†' if p < 0.1 else '')))
    supp = '가설지지(β>0)' if coef > 0 else '불지지(β<0)'
    print(f"  {name:38s}: β={coef:+.4f}, p={p:.4f}{sig} → {supp}")

print("\n[역인과 차단 논리]")
print("  SDI는 F(인증·선임·전담부서)와 S(경영강조·행동·감독자역량)으로 구성.")
print("  위험성평가 수준(Q14/Q15)은 SDI 구성 변수에 포함되지 않음.")
print("  따라서 '위험성평가 나빠서 SDI가 낮아진다'는 역인과 경로는 구조적으로 차단됨.")

print(f"\n산출물: {OUT}")
print("완료.")
