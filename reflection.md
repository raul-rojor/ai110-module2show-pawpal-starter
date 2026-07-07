# PawPal+ Project Reflection

## 1. System Design

My app should allow users to add pets, detail their own personal schedule (the user's schedule), describe their pet-caring preferences and their pets' preferences, and view their optimized pet-caring schedule.

BRAINSTORMING OBJECTS:

Class   |       Attributes          |       Methods         |
Pet | Species, ideal weight, weight, pet's preferences | init, update weight, update preferences |
User | pets, user schedule, pet-caring preferences, pet-caring schedule | init, add pet, remove pet, update schedule, update pet-caring preferences |
User schedule | time-specific activites | init, remove activity, add activity |
Pet-caring schedule | user | init
Preferences | walking amount, walking time(s), feeding amount, feeding times | init, update walking amount, update walking time(s), update feeding amount, update feeding times |

**a. Initial design**

- Briefly describe your initial UML design.
My initital UML design includes 5 classes. The User class has a list of Pet objects, a UserSchedule object, a Preferences object, and a PetCaringSchedule object. The Pet class exists to instantiate Pet objects which are owned by a User object and each Pet also has a Preferences object. The UserSchedule class and the PetCaringSchedule exist for User objects to each have one instance of each of the two classes. The Preferences class exists for User and Pet objects to each have a Preferences object.
- What classes did you include, and what responsibilities did you assign to each?
I included User, Pet, UserSchedule, PetCaringSchedule, Activity, and Preferences classes. The Pet class holds one pet's data and allows updates to their weight and preferences, the User class owns pets and has personal and pet-caring schedules, the Preferences class stores the walking and pet feeding habits preferred by their owning object (user or pet), the Activity class represents one schedule entry, the UserSchedule class holds the owning user's personal schedule, and the PetCaringSchedule holds the user's pet-caring schedule.

**b. Design changes**

- Did your design change during implementation?
Yes, my design changed after recieving AI feedback.
- If yes, describe at least one change and why you made it.
The classes were changed to only these four classes -- Owner, Pet, Task, and Scheduler. The reason for this change is because the instructions at this point of the project now specify to use these particular classes, so my AI assistant had to adjust the logic to these classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considers time, priority, and owner preferences.
- How did you decide which constraints mattered most?
I looked at the instructions to decide which constraints mattered most and I also asked AI for potential practical additions to the app.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My scheduler does not automatically fix task time conflicts or tasks not matching owner preferences; it only points out conflicts while giving the user the judgement to alter their schedule.
- Why is that tradeoff reasonable for this scenario?
Giving the owner greater autonomy by not automatically changing tasks according to time or preference conflicts makes it so that users are not alienated from their pet schedule and are instead actively creating it using the app's tools.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude Code integrated into VS Code in order to design coding logic, to design code for the UI, and to test the newly implemented logic and UI changes across possible cases.
- What kinds of prompts or questions were most helpful?
The most helpful prompts in my AI-assisted coding process were the 'design this coding logic' prompts that referenced exactly where to implement changes, detailed what the changes should add to the program, and provided the locations of relevant code and context.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
At one point, Claude Code suggested implementing 'do-not-disturb' and 'available' time periods for the user to input in the 'User preferences' section. I instead opted for the user to input their preferred time period for particular tasks as this option already implies availability while offering specificity of tasks to the user's preferences. 
- How did you evaluate or verify what the AI suggested?
I evaluated AI suggestions by opening a second AI agent tab and pasting the suggestions as prompts while asking the second agent to review the instructions and the purpose of the program to judge how well the suggestion matches the goals of the app.
I then manually judged this evaluation and made my own decisions for the program accordingly.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested the flipping of task completion statuses, sorting correctness, recurrence logic, conflict detection, the use of preferences, and scheduling and filtering logic.
- Why were these tests important?
These tests were highly important because they ensure that the core logic off the app is sound and that further layers (such as UI) can be built around it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am very confident that the scheduler works correctly; I would use the app myself if I owned pets.
- What edge cases would you test next if you had more time?
With more time, I would test the actual Streamlit display with systemic tests. Currently, I test the display manually and unsystematically.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the simplicity of the UI and intuitive presentation of the program to the user. The app is very straightforward and lets the user maintain control over their schedule while meaningfully organizing their constraints.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would improve the schedule maker by having an 'Import your current personal schedule' option that would allow users to work around their personal schedule more easily by having it be viewable within the app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned while designing this project is that it is important to consider the implications of changes in one file in all other files. Changing one file can often mean that unexpected parts of code in other files also require reworking or at least comments.