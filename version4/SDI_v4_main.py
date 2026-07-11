# SDI_v4 분석 스크립트 (version4.md 기준)
# 해결 과제: 고질적 문제 4 — F/S 이론적 경계의 모호성
# 전략: SDI = S - F 단일 지수 분해 → F_score + S_score 독립 예측변수로 분리
#
# 가설:
#   β_S > 0  (p<0.05): 실질 안전이 위험성평가 실질성을 양으로 예측
#   β_F ≈ 0  (p>0.1) : 형식 안전은 위험성평가 실질성을 설명하지 못함
#   β_S > β_F         : Wald 검정으로 직접 확인
# 결과변수: ra_score (Version 3와 동일 — 문제 1 해결 유지)
# F/S 변수: Version 2/3와 동일

import os, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel
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
print("SDI Version 4 분석")
print("목표: F_score + S_score 분리 투입 (문제 4 해결)")
print("=" * 60)

# ============================================================
# 공통 함수
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

def compute_fs(df, f_groups, s_groups, label=''):
    f_comp, s_comp = {}, {}
    for gname, cols in f_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            f_comp[gname] = df[avail].mean(axis=1)
    for gname, cols in s_groups.items():
        avail = [c for c in cols if c in df.columns]
        if avail:
            s_comp[gname] = df[avail].mean(axis=1)
    F = pd.DataFrame(f_comp).mean(axis=1)
    S = pd.DataFrame(s_comp).mean(axis=1)
    f_total = sum(len(v) for v in f_groups.values())
    s_total = sum(len(v) for v in s_groups.values())
    print(f"  [{label}] F={f_total}개({len(f_groups)}그룹) / S={s_total}개({len(s_groups)}그룹)")
    print(f"  [{label}] F_score mean={F.mean():.4f} / S_score mean={S.mean():.4f}")
    return F, S

def wald_test(res, var_a, var_b):
    """β_a - β_b의 Wald 검정 (양측). β_a > β_b 단측은 p/2."""
    b_a = res.params[var_a]
    b_b = res.params[var_b]
    se_a = res.bse[var_a]
    se_b = res.bse[var_b]
    cov = res.cov_params().loc[var_a, var_b]
    se_diff = np.sqrt(se_a**2 + se_b**2 - 2*cov)
    t = (b_a - b_b) / se_diff
    p_two = 2 * (1 - norm.cdf(abs(t)))
    p_one = p_two / 2 if t > 0 else 1 - p_two / 2
    return b_a - b_b, t, p_two, p_one

# ============================================================
# STEP 1: 데이터 로드 및 전처리 (Version 3와 동일)
# ============================================================
print("\n[Step 1] 데이터 로드 및 전처리")

# ── 건설업 ─────────────────────────────────────────────────
df_con = pd.read_csv(F_CON)

