from flask import Flask, redirect, url_for, render_template, request, flash
from openpyxl import load_workbook
import random

RULESFILE = r"C:\Users\Nick\Desktop\IndyAssassains\app\RulesOfWar.txt"
DATAFILE = r"C:\Users\Nick\Desktop\IndyAssassains\app\IndependenceAssassins.xlsx"
QUOTEFILE = r"C:\Users\Nick\Desktop\IndyAssassains\WarQuotes.txt"
CLASSCOUNT = 500
ENTRYCOST = 30

def generateRules():                                                    # Loads RULESFILE when needed
    ruleFile = open(RULESFILE,"r")
    rules = []
    for line in ruleFile.readlines():
        rules.append(line)
        rules.append("<br>")
        
    ruleFile.close()
        
    global ruleList
    ruleList = "".join(rules)
    
    return ruleList

def createNewAccount(firstName, lastName,password,number):              # Checks if account ID exists then creates account with entered information

    id = (firstName[:1].lower()+lastName[:5].lower()+number[-4:])       # Player ID's will be the first letter of their first name, first 5 letters of their last name and the last 4 digits of their phone number
    
    wb = load_workbook(DATAFILE)
    
    '''
        Usable columns and rows in each sheet (all are automatically filled by bot):
        Players:
            A2-A1000:Player ID's (See line 32 to see how they are generated)
            B2-B1000: First Names
            C2-C1000: Last Names
            D2-D1000: Status (Dead or Alive)
            E2-E1000: Special Titles (Space to show if anyone has done anything interesting)
            F3-F1000: Phone Numbers (Both for group chat and for player information)
    '''
    
    sheet = wb["Players"]
    next_row = len(sheet['A']) + 1
    
    match = False                           # match will be used to tell code whether or not found an already existing ID
    
    # checking for matches of ID's

    for row in range(2, next_row):
        if id == (sheet[f"A{row}"].value):
            
            match = True                            # if lines 52-53 finds a match to the potential new id, it will throw 409 (Conflict Error) to show this id already exists
            
    if match == True:
        return 409
    
    elif match == False:
    
        # processing Player ID into database
        playerID = sheet.cell(row=next_row, column = 1)
        playerID.value = id
        
        # processing First Name into database
        fName = sheet.cell(row=next_row, column = 2)
        fName.value = firstName
        
        # processing Last Name into database
        lName = sheet.cell(row=next_row, column = 3)
        lName.value = lastName
        
        # processing Phone Number into database
        phoneNumber = sheet.cell(row = next_row, column = 6)
        phoneNumber.value = number
        
        # processing password into database
        passcode = sheet.cell(row = next_row, column = 7)
        passcode.value = password
        
        # setting new Player to Alive
        status = sheet.cell(row = next_row, column = 4)
        status.value = "alive"
            
        
        wb.save(DATAFILE)
        
        return 200                                      # if the function is run successfully (doesn't catch a matching id), it will return 200 (OK) to allow the code to continue
        
def generateQuote():        # Picks random Sun Tzu Quote from QUOTEFILE variable above
    
    # Geting Line Count
    file = open(QUOTEFILE,"r")
    for i, line in enumerate(file):
        pass
    lastLine = i

    
    # Getting random number
    quoteNumber = random.randint(0,lastLine)
    
    # matching random number to quote
    file.seek(0)                            # starting search back at the top.  Lines 98-100 push the "start" of the file to the last line.  Using file.seek(0) pushes the "start" back to line 1
    quotes = file.readlines()
    randomQuote = quotes[quoteNumber]
    
    return randomQuote
    
    file.close()
    
def cashPrize():            # Divide cash prize by current number of alive players from DATAFILE above
    wb = load_workbook(DATAFILE)
    
    '''
        Usable columns and rows in each sheet (all are automatically filled by bot):
        Players:
            A2-A1000:Player ID's (See line 32 to see how they are generated)
            B2-B1000: First Names
            C2-C1000: Last Names
            D2-D1000: Status (Dead or Alive)
            E2-E1000: Special Titles (Space to show if anyone has done anything interesting)
            F3-F1000: Phone Numbers (Both for group chat and for player information)
    '''
    sheet = wb["Players"]
    row_count = len(sheet['D'])
    
    alive_count = row_count
    
    for row in range(2,row_count):
        if sheet[f"D{row}"] != "alive":
            alive_count -= 1
    
    cashprize = (ENTRYCOST*row_count)/alive_count
    
    return cashprize
    
    
# Everything above this line is backend management, below this line is front end:
###########################################    

app = Flask(__name__)

@app.route('/', methods = ["POST", "GET"])
def home():
    
    if request.method == "POST":
        
        if request.form.get("create_account", False):
            return redirect(url_for('newAccount'))
    
    return render_template('home.html', quote = generateQuote(), cashPerWinner = cashPrize())

@app.route('/new_account/', methods = ["POST","GET"])
def newAccount():
    if request.method == "POST":
        if request.form.get("create", False):
            
            firstName = request.form.get("firstName")           # grabs whatever was inputted into the input box with name = "firstName" in new.html
            lastName = request.form.get("lastName")             # grabs whatever was inputted into the input box with name = "lasttName" in new.html
            password = request.form.get("password")             # grabs whatever was inputted into the input box with name = "password" in new.html
            number = request.form.get("number").replace("-","") # grabs whatever was inputted into the input box with name = "number" in new.html and get rid of any dashes entered with the phone number
            confirm = request.form.get("confirmPassword")       # grabs whatever was inputted into the input box with name = "confirmPassword" in new.html
            
            if password == confirm:                                                 # checks if the passwords match. Ifthey do, the system will process all of the information into the database and will move on to the other questions for setup. 
                flash("Account has been created successfully.  Try logging in!")
                response = createNewAccount(firstName,lastName,password,number)
                if response == 409:                             # 409 = Conflict Error
                    return render_template('new.html',ruleList = generateRules())
                elif response == 200:                           # 200 = OK
                    return render_template('home.html')

    
    return render_template('new.html',ruleList = generateRules(), quote = generateQuote())

@app.route('/new_teams', methods = ['POST','GET'])
def new_teams():
    
    
    return render_template('teamsignup.html')

if __name__ == "__main__":
    app.secret_key = "INDYassassains23"
    app.run(host = "0.0.0.0", debug = True)
