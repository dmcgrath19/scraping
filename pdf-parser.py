import pandas as pd
import camelot 
import pdftotext
import re

def parsePdf(filePath, chosenScale, chosenPages, columnHeaders): 
    # Set default number of columns
    numberOfCols = 10

    # Adjust number of columns based on specific page conditions 
    # (large document that doesn't maintain structure, these values are hardcoded as this code is for particular pdf, but numbers can be adjusted)
    if(chosenPages <= 162 and chosenPages >= 159) or chosenPages == 269: 
        numberOfCols = 12
    elif chosenPages in [255, 257, 259, 261, 267, 271, 273, 275, 281, 289, 295, 299, 301, 303, 305, 307, 327, 329]:
        numberOfCols = 9
    elif chosenPages == 291: 
        numberOfCols = 6

    # Read tables from the PDF using Camelot
    tables = camelot.read_pdf(filePath, pages=str(chosenPages), line_scale=chosenScale, shift_text=['r', 't'], encoding='utf8')
    if len(tables) == 0:
        return False, pd.DataFrame()

    correctTable  = len(tables) - 1
    df = tables[correctTable].df

    # Adjust line scale if columns are not within the expected range
    i = 0
    while (len(df.columns) < 20 and len(df.columns) != numberOfCols and len(df.columns) > 6) and i < 8:
        chosenScale = chosenScale - 5
        tables = camelot.read_pdf(filePath, pages=str(chosenPages), line_scale=chosenScale, shift_text=['r', 't'], encoding='utf8')
        correctTable  = len(tables) - 1
        df = tables[correctTable].df
        i += 1

    isValid = True

    # Check and process the extracted DataFrame
    if (len(df.columns) != numberOfCols):
        isValid = False
    else:
        if(df[0].str.contains('Other')).any():
            df = df[1:]
        if(df[1].str.contains('Fellowship')).any():
            df = df[1:]

        if(chosenPages == 287):
            df[5] = df[5].str.upper()
        if(numberOfCols == 12):
            df = df.iloc[:, 2:]
        elif(numberOfCols == 9):
            df[9] = ''

        if numberOfCols == 6: 
            df = df[1:]
            df[6] = ''
            df.columns = ['Master', 'High Diploma', 'Bachelor', 'Diploma', 'Disciplines', 'Department', 'College']
            df.insert(0, "Doctorate", "")
            df.insert(0, "Fellowship", "")
            df.insert(0, "Other", "")
        else:
            df.columns = columnHeaders

        df['University'] = ''

        j = 0
        isNotSupported = True
        for col in df.columns: 
            #clean up the data
            df[col] = df[col].str.replace('[^a-z &A-Z]+', '', regex=True)
            df[col] = df[col].str.strip()

            if(df[col].str.contains('SUPPORT')).any() and j < 8 and isNotSupported == True:
                isNotSupported = False
                for i in range(df.shape[0]):
                    val = df[col].iloc[i]
                    if "SUPPORT" in val:
                        print("support")
                        df.iloc[i, :7] = 'SUPPORT'
                j += 1

    return isValid, df

def getUniversityName(pdf, page):
    name = ''
    page = page - 1
    with open('university.txt', 'w') as f:
        f.write("".join(pdf[int(page)]))

    # Read lines from the temporary file
    file1 = open('university.txt', 'r')
    Lines = file1.readlines()
    
    count = 0
    name = ''
    # Extract university name based on keywords
    for line in Lines:
        count += 1
        if "university" in line.lower() or "college" in line.lower() or "institute" in line.lower() or "training" in line.lower():
            name = line
            break

    # Clean and format the extracted university name
    name = re.sub("[()]", "", name)
    name = re.sub("[^ -_A-Za-z]", "", name)
    name = name.strip()

    return name

# Initial setup
colHeaders = ['Other', 'Fellowship', 'Doctorate', 'Master', 'High Diploma', 'Bachelor', 'Diploma', 'Disciplines', 'Department', 'College']
numUniversities = 0
mainFile = "education.pdf"
currScale = 76

# Extract text from PDF
with open("education.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)
# Count the number of pages in the PDF file
numPages = len(pdf)
i = 0
isNew = True
needsName = True
dfCombined = pd.DataFrame()
dfCurrentUniversity = pd.DataFrame()

# Placeholder for university name row
rowUniversityName = pd.DataFrame([['', '', '', '', '', '', '', '', '', '', 'universityNameHere']], columns=colHeaders+['University'])

name = ''
# Iterate through pages and extract information
for i in range(0, numPages+1):
    # Parse PDF and get DataFrame
    correct, df = parsePdf(mainFile, currScale, i, columnHeaders=colHeaders)
    print("Page " + str(i))
    print(df)

    if correct:
        if isNew:
            # Start a new university section
            dfCurrentUniversity = df
            name = getUniversityName(pdf, i)
            rowUniversityName.iloc[0, 10] = name
            print("changing uni")
            dfCurrentUniversity = pd.concat([rowUniversityName, dfCurrentUniversity]).reset_index(drop=True)
            print(dfCurrentUniversity)
            print(name)
            isNew = False
            numUniversities += 1
        else:
            # Add to existing university section
            dfCurrentUniversity = pd.concat([dfCurrentUniversity, df]).reset_index(drop=True)
    elif not isNew:
        # End of university section
        isNew = True
        dfCombined = pd.concat([dfCombined, dfCurrentUniversity]).reset_index(drop=True)

# Save the combined DataFrame to a CSV file
dfCombined.to_csv('combinedUniversityCSV/allUniversities.csv')
print(numUniversities)
print(dfCombined)
