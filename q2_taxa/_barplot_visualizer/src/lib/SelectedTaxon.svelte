<script lang="ts">
    import { sampleManager } from "./../classes/sampleManager.svelte";

    sampleManager.eventBus.addEventListener("taxon-selected", (e) => {
        const viewTaxon = (e as any).detail.viewTaxon;
        sampleManager.selectedTaxon = viewTaxon;
    });

    function handleFilter(event: Event) {
        if (sampleManager.selectedTaxon == null) {
            return;
        }

        if (sampleManager.selectedTaxon.taxon.filtered) {
            sampleManager.featureControls.addTaxonFilter(
                sampleManager.selectedTaxon.taxon,
            );
            sampleManager.selectedTaxon.taxon.filtered = true;
        } else {
            sampleManager.featureControls.removeFilter(
                sampleManager.selectedTaxon.taxon.name,
            );
            sampleManager.selectedTaxon.taxon.filtered = false;
        }

        sampleManager.render();
    }

    function handleColorChange(event: Event) {
        const oldColor = sampleManager.colors.getTaxonColor(
            sampleManager.selectedTaxon!.taxon,
        );

        const newColor = (event.target as HTMLInputElement).value;

        if (oldColor!.toLowerCase() == newColor.toLowerCase()) {
            return;
        }

        sampleManager.colors.addCustomColor(
            sampleManager.selectedTaxon!.taxon,
            newColor,
        );

        sampleManager.render();
    }

    function handleExpansion(event: Event) {
        const selectedTaxonDepth =
            sampleManager.selectedTaxon!.taxon.getLevel();
        const maxDepth = sampleManager.taxonomy.getDepth();

        let expandToValue = Number(sampleManager.selectedTaxon!.taxon.expandTo);

        if (expandToValue == 0) {
            // empty input acts as reset
            sampleManager.selectedTaxon!.taxon.expandTo = null;
            sampleManager.taxonomy.expansions.delete(
                sampleManager.selectedTaxon!.taxon,
            );
            sampleManager.render();
            return;
        }

        if (isNaN(expandToValue)) {
            sampleManager.selectedTaxon!.taxon.expandTo = null;
            alert("Please enter a number for the expand-to level.");
            return;
        }

        if (expandToValue <= selectedTaxonDepth || expandToValue > maxDepth) {
            sampleManager.selectedTaxon!.taxon.expandTo = null;
            alert(
                `Level must be between ${selectedTaxonDepth + 1} and ${maxDepth}`,
            );
            return;
        }

        sampleManager.selectedTaxon!.taxon.expandTo = expandToValue;
        sampleManager.taxonomy.expansions.add(
            sampleManager.selectedTaxon!.taxon,
        );
        sampleManager.render();
    }
</script>

<div
    class="grid rows-auto-min grid-cols-[30%_70%] gap-x-[0.5rem] w-[22rem] h-[16rem] bg-gray-100 rounded-lg"
>
    <p class="row-start-2 col-start-1 justify-self-end">Name:</p>
    <p class="row-start-2 col-start-2 justify-self-start w-[14rem] truncate">
        {#if sampleManager.selectedTaxon}
            {sampleManager.selectedTaxon.taxon.name}
        {/if}
    </p>
    <p class="row-start-3 col-start-1 justify-self-end">Mean Abun:</p>
    <p class="row-start-3 col-start-2 justify-self-start">
        {#if sampleManager.selectedTaxon}
            {sampleManager.selectedTaxon.meanRelAbun.toFixed(3)}
        {/if}
    </p>
    <p class="row-start-4 col-start-1 justify-self-end">Prevalence:</p>
    <p class="row-start-4 col-start-2 justify-self-start">
        {#if sampleManager.selectedTaxon}
            {`${sampleManager.selectedTaxon.preval.toString()}
            (${sampleManager.selectedTaxon.prevalProp.toFixed(3)})`}
        {/if}
    </p>
    <p class="row-start-5 col-start-1 justify-self-end">Color:</p>
    {#if sampleManager.selectedTaxon != null}
        <input
            class="row-start-5 col-start-2 w-[1.5rem] h-[1.5rem] rounded-md border-2 border-gray-300 hover:cursor-pointer"
            type="color"
            bind:value={sampleManager.selectedTaxon.taxon.color}
            onchange={handleColorChange}
        />
    {/if}
    <p class="row-start-6 col-start-1 justify-self-end">Filter:</p>
    {#if sampleManager.selectedTaxon != null}
        <input
            class="row-start-6 col-start-2 justify-self-start checkbox-primary mt-[0.2rem]"
            type="checkbox"
            bind:checked={sampleManager.selectedTaxon.taxon.filtered}
            onchange={handleFilter}
        />
    {/if}
    <p class="row-start-7 col-start-1 justify-self-end">Level:</p>
    {#if sampleManager.selectedTaxon != null}
        <p class="row-start-7 col-start-2 text-md font-bold">
            {sampleManager.selectedTaxon.taxon.getLevel()}
        </p>
    {/if}
    <p class="row-start-8 col-start-1 justify-self-end">Expand to:</p>
    {#if sampleManager.selectedTaxon != null}
        <div class="row-start-8 col-start-2 flex">
            <input
                class="input-primary w-[4rem] mr-[0.75rem]"
                type="text"
                bind:value={sampleManager.selectedTaxon.taxon.expandTo}
            />
            <button
                class="button-primary mt-[-0.1rem]"
                onclick={handleExpansion}
            >
                Apply
            </button>
        </div>
    {/if}
</div>