likert_con = ([f'Q15_2_{i}' for i in range(1, 8)] +
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

df_con['ra_score']   = df_con['Q14'].map({1: 2, 2: 1, 3: 0})
df_con['env_meas']   = df_con['Q21_1'].map({1: 1.0, 2: 0.0, 3: np.nan, 4: np.nan})
df_con['elder_rate']   = (df_con['Q4_2'] / df_con['Q4_1']).clip(0, 1)
df_con['foreign_rate'] = (df_con['Q4_3'] / df_con['Q4_1']).clip(0, 1)
df_con['female_rate']  = (df_con['Q4_4'] / df_con['Q4_1']).clip(0, 1)
df_con['log_workers']  = np.log(df_con['Q4_1'].clip(lower=1))
print(f"  건설 ra_score: {df_con['ra_score'].value_counts(dropna=False).sort_index().to_dict()}")

# ── 제조·서비스업 ──────────────────────────────────────────
likert_ms = ([f'Q16_2_{i}' for i in range(1, 8)] +
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
    df['ra_score']    = df['Q15'].map({1: 2, 2: 1, 3: 0})
    df['env_meas']    = df['Q22_1'].map({1: 1.0, 2: 0.0, 3: np.nan, 4: np.nan})
    df['elder_rate']   = (df['Q1_2'] / df['Q1_1']).clip(0, 1)
    df['foreign_rate'] = (df['Q1_3'] / df['Q1_1']).clip(0, 1)
    df['female_rate']  = (df['Q1_4'] / df['Q1_1']).clip(0, 1)
    df['log_workers']  = np.log(df['Q1_1'].clip(lower=1))
    df['industry']     = label
    print(f"  {label} ra_score: {df['ra_score'].value_counts(dropna=False).sort_index().to_dict()}")
    return df

df_mfg = preprocess_ms(F_MFG, '제조')
df_svc = preprocess_ms(F_SVC, '서비스')

# ============================================================
# STEP 2: F_score / S_score 계산 (SDI는 참고용으로만)
# ============================================================
print("\n" + "=" * 60)
print("[Step 2] F_score / S_score 계산")
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
for c in ([f'Q15_2_{i}' for i in range(1, 8)] +
          ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
           'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4','Q21_2']):
    df_con[c + '_n'] = minmax(df_con[c])

f_groups_con = {
    'F-C1': ['Q6_n'], 'F-C2': ['Q8_1_n','Q8_2_n'], 'F-C3': ['Q8_3_n','Q8_4_n'],
    'F-C4': ['Q9_n'], 'F-C5': ['Q10_norm'], 'F-C6': ['Q12_1_n'], 'F-C7': ['Q12_2_n'],
}
s_groups_con = {
    'S-C1': [f'Q15_2_{i}_n' for i in range(1, 8)],
    'S-C2': ['Q16_1_n','Q16_2_n','Q16_3_n'],
    'S-C3': ['Q16_9_n','Q16_10_n'],
    'S-C4': ['Q16_16_n','Q16_17_n','Q16_18_n'],
    'S-C5': ['Q17_1_n','Q17_2_n','Q17_4_n'],
    'S-C6': ['Q21_2_n'],
}
print("\n  === 건설업 ===")
df_con['F_score'], df_con['S_score'] = compute_fs(df_con, f_groups_con, s_groups_con, '건설')
df_con['SDI'] = df_con['S_score'] - df_con['F_score']  # 참고용

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
    for c in ([f'Q16_2_{i}' for i in range(1, 8)] +
              ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
               'Q17_12','Q17_15','Q17_16','Q17_17',
               'Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']):
        df_[c + '_n'] = minmax(df_[c])

f_groups_ms = {
    'F-M1': ['Q6_n'], 'F-M2': ['Q8_1_n','Q8_2_n'],
    'F-M3': ['Q9_1_n','Q9_2_n'], 'F-M4': ['Q10_norm'],
    'F-M5': ['Q11_n'], 'F-M6': ['Q13_1_n'],
    'F-M7': ['Q13_2_n'], 'F-M8': ['Q17_13_n'],  # 경계 변수
}
s_groups_ms = {
    'S-M1': [f'Q16_2_{i}_n' for i in range(1, 8)],
    'S-M2': ['Q17_1_n','Q17_2_n','Q17_3_n'],
    'S-M3': ['Q17_9_n','Q17_10_n'],
    'S-M4': ['Q17_12_n'],
    'S-M5': ['Q17_15_n','Q17_16_n','Q17_17_n'],
    'S-M6': ['Q18_1_n','Q18_2_n','Q18_3_n','Q18_4_n'],
    'S-M7': ['Q22_2_n'],
}
print("\n  === 제조업 ===")
df_mfg['F_score'], df_mfg['S_score'] = compute_fs(df_mfg, f_groups_ms, s_groups_ms, '제조')
df_mfg['SDI'] = df_mfg['S_score'] - df_mfg['F_score']
print("\n  === 서비스업 ===")
df_svc['F_score'], df_svc['S_score'] = compute_fs(df_svc, f_groups_ms, s_groups_ms, '서비스')
df_svc['SDI'] = df_svc['S_score'] - df_svc['F_score']

# ============================================================
# STEP 3: 단변량 패턴 확인
# ============================================================
print("\n" + "=" * 60)
print("[Step 3] 단변량 Spearman 상관 (F_score, S_score vs ra_score)")
print("=" * 60)
print("  가설 방향: r_S > r_F\n")

