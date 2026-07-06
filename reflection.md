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
My scheduler considers time, priority, 
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
