**ID:**
TB-2

**Goal:**
Sort the samples in the stacked bar chart by corresponding data from a metadata column.

**Preconditions:**
- The sample metadata is available, i.e. was supplied to the visualization command.

**Postconditions:**
- The order of the individual bars in the stacked bar chart are in the order specified by the user's sort(s).
- The sorting metadata is stored by the system and displayed in the UI.

**Main success scenario:**
1. The user indicates that they want to sort by metadata.
2. The user selects which metadata column to sort by.
3. The user selects whether to sort in ascending or descending order.
4. The system performs the required sort and renders the stacked bar plot accordingly.
5. The system logs the sort's metadata and displays it in the UI.

**Extensions:**
1a. One or more other sorts have already been applied.
	1. The user indicates the priority of the new sort that will be applied.
	2. Returns to MSS step 2.
