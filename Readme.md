# Weather Report Generator

This script is python script to extract data from Firebird Database for weather measurement. Firebird SQL Database contains my weather data. This scripti queries the database and creates a monthly report. The report's contents must be the daily maximum and minimum temperature for the prior 24 hours ending at 7AM. Also, rainfall for the past 24 hours ending at 7AM as well as the current temperature at 7AM. And this script ouput results of query on google sheets as report format.
## Step

### Step 1: Install Firebird database

- Install Firebird-2.5.9 [https://github.com/FirebirdSQL/firebird/releases/download/R2_5_9/Firebird-2.5.9.27139_0_x64.exe]
- Install Flamerobin 0.9.3.12

### Step 2: Set Google Drive APIs

- 1. Head over to the Google API Console.
- 2. Create a new project by selecting My Project -> + button
- 3. Search for 'Google Drive API', enable it.
- 4. Head over to 'Credentials' (sidebar), click 'Create Credentials' -> 'Service Account Key'
- 5. Create Key as JSON format and Save.
- 6. Copy Json file as name "cred.json"

Please show here [https://www.geeksforgeeks.org/how-to-automate-google-sheets-with-python/]

### Step 3: install python library

`pip install -r requirements.txt`

## Run report.py
`python report.py --year 2023 --month 8`

## Check out

Check out on your google drive
![enter image description here](https://github.com/LoveNui/Weather-MonthlyReporter/blob/main/picture/Google_Driver.png)
![enter image description here](https://github.com/LoveNui/Weather-MonthlyReporter/blob/main/picture/Result.PNG)
