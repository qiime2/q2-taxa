# Requirements

## Functional Requirements

**ID:** TBR-01
**Title:** Display per sample feature counts
**Description:** The system shall display the total feature count of each sample in the stacked bar chart.
**Rationale:** This gives additional context when one sample has only one or few taxa present in the stacked bar.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-02
**Title:** Custom taxon coloring
**Description:** The system shall allow each taxon (i.e. each rectangle in each stacked bar) to be colored with a color of choice that is specifiable within the UI.
**Rationale:** This allows taxa of interest to be highlighted.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-03
**Title:** Clade-aware taxon coloring
**Description:** The system should allow the taxa at the displayed taxonomic depth to be colored with reference to their higher level taxonomic groupings. For example, when displaying genera, all genera belonging to one family may be colored in different opacities of red, while all genera belonging to another family may be colored in different opacities of blue, and so on. The higher level taxonomic group determines the color and the specific taxon determines the opacity of the color. The system should allow the level that defines the higher level groupings to be specifiable within the UI.
**Rationale:** Similar colors that differ only in opacity allow the user to visually recognize phylogenetic groupings. The number of colors needed to unqiuely identify the set of taxa at a higher taxonomic level will usually be much less than the number of colors needed to unqiuely identify the set of taxa at a lower level, leading to a less overwhelming number of colors in the stacked bar plot.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-04
**Title:** Metadata-based sample filtering
**Description:** The system should allow users to filter the set of samples displayed in the stacked bar chart according to corresponding data in the metadata. Categorical metadata columns should have an include/exclude option for each level in the column. Numerical metadata columns should have the option
to filter or retain values that are less than or greater than a specifiable value. Additionally, these filters should be logged in and removable through the UI.
**Rationale:** This functionality will make common exploratory workflows performable in real time within the visualization. Without this function, similar operations are possible only by using dedicated qiime2 actions.
**Dependencies:**
    - Each metadata filter should create a new sample label as described in **TBR-08**.
**Source:** Github issue.

**ID:** TBR-05
**Title:** Abundance-based filtering
**Description:** The system shall allow the taxa displayed in the stacked bar to be filterable by absolute and relative abundance within each sample. The system shall display any applied filters in the UI and allow them to be removed.
**Rationale:** Taxa that fall beneath an abundance threshold may not be of concern and thus should not clutter the stacked bar chart. Alternatively, highly abundant taxa may not be of concern (e.g. because their presence is common and uninteresting) and thus should be removable to allow the lower
abundance taxa to become visible.
**Dependencies:**
    - Once abundance filters have been perfomed the axis adjustment options described in **TBR-06** become applicable.
**Source:** Github issue.

**ID:** TBR-06
**Title:** Y-axis scale readjustment and rectangle repositioning
**Description:** The system shall allow the relative abundance axis of the stacked bar chart to be displayed in the following ways after taxon filtering has been performed. By default, the filtered taxa will cease to be displayed in each stacked bar and the axis will continue to exend from 0% to 100% relative abundance, with a certain amount of empty space present in each stacked bar. The remaining taxon rectangles shall be positioned such that they are all contiguous and all empty space resides at the top of the stacked bar. Alternatively a user shall be able to renormalize each sample such that the scale continues to extend from 0% to 100% relative abundance, but with the relative abundances of the remaining taxa recomputed to sum to 100%--in this case there will be no empty space in the stacked bars.
**Rationale:** After filtering taxa from each sample the space that the filtered taxa occupied is wasted. Renormalizing allows this wasted space to be refilled, and the remaining taxa to be visualized more clearly.
**Dependencies:**
    - The scale adjustment options listed here are only applicable if taxon filtering as described in **TBR-05** has been performed.
**Source:** Github issue, Colin Wood.

**ID:** TBR-07
**Title:** Custom sample labels
**Description:** The system shall allow the x-axis labels of each sample to be set manually to text that the user can specify within the UI.
**Rationale:** This allows user to keep track of certain samples of interest when samples are sorted. This also allows final touches to be made before exporting the stacked bar chart figure.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-08
**Title:** Multiple sample labels
**Description:** The system should allow each sample in the stacked bar chart to be labeled with any number of corresponding values from the metadata.
**Rationale:** This allows a user to spot trends that involve multiple metadata values.
**Dependencies:**
    - Any metadata filter created as described in **TBR-04** should be added automatically as an additional sample label.
