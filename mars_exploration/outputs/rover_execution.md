<think>
Okay, the user wants me to output only the rover steps from the mission plan with specific fields. Let me go through the steps carefully.

First, I need to extract all steps where "unit" is "rover". From the mission plan JSON provided, the actions list shows:

- Step 1: unit = "rover", node = "N12", task = "subsurface sampling"
- Step 2: unit = "rover", node = "N45", task = "subsurface sampling"
- Step 3: unit = "rover", node = "N78", task = "subsurface sampling"
- Step 7: unit = "rover", node = "N90", task = "radiation measurement"

So those are the four rover steps.

Next, for Notes: The user mentioned to check the risks list. The risks array has one entry: "Rover energy constraints may delay N90 radiation measurement". This risk specifically references N90, which is the target of step 7. So step 7 gets this risk as Notes. The other steps (1, 2, 3) have no associated risks, so their Notes are "none".

I need to make sure all fields are present. The mission plan provides step number, target node, and task for all steps. No fields are missing, so no "unknown" needed.

The output format should be a list of rover steps with Step, Target, Task, and Notes. The user's example shows a clean markdown list with each step's details.

Let me double-check the risk application: The risk string says "N90", which matches step 7's target. So step 7's Notes are exactly that risk string. Steps 1-3 have no risks, so "none".

Everything checks out. The answer should be as written.
</think>

Rover Objectives:
- Step: 1, Target: N12, Task: subsurface sampling, Notes: none
- Step: 2, Target: N45, Task: subsurface sampling, Notes: none
- Step: 3, Target: N78, Task: subsurface sampling, Notes: none
- Step: 7, Target: N90, Task: radiation measurement, Notes: Rover energy constraints may delay N90 radiation measurement