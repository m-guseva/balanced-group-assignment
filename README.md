# balanced-group-assignment


This GitHub repository contains a script `conditionAssignment.py` that allows you to assign participants to an experimental group in a way that balances the mean age and sex ratio in each group. This is useful when you do not know the person's attributes in advance but still need to create balanced groups. 

The other script `simulation.py`provides a way to simulate an experiment based on different population parameters (e.g. an experiment with more female than male participants or more older females than males) and check the resulting group assignment.

For now the procedure only balances according to **two attributes**, sex and age. In future versions I might add a more general script to allow for other variables (e.g. education levels) to be balanced.
  

## What needs to be specified for your experiment:
In the head of the code (`conditionAssignment.py`) you need to choose the number of people you need in each group `nPeoplePerCond` (assuming equal group sizes). You also have to adjust the list of group names to fit to your particular experiment (`condition_names`, e.g. ["group1", "group2", "group3"]). Finally, don't forget to set a file path where the output (the csv file of the running group allocation file) will be stored (under `file_path`).

  
## How it works:
run the python script with $python3 conditionAssignment.py in terminal.

1. In the beginning the script initialises an empty dataframe `runningallocation` where the upcoming participants' attributes (sex, age, participantId) and assigned group will documented. This is saved under `runningAllocation.csv`.
2. The dataframe is read from `file_path`.
3. In the terminal the user is asked to enter the participantId (could be anything), the age (in years) and sex (m/f/d). Please note: For now I arbitrarily chose to display an error if the age is >100 (in case the user made a mistake) but this can be easily modified. Regarding the sex variable, if "d" (=diverse) is chosen, the script randomizes between "m" and "f". This can be easily modified as that was an arbitrary (and arguably controversial) choice as well. Pressing anything other than "m", "f" or "d" aborts the script.
4. Once the participant's attributes are entered in the terminal, they are used to determine the appropriate group allocation. See section below for a description of how the assignment method works.
5. The assigned group is displayed in the terminal and the dataframe `runningAllocation` is updated accordingly.
6. Next the terminal prompts the user to decide whether the updated dataframe should be saved in the `runningAllocation.csv` file. Pressing "y" saves the new row to the file, pressing "n" aborts the assignment.
7. An overview over the allocation is shown in the terminal. For each group we can see the number of people within that group, the number of females and males per group as well as the proportion of females (females/(females+males)) for a quick overview. Finally, we can also see the running mean age within each group.

  

## Adaptive Stratified Sampling Method (Minimization)
This procedure is based on a stratified sampling method, see [here](https://en.wikipedia.org/wiki/Minimisation_(clinical_trials)).
After observing a person's attributes of interest, we construct a measure of imbalance for each attribute and each group.
- For the first balancing attribute **sex** (which is a categorical/nominal variable) the imbalance measure is simply the count of participants with the same sex in each group. E.g. participant-to-be-allocated is female, the number of females in group 1 is 5, in group 2 is 3 and in group 3 is 1, so the imbalance measures are [5, 3, 1].
- For the other balancing attribute **age** (which is a continuous/ratio scaled variable) the imbalance measure requires more steps. For each group we create a hypothetical scenario. We add the person in question whose age is some number x to a given group and calculate the mean for <u>every</u> group. Then we check what the distance between the group means would be in this scenario. The distance is calculated as the range between the group means, i.e. highest mean age - lowest mean age. The range is then used as an imbalance measure. This procedure of creating hypothetical scenarios is repeated for every group, so that we end up with one imbalance measure for every group.
- There is a third necessary/implicit balancing factor which is the **number of people per group**. This needs to be accounted for to ascertain that if we stop data acquisition earlier than planned (e.g. instead of 90 people we only test 50), the amount of people in each group is still as balanced as possible.

Having collected the 3 imbalance measures for each group, we create a table (`MT_Table`) with groups as columns and the three attributes used for stratification as rows. We then sum up the imbalance measures within each group (`marginalTotal`). The group where the sum of imbalance measures is the smallest is the group that will be chosen for group assignment. If there is a tie, the group is chosen at random.

  
  
## Simulation.py
The simulation works exactly the same as the main code `conditionAssignment.py`, the only difference is that the participant attributes are not entered via the input dialogue in the terminal but are sampled from a specified distribution. The desired parameters of the distribution should be specified in the top of the script. The group assignment then repeats in a loop according to the desired number of people in a condition. The final output is a `sim_runningAllocation.csv` file which contains an overview over the group allocation for each participant.

---
Note: I use the words "group" and "condition" interchangeably. This code uses Python 3.9