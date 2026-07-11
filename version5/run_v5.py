"""SDI v5 분석 스크립트 — DESIGN.md 기반 from-scratch 분석"""
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

# 변수 존재 확인
print("\n[제조업 Q16_2계열]:", sorted(df_mfg.filter(like='Q16_2').columns.tolist()))
print("[제조업 Q17계열]:",   sorted(df_mfg.filter(like='Q17_').columns.tolist()))
print("[건설업 Q15_2계열]:", sorted(df_con.filter(like='Q15_2').columns.tolist()))
print("[건설업 Q16계열]:",   sorted(df_con.filter(like='Q16_').columns.tolist()))

# 무응답 NaN
def apply_nan(df, cols, codes):
    existing = [c for c in cols if c in df.columns]
    df[existing] = df[existing].replace(codes, np.nan)
    return df

for df in [df_mfg, df_svc]:
    likert = [c for c in df.columns if c.startswith(('Q15_','Q16_','Q17_','Q18_','Q22_'))]
    df = apply_nan(df, likert, 9)
    df = apply_nan(df, ['Q6','Q9_1','Q9_2','Q10','Q11','Q13_1','Q13_2'], 9)
    df = apply_nan(df, ['Q8_1','Q8_2'], [999,99999])
    if df is df_mfg: df_mfg = df
    else: df_svc = df

likert_con = [c for c in df_con.columns if c.startswith(('Q14_','Q15_','Q16_','Q17_','Q21_'))]
df_con = apply_nan(df_con, likert_con, 9)
df_con = apply_nan(df_con, ['Q6','Q9','Q10','Q12_1','Q12_2'], 9)
df_con = apply_nan(df_con, ['Q8_1','Q8_2','Q8_3','Q8_4'], [999,99999])

# 이진 재코딩
def binary_recode(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map({1: 1.0, 2: 0.0})
    return df

df_mfg = binary_recode(df_mfg, ['Q6','Q9_1','Q9_2','Q11','Q13_1','Q13_2'])
df_svc = binary_recode(df_svc, ['Q6','Q9_1','Q9_2','Q11','Q13_1','Q13_2'])
df_con = binary_recode(df_con, ['Q6','Q9','Q12_1','Q12_2'])

# Q10 범주 재코딩
for df in [df_mfg, df_svc]:
    if 'Q10' in df.columns:
        df['Q10'] = df['Q10'].map({1: 1.0, 2: 0.0, 3: np.nan})

# 건설 Q10 빈도 확인
print("\n건설 Q10 분포:", df_con['Q10'].value_counts(dropna=False).to_dict())
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

# ra_score — 코드북 기준: 1=실시한 적 없음, 2=비정기 실시, 3=정기 실시
ra_map = {1: 0, 2: 1, 3: 2}
df_mfg['ra_score'] = df_mfg['Q15'].map(ra_map)
df_svc['ra_score'] = df_svc['Q15'].map(ra_map)
df_con['ra_score'] = df_con['Q14'].map(ra_map)

# 통제변수 (inf → NaN 처리 포함)
def safe_rate(num, denom):
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(denom > 0, num / denom, np.nan)
    return pd.Series(r).clip(0, 1)

for df, wc in [(df_mfg,'Q1_1'),(df_svc,'Q1_1')]:
    w = df[wc].replace([999,99999], np.nan)
    df['log_workers']  = np.log1p(w.fillna(0))
    df['elder_rate']   = safe_rate(df['Q1_2'].values, w.values).values
    df['foreign_rate'] = safe_rate(df['Q1_3'].values, w.values).values
    df['female_rate']  = safe_rate(df['Q1_4'].values, w.values).values

w_con = df_con['Q4_1'].replace([999,99999], np.nan)
df_con['log_workers']  = np.log1p(w_con.fillna(0))
df_con['elder_rate']   = safe_rate(df_con['Q4_2'].values, w_con.values).values
df_con['foreign_rate'] = safe_rate(df_con['Q4_3'].values, w_con.values).values
df_con['female_rate']  = safe_rate(df_con['Q4_4'].values, w_con.values).values

# 통합
df_mfg['industry'] = '제조'
df_svc['industry'] = '서비스'
df_ms = pd.concat([df_mfg, df_svc], ignore_index=True)
df_ms['ind_mfg'] = (df_ms['industry'] == '제조').astype(float)
print(f"\n통합: 제조+서비스 {len(df_ms):,}행, 건설 {len(df_con):,}행")

# 결측률 확인
key_f = ['Q6','Q8_1','Q8_2','Q9_1','Q9_2','Q10','Q11','Q13_1','Q13_2','Q17_13']
key_s = ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10','Q17_12','Q17_15','Q17_16','Q17_17','Q18_1','Q22_2']
for label, df, keys in [('제조+서비스 F', df_ms, key_f), ('제조+서비스 S', df_ms, key_s)]:
    avail = [c for c in keys if c in df.columns]
    miss  = df[avail].isnull().mean() * 100
    bad   = miss[miss >= 10]
    if bad.empty:
        print(f"[{label}] ✅ 모든 변수 결측률 10% 미만")
    else:
        print(f"[{label}] ⚠️ 10%↑: {bad.to_dict()}")

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
    if k < 2 or len(data) < 10:
        return np.nan
    item_var   = data.var(axis=0, ddof=1).sum()
    total_var  = data.sum(axis=1).var(ddof=1)
    return (k / (k-1)) * (1 - item_var / total_var)

s_core_ms = ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10','Q17_12',
             'Q17_15','Q17_16','Q17_17','Q18_1','Q18_2','Q18_3','Q18_4','Q22_2']
