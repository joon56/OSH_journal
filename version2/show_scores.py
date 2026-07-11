# 변수별 EFA 적재량 + 정규화 점수 통합 출력
import os, warnings
import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep
RAW  = BASE + 'data' + os.sep + 'raw' + os.sep
OUT  = BASE + 'output' + os.sep + 'v2' + os.sep

files = os.listdir(RAW)
F_CON = RAW + [f for f in files if '건설' in f and f.lower().endswith('.csv')][0]
F_MFG = RAW + [f for f in files if '제조' in f and f.lower().endswith('.csv')][0]

df_con = pd.read_csv(F_CON)
df_mfg = pd.read_csv(F_MFG)

def minmax(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) if mx > mn else pd.Series(0.0, index=s.index)

def binary_norm(s):
    return s.map({1: 1.0, 2: 0.0})

def q10_con_norm(s):
    return s.map({1: 1.0, 2: 0.5, 3: 0.0, 4: np.nan, 9: np.nan})

def q10_ms_norm(s):
    return s.map({1: 1.0, 2: 0.0, 3: np.nan})

# ── 건설업 전처리 ────────────────────────────────────────────
likert_con = ([f'Q15_2_{i}' for i in range(1,8)] +
              ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
               'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4'])
df_con[likert_con] = df_con[likert_con].replace(9, np.nan)
df_con['Q21_2'] = df_con['Q21_2'].replace(9, np.nan)
df_con['Q6']    = df_con['Q6'].replace(9, np.nan)
df_con['Q9']    = df_con['Q9'].replace(9, np.nan)
for c in ['Q8_1','Q8_2','Q8_3','Q8_4']:
    df_con[c] = df_con[c].replace(999, np.nan)

# 건설 정규화
norm_con = {}
norm_con['Q6']    = binary_norm(df_con['Q6'])
norm_con['Q8_1']  = minmax(df_con['Q8_1'])
norm_con['Q8_2']  = minmax(df_con['Q8_2'])
norm_con['Q8_3']  = minmax(df_con['Q8_3'])
norm_con['Q8_4']  = minmax(df_con['Q8_4'])
norm_con['Q9']    = binary_norm(df_con['Q9'])
norm_con['Q10']   = q10_con_norm(df_con['Q10'])
norm_con['Q12_1'] = binary_norm(df_con['Q12_1'])
norm_con['Q12_2'] = binary_norm(df_con['Q12_2'])
for c in likert_con + ['Q21_2']:
    norm_con[c] = minmax(df_con[c])

# ── 제조업 전처리 ────────────────────────────────────────────
likert_mfg = ([f'Q16_2_{i}' for i in range(1,8)] +
              ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
               'Q17_12','Q17_13','Q17_15','Q17_16','Q17_17',
               'Q18_1','Q18_2','Q18_3','Q18_4'])
df_mfg[likert_mfg] = df_mfg[likert_mfg].replace(9, np.nan)
df_mfg['Q22_2'] = df_mfg['Q22_2'].replace(9, np.nan)
df_mfg['Q6']    = df_mfg['Q6'].replace(9, np.nan)
for c in ['Q9_1','Q9_2','Q11']:
    df_mfg[c] = df_mfg[c].replace(9, np.nan)
for c in ['Q8_1','Q8_2']:
    df_mfg[c] = df_mfg[c].replace(999, np.nan)

norm_mfg = {}
norm_mfg['Q6']    = binary_norm(df_mfg['Q6'])
norm_mfg['Q8_1']  = minmax(df_mfg['Q8_1'])
norm_mfg['Q8_2']  = minmax(df_mfg['Q8_2'])
norm_mfg['Q9_1']  = binary_norm(df_mfg['Q9_1'])
norm_mfg['Q9_2']  = binary_norm(df_mfg['Q9_2'])
norm_mfg['Q10']   = q10_ms_norm(df_mfg['Q10'])
norm_mfg['Q11']   = binary_norm(df_mfg['Q11'])
norm_mfg['Q13_1'] = binary_norm(df_mfg['Q13_1'])
norm_mfg['Q13_2'] = binary_norm(df_mfg['Q13_2'])
for c in likert_mfg + ['Q22_2']:
    norm_mfg[c] = minmax(df_mfg[c])

