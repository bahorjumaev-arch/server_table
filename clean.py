import pandas as pd
import numpy as np
import requests 

servers_inventory = pd.read_csv('data/raw/servers_inventory.csv')

servers_inventory = servers_inventory.rename(columns={
    'Hostname':'hostname',
    'OS':'os',
    'RAM':'ram_gb',
    'cluster ':'cluster'
 },errors="raise")  # errors="raise" agar column mavjud bolmasa Keyerror chiqaradi

def q1_matnlarni_tozalash(servers_inventory):
    df = servers_inventory.copy()

    for col in ['server_id', 'hostname', 'cluster', 'status']:
        df[col] = df[col].str.strip().str.lower()

    for col in ['rack', 'os']:
        df[col] = df[col].str.strip()

    df['ram_gb'] = pd.to_numeric(
        df['ram_gb']
        .astype(str)
        .str.replace('GB', '', case=False, regex=True)
        .str.strip(),
        errors='coerce',
    )
    return df