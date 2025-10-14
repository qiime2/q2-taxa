<script lang="ts">
    import { onMount } from "svelte";
    import { sampleManager } from "../../classes/sampleManager.svelte";

    let filters: string[] = $state([]);

    let categoricalForm = $state({ column: "", levels: [], filter: false });
    let numericForm = $state({ column: "", value: "", operator: "" });
    let taxonForm = $state({ taxonId: "", operator: "", value: "" });

    let categoricalColumnLevels: string[] = $derived(
        categoricalForm.column != ""
            ? sampleManager.sampleControls.metadata.getCategoricalColumnLevels(
                  categoricalForm.column,
              )
            : [],
    );

    // TODO: render hook
    let viewTaxaNames: string[] = $state([]);
    onMount(() => {
        viewTaxaNames = sampleManager
            .getAllViewTaxa()
            .map((vt) => vt.taxon.getFullTaxonomicString());
    });

    function clearForms() {
        categoricalForm = { column: "", levels: [], filter: false };
        numericForm = { column: "", value: "", operator: ">" };
        taxonForm = { taxonId: "", operator: "", value: "" };
    }

    function updateLocalFilters() {
        filters = sampleManager.sampleControls.filters.map((f) => f.name);
    }

    function handleAddCategoricalFilter(event: Event) {
        sampleManager.sampleControls.addCategoricalMetadataFilter(
            categoricalForm.column,
            categoricalForm.levels,
            !categoricalForm.filter,
        );

        clearForms();
        updateLocalFilters();
        sampleManager.render();
    }

    function handleAddNumericFilter(event: Event) {
        if (isNaN(Number(numericForm.value))) {
            alert("Please enter a valid number for 'value'.");
            clearForms();
            return;
        }

        sampleManager.sampleControls.addNumericMetadataFilter(
            numericForm.column,
            Number(numericForm.value),
            numericForm.operator as ">" | "<",
        );

        clearForms();
        updateLocalFilters();
        sampleManager.render();
    }

    function handleAddTaxonFilter(event: Event) {
        if (isNaN(Number(taxonForm.value))) {
            alert("Please enter a valid number for 'value'.");
            clearForms();
            return;
        }

        sampleManager.sampleControls.addAbundanceFilter(
            taxonForm.taxonId,
            Number(taxonForm.value),
            taxonForm.operator as ">" | "<",
        );

        clearForms();
        updateLocalFilters();
        sampleManager.render();
    }

    function handleRemoveFilter(name: string) {
        return (event: Event) => {
            sampleManager.sampleControls.removeFilter(name);
            updateLocalFilters();
            sampleManager.render();
        };
    }

    const categoricalColumns =
        sampleManager.sampleControls.metadata.getColumnNamesOfType(
            "categorical",
        );
    const numericColumns =
        sampleManager.sampleControls.metadata.getColumnNamesOfType("numeric");
</script>

