# Weather Report Generator

This project is to extract data from firebird database. This project write results on google sheet. 
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
![enter image description here](https://github.com/montesound/WeatherMaster-MonthlyReporter/blob/main/picture/Google_Driver.png)
![enter image description here](https://github.com/montesound/WeatherMaster-MonthlyReporter/blob/main/picture/result.JPG)