**Source:** Github issue.

**ID:** TBR-09
**Title:** Taxon sorting
**Description:** The system shall allow the taxa in each stacked bar chart to be sorted in the following ways: alphabetically, by mean absolute abundance, by mean relative abundance, and by prevalence. The system shall allow each of these sorts to be applied in either ascending or descending order. The system shall present the taxon legend, which displays the name of each taxon and its color in the stacked bar chart, in the order enforced by the sort. The system shall use the mean relative abundance (descending) sort by default.
**Rationale:** The abundance and prevalence sorts highlight taxa with the highest and lowest values of these criteria by placing them towards the top or bottom of the stacked bars. Alphabetic sorting allows the user to find taxa of interest by using a dictionary-like visual scan.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-10
**Title:** Figure exporting
**Description:** The system shall allow the stacked bar chart be exported as an .svg, .png, or .jpeg file. The exported figure shall contain the stacked bar chart, the axes, and optionally the legend. The user shall be able to specify the filename before exporting.
**Rationale:** This allows the user to save the stacked bar chart for future reference, for publication, and so on.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-11
**Title:** Taxonomic collapsing (grouping)
**Description:** The system should allow users to collapse related taxa to an ancestor taxon. For example, when viewing the stacked bar chart at the genus level the user may wish to collapse all genera in a certain family to that family, so that a rectangle representing the family is drawn in place of the separate genera rectangles. Groups should not be restricted to parents, but should be allowed to be any ancestor taxon.
**Rationale:** This allows the user to achieve the advantages of visualizing at higher taxonomic levels (decreased clutter) and the advantages of visualizing at lower taxonomic levels (increased resolution & information) simultaneously.
**Dependencies:**
    - The expansion feature discussed in **TBR-12** will likely be similar in implementation.
**Source:** Github issue, Colin Wood.

**ID:** TBR-12
**Title:** Taxonomic expansion
**Description:** The system should allow users to exapand a taxon at a given level to a set of descendant taxa in the stacked bar chart. For example, when viewing the stacked bar chart at the family level, the user may wish to expand all the genera in a given family, so that one or more rectangles representing the genera descendants of the family are drawn in place of the parent family.
**Rationale:** This allows the user to achieve the advantages of visualizing at higher taxonomic levels (decreased clutter) and the advantages of visualizing at lower taxonomic levels (increased resolution & information) simultaneously.
**Dependencies:**
    - The collapsing feature discussed in **TBR-11** will likely be similar in implementation.
**Source:** Colin Wood.

**ID:** TBR-13
**Title:** Taxon selection
**Description:** The system shall allow individual taxa to be selected and deselected in the taxa legend with the following behavior. If one or more taxa are selected, only these taxa are displayed in the stacked bar chart. The system shall have select all and unselect all features.
**Rationale:** This allows the user to visualize only taxa of interest.
**Dependencies:**
    - When this functionality changes the number of taxa that are displayed in the stacked bar chart, the y-axis may need to be readjusted as explained in **TBR-06**.
**Source:** Github issue.

**ID:** TBR-14
**Title:** Taxon information table
**Description:** The system shall allow the user to click on any rectangle in the stacked bar chart and display a corresponding set of information about the selected taxon including the full taxonomy string of the taxon, its relative and absolute abundance in the sample in which it was selected, the mean relative and absolute abundance across all samples, and its prevalence across all samples.
**Rationale:** This allows the user to gain useful information about taxa of interest.
**Dependencies:** None.
**Source:** Github issue.

**ID:** TBR-15
**Title:** Persisting custom settings
**Description:** The system shall to the extent possible persist all previously applied settings (sample sorting, taxon filtering, etc.) when changing a new setting. For example, if the user changes the stacked bar chart from the genus level to the family level any sample sorts, custom sample labels, and taxon abundance filters should continue to apply.
**Rationale:** This reduces the amount of work the user must perform when making changes to the UI settings that would otherwise reset previously applied settings.
**Dependencies:** None.
**Source:** Github issue.