<div class="grid auto-rows-min grid-cols-3 gap-2 w-[22rem] pb-[0.75rem]">
    <p class="row-start-1 col-start-1 col-end-4 widget-subheading">
        Add a Categorical Metadata Filter
    </p>

    <label class="row-start-2 col-start-1 justify-self-end" for="catColumn">
        Column:
    </label>
    <select
        class="row-start-2 col-start-2 select-primary"
        name="catColumn"
        bind:value={categoricalForm.column}
    >
        {#each categoricalColumns as name}
            <option value={name}>{name}</option>
        {/each}
    </select>

    <p class="row-start-3 col-start-1 col-end-4 widget-subheading">
        Column Levels
    </p>
    <div
        class="row-start-4 col-start-1 col-end-4 flex flex-col justify-self-center py-1 w-[18rem] h-[7rem] bg-white border-2 border-gray-300 rounded-sm overflow-y-scroll"
    >
        {#each categoricalColumnLevels as level}
            <div
                class="flex flex-row justify-between mx-2 my-1 p-2 bg-white border-2 border-gray-300 rounded-lg"
            >
                <label class="text-sm max-w-[15rem] truncate" for={level}>
                    {level}
                </label>
                <input
                    class="w-[1rem] h-[1rem] bg-gray-50 rounded-sm hover:cursor-pointer"
                    type="checkbox"
                    value={level}
                    name={level}
                    bind:group={categoricalForm.levels}
                />
            </div>
        {/each}
    </div>
    <label
        class="row-start-5 col-start-1 col-end-3 justify-self-center inline-flex items-center cursor-pointer"
    >
        <input
            type="checkbox"
            value=""
            class="sr-only peer"
            bind:checked={categoricalForm.filter}
        />
        <span class="mr-2 text-sm"> Retain </span>
        <div
            class={`
            relative w-[3rem] h-[1.4rem] bg-green-300 rounded-full peer peer-checked:after:translate-x-[1.5rem]
            rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-['']
            after:absolute after:top-[0.2rem] after:start-[0.25rem] after:bg-white
            after:rounded-full after:h-[1rem] after:w-[1rem] after:transition-all peer-checked:bg-red-400
            `}
        ></div>
        <span class="ml-2 text-sm"> Filter </span>
    </label>

    <button
        class="row-start-5 col-start-3 col-end-4 justify-self-start button-primary"
        onclick={handleAddCategoricalFilter}
    >
        Apply
    </button>

    <p class="row-start-6 col-start-1 col-end-4 widget-subheading">
        Add a Numeric Metadata Filter
    </p>

    <label class="row-start-7 col-start-1 justify-self-end" for="numColumn">
        Column:
    </label>
    <select
        class="row-start-7 col-start-2 select-primary"
        name="numColumn"
        bind:value={numericForm.column}
    >
        {#each numericColumns as name}
            <option value={name}>{name}</option>
        {/each}
    </select>

    <label class="row-start-8 col-start-1 justify-self-end" for="numOperator">
        Relationship:
    </label>
    <select
        class="row-start-8 col-start-2 select-primary"
        name="numOperator"
        bind:value={numericForm.operator}
    >
        <option value=">">Greater than</option>
        <option value="<">Less than</option>
    </select>

    <label class="row-start-9 col-start-1 justify-self-end" for="numValue">
        Value:
    </label>
    <input
        class="row-start-9 col-start-2 input-primary w-[12rem]"
        type="text"
        name="numValue"
        bind:value={numericForm.value}
    />

    <button
        class="row-start-10 col-start-1 col-end-4 justify-self-center button-primary"
        onclick={handleAddNumericFilter}
    >
        Apply
    </button>

    <p class="row-start-11 col-start-1 col-end-4 widget-subheading">
        Add a Taxon Abundance Filter
    </p>

    <label class="row-start-12 col-start-1 justify-self-end" for="taxon">
        Taxon:
    </label>
    <select
        class="row-start-12 col-start-2 select-primary"
        name="taxon"
        bind:value={taxonForm.taxonId}
    >
        {#each viewTaxaNames as name}
            <option value={name}>{name}</option>
        {/each}
    </select>

    <label
        class="row-start-13 col-start-1 justify-self-end"
        for="taxonOperator"
    >
        Relationship:
    </label>
    <select
        class="row-start-13 col-start-2 select-primary"
        name="taxonOperator"
        bind:value={taxonForm.operator}
    >
        <option value=">">Greater than</option>
        <option value="<">Less than</option>
    </select>

    <label class="row-start-14 col-start-1 justify-self-end" for="taxonValue">
        Value:
    </label>
    <input
        class="row-start-14 col-start-2 input-primary w-[12rem]"
        type="text"
        name="taxonValue"
        bind:value={taxonForm.value}
    />

    <button
        class="row-start-15 col-start-1 col-end-4 justify-self-center button-primary"
        onclick={handleAddTaxonFilter}
    >
        Apply
    </button>

    <p
        class="row-start-16 col-start-1 col-end-4 justify-self-center widget-subheading"
    >
        Applied Filters
    </p>
    <div
        class="row-start-17 col-start-1 col-end-4 w-[18rem] h-[7rem] justify-self-center bg-white border-2 border-gray-300 rounded-sm overflow-y-scroll"
    >
        {#each filters as filter}
            <div
                class="flex justify-between items-center mx-2 mt-1 p-2 min-h-8 bg-white border-2 border-gray-300 rounded-lg"
            >
                <p class="text-sm max-w-[15rem] truncate">
                    {filter}
                </p>
                <button
                    class="bg-red-400 rounded-lg w-6 h-6 hover:cursor-pointer"
                    onclick={handleRemoveFilter(filter)}>X</button
                >
            </div>
        {/each}
    </div>
</div>
