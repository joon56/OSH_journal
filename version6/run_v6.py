"""SDI v6 분석 스크립트
DV: any_accident (Q27_3_* 이진) — 2021년 업무상 사고 발생 여부
가설: β_SDI < 0 (SDI↑ → 사고↓), β_S < β_F (실질이 형식보다 사고 억제 강함)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings, os
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

BASE   = "../data/raw/"
OUTDIR = "output/"
os.makedirs(OUTDIR, exist_ok=True)

# ──────────────────────────────────────────────────────────
# PHASE 1: 데이터 전처리
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 1: 데이터 전처리")
print("="*60)

df_mfg = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_제조업_230824.csv")
df_svc = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_서비스업_230824.csv")
df_con = pd.read_csv(BASE + "제10차_산업안전보건_실태조사_raw_data_건설업_230824.CSV")
print(f"제조: {df_mfg.shape}, 서비스: {df_svc.shape}, 건설: {df_con.shape}")

def apply_nan(df, cols, codes):
    existing = [c for c in cols if c in df.columns]
    df[existing] = df[existing].replace(codes, np.nan)
    return df

# 무응답 NaN 처리
for df in [df_mfg, df_svc]:
    likert = [c for c in df.columns if c.startswith(('Q15_','Q16_','Q17_','Q18_','Q22_'))]
    df = apply_nan(df, likert, 9)
    df = apply_nan(df, ['Q6','Q9_1','Q9_2','Q10','Q11','Q13_1','Q13_2'], 9)
    df = apply_nan(df, ['Q8_1','Q8_2'], [999, 99999])
    if df is df_mfg: df_mfg = df
    else: df_svc = df

likert_con = [c for c in df_con.columns if c.startswith(('Q14_','Q15_','Q16_','Q17_','Q21_'))]
df_con = apply_nan(df_con, likert_con, 9)
df_con = apply_nan(df_con, ['Q6','Q9','Q10','Q12_1','Q12_2'], 9)
df_con = apply_nan(df_con, ['Q8_1','Q8_2','Q8_3','Q8_4'], [999, 99999])

# Q27 무응답 처리 (999)
q27_cols = [f'Q27_{y}_{s}' for y in [1,2,3,4] for s in [1,2,3]]
for df in [df_mfg, df_svc, df_con]:
    df = apply_nan(df, q27_cols, [999, 99999])

# 이진 재코딩 (F 변수)
def binary_recode(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map({1: 1.0, 2: 0.0})
    return df

df_mfg = binary_recode(df_mfg, ['Q6','Q9_1','Q9_2','Q11','Q13_1','Q13_2'])
df_svc = binary_recode(df_svc, ['Q6','Q9_1','Q9_2','Q11','Q13_1','Q13_2'])
df_con = binary_recode(df_con, ['Q6','Q9','Q12_1','Q12_2'])

for df in [df_mfg, df_svc]:
    if 'Q10' in df.columns:
        df['Q10'] = df['Q10'].map({1: 1.0, 2: 0.0, 3: np.nan})
df_con['Q10'] = df_con['Q10'].map({1: 1.0, 2: 0.5, 3: 0.0, 4: np.nan})

# 이상치 윈저화
for col in ['Q8_1','Q8_2']:
    for df, name in [(df_mfg,'제조'),(df_svc,'서비스'),(df_con,'건설')]:
        if col in df.columns and df[col].notna().sum() > 0:
            p99 = df[col].quantile(0.99)
            n_clip = (df[col] > p99).sum()
            df[col] = df[col].clip(upper=p99)
            if n_clip > 0:
                print(f"  [{name}] {col} 윈저화 {n_clip}건 (p99={p99:.1f})")

# ── 주 DV: any_accident (2021년 업무상 사고) ──
def make_accident_dv(df, year_prefix):
    # year_prefix: 3=2021, 1=2020
    cols = [f'Q27_{year_prefix}_1', f'Q27_{year_prefix}_2', f'Q27_{year_prefix}_3']
    avail = [c for c in cols if c in df.columns]
    total = df[avail].fillna(0).sum(axis=1)
    # 모든 항목이 NaN인 행은 NaN 처리
    all_nan = df[avail].isnull().all(axis=1)
    any_acc = (total > 0).astype(float)
    any_acc[all_nan] = np.nan
    return any_acc

for df, name in [(df_mfg,'제조'),(df_svc,'서비스'),(df_con,'건설')]:
    df['any_accident'] = make_accident_dv(df, year_prefix=3)  # 2021년
    df['any_accident_2020'] = make_accident_dv(df, year_prefix=1)  # 강건성용
    # 사고+질병 복합 (강건성)
    acc_cols = [f'Q27_3_{i}' for i in [1,2,3]] + [f'Q27_4_{i}' for i in [1,2,3]]
    avail = [c for c in acc_cols if c in df.columns]
    total2 = df[avail].fillna(0).sum(axis=1)
    all_nan2 = df[avail].isnull().all(axis=1)
    df['any_acc_dis'] = (total2 > 0).astype(float)
    df['any_acc_dis'][all_nan2] = np.nan
    n_acc = df['any_accident'].sum()
    rate = df['any_accident'].mean() * 100
    print(f"[{name}] 2021 any_accident: {n_acc:.0f}건 / {len(df)}개소 = {rate:.1f}%")

# ra_score (V5 수정 매핑 — 보조 분석용)
ra_map = {1: 0, 2: 1, 3: 2}
df_mfg['ra_score'] = df_mfg['Q15'].map(ra_map)
df_svc['ra_score'] = df_svc['Q15'].map(ra_map)
df_con['ra_score'] = df_con['Q14'].map(ra_map)

# 통제변수
def safe_rate(num, denom):
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(denom > 0, num / denom, np.nan)
    return pd.Series(r, index=num.index if hasattr(num,'index') else range(len(num))).clip(0, 1)

for df, wc in [(df_mfg,'Q1_1'),(df_svc,'Q1_1')]:
    w = df[wc].replace([999,99999], np.nan)
    df['log_workers']  = np.log1p(w.fillna(0))
    df['elder_rate']   = safe_rate(df['Q1_2'], w).values
    df['foreign_rate'] = safe_rate(df['Q1_3'], w).values
    df['female_rate']  = safe_rate(df['Q1_4'], w).values

w_con = df_con['Q4_1'].replace([999,99999], np.nan)
df_con['log_workers']  = np.log1p(w_con.fillna(0))
df_con['elder_rate']   = safe_rate(df_con['Q4_2'], w_con).values
df_con['foreign_rate'] = safe_rate(df_con['Q4_3'], w_con).values
df_con['female_rate']  = safe_rate(df_con['Q4_4'], w_con).values

# 통합
df_mfg['industry'] = '제조'
df_svc['industry'] = '서비스'
df_ms = pd.concat([df_mfg, df_svc], ignore_index=True)
df_ms['ind_mfg'] = (df_ms['industry'] == '제조').astype(float)
print(f"\n통합: 제조+서비스 {len(df_ms):,}행, 건설 {len(df_con):,}행")

# ──────────────────────────────────────────────────────────
# PHASE 2: 측정 타당성 검증
# ──────────────────────────────────────────────────────────
from scipy import stats

print("\n" + "="*60)
print("PHASE 2: 측정 타당성 검증")
print("="*60)

def cronbach_alpha(df, cols):
    data = df[[c for c in cols if c in df.columns]].dropna()
    k = data.shape[1]
    if k < 2 or len(data) < 10: return np.nan
    item_var  = data.var(axis=0, ddof=1).sum()
    total_var = data.sum(axis=1).var(ddof=1)
    return (k / (k-1)) * (1 - item_var / total_var)

s_core_ms = ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10','Q17_12',
             'Q17_15','Q17_16','Q17_17','Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']
alpha_ms = cronbach_alpha(df_ms, s_core_ms)

s_core_con = ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
              'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4']
alpha_con = cronbach_alpha(df_con, s_core_con)
print(f"Cronbach α — 제조+서비스 S: {alpha_ms:.3f} {'OK' if alpha_ms>0.70 else 'LOW'}")
print(f"Cronbach α — 건설 S:        {alpha_con:.3f} {'OK' if alpha_con>0.70 else 'LOW'}")

try:
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
    efa_items = [c for c in s_core_ms if c in df_ms.columns]
    X_efa = df_ms[efa_items].dropna()
    kmo_val = calculate_kmo(X_efa)[1]
    bart_p  = calculate_bartlett_sphericity(X_efa)[1]
    print(f"EFA 사전검정: KMO={kmo_val:.3f}, Bartlett p={bart_p:.2e}")
    fa2 = FactorAnalyzer(n_factors=2, method='principal', rotation='varimax')
    fa2.fit(X_efa)
    ev, _ = fa2.get_eigenvalues()
    print(f"고유값 상위4: {ev[:4].round(3)}")
except Exception as e:
    print(f"EFA 오류: {e}")

def minmax_col(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-10) if mx > mn else s * 0.0

f_tmp = df_ms[['Q6','Q13_1','Q13_2']].apply(minmax_col).mean(axis=1)
s_tmp = df_ms[['Q17_1','Q17_2','Q17_3']].apply(minmax_col).mean(axis=1)
print(f"판별 타당도: F-S 상관 r={f_tmp.corr(s_tmp):.3f}")

# ──────────────────────────────────────────────────────────
# PHASE 3: F/S/SDI 산출
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 3: F_score / S_score / SDI 산출")
print("="*60)

def compute_group_composite(df, group_dict, label=''):
    group_scores = {}
    for gname, cols in group_dict.items():
        avail = [c for c in cols if c in df.columns]
        if not avail:
            print(f"  [경고] [{label}] 그룹 {gname} 없음: {cols}")
            continue
        normed = df[avail].apply(minmax_col)
        group_scores[gname] = normed.mean(axis=1)
    if not group_scores:
        return pd.Series(np.nan, index=df.index)
    score = pd.DataFrame(group_scores).mean(axis=1)
    print(f"  [{label}] {len(group_scores)}그룹 | 평균={score.mean():.4f} | 비결측={score.notna().sum()}")
    return score

# 제조+서비스 그룹
formal_groups_ms = {
    'F-M1': ['Q6'],
    'F-M2': ['Q8_1','Q8_2'],
    'F-M3': ['Q9_1','Q9_2'],
    'F-M4': ['Q10'],
    'F-M5': ['Q11'],
    'F-M6': ['Q13_1'],
    'F-M7': ['Q13_2'],
    'F-M8': ['Q17_13'],  # 경계변수, F 고정
}
subst_groups_ms = {
    # S-M1: 스트레스 관리 노력 (Q16_2_* = 감정노동·장시간노동 등 7개 항목)
    'S-M1': [c for c in df_ms.columns if c.startswith('Q16_2_')],
    'S-M2': ['Q17_1','Q17_2','Q17_3'],
    'S-M3': ['Q17_9','Q17_10'],
    'S-M4': ['Q17_12'],
    'S-M5': ['Q17_15','Q17_16','Q17_17'],
    'S-M6': ['Q18_1','Q18_2','Q18_3','Q18_4'],
    'S-M7': ['Q22_2'],
}
print(f"[제조+서비스] F 그룹수: {len(formal_groups_ms)}, S 그룹수: {len(subst_groups_ms)}")
df_ms['F_score'] = compute_group_composite(df_ms, formal_groups_ms, '제조+서비스 F')
df_ms['S_score'] = compute_group_composite(df_ms, subst_groups_ms,  '제조+서비스 S')
df_ms['SDI']     = df_ms['S_score'] - df_ms['F_score']

# 건설 그룹
formal_groups_con = {
    'F-C1': ['Q6'],
    'F-C2': ['Q8_1','Q8_2'],
    'F-C3': ['Q8_3','Q8_4'],
    'F-C4': ['Q9'],
    'F-C5': ['Q10'],
    'F-C6': ['Q12_1'],
    'F-C7': ['Q12_2'],
}
subst_groups_con = {
    # S-C1: 스트레스 관리 노력 (Q15_2_* = 건설업 스트레스 관리 7개 항목)
    'S-C1': [c for c in df_con.columns if c.startswith('Q15_2_')],
    'S-C2': ['Q16_1','Q16_2','Q16_3'],
    'S-C3': ['Q16_9','Q16_10'],
    'S-C4': ['Q16_16','Q16_17','Q16_18'],
    'S-C5': ['Q17_1','Q17_2','Q17_4'],
    'S-C6': ['Q21_2'],
}
print(f"[건설] F 그룹수: {len(formal_groups_con)}, S 그룹수: {len(subst_groups_con)}")
df_con['F_score'] = compute_group_composite(df_con, formal_groups_con, '건설 F')
df_con['S_score'] = compute_group_composite(df_con, subst_groups_con,  '건설 S')
df_con['SDI']     = df_con['S_score'] - df_con['F_score']

# 기술통계
rows = []
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    for col in ['F_score','S_score','SDI']:
        s = df[col].dropna()
        w = df.loc[s.index, 'WT2']
        rows.append({'업종': name, '변수': col, 'n': len(s),
                     '평균(비가중)': round(s.mean(),4), '표준편차': round(s.std(),4),
                     'Q1': round(s.quantile(0.25),4), '중앙값': round(s.median(),4),
                     'Q3': round(s.quantile(0.75),4),
                     '평균(가중)': round(np.average(s, weights=w),4)})

desc_df = pd.DataFrame(rows)
print(desc_df.to_string(index=False))
desc_df.to_csv(OUTDIR+'descriptive_v6.csv', index=False, encoding='utf-8-sig')

# ──────────────────────────────────────────────────────────
# PHASE 4: 사고 발생 기술통계
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 4: 사고 발생 기술통계")
print("="*60)

# SDI 분위수별 사고율
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    d = df[['SDI','any_accident']].dropna()
    d['SDI_q'] = pd.qcut(d['SDI'], q=4, labels=['Q1(낮음)','Q2','Q3','Q4(높음)'])
    tbl = d.groupby('SDI_q')['any_accident'].agg(['mean','count'])
    tbl['사고율(%)'] = (tbl['mean']*100).round(1)
    print(f"\n[{name}] SDI 분위수별 사고율:")
    print(tbl[['count','사고율(%)']].to_string())
    total_rate = d['any_accident'].mean()*100
    print(f"  전체 사고율: {total_rate:.1f}%")

# 산점도
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, (name, df) in zip(axes, [('제조+서비스', df_ms), ('건설', df_con)]):
    d = df[['SDI','any_accident']].dropna()
    # SDI 구간별 사고율 라인
    bins = pd.cut(d['SDI'], bins=10)
    rate_by_bin = d.groupby(bins)['any_accident'].mean()
    mid = rate_by_bin.index.map(lambda x: x.mid)
    ax.plot(mid, rate_by_bin.values * 100, 'o-', color='#1976D2', lw=2)
    ax.set_xlabel('SDI (S_score - F_score)')
    ax.set_ylabel('사고 발생률 (%)')
    ax.set_title(f'{name}\n(n={len(d):,}, 전체 사고율={d["any_accident"].mean()*100:.1f}%)')
    ax.grid(alpha=0.3)
plt.suptitle('SDI vs 사고 발생률', fontsize=13)
plt.tight_layout()
plt.savefig(OUTDIR+'sdi_accident_v6.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[저장] sdi_accident_v6.png")

# ──────────────────────────────────────────────────────────
# PHASE 5: 주 추론 모형
# ──────────────────────────────────────────────────────────
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel

print("\n" + "="*60)
print("PHASE 5: 주 추론 모형")
print("="*60)

controls_ms  = 'ind_mfg + log_workers + elder_rate + foreign_rate + female_rate'
controls_con = 'log_workers + elder_rate + foreign_rate + female_rate'

def wald_bs_lt_bf(res, sname='S_score', fname='F_score'):
    """Wald 검정: β_S < β_F (단측, 음의 방향) — 사고 DV에서 S가 더 강하게 억제"""
    if sname not in res.params or fname not in res.params:
        return dict(bs=np.nan, bf=np.nan, diff=np.nan, t=np.nan, p2=np.nan, p1=np.nan, direction=False)
    b_s  = res.params[sname]; b_f  = res.params[fname]
    se_s = res.bse[sname];    se_f = res.bse[fname]
    cov  = res.cov_params().loc[sname, fname]
    se_d = np.sqrt(se_s**2 + se_f**2 - 2*cov)
    t_d  = (b_s - b_f) / se_d
    p2   = 2*(1 - stats.norm.cdf(abs(t_d)))
    p1   = stats.norm.cdf(t_d)   # 단측: β_S < β_F 방향 (t < 0이면 지지)
    return dict(bs=round(b_s,4), bf=round(b_f,4), diff=round(b_s-b_f,4),
                t=round(t_d,4), p2=round(p2,4), p1=round(p1,4), direction=(b_s < b_f))

# 5-1. 모형 A — 로지스틱 (주)
print("\n[5-1] 모형 A: 로지스틱 (any_accident ~ SDI + controls)")
res_LA_ms  = smf.logit(f'any_accident ~ SDI + {controls_ms}',  data=df_ms).fit(disp=False)
res_LA_con = smf.logit(f'any_accident ~ SDI + {controls_con}', data=df_con).fit(disp=False)

for res, lab in [(res_LA_ms,'제조+서비스'),(res_LA_con,'건설')]:
    b = res.params.get('SDI', np.nan)
    p = res.pvalues.get('SDI', np.nan)
    star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
    # 오즈비
    or_val = np.exp(b)
    n = int(res.nobs)
    print(f"  [{lab}] n={n} | β_SDI={b:+.4f}({star}) OR={or_val:.3f} p={p:.4f}")

# 5-2. 모형 A — OLS (LPM, 방향 확인용)
print("\n[5-2] 모형 A 보조: OLS LPM")
res_OA_ms  = smf.ols(f'any_accident ~ SDI + {controls_ms}',  data=df_ms).fit()
res_OA_con = smf.ols(f'any_accident ~ SDI + {controls_con}', data=df_con).fit()

for res, lab in [(res_OA_ms,'제조+서비스'),(res_OA_con,'건설')]:
    b = res.params.get('SDI', np.nan)
    p = res.pvalues.get('SDI', np.nan)
    star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
    print(f"  [{lab}] β_SDI={b:+.4f}({star}) p={p:.4f} R²={res.rsquared:.4f}")

# 5-3. 모형 B — 로지스틱
print("\n[5-3] 모형 B: 로지스틱 (any_accident ~ F_score + S_score + controls)")
res_LB_ms  = smf.logit(f'any_accident ~ F_score + S_score + {controls_ms}',  data=df_ms).fit(disp=False)
res_LB_con = smf.logit(f'any_accident ~ F_score + S_score + {controls_con}', data=df_con).fit(disp=False)
wald_ms  = wald_bs_lt_bf(res_LB_ms)
wald_con = wald_bs_lt_bf(res_LB_con)

print(f"\n  [제조+서비스] n={int(res_LB_ms.nobs)}")
print(f"    β_F={wald_ms['bf']:+.4f}, β_S={wald_ms['bs']:+.4f}")
print(f"    diff(β_S-β_F)={wald_ms['diff']:+.4f}, t={wald_ms['t']:.4f}, p(단측 β_S<β_F)={wald_ms['p1']:.4f}")
print(f"    β_S < β_F: {wald_ms['direction']}")

print(f"\n  [건설] n={int(res_LB_con.nobs)}")
print(f"    β_F={wald_con['bf']:+.4f}, β_S={wald_con['bs']:+.4f}")
print(f"    diff(β_S-β_F)={wald_con['diff']:+.4f}, t={wald_con['t']:.4f}, p(단측 β_S<β_F)={wald_con['p1']:.4f}")
print(f"    β_S < β_F: {wald_con['direction']}")

# 5-4. 가설 판정
print("\n" + "="*60)
print("가설 판정 종합")
print("="*60)

judg_rows = []
for lab, res_A_log, res_A_ols, w in [
    ('제조+서비스', res_LA_ms, res_OA_ms, wald_ms),
    ('건설',       res_LA_con, res_OA_con, wald_con)
]:
    b_sdi_log = res_A_log.params.get('SDI', np.nan)
    p_sdi_log = res_A_log.pvalues.get('SDI', np.nan)
    b_sdi_ols = res_A_ols.params.get('SDI', np.nan)
    p_sdi_ols = res_A_ols.pvalues.get('SDI', np.nan)

    h1 = (b_sdi_log < 0) and (p_sdi_log < 0.05)
    h2 = w['direction'] and (w['p1'] < 0.05)
    dir_match = (b_sdi_log < 0) == (b_sdi_ols < 0)  # 로지스틱·OLS 방향 일치

    verdict = ('수준1+2 지지(최강)' if h1 and h2
               else '수준2만 지지' if h2
               else '수준1만 지지' if h1
               else '불지지')

    print(f"\n[{lab}]")
    print(f"  수준1 (β_SDI<0, p<0.05): 로지β={b_sdi_log:+.4f} p={p_sdi_log:.4f} | OLS β={b_sdi_ols:+.4f} → {'OK' if h1 else 'FAIL'}")
    print(f"  방향 일치(로지↔OLS): {'OK' if dir_match else 'MISMATCH'}")
    print(f"  수준2 (β_S<β_F, p<0.05): diff={w['diff']:+.4f} p(단)={w['p1']:.4f} → {'OK' if h2 else 'FAIL'}")
    print(f"  → 종합: {verdict}")

    judg_rows.append({'업종': lab,
                      'β_SDI(logit)': b_sdi_log, 'p_SDI(logit)': p_sdi_log,
                      'β_SDI(OLS)': b_sdi_ols, 'p_SDI(OLS)': p_sdi_ols,
                      'bs': w['bs'], 'bf': w['bf'], 'diff': w['diff'],
                      't': w['t'], 'p1': w['p1'], 'direction': w['direction'],
                      '판정': verdict})

pd.DataFrame(judg_rows).to_csv(OUTDIR+'hypothesis_judgment_v6.csv', index=False, encoding='utf-8-sig')

# 5-5. 업종 조절효과
print("\n[5-5] 업종 조절효과")
df_all = pd.concat([df_ms.assign(is_con=0), df_con.assign(is_con=1, ind_mfg=np.nan)], ignore_index=True)
res_inter = smf.logit('any_accident ~ SDI * is_con + log_workers + elder_rate + foreign_rate + female_rate',
                      data=df_all).fit(disp=False)
b_i = res_inter.params.get('SDI:is_con', np.nan)
p_i = res_inter.pvalues.get('SDI:is_con', np.nan)
print(f"  SDI × 건설더미: β={b_i:+.4f} p={p_i:.4f} → {'이질성 확인' if p_i<0.05 else '이질성 불확인'}")

# ──────────────────────────────────────────────────────────
# PHASE 6: 강건성 검증
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 6: 강건성 검증")
print("="*60)

rob_rows = []

# 기본 결과 저장
for lab, res_A, w in [('제조+서비스', res_LA_ms, wald_ms), ('건설', res_LA_con, wald_con)]:
    rob_rows.append({'검증': '기본(로지스틱)', '업종': lab,
                     'n': int(res_A.nobs),
                     'β_SDI': round(res_A.params.get('SDI',np.nan),4),
                     'p': round(res_A.pvalues.get('SDI',np.nan),4),
                     'β_S-β_F': w['diff'], 'p(단측)': w['p1']})

# 강건성 1: Q17_13 → S
print("\n[R1] Q17_13 → S 민감도")
formal_sens = {k: v for k,v in formal_groups_ms.items() if k != 'F-M8'}
subst_sens  = {**subst_groups_ms, 'S-M8': ['Q17_13']}
df_ms['F_score_s'] = compute_group_composite(df_ms, formal_sens, '민감도F')
df_ms['S_score_s'] = compute_group_composite(df_ms, subst_sens,  '민감도S')
df_ms['SDI_s'] = df_ms['S_score_s'] - df_ms['F_score_s']

res_sA = smf.logit(f'any_accident ~ SDI_s + {controls_ms}', data=df_ms).fit(disp=False)
res_sB = smf.logit(f'any_accident ~ F_score_s + S_score_s + {controls_ms}', data=df_ms).fit(disp=False)
w_s = wald_bs_lt_bf(res_sB, 'S_score_s', 'F_score_s')
b_sA = res_sA.params.get('SDI_s', np.nan)
p_sA = res_sA.pvalues.get('SDI_s', np.nan)
print(f"  모형A: β_SDI={b_sA:+.4f} p={p_sA:.4f} | 모형B diff={w_s['diff']:+.4f} p={w_s['p1']:.4f}")
rob_rows.append({'검증': 'Q17_13→S', '업종': '제조+서비스',
                 'n': int(res_sA.nobs),
                 'β_SDI': round(b_sA,4), 'p': round(p_sA,4),
                 'β_S-β_F': w_s['diff'], 'p(단측)': w_s['p1']})

# 강건성 2: 50인 이상
print("\n[R2] 50인 이상 표본 제한")
for wc, df, lab, ctrl in [('Q1_1',df_ms,'제조+서비스',controls_ms),
                           ('Q4_1',df_con,'건설',controls_con)]:
    df50 = df[df[wc] >= 50].copy() if wc in df.columns else df.copy()
    res50 = smf.logit(f'any_accident ~ SDI + {ctrl}', data=df50).fit(disp=False)
    b50 = res50.params.get('SDI', np.nan); p50 = res50.pvalues.get('SDI', np.nan)
    print(f"  [{lab}] n={int(res50.nobs)} β_SDI={b50:+.4f} p={p50:.4f}")
    rob_rows.append({'검증': '50인↑', '업종': lab,
                     'n': int(res50.nobs), 'β_SDI': round(b50,4), 'p': round(p50,4),
                     'β_S-β_F': np.nan, 'p(단측)': np.nan})

# 강건성 3: 2020년 사고 데이터
print("\n[R3] 2020년 사고 데이터")
for df, lab, ctrl in [(df_ms,'제조+서비스',controls_ms),(df_con,'건설',controls_con)]:
    res20 = smf.logit(f'any_accident_2020 ~ SDI + {ctrl}', data=df).fit(disp=False)
    b20 = res20.params.get('SDI', np.nan); p20 = res20.pvalues.get('SDI', np.nan)
    rate20 = df['any_accident_2020'].mean()*100
    print(f"  [{lab}] 사고율={rate20:.1f}% | β_SDI={b20:+.4f} p={p20:.4f}")
    rob_rows.append({'검증': '2020년DV', '업종': lab,
                     'n': int(res20.nobs), 'β_SDI': round(b20,4), 'p': round(p20,4),
                     'β_S-β_F': np.nan, 'p(단측)': np.nan})

# 강건성 4: 사고+질병 복합
print("\n[R4] 사고+질병 복합 DV")
for df, lab, ctrl in [(df_ms,'제조+서비스',controls_ms),(df_con,'건설',controls_con)]:
    resAD = smf.logit(f'any_acc_dis ~ SDI + {ctrl}', data=df).fit(disp=False)
    bAD = resAD.params.get('SDI', np.nan); pAD = resAD.pvalues.get('SDI', np.nan)
    rate_ad = df['any_acc_dis'].mean()*100
    print(f"  [{lab}] 사고+질병 발생률={rate_ad:.1f}% | β_SDI={bAD:+.4f} p={pAD:.4f}")
    rob_rows.append({'검증': '사고+질병DV', '업종': lab,
                     'n': int(resAD.nobs), 'β_SDI': round(bAD,4), 'p': round(pAD,4),
                     'β_S-β_F': np.nan, 'p(단측)': np.nan})

rob_df = pd.DataFrame(rob_rows)
print("\n[강건성 요약]")
print(rob_df.to_string(index=False))
rob_df.to_csv(OUTDIR+'robustness_v6.csv', index=False, encoding='utf-8-sig')

# ──────────────────────────────────────────────────────────
# PHASE 7: 보조 분석 — RA 빈도 (V5 수정 결과 재확인)
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 7: 보조 분석 — RA 빈도 (V5 수정 재확인)")
print("="*60)
print("(형식 준수가 RA 빈도를 이끈다는 보조 발견)")

res_ra_ms  = smf.ols(f'ra_score ~ SDI + {controls_ms}',  data=df_ms).fit()
res_ra_con = smf.ols(f'ra_score ~ SDI + {controls_con}', data=df_con).fit()

for res, lab in [(res_ra_ms,'제조+서비스'),(res_ra_con,'건설')]:
    b = res.params.get('SDI',np.nan); p = res.pvalues.get('SDI',np.nan)
    star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
    print(f"  [{lab}] ra_score ~ SDI: β={b:+.4f}({star}) p={p:.4f}")

res_ra_B_ms = smf.ols(f'ra_score ~ F_score + S_score + {controls_ms}', data=df_ms).fit()
w_ra = wald_bs_lt_bf(res_ra_B_ms)  # 여기서는 β_S > β_F (RA빈도는 F가 더 강)
print(f"\n  [제조+서비스 모형B] β_F={w_ra['bf']:+.4f}, β_S={w_ra['bs']:+.4f}, diff={w_ra['diff']:+.4f} p={w_ra['p2']:.4f}")
print(f"  → β_F > β_S (형식 준수 → RA 빈도 강하게 예측): {'확인' if w_ra['bf'] > w_ra['bs'] else '미확인'}")

# ──────────────────────────────────────────────────────────
# PHASE 8: 건설업 이질성 분석
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 8: 건설업 이질성 분석")
print("="*60)

print(f"C1 SDI 분산 | 제조+서비스 σ={df_ms['SDI'].std():.4f}, 건설 σ={df_con['SDI'].std():.4f}")

print("\nC2 any_accident 분포:")
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    rate = df['any_accident'].mean()*100
    print(f"  [{name}] 사고 발생률: {rate:.1f}% (n={df['any_accident'].notna().sum()})")

# SDI 분위수별 사고율 상세
print("\n건설업 SDI 분위수별 사고율 (건설업 이질성 탐색):")
d = df_con[['SDI','any_accident']].dropna()
d['SDI_q'] = pd.qcut(d['SDI'], q=4, labels=['Q1(낮음)','Q2','Q3','Q4(높음)'])
tbl = d.groupby('SDI_q')['any_accident'].agg(['mean','count'])
tbl['사고율(%)'] = (tbl['mean']*100).round(1)
print(tbl[['count','사고율(%)']].to_string())

print("\n" + "="*60)
print("모든 Phase 완료")
print(f"산출물: {OUTDIR}")
print("="*60)