alpha_ms = cronbach_alpha(df_ms, s_core_ms)

s_core_con = ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
              'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4']
alpha_con = cronbach_alpha(df_con, s_core_con)

print(f"Cronbach α — 제조+서비스 S: {alpha_ms:.3f} {'✅' if alpha_ms>0.70 else '⚠️'}")
print(f"Cronbach α — 건설 S:        {alpha_con:.3f} {'✅' if alpha_con>0.70 else '⚠️'}")

# EFA
try:
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

    efa_items = [c for c in s_core_ms if c in df_ms.columns]
    X_efa = df_ms[efa_items].dropna()
    kmo_val = calculate_kmo(X_efa)[1]
    bart_p  = calculate_bartlett_sphericity(X_efa)[1]
    print(f"\nEFA 사전검정: KMO={kmo_val:.3f} {'✅' if kmo_val>0.6 else '⚠️'}, Bartlett p={bart_p:.2e} {'✅' if bart_p<0.05 else '⚠️'}")

    fa2 = FactorAnalyzer(n_factors=2, method='principal', rotation='varimax')
    fa2.fit(X_efa)
    ev, _ = fa2.get_eigenvalues()
    print(f"고유값 상위4: {ev[:4].round(3)}")
    load_df = pd.DataFrame(fa2.loadings_, index=efa_items, columns=['F1','F2']).round(3)
    print(load_df.to_string())
    if 'Q17_13' in load_df.index:
        row = load_df.loc['Q17_13']
        print(f"\n★ Q17_13 적재: F1={row['F1']}, F2={row['F2']} → {'F1' if abs(row['F1'])>abs(row['F2']) else 'F2'}")
        print("  (사전결정: Formal 유지 — 이론적 정의 우선)")
except Exception as e:
    print(f"EFA 오류: {e}")

# 판별 타당도
def minmax_col(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-10) if mx > mn else s * 0.0

