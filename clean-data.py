import pandas as pd
import numpy as np

def createCSVs(scrapedFile, mappedFile):
    # Read CSV files into DataFrames
    df = pd.read_csv(scrapedFile)
    df1 = pd.read_csv(mappedFile, usecols=['Other Specializations Included In The Definition', 'Code of Included Specialization '])
    df2 = pd.read_csv(mappedFile, usecols=[' Specialization Name', 'Specialization Code'])

    # Insert a new column 'code' at position 8 in the main DataFrame
    df.insert(loc=8, column='code', value='')

    # Rename columns in df1 and df2
    df1 = df1.rename(columns={'Other Specializations Included In The Definition': 'name', 'Code of Included Specialization ': 'code'})
    df2 = df2.rename(columns={' Specialization Name': 'name', 'Specialization Code': 'code'})

    # Clean and strip whitespace from name columns in df1 and df2
    df1['name'] = df1['name'].str.replace('[^a-z &A-Z]+', '', regex=True)
    df1['name'] = df1['name'].str.strip()
    df2['name'] = df2['name'].str.replace('[^a-z &A-Z]+', '', regex=True)
    df2['name'] = df2['name'].str.strip()

    # Drop rows with NaN values in the 'name' column
    df1.dropna(subset=['name'], inplace=True)
    df2.dropna(subset=['name'], inplace=True)

    # Call separateAnds function on df1 and store the result in df3
    df3 = separateAnds(df1)

    return df, df1, df2, df3

def findDuplicates():
    # Read CSV file into DataFrame
    df = pd.read_csv('working.csv')
    
    # Find duplicates based on the 'name' column
    a = df[df.duplicated(['name'])]

    # Save DataFrame to CSV
    df.to_csv('newWorking.csv')

    # Drop duplicates based on both 'code' and 'name' columns, keeping the last occurrence
    df.drop_duplicates(subset=['code', 'name'], keep='last', inplace=True)

    # Save DataFrame to CSV
    df.to_csv('newWorking.csv')

    # Find duplicates again based on the 'name' column
    a = df[df.duplicated(['name'])]
    a

def separateAnds(specs):
    # Create an empty DataFrame with columns 'name' and 'code'
    df = pd.DataFrame()
    df['name'] = ''
    df['code'] = ''

    j = 1
    print(specs.shape[0])
    
    # Iterate through rows of the input DataFrame
    for i in range(specs.shape[0]):
        val = specs['name'].iloc[i]

        # Check for the presence of " And" in the value
        if " And" in val:
            a, b = val.split(" And", 1)
            a = a.strip()
            b = b.strip()
            c = val.replace(" And", " &")
            code = specs.iloc[i]['code']

            if code != 0 and code != 9999:
                df.loc[j] = [code, a]
                j += 1
                df.loc[j] = [code, b]
                j += 1
                df.loc[j] = [code, c]
                j += 1

        # Check for the presence of " &" in the value
        if " &" in val:
            a, b = val.split(" &", 1)
            a = a.strip()
            b = b.strip()
            c = val.replace(" &", " And")
            code = specs.iloc[i]['code']

            if code != 0 and code != 9999:
                df.loc[j] = [code, a]
                j += 1
                df.loc[j] = [code, b]
                j += 1
                df.loc[j] = [code, c]
                j += 1
    print(df)
    df.to_csv('divided.csv')
    return df

def combineDfs(df1, df2):
    # Concatenate two DataFrames and reset the index
    return pd.concat([df1, df2]).reset_index(drop=True)

# File names for input CSVs
scrapedFileName = 'combinedUniversityCSV/allUniversities.csv'
mappedFileName = 'specialisations.csv'

# Call createCSVs function to obtain DataFrames
df, df1, df2, df3 = createCSVs(scrapedFileName, mappedFileName)

# Store scraped DataFrame in a variable
scrapedDf = df
i = 0

# Add columns to check if Disciplines are present in df1, df2, and df3
scrapedDf['a'] = scrapedDf.Disciplines.isin(df1['name'])
scrapedDf['b'] = scrapedDf.Disciplines.isin(df2['name'])
scrapedDf['c'] = scrapedDf.Disciplines.isin(df3['name'])
scrapedDf['code'] = ''

# Iterate through rows and update 'code' based on matches in df1, df2, and df3
for index, row in scrapedDf.iterrows():
    i += 1
    discipline = row['Disciplines']

    if discipline:
        if row['a']:
            temp = df1[df1["name"] == discipline].reset_index(drop=True)
            df.loc[index, 'code'] = temp['code'].loc[0]

        elif row['b']:
            temp = df2[df2["name"] == discipline].reset_index(drop=True)
            df.loc[index, 'code'] = temp['code'].loc[0]

        elif row['c']:
            temp = df3[df3["name"] == discipline].reset_index(drop=True)
            df.loc[index, 'code'] = temp['code'].loc[0]

# Save the result to a new CSV file
scrapedDf.to_csv('OtherSpecialtiesMatch.csv')
