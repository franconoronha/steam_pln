import pandas as pd

path = './data/merged_output.csv'
df = pd.read_csv(path, sep=';')

print(df['voted_up'].value_counts(dropna=False))