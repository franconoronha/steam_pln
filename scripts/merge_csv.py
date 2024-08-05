import pandas as pd
import glob

path = './ignore/reviews'
all_files = glob.glob(path + '/*.csv')

dfs = []
for filename in all_files:
    df = pd.read_csv(filename, sep=';')
    dfs.append(df)

merged_df = pd.concat(dfs, ignore_index=True)
merged_df.to_csv('./data/merged_output.csv', index=False, sep=';')

print('Merged file saved to data/merged_output.csv')