# ── EFA ─────────────────────────────────────────────────────
efa_con_items = ([f'Q15_2_{i}' for i in range(1,8)] +
                 ['Q16_1','Q16_2','Q16_3','Q16_9','Q16_10',
                  'Q16_16','Q16_17','Q16_18','Q17_1','Q17_2','Q17_4','Q21_2'])
X_con = df_con[efa_con_items].dropna()
fa_con = FactorAnalyzer(n_factors=2, method='principal', rotation='varimax')
fa_con.fit(X_con)
load_con = pd.DataFrame(fa_con.loadings_, index=efa_con_items, columns=['EFA_F1','EFA_F2'])

efa_mfg_items = ([f'Q16_2_{i}' for i in range(1,8)] +
                 ['Q17_1','Q17_2','Q17_3','Q17_9','Q17_10',
                  'Q17_12','Q17_13','Q17_15','Q17_16','Q17_17',
                  'Q18_1','Q18_2','Q18_3','Q18_4','Q22_2'])
X_mfg = df_mfg[efa_mfg_items].dropna()
fa_mfg = FactorAnalyzer(n_factors=2, method='principal', rotation='varimax')
fa_mfg.fit(X_mfg)
load_mfg = pd.DataFrame(fa_mfg.loadings_, index=efa_mfg_items, columns=['EFA_F1','EFA_F2'])

# ── 테이블 구성 ──────────────────────────────────────────────
def build_table(norm_dict, load_df, var_meta):
    """
    var_meta: [(코드, 분류, 그룹명), ...]
    """
    rows = []
    for code, cls, grp in var_meta:
        n_vals = norm_dict[code]
        mean_n = round(n_vals.mean(), 3)
        std_n  = round(n_vals.std(),  3)
        notna  = n_vals.notna().sum()

        if code in load_df.index:
            f1 = round(load_df.loc[code,'EFA_F1'], 3)
            f2 = round(load_df.loc[code,'EFA_F2'], 3)
        else:
            f1, f2 = '-', '-'

        rows.append({'변수코드': code, '분류': cls, '그룹': grp,
                     'EFA_F1': f1, 'EFA_F2': f2,
                     '정규화_mean': mean_n, '정규화_std': std_n, 'n_유효': notna})
    return pd.DataFrame(rows)

# 건설 변수 메타
con_meta = [
    ('Q6',    'F', 'F-C1_전담부서'),
    ('Q8_1',  'F', 'F-C2_선임인원'),
    ('Q8_2',  'F', 'F-C2_선임인원'),
    ('Q8_3',  'F', 'F-C3_전담직원'),
    ('Q8_4',  'F', 'F-C3_전담직원'),
    ('Q9',    'F', 'F-C4_기술지도'),
    ('Q10',   'F', 'F-C5_위원회'),
    ('Q12_1', 'F', 'F-C6_KOSHA'),
    ('Q12_2', 'F', 'F-C7_ISO'),
    ('Q15_2_1','S','S-C2_스트레스관리'),
    ('Q15_2_2','S','S-C2_스트레스관리'),
    ('Q15_2_3','S','S-C2_스트레스관리'),
    ('Q15_2_4','S','S-C2_스트레스관리'),
    ('Q15_2_5','S','S-C2_스트레스관리'),
    ('Q15_2_6','S','S-C2_스트레스관리'),
    ('Q15_2_7','S','S-C2_스트레스관리'),
    ('Q16_1', 'S', 'S-C3_경영강조'),
    ('Q16_2', 'S', 'S-C3_경영강조'),
    ('Q16_3', 'S', 'S-C3_경영강조'),
    ('Q16_9', 'S', 'S-C4_교육효과'),
    ('Q16_10','S', 'S-C4_교육효과'),
    ('Q16_16','S', 'S-C5_행동준수'),
    ('Q16_17','S', 'S-C5_행동준수'),
    ('Q16_18','S', 'S-C5_행동준수'),
    ('Q17_1', 'S', 'S-C6_감독자역량'),
    ('Q17_2', 'S', 'S-C6_감독자역량'),
    ('Q17_4', 'S', 'S-C6_감독자역량'),
    ('Q21_2', 'S', 'S-C7_환경노력'),
]

