import pandas as pd
import random
import csv
import numpy as np
import os

####################################################################################
########################## Simulation of group allocation ##########################
####################################################################################
'''
This script simulates a condition allocation by running the whole script in a loop. Instead of
retrieving the participant attributes from the user input dialogue in the terminal this script simulates values (see below). 
You can adjust the parameters to create your desired population, e.g. by selecting whether you expect an
imbalanced sex ratio (which is often the case in psychology experiments as more women participate).

Author: Maja Guseva (2023)
'''
# maximum number of people per condition:
nPeoplePerCond = 10

# list of condition names:
condition_names = ["C1", "C2", "C3"] 

n_conditions = len(condition_names)

# path where the allocation overview csv file is stored (don't forget the "/" at the end of the path)
file_path = "INSERT_YOUR_PATH_.../balanced-group-assignment/output/" 

####################################################################################
###### The following parameters can be changed to create different distributions

#Simulate different sex distribution populations (comment out the one you are not interested in)
#Equal sex ratio:
population = ['m','f']
# OR More f than m (3:1):
population = ['m','f','f','f']

#Simulate different age distribution depending on gender (values are exemplary, choose your own)
meanF = 26
meanM = 22
stdF = 4
stdM = 4
agef = np.round(np.random.normal(meanF,stdF,nPeoplePerCond*n_conditions))
agem = np.round(np.random.normal(meanM,stdM,nPeoplePerCond*n_conditions))

####################################################################################

def main():    
     
    print('iteration' + str(step))
    
    # Inititalize table at the start
    if os.path.exists(file_path + "runningAllocation.csv") == False:
        runningAllocation = initTable(condition_names, file_path)

    # Read file and retrieve table
    runningAllocation  = readFile(file_path)

    
    # Instead of retrieving participant information via input in terminal, we simulate participant attributes
    participantId = step + 1
    sex = random.choice(population)
    if sex == 'f':
        age = random.choice(agef)
    elif sex == 'm':
        age = random.choice(agem)
   
    # Select condition based on participantInfo
    condition, _ = conditionSelection(runningAllocation, condition_names, nPeoplePerCond, sex, age, participantId)
    
    # Update table
    runningAllocation =  updateTable(runningAllocation, sex, age, participantId, condition)

    # Save new table
    saveTable(runningAllocation, file_path)

    # Print overview over sample
    printInfo(runningAllocation, condition_names)
    
    return runningAllocation




def initTable(condition_names, file_path):
    """ Initializes new runningAllocation table (needs to only be done once) """
    
    runningAllocation = pd.DataFrame({
    "participantId": ['na'],
    "sex": ['na'],
    "age": [0],
    **{name: [0] for name in condition_names}})
    
    #Save everything as csv:
    runningAllocation.to_csv(file_path + "runningAllocation.csv")
    return runningAllocation


def readFile(file_path): 
    """ Reads csv file in file_path  where runningAllocation is stored """

    runningAllocation = pd.read_csv(file_path +"runningAllocation.csv", index_col = 0)
    return runningAllocation

def getParticipantInfo(): 
    """
    Dialog input box in terminal to set the participant's attributes
    THIS FUNCTION IS NOT CALLED IN THIS SIMULATION SCRIPT BECAUSE
    WE USE SIMULATED VALUES!!
    """
    
    participantId = input("ParticipantId: ")

    sexInput = input("Sex (m/f/d): ")
    if sexInput != "f" and sexInput != "m" and sexInput != "d":
        print("ERROR: Sex input incorrect")
        exit()
    elif sexInput == "d": #this is an arbitrary choice to keep it simple, "d" could be made its own category
        sex  = random.choice(["m", "f"])
    else:
        sex = sexInput

    age = int(input("Age (in years): ")) 
    if age > 100 :
        print("ERROR: Age implausible")
        exit()
    
    return participantId, sex, age




