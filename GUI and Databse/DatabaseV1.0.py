import pandas as pd #Pandas for database creation
import matplotlib as plt # Matplotlib for plotting data


#   This generates a Pandas 'database' Object by reading a CSV file
#   NOTE: Change input to name of finalized CSV file   

database = pd.read_csv("dummy1.csv")

#   Seperate different sections based on operating mode;
#   Pandas does this by checking column with label "MODE" (label in row 0, col n)
#   We then take the entries (individual rows) that match the case for that column
#
#   NOTE:If we decide on utilising 2-bit indicator, we must instead check
#        both bits ("MODE"[0] and "MODE"[1])

dataChargeFree = database[database["MODE"] == 1] 
#If operating code is 1, system is Charging in Free-Axis mode

dataChargeFix = database[database["MODE"] == 2]
#If operating code is 1, system is Charging in Fixed-Axis mode

dataDischarge = database[database["MODE"] == 3]
#If operating code is 1, system is in Discharging mode
# Note: Discharge mode does not care if system is fixed/free 


plt.figure()
df = pd.DataFrame(data=dataChargeFree,index = database["TIME"])
# . . . . .