f_tmp = df_ms[['Q6','Q13_1','Q13_2']].apply(minmax_col).mean(axis=1)
s_tmp = df_ms[['Q17_1','Q17_2','Q17_3']].apply(minmax_col).mean(axis=1)
r_fs = f_tmp.corr(s_tmp)
print(f"\n판별 타당도: F-S 상관 r={r_fs:.3f} {'✅ r<0.85' if abs(r_fs)<0.85 else '⚠️ 재검토'}")

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
            print(f"  ⚠️  [{label}] 그룹 {gname}: 없음 {cols}")
            continue
        normed = df[avail].apply(minmax_col)
        group_scores[gname] = normed.mean(axis=1)
    if not group_scores:
        return pd.Series(np.nan, index=df.index)
    score = pd.DataFrame(group_scores).mean(axis=1)
    print(f"  [{label}] {len(group_scores)}그룹 | 평균={score.mean():.3f} | 비결측={score.notna().sum()}")
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
    'F-M8': ['Q17_13'],
}
subst_groups_ms = {
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
        rows.append({
            '업종': name, '변수': col, 'n': len(s),
            '평균(비가중)': round(s.mean(),4), '표준편차': round(s.std(),4),
            'Q1': round(s.quantile(0.25),4), '중앙값': round(s.median(),4),
            'Q3': round(s.quantile(0.75),4),
            '평균(가중)': round(np.average(s, weights=w),4),
        })
    neg_pct = (df['SDI'] < 0).mean()*100
    print(f"[{name}] SDI<0(형식주의): {neg_pct:.1f}%")

desc_df = pd.DataFrame(rows)
print(desc_df.to_string(index=False))
desc_df.to_csv(OUTDIR+'descriptive_v5.csv', index=False, encoding='utf-8-sig')

# F vs S 산포도
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (name, df, colors) in zip(axes, [
    ('제조+서비스', df_ms, {'제조':'#1976D2','서비스':'#FF8F00'}),
    ('건설',       df_con, {'건설':'#2E7D32'}),
]):
    for ind, color in colors.items():
        mask = df.get('industry', pd.Series(['건설']*len(df))) == ind if '건설' not in colors else pd.Series([True]*len(df))
        ax.scatter(df['F_score'], df['S_score'],
                   alpha=0.2, s=8, color=color, label=ind, rasterized=True)
        break  # 건설은 단일색
    ax.plot([0,1],[0,1],'k--',lw=1.5,label='F=S (SDI=0)')
    ax.set_xlabel('F_score (형식)'); ax.set_ylabel('S_score (실질)')
    ax.set_title(f'{name}\n(n={len(df):,})'); ax.legend(fontsize=8)
    ax.set_xlim(0,1); ax.set_ylim(0,1)

# 제조+서비스 좌측 산포도 재그리기
ax = axes[0]; ax.cla()
for ind, color in {'제조':'#1976D2','서비스':'#FF8F00'}.items():
    mask = df_ms['industry'] == ind
    ax.scatter(df_ms.loc[mask,'F_score'], df_ms.loc[mask,'S_score'],
               alpha=0.2, s=8, color=color, label=ind, rasterized=True)
ax.plot([0,1],[0,1],'k--',lw=1.5,label='F=S')
ax.set_xlabel('F_score (형식)'); ax.set_ylabel('S_score (실질)')
ax.set_title(f'제조+서비스 (n={len(df_ms):,})'); ax.legend(fontsize=8)
ax.set_xlim(0,1); ax.set_ylim(0,1)

plt.suptitle('F_score vs S_score — 대각선 아래: 형식주의(SDI<0)', fontsize=13)
plt.tight_layout()
plt.savefig(OUTDIR+'fs_scatter_v5.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[저장] fs_scatter_v5.png")

# ──────────────────────────────────────────────────────────
# PHASE 4: 주 추론 모형
# ──────────────────────────────────────────────────────────
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel

print("\n" + "="*60)
print("PHASE 4: 주 추론 모형")
print("="*60)

controls_ms  = 'ind_mfg + log_workers + elder_rate + foreign_rate + female_rate'
controls_con = 'log_workers + elder_rate + foreign_rate + female_rate'

def wald_bs_gt_bf(res):
    b_s  = res.params.get('S_score', np.nan)
    b_f  = res.params.get('F_score', np.nan)
    se_s = res.bse.get('S_score', np.nan)
    se_f = res.bse.get('F_score', np.nan)
    if 'S_score' not in res.params or 'F_score' not in res.params:
        return dict(bs=np.nan, bf=np.nan, diff=np.nan, t=np.nan, p2=np.nan, p1=np.nan, direction=False)
    cov  = res.cov_params().loc['S_score','F_score']
    se_d = np.sqrt(se_s**2 + se_f**2 - 2*cov)
    t_d  = (b_s - b_f) / se_d
    p2   = 2*(1-stats.norm.cdf(abs(t_d)))
    return dict(bs=b_s, bf=b_f, diff=b_s-b_f, t=t_d, p2=p2, p1=p2/2, direction=b_s>b_f)

def prep_ordered(df, dep, indeps):
    """순서형 로지스틱을 위한 데이터 준비 (inf→NaN 처리)."""
    cols = [dep] + indeps
    avail = [c for c in cols if c in df.columns]
    d = df[avail].copy().replace([np.inf, -np.inf], np.nan).dropna()
    if dep in d.columns:
        d[dep] = d[dep].astype(int)
    return d

# 4-1. 모형 A — OLS
res_A_ms  = smf.ols(f'ra_score ~ SDI + {controls_ms}',  data=df_ms).fit()
res_A_con = smf.ols(f'ra_score ~ SDI + {controls_con}', data=df_con).fit()

for res, lab in [(res_A_ms,'제조+서비스 OLS A'),(res_A_con,'건설 OLS A')]:
    b = res.params.get('SDI',np.nan); p = res.pvalues.get('SDI',np.nan)
    star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
    print(f"[{lab}] n={int(res.nobs)} R²={res.rsquared:.4f} | β_SDI={b:+.4f} p={p:.4f}({star})")

# 4-2. 모형 A — 순서형 로지스틱
ctrl_ms_list  = controls_ms.replace(' ','').split('+')
ctrl_con_list = controls_con.replace(' ','').split('+')

for df, ctrl_list, lab in [
    (df_ms,  ctrl_ms_list,  '제조+서비스 순서형 A'),
    (df_con, ctrl_con_list, '건설 순서형 A'),
]:
    try:
        d = prep_ordered(df, 'ra_score', ctrl_list + ['SDI'])
        print(f"  [{lab}] 유효행: {len(d)}")
        if len(d) < 50:
            print(f"  ⚠️ 유효행 부족 — 순서형 생략"); continue
        X = d[ctrl_list + ['SDI']]
        res_ord = OrderedModel(d['ra_score'], X, distr='logit').fit(method='bfgs', disp=False)
        b = res_ord.params.get('SDI',np.nan); p = res_ord.pvalues.get('SDI',np.nan)
        star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
        print(f"  [{lab}] β_SDI={b:+.4f} p={p:.4f}({star})")
    except Exception as e:
        print(f"  [{lab}] 오류: {e}")

# 4-3. 모형 B — OLS
res_B_ms  = smf.ols(f'ra_score ~ F_score + S_score + {controls_ms}',  data=df_ms).fit()
res_B_con = smf.ols(f'ra_score ~ F_score + S_score + {controls_con}', data=df_con).fit()
wald_ms  = wald_bs_gt_bf(res_B_ms)
wald_con = wald_bs_gt_bf(res_B_con)

print(f"\n[모형 B OLS]")
for res, lab, w in [(res_B_ms,'제조+서비스',wald_ms),(res_B_con,'건설',wald_con)]:
    print(f"  [{lab}] n={int(res.nobs)} R²={res.rsquared:.4f}")
    print(f"    β_F={w['bf']:+.4f}, β_S={w['bs']:+.4f}, diff={w['diff']:+.4f}, t={w['t']:.4f}, p(단측)={w['p1']:.4f} → β_S>β_F: {w['direction']}")

# 4-4. 모형 B — 순서형 로지스틱
print("\n[모형 B 순서형 로지스틱]")
for df, ctrl_list, lab in [
    (df_ms,  ctrl_ms_list,  '제조+서비스'),
    (df_con, ctrl_con_list, '건설'),
]:
    try:
        d = prep_ordered(df, 'ra_score', ctrl_list + ['F_score','S_score'])
        print(f"  [{lab}] 유효행: {len(d)}")
        if len(d) < 50:
            print(f"  ⚠️ 유효행 부족 — 생략"); continue
        X = d[ctrl_list + ['F_score','S_score']]
        res_ord = OrderedModel(d['ra_score'], X, distr='logit').fit(method='bfgs', disp=False)
        bs = res_ord.params.get('S_score',np.nan)
        bf = res_ord.params.get('F_score',np.nan)
        print(f"  [{lab}] β_S={bs:+.4f}, β_F={bf:+.4f} → β_S>β_F: {bs>bf}")
    except Exception as e:
        print(f"  [{lab}] 오류: {e}")

# 4-5. 가설 판정 종합
print("\n" + "="*60)
print("가설 판정 종합")
print("="*60)
judg_rows = []
for lab, res_A, w in [('제조+서비스', res_A_ms, wald_ms), ('건설', res_A_con, wald_con)]:
    b_sdi = res_A.params.get('SDI',np.nan)
    p_sdi = res_A.pvalues.get('SDI',np.nan)
    h1 = (b_sdi > 0) and (p_sdi < 0.05)
    h2 = w['direction'] and (w['p1'] < 0.05)
    verdict = ('수준1+2 지지(최강)' if h1 and h2
               else '수준2만 지지' if h2
               else '수준1만 지지' if h1
               else '불지지')
    print(f"\n[{lab}]")
    print(f"  수준1 (β_SDI>0, p<0.05): β={b_sdi:+.4f} p={p_sdi:.4f} → {'✅' if h1 else '✗'}")
    print(f"  수준2 (β_S>β_F, p<0.05): diff={w['diff']:+.4f} p(단)={w['p1']:.4f} → {'✅' if h2 else '✗'}")
    print(f"  → 종합: {verdict}")
    judg_rows.append({'업종': lab, 'β_SDI': b_sdi, 'p_SDI': p_sdi,
                      **{k: round(v,4) if isinstance(v,float) else v for k,v in w.items()},
                      '판정': verdict})

pd.DataFrame(judg_rows).to_csv(OUTDIR+'hypothesis_judgment_v5.csv', index=False, encoding='utf-8-sig')

# 4-6. 업종 조절 효과 (탐색)
df_all = pd.concat([df_ms.assign(is_con=0), df_con.assign(is_con=1, ind_mfg=np.nan)], ignore_index=True)
res_inter = smf.ols('ra_score ~ SDI * is_con + log_workers + elder_rate + foreign_rate + female_rate',
                    data=df_all).fit()
b_i = res_inter.params.get('SDI:is_con',np.nan)
p_i = res_inter.pvalues.get('SDI:is_con',np.nan)
print(f"\n[업종 조절효과 탐색] SDI×건설: β={b_i:+.4f} p={p_i:.4f} → {'✅ 이질성 지지' if p_i<0.05 else '✗'}")

# ──────────────────────────────────────────────────────────
# PHASE 5: 강건성 검증
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 5: 강건성 검증")
print("="*60)

# 민감도 1: Q17_13 → S
formal_sens = {k: v for k,v in formal_groups_ms.items() if k != 'F-M8'}
subst_sens  = {**subst_groups_ms, 'S-M8': ['Q17_13']}
df_ms['F_score_s'] = compute_group_composite(df_ms, formal_sens, '민감도 F')
df_ms['S_score_s'] = compute_group_composite(df_ms, subst_sens,  '민감도 S')
df_ms['SDI_s']     = df_ms['S_score_s'] - df_ms['F_score_s']

res_sA = smf.ols(f'ra_score ~ SDI_s + {controls_ms}', data=df_ms).fit()
res_sB = smf.ols(f'ra_score ~ F_score_s + S_score_s + {controls_ms}', data=df_ms).fit()

bs_s = res_sB.params.get('S_score_s',np.nan)
bf_s = res_sB.params.get('F_score_s',np.nan)
se_bs = res_sB.bse.get('S_score_s',np.nan)
se_bf = res_sB.bse.get('F_score_s',np.nan)
cov_s = res_sB.cov_params().loc['S_score_s','F_score_s']
se_d  = np.sqrt(se_bs**2 + se_bf**2 - 2*cov_s)
t_d   = (bs_s - bf_s) / se_d
p1_s  = (1 - stats.norm.cdf(abs(t_d)))

print(f"민감도(Q17_13→S) | 모형A: β_SDI={res_sA.params.get('SDI_s',np.nan):+.4f} p={res_sA.pvalues.get('SDI_s',np.nan):.4f}")
print(f"                 | 모형B: diff={bs_s-bf_s:+.4f} p(단)={p1_s:.4f} β_S>β_F: {bs_s>bf_s}")

# 민감도 2: 50인 이상
for wc, df, lab in [('Q1_1',df_ms,'제조+서비스'),('Q4_1',df_con,'건설')]:
    df50 = df[df[wc] >= 50].copy() if wc in df.columns else df.copy()
    ctrl = controls_ms if lab!='건설' else controls_con
    res50 = smf.ols(f'ra_score ~ SDI + {ctrl}', data=df50).fit()
    print(f"50인↑ [{lab}] n={int(res50.nobs)} β_SDI={res50.params.get('SDI',np.nan):+.4f} p={res50.pvalues.get('SDI',np.nan):.4f}")

# 강건성 결과표
rob_rows = [
    {'분석':'기본(모형A)', '업종':'제조+서비스', 'n':int(res_A_ms.nobs),
     'β_SDI':round(res_A_ms.params['SDI'],4), 'p':round(res_A_ms.pvalues['SDI'],4),
     'β_S-β_F':round(wald_ms['diff'],4), 'p(단)':round(wald_ms['p1'],4)},
    {'분석':'기본(모형A)', '업종':'건설', 'n':int(res_A_con.nobs),
     'β_SDI':round(res_A_con.params['SDI'],4), 'p':round(res_A_con.pvalues['SDI'],4),
     'β_S-β_F':round(wald_con['diff'],4), 'p(단)':round(wald_con['p1'],4)},
    {'분석':'Q17_13→S', '업종':'제조+서비스', 'n':int(res_sA.nobs),
     'β_SDI':round(res_sA.params.get('SDI_s',np.nan),4), 'p':round(res_sA.pvalues.get('SDI_s',np.nan),4),
     'β_S-β_F':round(bs_s-bf_s,4), 'p(단)':round(p1_s,4)},
]
rob_df = pd.DataFrame(rob_rows)
print(rob_df.to_string(index=False))
rob_df.to_csv(OUTDIR+'robustness_v5.csv', index=False, encoding='utf-8-sig')

# ──────────────────────────────────────────────────────────
# PHASE 6: 건설업 이질성 분석
# ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PHASE 6: 건설업 이질성 분석")
print("="*60)

# C1: 분산
sdi_std_ms  = df_ms['SDI'].std()
sdi_std_con = df_con['SDI'].std()
print(f"C1 SDI분산 | 제조+서비스 σ={sdi_std_ms:.4f}, 건설 σ={sdi_std_con:.4f}")
print(f"  → C1 지지: {'✅' if sdi_std_con < sdi_std_ms else '✗'} (건설 분산 {'작음→검력 낮을 수 있음' if sdi_std_con<sdi_std_ms else '큼'})")

# C2: ra_score 분포
print("\nC2 ra_score 분포:")
for name, df in [('제조+서비스', df_ms), ('건설', df_con)]:
    vc = df['ra_score'].value_counts(normalize=True).sort_index()
    print(f"  [{name}] 미실시(0): {vc.get(0,0)*100:.1f}%  비정기(1): {vc.get(1,0)*100:.1f}%  정기(2): {vc.get(2,0)*100:.1f}%")

# ra_score 분포 시각화
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, (name, df) in zip(axes, [('제조+서비스', df_ms), ('건설', df_con)]):
    vc = df['ra_score'].value_counts(normalize=True).sort_index()*100
    vals = [vc.get(i,0) for i in [0,1,2]]
    bars = ax.bar(['미실시(0)','비정기(1)','정기(2)'], vals,
                  color=['#EF5350','#FFA726','#66BB6A'])
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                f'{v:.1f}%', ha='center', fontsize=10)
    ax.set_title(f'{name}\nra_score 분포'); ax.set_ylabel('%'); ax.set_ylim(0,100)
plt.tight_layout()
plt.savefig(OUTDIR+'ra_score_dist_v5.png', dpi=150, bbox_inches='tight')
plt.close()
print("[저장] ra_score_dist_v5.png")

# C3: 건설업 외생 변수 탐색
q23_cols = sorted([c for c in df_con.columns if c.startswith(('Q23','Q24','Q25','Q26'))])
print(f"\nC3 건설업 Q23~Q26 변수: {q23_cols[:15]}")
avail_c3 = [c for c in ['Q23_1','Q23_2','Q24_1','Q24_2'] if c in df_con.columns]
if avail_c3:
    df_con_c3 = df_con.copy()
    df_con_c3 = apply_nan(df_con_c3, avail_c3, 9)
    # 결측 통계 먼저 출력
    for c in avail_c3:
        miss_pct = df_con_c3[c].isnull().mean()*100
        print(f"  C3 {c} 결측률: {miss_pct:.1f}%")
    formula_c3 = f'ra_score ~ SDI + {" + ".join(avail_c3)} + {controls_con}'
    ctrl_cols = controls_con.replace(' ','').split('+')
    needed = ['ra_score','SDI'] + avail_c3 + ctrl_cols
    needed_avail = [c for c in needed if c in df_con_c3.columns]
    d_c3 = df_con_c3[needed_avail].replace([np.inf,-np.inf], np.nan).dropna()
    print(f"  C3 유효 관측치: {len(d_c3)}")
    if len(d_c3) >= 50:
        res_c3 = smf.ols(formula_c3, data=d_c3).fit()
        b_orig = res_A_con.params.get('SDI', np.nan)
        b_c3   = res_c3.params.get('SDI', np.nan)
        print(f"  C3 통제 전 β_SDI={b_orig:+.4f}, 통제 후 β_SDI={b_c3:+.4f} (변화={b_c3-b_orig:+.4f})")
    else:
        print("  C3: 유효 관측치 부족(<50) — Q23/Q24 결측률 과다, 협력업체 있는 사업장만 응답")
        print("  → 협력업체 보유 여부 별도 이진 변수 활용 권고")
else:
    print("  C3: Q23~Q24 변수 없음 — 코드북 재확인 필요")
    print("  건설업 Q20↑ 변수:", sorted([c for c in df_con.columns if c>='Q20']))

print("\n" + "="*60)
print("모든 Phase 완료")
print(f"산출물: {OUTDIR}")
print("="*60)