def conditionSelection(runningAllocation, condition_names, nPeoplePerCond, sex, age, participantId):
    """
    Executes condition selection based on participant attributes by minimizing strata
    """

    ############################################################################################################
    ### ### ### Stratum 1: Sex  ### ### ###
    # amount of people with current sex per condition:
    strat1 = {condition_names[i]:len(runningAllocation[(runningAllocation.sex == sex)  & (runningAllocation[condition_names[i]] == 1)])  for i in range(len(condition_names))}

    ############################################################################################################
    ### ### ### Stratum 2: Age  ### ### ###
    strat2 = []
    currentMeanAge = []
    for i in range(len(condition_names)):
        # Amount of people per condition
        nPerCond = sum(runningAllocation[condition_names[i]] == 1)
        
        if nPerCond != 0: 
             # Extract ages of people with condition of interest
            currentAge = runningAllocation.age[runningAllocation[condition_names[i]] == 1]
            # Take the mean age
            currentMeanAge.append(sum(currentAge)/nPerCond)
        else:
            currentMeanAge.append(0) # If there was no one added yet, happens only once

    for i in range(len(condition_names)):
        #Create dictionary with mean ages that would result if current person was added:
        hypotheticalList = list(runningAllocation.age[runningAllocation[condition_names[i]] == 1])
        hypotheticalList.append(age) # append new age 
        hypotheticalMean =  sum(hypotheticalList)/len(hypotheticalList)
        
        #list of conditions other than the one we're testing
        otherConds = [*filter(lambda x: x != i,list(range(len(condition_names))))]
 
        #Test combinations of conditions and find the mean combination that minimizes distance
        newMeansToTest = [hypotheticalMean] + [currentMeanAge[cond] for cond in otherConds]
 
        #Calculate range between biggest and smallest mean (this will be  minimized later)
        strat2.append(max(newMeansToTest)-min(newMeansToTest))


    ############################################################################################################
    ### Stratum 3: n people per condition
    strat3 = runningAllocation.sum()[condition_names]

    ############################################################################################################

    #Create Marginal Totals table
    MT_Table = pd.DataFrame([strat1])
    MT_Table.loc[len(MT_Table)] = strat2
    MT_Table.loc[len(MT_Table)] = strat3
    MT_Table.index = ["strat1_sex", "strat2_age", "strat3_nPerCondition"]

    marginalTotal = MT_Table.sum()
   
    #Make sure that we won't exceed desired amount of people per condition
    for i in range(len(condition_names)):
        if runningAllocation.sum()[condition_names[i]] >= nPeoplePerCond:
            marginalTotal.loc[condition_names[i]] = 999 # Make number so high that it will never be chosen

    
    # Select minimum of marginal totals, if it's ambiguous, randomize:
    # save all minima (at least one in list)
    minima=[idx for idx,val in enumerate(marginalTotal) if val==min(marginalTotal)]
    # Randomize over minima (trivial if only one minimum)
    condition = condition_names[random.choice(minima)] 
    print("\nAllocate participant to condition: " +  condition)

    return condition, marginalTotal

def updateTable(runningAllocation, sex, age, participantId, condition):
    """
    Updates runningAllocation table with new values (condition allocation, sex, age, participantID)
    Returns new updated runningAllocation dataframe
    """
    #Create new row and fill with participant information
    newRow = [0]*(len(runningAllocation.columns))
    dfCols = list(runningAllocation.columns)
    newRow[dfCols.index("sex")] = sex
    newRow[dfCols.index("participantId")] = participantId
    newRow[dfCols.index("age")] = age
    newRow[dfCols.index(condition)] = 1

    #Update runningAllocation:
    runningAllocation.loc[len(runningAllocation)] = newRow

    return runningAllocation


def saveTable(runningAllocation, file_path):
    """ Saves updated runningAllocation dataframe in file_path """
    runningAllocation.to_csv(file_path + "runningAllocation.csv")

    return


def printInfo(runningAllocation, condition_names):    
    """ Prints an overview over the variables of interest after condition allocation """
    
    print("\nALLOCATION OVERVIEW")
    print("------------")

    for i in range(len(condition_names)):
        nPeople = str(sum(runningAllocation[condition_names[i]] == 1))
        nPeopleFemale = len(runningAllocation.query(f"{condition_names[i]} == 1 and sex == 'f'"))
        nPeopleMale = len(runningAllocation.query(f"{condition_names[i]} == 1 and sex == 'm'"))
        if (nPeopleFemale+nPeopleMale) > 0:
            proportion = nPeopleFemale/(nPeopleMale+nPeopleFemale)
        else:
            proportion = "nan"
        meanAge = runningAllocation.loc[runningAllocation[condition_names[i]] == 1, 'age'].mean()   

        print("Condition "+condition_names[i]+ ": ")        
        print("n: " + str(nPeople))
        print("sex: f: " + str(nPeopleFemale) + ", m: " +str(nPeopleMale) + "; proportion females: " + str(proportion))
        print("mean age: " + str(meanAge))
        print("------------")
    return



        
if __name__ == "__main__":
    for step in range(nPeoplePerCond*n_conditions):
        main() 
