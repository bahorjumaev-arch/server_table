import pandas as pd
import numpy as np
def rename_columns(df):
    return df.rename(columns={
        'Hostname': 'hostname', 'OS': 'os', 'RAM': 'ram_gb', 'cluster ': 'cluster'
    }, errors='raise')

def clean_text(df):
    df = df.copy()
    for col in ['server_id', 'hostname', 'cluster', 'status']:
        df[col] = df[col].str.strip().str.lower()
    for col in ['rack', 'os']:
        df[col] = df[col].str.strip()
    return df

def clean_ram(df):
    df = df.copy()
    df['ram_gb'] = pd.to_numeric(
        df['ram_gb'].astype(str).str.replace('GB', '', case=False, regex=True).str.strip(),
        errors='coerce',
    )
    return df

def clean_dates(df, col='purchase_date'):
    df = df.copy()
    s = df[col].astype(str).str.strip()
    s_norm = s.str.replace(r"[/\-]", ".", regex=True)
    kun_birinchi = pd.to_datetime(s_norm, format="%d.%m.%Y", errors="coerce")
    yil_birinchi = pd.to_datetime(s_norm, format="%Y.%m.%d", errors="coerce")
    oy_nomi      = pd.to_datetime(s,      format="%b %d, %Y", errors="coerce")
    df[col] = kun_birinchi.fillna(yil_birinchi).fillna(oy_nomi)
    return df

def clean_cpu(df):
    df = df.copy()
    differ_ = (df['cpu_cores'] < 1.0) | (df['cpu_cores'] > 100.0)
    df.loc[differ_,'cpu_cores'] = np.nan
    return df

def clean_status(df):
    df = df.copy()
    status_map = pd.Series({
        'active':'active',
        'up':'active',
        'maint':'maintenance',
        'retired':'decommissioned',
        'maintenance':'maintenance',
        'decommissioned':'decommissioned'
    })

    df['status'] = df['status'].map(status_map)
    return df


def clean_server_id(df):
    df = df.copy()
    df['server_id'] = df['server_id'].str.replace(r'^srv(\d{3})$', r'srv-\1', regex=True)
    return df

def clean_dup(df):
    df = df.copy()
    df = df.drop_duplicates(subset='server_id',keep='first')
    return df

# ---- ishga tushirish ----
raw = pd.read_csv('data/raw/servers_inventory.csv')   # bir marta o'qiladi, hech qachon o'zgarmaydi

df = rename_columns(raw)
df = clean_text(df)
df = clean_ram(df)
df = clean_dates(df)
df = clean_cpu(df)
df = clean_status(df)
df = clean_server_id(df)
df = clean_dup(df)
df.to_csv('data/clean/servers_clean.csv',index=False)







import json
from pathlib import Path
import pandas as pd

def ingest_metrics(raw_dir):
    good, bad = [], []
    for path in sorted(Path(raw_dir).glob('metrics_*.jsonl')):
        with open(path, encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    rec['source_file'] = path.name
                    good.append(rec)
                except json.JSONDecodeError as e:
                    bad.append((path.name, i, e.msg, line))
    return (
        pd.DataFrame(good),
        pd.DataFrame(bad, columns=['source_file', 'line_no', 'reason', 'raw']),
    )

metrics, rejected = ingest_metrics('data/raw')


def unify_columns(metrics):
    df = metrics.copy()
    df['ts'] = df['ts'].combine_first(df['timestamp'])
    df['cpu_pct'] = df['cpu_pct'].combine_first(df['cpu_usage'])
    df['mem_pct'] = df['mem_pct'].combine_first(df['memory_pct'])

    df = df.drop(columns=['timestamp','cpu_usage','memory_pct'])
    return df

def clean_server_id(metrics):
    df = metrics.copy()
    df['server_id'] = df['server_id'].str.strip().str.lower()
    df['server_id'] = df['server_id'].str.replace(r'^srv(\d{3})$', r'srv-\1', regex=True)
    return df

def clean_ts(df, col='ts'):
    df = df.copy()
    s = df[col].astype(str).str.strip()

    f1 = pd.to_datetime(s, format="%Y-%m-%dT%H:%M:%S", errors="coerce")   # 2026-10-01T00:00:00
    f2 = pd.to_datetime(s, format="...", errors="coerce")                 # 2026-10-01 00:00:00
    f3 = pd.to_datetime(s, format="...", errors="coerce")                 # 01/10/2026 00:00
    f4 = pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit="s")      # 1790812800

    df[col] = f1.fillna(f2).fillna(f3).fillna(f4)
    return df

metrics = unify_columns(metrics)
metrics = clean_server_id(metrics)
metrics = clean_ts(metrics)