for label, df_ in [('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)]:
    d = df_[['F_score','S_score','ra_score']].dropna()
    r_f, p_f = stats.spearmanr(d['F_score'], d['ra_score'])
    r_s, p_s = stats.spearmanr(d['S_score'], d['ra_score'])
    direction = "r_S > r_F [가설지지]" if r_s > r_f else "r_S <= r_F [불지지]"
    print(f"  {label}: r_F={r_f:+.3f}(p={p_f:.4f}) | r_S={r_s:+.3f}(p={p_s:.4f}) → {direction}")

    # F-S 간 상관 (다중공선성 사전 점검)
    r_fs, _ = stats.pearsonr(d['F_score'], d['S_score'])
    vif_warn = " ⚠️ 상관 높음(VIF 확인 필요)" if abs(r_fs) > 0.7 else ""
    print(f"    F-S 간 Pearson r={r_fs:.3f}{vif_warn}")

# 시각화: F_score vs S_score 분포 및 ra_score와의 산점도
fig, axes = plt.subplots(2, 3, figsize=(13, 8))
colors = {'건설':'#4e79a7','제조':'#f28e2b','서비스':'#59a14f'}
for col, (label, df_) in enumerate([('건설', df_con), ('제조', df_mfg), ('서비스', df_svc)]):
    d = df_[['F_score','S_score','ra_score']].dropna()
    c = colors[label]
    # 위: F_score vs ra_score
    axes[0, col].scatter(d['F_score'], d['ra_score'], alpha=0.15, s=8, color=c)
    r_f, _ = stats.spearmanr(d['F_score'], d['ra_score'])
    axes[0, col].set_title(f'{label}업 F_score vs ra_score\n(r={r_f:.3f})')
    axes[0, col].set_xlabel('F_score'); axes[0, col].set_ylabel('ra_score')
    # 아래: S_score vs ra_score
    axes[1, col].scatter(d['S_score'], d['ra_score'], alpha=0.15, s=8, color=c)
    r_s, _ = stats.spearmanr(d['S_score'], d['ra_score'])
    axes[1, col].set_title(f'{label}업 S_score vs ra_score\n(r={r_s:.3f})')
    axes[1, col].set_xlabel('S_score'); axes[1, col].set_ylabel('ra_score')
fig.suptitle('F_score / S_score vs 위험성평가 실질성 (Version 4)', fontsize=12, fontweight='bold')
plt.tight_layout()
fig.savefig(OUT + 'fs_scatter_v4.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  산점도 저장: {OUT}fs_scatter_v4.png")

# ============================================================
# STEP 4: 회귀 분석
# ============================================================
print("\n" + "=" * 60)
print("[Step 4] 회귀 분석: F_score + S_score 분리 투입")
print("=" * 60)

def run_regression(df_, ctrl_cols, label, out_prefix):
    """OLS + 순서형 로지스틱 실행, Wald 검정 포함."""
    iv_cols = ['F_score','S_score'] + ctrl_cols
    d = df_[iv_cols + ['ra_score']].dropna()
    print(f"\n  [{label}] n={len(d)}")
    X = sm.add_constant(d[iv_cols])

    # OLS
    res_ols = sm.OLS(d['ra_score'], X).fit()
    coef_ols = pd.DataFrame({
        'coef': res_ols.params, 'std': res_ols.bse,
        't': res_ols.tvalues, 'p': res_ols.pvalues,
        'CI_lo': res_ols.conf_int()[0], 'CI_hi': res_ols.conf_int()[1]
    })
    print(f"\n  --- {label} OLS (ra_score ~ F_score + S_score + 통제변수) ---")
    print(coef_ols.round(4).to_string())
    print(f"  R²={res_ols.rsquared:.4f}")

    b_f_ols = res_ols.params['F_score']
    p_f_ols = res_ols.pvalues['F_score']
    b_s_ols = res_ols.params['S_score']
    p_s_ols = res_ols.pvalues['S_score']

    diff, t_w, p_two, p_one = wald_test(res_ols, 'S_score', 'F_score')
    print(f"\n  Wald 검정 (β_S - β_F): diff={diff:+.4f}, t={t_w:.4f}, "
          f"p(양측)={p_two:.4f}, p(단측 β_S>β_F)={p_one:.4f}")
    coef_ols.to_csv(OUT + f'regression_fs_ols_{out_prefix}_v4.csv', encoding='utf-8-sig')

    # 순서형 로지스틱
    sdi_ord = (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
    try:
        mod_ord = OrderedModel(d['ra_score'].astype(int), d[iv_cols], distr='logit')
        res_ord = mod_ord.fit(method='bfgs', maxiter=300, disp=False)
        coef_ord = pd.DataFrame({'coef': res_ord.params, 'p': res_ord.pvalues})
        print(f"\n  --- {label} 순서형 로지스틱 ---")
        print(coef_ord.round(4).to_string())
        b_f_ord = res_ord.params.get('F_score', np.nan)
        p_f_ord = res_ord.pvalues.get('F_score', np.nan)
        b_s_ord = res_ord.params.get('S_score', np.nan)
        p_s_ord = res_ord.pvalues.get('S_score', np.nan)
        sdi_ord = (b_f_ord, p_f_ord, b_s_ord, p_s_ord)
        coef_ord.to_csv(OUT + f'regression_fs_ordinal_{out_prefix}_v4.csv', encoding='utf-8-sig')
    except Exception as e:
        print(f"  순서형 로지스틱 실패: {e}")
        b_f_ord = b_s_ord = p_f_ord = p_s_ord = np.nan

    return b_f_ols, p_f_ols, b_s_ols, p_s_ols, b_f_ord, p_f_ord, b_s_ord, p_s_ord, diff, p_one

# 건설업
ctrl_con = ['elder_rate','foreign_rate','female_rate','log_workers']
bf_c_ols, pf_c_ols, bs_c_ols, ps_c_ols, bf_c_ord, pf_c_ord, bs_c_ord, ps_c_ord, diff_c, p1_c = \
    run_regression(df_con, ctrl_con, '건설', 'con')

# 제조+서비스 합산
df_mfg['ind_mfg'] = 1
df_svc['ind_mfg'] = 0
merge_cols = ['F_score','S_score','SDI','ra_score','env_meas',
              'elder_rate','foreign_rate','female_rate','log_workers','ind_mfg','WT2']
df_ms = pd.concat([df_mfg[merge_cols], df_svc[merge_cols]], ignore_index=True)
ctrl_ms = ['ind_mfg','elder_rate','foreign_rate','female_rate','log_workers']
bf_m_ols, pf_m_ols, bs_m_ols, ps_m_ols, bf_m_ord, pf_m_ord, bs_m_ord, ps_m_ord, diff_m, p1_m = \
    run_regression(df_ms, ctrl_ms, '제조+서비스', 'ms')

# ============================================================
# STEP 5: 민감도 분석 — Q17_13 F→S 재분류
# ============================================================
print("\n" + "=" * 60)
print("[Step 5] 민감도 분석: Q17_13(시설보호구 보유) F→S 재분류")
print("=" * 60)
print("  기본: Q17_13 ∈ F-M8 (형식, 코드북 기준)")
print("  대안: Q17_13 in S-M8 (실질, EFA 적재 기준 - 적재량 0.680)")

f_groups_sens = {k: v for k, v in f_groups_ms.items() if k != 'F-M8'}
s_groups_sens = {**s_groups_ms, 'S-M8': ['Q17_13_n']}

for df_, label in [(df_mfg, '제조'), (df_svc, '서비스')]:
    df_['F_sens'], df_['S_sens'] = compute_fs(df_, f_groups_sens, s_groups_sens, f'{label}(민감도)')
df_ms['F_sens'] = pd.concat([df_mfg['F_sens'], df_svc['F_sens']], ignore_index=True)
df_ms['S_sens'] = pd.concat([df_mfg['S_sens'], df_svc['S_sens']], ignore_index=True)

# 민감도 회귀 (제조+서비스)
iv_sens = ['F_sens','S_sens'] + ctrl_ms
d_sens = df_ms[iv_sens + ['ra_score']].dropna()
X_sens = sm.add_constant(d_sens[iv_sens])
res_sens = sm.OLS(d_sens['ra_score'], X_sens).fit()
b_f_sens = res_sens.params['F_sens']
p_f_sens = res_sens.pvalues['F_sens']
b_s_sens = res_sens.params['S_sens']
p_s_sens = res_sens.pvalues['S_sens']
diff_sens, t_sens, p2_sens, p1_sens = wald_test(res_sens, 'S_sens', 'F_sens')

print(f"\n  --- 민감도 OLS (제조+서비스, n={len(d_sens)}) ---")
sens_show = pd.DataFrame({
    'coef': res_sens.params[['F_sens','S_sens']],
    'p':    res_sens.pvalues[['F_sens','S_sens']]
})
print(sens_show.round(4).to_string())
print(f"  Wald(β_S-β_F): diff={diff_sens:+.4f}, p(단측)={p1_sens:.4f}")

# 민감도 분석 결과 저장
sens_df = pd.DataFrame({
    '분류': ['기본(Q17_13=F)', '민감도(Q17_13=S)'],
    'β_F(OLS)': [bf_m_ols, b_f_sens],
    'p_F': [pf_m_ols, p_f_sens],
    'β_S(OLS)': [bs_m_ols, b_s_sens],
    'p_S': [ps_m_ols, p_s_sens],
    'β_S-β_F': [diff_m, diff_sens],
    'p(단측)': [p1_m, p1_sens],
    'β_S>β_F': [diff_m > 0, diff_sens > 0],
    '결론일치': ['기준', diff_m * diff_sens > 0],
})
print("\n  === 민감도 분석 비교 ===")
print(sens_df.round(4).to_string(index=False))
sens_df.to_csv(OUT + 'sensitivity_v4.csv', encoding='utf-8-sig', index=False)

# ============================================================
# STEP 6: Version 3 SDI 방식과 비교 (참고)
# ============================================================
print("\n" + "=" * 60)
print("[Step 6] Version 3 SDI 방식과 비교 (참고)")
print("=" * 60)

for label, df_, ctrl in [('건설', df_con, ctrl_con), ('제조+서비스', df_ms, ctrl_ms)]:
    d = df_[['SDI'] + ctrl + ['ra_score']].dropna()
    X = sm.add_constant(d[['SDI'] + ctrl])
    res_sdi = sm.OLS(d['ra_score'], X).fit()
    b_sdi = res_sdi.params['SDI']
    p_sdi = res_sdi.pvalues['SDI']
    print(f"  {label} SDI(비교): β={b_sdi:+.4f}, p={p_sdi:.4f} | "
          f"R²={res_sdi.rsquared:.4f}")

# ============================================================
# 최종 요약
# ============================================================
print("\n" + "=" * 60)
print("최종 요약: F_score vs S_score 분리 검증")
print("가설: (1) beta_S>0(p<0.05)  (2) beta_F~0(p>0.1)  (3) beta_S>beta_F(Wald p<0.05)")
print("=" * 60)

def sig(p):
    return '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ('†' if p < 0.1 else 'ns')))

def judge(b_f, p_f, b_s, p_s, diff, p1):
    c1 = b_s > 0 and p_s < 0.05
    c2 = p_f > 0.1
    c3 = diff > 0 and p1 < 0.05
    n = sum([c1, c2, c3])
    label = ['불지지','약한지지','부분지지','강한지지'][n]
    return c1, c2, c3, label

rows = []
for label, b_f, p_f, b_s, p_s, diff, p1 in [
    ('건설   OLS',         bf_c_ols, pf_c_ols, bs_c_ols, ps_c_ols, diff_c, p1_c),
    ('건설   순서형',       bf_c_ord, pf_c_ord, bs_c_ord, ps_c_ord, np.nan, np.nan),
    ('제조+서비스 OLS',    bf_m_ols, pf_m_ols, bs_m_ols, ps_m_ols, diff_m, p1_m),
    ('제조+서비스 순서형', bf_m_ord, pf_m_ord, bs_m_ord, ps_m_ord, np.nan, np.nan),
]:
    if np.isnan(b_f):
        print(f"  {label:20s}: 결과없음")
        continue
    c1, c2, c3, verdict = judge(b_f, p_f, b_s, p_s, diff if not np.isnan(diff) else -1, p1 if not np.isnan(p1) else 1)
    print(f"  {label:20s}: β_F={b_f:+.4f}({sig(p_f)}) β_S={b_s:+.4f}({sig(p_s)}) "
          f"Wald={'p='+f'{p1:.4f}' if not np.isnan(p1) else 'N/A':>10s} → {verdict}")
    rows.append({'모형': label, 'beta_F': b_f, 'p_F': p_f, 'beta_S': b_s, 'p_S': p_s,
                 '(1)beta_S>0': c1, '(2)beta_F비유의': c2, '(3)Wald': c3, '판정': verdict})

print("\n  [민감도 분석 강건성]")
same_dir = (diff_m > 0) == (diff_sens > 0)
print(f"  Q17_13 F->S 재분류 후 beta_S>beta_F 방향 유지: {'OK' if same_dir else 'FAIL'}")

summary_df = pd.DataFrame(rows)
if not summary_df.empty:
    summary_df.to_csv(OUT + 'summary_v4.csv', encoding='utf-8-sig', index=False)

print(f"\n산출물: {OUT}")
print("완료.")
