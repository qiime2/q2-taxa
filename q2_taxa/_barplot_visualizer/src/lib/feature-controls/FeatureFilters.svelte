<script lang="ts">
    import { sampleManager } from "../../classes/sampleManager.svelte";
    import { Taxon } from "../../classes/taxonomy.svelte";

    let form = $state({ type: "", operator: "", value: "" });

    function handleAddFilter(event: Event) {
        if (isNaN(Number(form.value))) {
            alert("Please enter a number for filter value.");
            return;
        }

        // apply filter
        if (form.type == "relAbun") {
            sampleManager.featureControls.addAbundanceFilter(
                Number(form.value),
                form.operator as ">" | "<",
            );
        } else if (form.type == "prevalAbs") {
            sampleManager.featureControls.addPrevalenceFilter(
                Number(form.value),
                "absolute",
                form.operator as ">" | "<",
            );
        } else if (form.type == "prevalProp") {
            sampleManager.featureControls.addPrevalenceFilter(
                Number(form.value),
                "proportion",
                form.operator as ">" | "<",
            );
        }

        form = { type: "", value: "", operator: "" };

        sampleManager.render();
    }

    function handleRemoveFilter(name: string) {
        return (event: Event) => {
            sampleManager.featureControls.removeFilter(name);
            sampleManager.render();
        };
    }
    function handleRemoveExpansion(taxon: Taxon) {
        return (event: Event) => {
            taxon.expandTo = null;
            sampleManager.taxonomy.expansions.delete(taxon);
            sampleManager.render();
        };
    }
</script>

<div
    class="grid grid-cols-3 rows-auto-min gap-x-[0.5rem] w-[22rem] h-[26rem] bg-gray-100 rounded-lg"
>
    <label class="row-start-1 col-start-1 justify-self-end" for="filterType">
        Type:
    </label>
    <select
        class="row-start-1 col-start-2 select-primary w-[12rem]"
        name="filterType"
        bind:value={form.type}
    >
        <option value="relAbun">Relative Abundance</option>
        <option value="prevalAbs">Prevalence (number)</option>
        <option value="prevalProp">Prevalence (proportion)</option>
    </select>

    <label
        class="row-start-2 col-start-1 justify-self-end"
        for="filterOperator"
    >
        Relationship:
    </label>
    <select
        class="row-start-2 col-start-2 select-primary w-[12rem]"
        name="filterOperator"
        bind:value={form.operator}
    >
        <option value=">">Greater than</option>
        <option value="<">Less than</option>
    </select>

    <label class="row-start-3 col-start-1 justify-self-end" for="filterValue">
        Value:
    </label>
    <div class="row-start-3 col-start-2 flex">
        <input
            class="input-primary w-[6rem]"
            type="text"
            name="filterValue"
            bind:value={form.value}
        />
        <button
            class="row-start-4 col-start-2 mx-4 button-primary mt-[-0.1rem]"
            onclick={handleAddFilter}
        >
            Add
        </button>
    </div>
    <p class="row-start-5 col-start-2 justify-self-center widget-subheading">
        Applied Filters
    </p>
    <div
        class="row-start-6 col-start-1 col-end-4 w-[18rem] h-[7rem] justify-self-center bg-white border-2 border-gray-300 rounded-sm overflow-scroll"
    >
        {#each sampleManager.featureControls.filters as filter}
            <div
                class="flex justify-between items-center mx-2 mt-1 p-2 min-h-8 bg-white border-2 border-gray-300 rounded-lg"
            >
                <p class="text-sm">
                    {filter.name}
                </p>
                <button
                    class="bg-red-400 rounded-lg w-6 h-6 hover:cursor-pointer"
                    onclick={handleRemoveFilter(filter.name)}>X</button
                >
            </div>
        {/each}
    </div>
    <p
        class="row-start-7 col-start-1 col-end-4 justify-self-center widget-subheading"
    >
        Applied Expansions
    </p>
    <div
        class="row-start-8 col-start-1 col-end-4 w-[18rem] h-[7rem] justify-self-center bg-white border-2 border-gray-300 rounded-sm overflow-scroll"
    >
        {#each sampleManager.taxonomy.expansions as taxon}
            <div
                class="flex justify-between items-center mx-2 mt-1 p-2 min-h-8 bg-white border-2 border-gray-300 rounded-lg"
            >
                <p class="text-sm">
                    {taxon.name}
                    {"->"}
                    {taxon.expandTo}
                </p>
                <button
                    class="bg-red-400 rounded-lg w-6 h-6 hover:cursor-pointer"
                    onclick={handleRemoveExpansion(taxon)}>X</button
                >
            </div>
        {/each}
    </div>
</div>