# 제조 변수 메타
mfg_meta = [
    ('Q6',     'F', 'F-M1_전담부서'),
    ('Q8_1',   'F', 'F-M2_선임신고'),
    ('Q8_2',   'F', 'F-M2_선임신고'),
    ('Q9_1',   'F', 'F-M3_위탁기관'),
    ('Q9_2',   'F', 'F-M3_위탁기관'),
    ('Q10',    'F', 'F-M4_위원회'),
    ('Q11',    'F', 'F-M5_담당자'),
    ('Q13_1',  'F', 'F-M6_KOSHA'),
    ('Q13_2',  'F', 'F-M7_ISO'),
    ('Q17_13', 'F', 'F-M8_시설보호구'),
    ('Q16_2_1','S', 'S-M1_스트레스관리'),
    ('Q16_2_2','S', 'S-M1_스트레스관리'),
    ('Q16_2_3','S', 'S-M1_스트레스관리'),
    ('Q16_2_4','S', 'S-M1_스트레스관리'),
    ('Q16_2_5','S', 'S-M1_스트레스관리'),
    ('Q16_2_6','S', 'S-M1_스트레스관리'),
    ('Q16_2_7','S', 'S-M1_스트레스관리'),
    ('Q17_1',  'S', 'S-M2_경영강조'),
    ('Q17_2',  'S', 'S-M2_경영강조'),
    ('Q17_3',  'S', 'S-M2_경영강조'),
    ('Q17_9',  'S', 'S-M3_교육효과'),
    ('Q17_10', 'S', 'S-M3_교육효과'),
    ('Q17_12', 'S', 'S-M4_규정효과'),
    ('Q17_15', 'S', 'S-M5_행동준수'),
    ('Q17_16', 'S', 'S-M5_행동준수'),
    ('Q17_17', 'S', 'S-M5_행동준수'),
    ('Q18_1',  'S', 'S-M6_감독자역량'),
    ('Q18_2',  'S', 'S-M6_감독자역량'),
    ('Q18_3',  'S', 'S-M6_감독자역량'),
    ('Q18_4',  'S', 'S-M6_감독자역량'),
    ('Q22_2',  'S', 'S-M7_환경노력'),
]

tbl_con = build_table(norm_con, load_con, con_meta)
tbl_mfg = build_table(norm_mfg, load_mfg, mfg_meta)

# ── 그룹 composite 계산 ──────────────────────────────────────
def group_composite(norm_dict, groups):
    rows = {}
    for gname, codes in groups.items():
        vals = pd.DataFrame({c: norm_dict[c] for c in codes})
        rows[gname] = vals.mean(axis=1)
    return pd.DataFrame(rows)

f_groups_con = {
    'F-C1_전담부서': ['Q6'],
    'F-C2_선임인원': ['Q8_1','Q8_2'],
    'F-C3_전담직원': ['Q8_3','Q8_4'],
    'F-C4_기술지도': ['Q9'],
    'F-C5_위원회':   ['Q10'],
    'F-C6_KOSHA':    ['Q12_1'],
    'F-C7_ISO':      ['Q12_2'],
}
s_groups_con = {
    'S-C2_스트레스관리': [f'Q15_2_{i}' for i in range(1,8)],
    'S-C3_경영강조':    ['Q16_1','Q16_2','Q16_3'],
    'S-C4_교육효과':    ['Q16_9','Q16_10'],
    'S-C5_행동준수':    ['Q16_16','Q16_17','Q16_18'],
    'S-C6_감독자역량':  ['Q17_1','Q17_2','Q17_4'],
    'S-C7_환경노력':    ['Q21_2'],
}
f_groups_mfg = {
    'F-M1_전담부서':  ['Q6'],
    'F-M2_선임신고':  ['Q8_1','Q8_2'],
    'F-M3_위탁기관':  ['Q9_1','Q9_2'],
    'F-M4_위원회':    ['Q10'],
    'F-M5_담당자':    ['Q11'],
    'F-M6_KOSHA':     ['Q13_1'],
    'F-M7_ISO':       ['Q13_2'],
    'F-M8_시설보호구':['Q17_13'],
}
s_groups_mfg = {
    'S-M1_스트레스관리': [f'Q16_2_{i}' for i in range(1,8)],
    'S-M2_경영강조':     ['Q17_1','Q17_2','Q17_3'],
    'S-M3_교육효과':     ['Q17_9','Q17_10'],
    'S-M4_규정효과':     ['Q17_12'],
    'S-M5_행동준수':     ['Q17_15','Q17_16','Q17_17'],
    'S-M6_감독자역량':   ['Q18_1','Q18_2','Q18_3','Q18_4'],
    'S-M7_환경노력':     ['Q22_2'],
}

