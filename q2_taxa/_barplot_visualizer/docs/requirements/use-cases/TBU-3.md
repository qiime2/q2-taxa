**ID:**
TB-3

**Goal:**
Sort the samples in the stacked bar chart by absolute abundance or relative abundance of a specific taxon.

**Preconditions:**
None

**Postconditions:**
- The order of the individual bars in the stacked bar chart are in the order specified by the user's sort(s).
- The sorting metadata is stored by the system and displayed in the UI.

**Main success scenario:**
1. The user indicates that they wish to sort by taxonomic abundance.
2. The user chooses whether the wish to sort by absolute or relative abundance.
3. The user indicates the taxon that will determine the sorting by choosing it from a drop-down list.
4. The user indicates whether to sort in ascending or descending order of taxonomic abundance.
5. The system performs the sorting and renders the sorted stacked bar chart.
6. The system logs the sort's metadata and displays it in the UI.

**Extensions:**
1a. One or more other sorts have already been applied.
	1. The user indicates the priority of the new sort that will be applied.
	2. Returns to MSS step 2.

2a. The user has provided a relative abundance feature table.
	1. The option for absolute abundance filtering is not available; the user must select the relative abundance filter.
	2. Returns to MSS step 3.

3a. The user wishes to search for the taxon of interest by typing or the list of total taxa to choose from is greater than one hundred.
	1. The user searches for the taxon of interest by typing the taxon's name.
	2. The system displays a list of the taxa that match the name entered by the user.
	3. The user selects the taxon of interest from this list.
	4. Returns to MSS step 4.
