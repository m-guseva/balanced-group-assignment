# balanced-group-assignment

This GitHub repository contains a script that allows you to assign participants to an experimental group in a way that balances the mean age and sex ratio in each group. This is useful when you do not know the person's attributes in advance but still need to create balanced groups.

For now this script only balances according to **two attributes**, sex and age. In future versions I might add a more general script to allow for other variables (e.g. education levels) to be balanced.

## What needs to be specified for your experiment:
In the head of the code you need to choose the number of people you need in each group `nPeoplePerCond` (assuming equal group sizes). You also have to adjust the list of group names to fit to your particular experiment (`condition_names`, e.g. ["group1", "group2", "group3"]). Finally, don't forget to set a file path where the output (the csv file of the running group allocation file) will be stored (under `file_path`).


## How it works:
1. In the beginning the script initialises an empty dataframe  `runningallocation` where the upcoming participants, their attributes (sex, age, participantId) and assigned group will documented. This is saved under `runningAllocation.csv`
2. The dataframe is read from `file_path`
3. In the terminal the user is asked to enter the participantId (could be anything), the age (in years) and sex (m/f/d). Please note: For now I arbitrarily chose to display an error if the age is >100 in case the user made a mistake but this can be easily modified. Also, regarding the sex variable, If "d" (=diverse) is chosen, the script randomizes between "m" and "f". This can be easily modified as that was an arbitrary choice as well. Pressing anything other than "m", "f" or "d" aborts the script.
4. The participant's attributes that have been entered in the terminal are then used to determine which group to be assigned to. See section below for a description how the assignment method works.
5. The assigned group is displayed in the terminal and the dataframe `runningAllocation` is updated. 
6. Next the terminal prompts the user to decide whether the updated dataframe should be saved in the runningAllocation.csv file. Pressing "y" saves the new row to the file, pressing "n" aborts the assignment.
7. An overview over the allocation is printed in the terminal. For each group we see the number of people within that group, the number of females and males as well as the proportion of females (femals/(females+males)) for a quick overview. Finally, we can also see the running mean age within each group.

## Adaptive Stratified Sampling Method (Minimization)

This is based on a stratified sampling method, see here https://en.wikipedia.org/wiki/Minimisation_(clinical_trials). 
After observing a person's attributes of interest, we construct a measure of imbalance for each attribute and each group.
- For the first balancing attribute **sex** (which is a categorical/nominal variable) the imbalance measure is simply the count of participants with the same sex in each group. E.g. participant-to-be-allocated is female, the number of females in group 1 is 5, in group 2 is 3 and in group 3 is 1.
- For the other balancing attribute **age** (which is a continuous/ratio scaled variable) the imbalance measure requires more steps. For each group we create a hypothetical scenario. We add the person in question whose age is some number x to a given group and calculate the mean for every group. Then we check what the distance between the group means would be. The distance is calculated as the range between the group means, i.e. highest mean age - lowest mean age. The range is then used as an imbalance measure. This procedure of creating hypothetical scenarios is repeated for every group, so that for every group we end up with one imbalance measure
- There is a third necessary/implicit balancing factor which is the **number of people per group**. This needs to be accounted for to ascertain that if we stop data acquisition earlier than planned (e.g. instead of 90 people we only test 50), the amount of people in each group is still kept balanced as much as possible. 
Having collected the 3 imbalance measures for each group, we create a table where the columns are the group and the rows the balance the three attributes used for stratification (`MT_Table`). We then sum up the imbalance measures within each group (`marginalTotal`). The group where the sum of imbalance measures is the smallest is the group that will be chosen for assignment. If there is a tie, the group is chosen at random.



---
Note: I use the words "group" and "condition" interchangeably.
This code uses Python 3.9