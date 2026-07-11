# Version 3 Step 1: 새 결과변수 실데이터 검증
import os, warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep
RAW  = ROOT + 'data' + os.sep + 'raw' + os.sep

files = os.listdir(RAW)
F_CON = RAW + [f for f in files if '건설' in f and f.lower().endswith('.csv')][0]
F_MFG = RAW + [f for f in files if '제조' in f and f.lower().endswith('.csv')][0]
F_SVC = RAW + [f for f in files if '서비스' in f and f.lower().endswith('.csv')][0]

df_con = pd.read_csv(F_CON)
df_mfg = pd.read_csv(F_MFG)
df_svc = pd.read_csv(F_SVC)

def check(df, code, label):
    if code in df.columns:
        vc = df[code].value_counts(dropna=False).sort_index().to_dict()
        print(f'  {label} {code}: OK | {vc}')
    else:
        pfx = code.split('_')[0]
        alts = sorted(df.filter(like=pfx).columns.tolist())
        print(f'  {label} {code}: NOT FOUND | 후보={alts[:8]}')

print('=== 건설업 신규 결과변수 검증 ===')
for c in ['Q14', 'Q21_1', 'Q19_1']:
    check(df_con, c, '건설')

print('\n=== 제조업 신규 결과변수 검증 ===')
for c in ['Q15', 'Q22_1', 'Q20_1']:
    check(df_mfg, c, '제조')

print('\n=== 서비스업 신규 결과변수 검증 ===')
for c in ['Q15', 'Q22_1', 'Q20_1']:
    check(df_svc, c, '서비스')

# 추가: Q22, Q21, Q20, Q19 전체 열 구조 확인 (실제 열 이름)
print('\n=== Q21/Q22/Q19/Q20 열 구조 확인 ===')
for pfx in ['Q21', 'Q22']:
    cols = sorted(df_con.filter(like=pfx).columns.tolist())
    print(f'  건설 {pfx}_*: {cols[:8]}')
for pfx in ['Q22', 'Q20']:
    cols = sorted(df_mfg.filter(like=pfx).columns.tolist())
    print(f'  제조 {pfx}_*: {cols[:8]}')
for pfx in ['Q19', 'Q21']:
    cols = sorted(df_con.filter(like=pfx).columns.tolist())
    print(f'  건설 {pfx}_*: {cols[:8]}')
for pfx in ['Q19', 'Q20']:
    cols = sorted(df_mfg.filter(like=pfx).columns.tolist())
    print(f'  제조 {pfx}_*: {cols[:8]}')

print('\n완료.')
