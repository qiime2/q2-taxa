**ID:**
TB-4

**Goal:**
The user wants to remove a previously specified sort.

**Preconditions:**
- One or more sorts have been applied by the user.

**Postconditions:**
- The order of the samples in the stacked bar chart does not take the removed sort into account.
- The sort's metadata is not present in the system state, and the UI does not display the sort.

**Main success scenario:**
1. The user indicates the sort that they wish to remove by selecting it.
2. The system removes the sort from its state.
3. The system resorts the samples in the stacked bar chart according to any remaining sorts or the default sort if no sorts remain.
4. The system removes the sort metadata from the list of applied sorts in the UI.