fc_con = group_composite(norm_con, f_groups_con)
sc_con = group_composite(norm_con, s_groups_con)
F_con = fc_con.mean(axis=1)
S_con = sc_con.mean(axis=1)
SDI_con = S_con - F_con

fc_mfg = group_composite(norm_mfg, f_groups_mfg)
sc_mfg = group_composite(norm_mfg, s_groups_mfg)
F_mfg = fc_mfg.mean(axis=1)
S_mfg = sc_mfg.mean(axis=1)
SDI_mfg = S_mfg - F_mfg

# ── 출력 ────────────────────────────────────────────────────
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', '{:.3f}'.format)

print("=" * 80)
print("건설업 - 변수별 EFA 적재량 + 정규화 점수")
print("  EFA_F1/F2: 없음(-) = 이진/연속형으로 EFA 미투입")
print("  정규화_mean: Min-Max 후 사업장 전체 평균 (0~1 범위)")
print("=" * 80)
print(tbl_con.to_string(index=False))

print("\n건설업 -그룹 composite 평균")
grp_con_rows = []
for g in fc_con.columns:
    grp_con_rows.append({'그룹': g, '분류': 'F', 'composite_mean': round(fc_con[g].mean(),3), 'composite_std': round(fc_con[g].std(),3)})
for g in sc_con.columns:
    grp_con_rows.append({'그룹': g, '분류': 'S', 'composite_mean': round(sc_con[g].mean(),3), 'composite_std': round(sc_con[g].std(),3)})
print(pd.DataFrame(grp_con_rows).to_string(index=False))

print(f"\n건설업 F_score: mean={F_con.mean():.3f}, std={F_con.std():.3f}")
print(f"건설업 S_score: mean={S_con.mean():.3f}, std={S_con.std():.3f}")
print(f"건설업 SDI:     mean={SDI_con.mean():.3f}, std={SDI_con.std():.3f}, SDI<0={( SDI_con<0 ).mean():.1%}")

print("\n" + "=" * 80)
print("제조업 - 변수별 EFA 적재량 + 정규화 점수")
print("=" * 80)
print(tbl_mfg.to_string(index=False))

print("\n제조업 -그룹 composite 평균")
grp_mfg_rows = []
for g in fc_mfg.columns:
    grp_mfg_rows.append({'그룹': g, '분류': 'F', 'composite_mean': round(fc_mfg[g].mean(),3), 'composite_std': round(fc_mfg[g].std(),3)})
for g in sc_mfg.columns:
    grp_mfg_rows.append({'그룹': g, '분류': 'S', 'composite_mean': round(sc_mfg[g].mean(),3), 'composite_std': round(sc_mfg[g].std(),3)})
print(pd.DataFrame(grp_mfg_rows).to_string(index=False))

print(f"\n제조업 F_score: mean={F_mfg.mean():.3f}, std={F_mfg.std():.3f}")
print(f"제조업 S_score: mean={S_mfg.mean():.3f}, std={S_mfg.std():.3f}")
print(f"제조업 SDI:     mean={SDI_mfg.mean():.3f}, std={SDI_mfg.std():.3f}, SDI<0={( SDI_mfg<0 ).mean():.1%}")

# CSV 저장
tbl_con.to_csv(OUT + 'var_scores_con_v2.csv', index=False, encoding='utf-8-sig')
tbl_mfg.to_csv(OUT + 'var_scores_mfg_v2.csv', index=False, encoding='utf-8-sig')
print(f"\nCSV 저장 완료: {OUT}")
