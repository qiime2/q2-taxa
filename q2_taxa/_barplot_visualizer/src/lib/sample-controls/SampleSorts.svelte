<script lang="ts">
    import { onMount } from "svelte";
    import { sampleManager } from "../../classes/sampleManager.svelte";

    let sorts: string[] = $state([]);

    let sortColumn: string = $state("");
    let mdSortDirection: string = $state("");

    let sortTaxon: string = $state("");
    let abunSortDirection: string = $state("");

    let dragIndex: number | null = $state(null);

    // TODO: render hook
    let viewTaxaNames: string[] = $state([]);
    onMount(() => {
        viewTaxaNames = sampleManager
            .getAllViewTaxa()
            .map((vt) => vt.taxon.getFullTaxonomicString());
    });

    function handleAddMetadataSort(event: Event) {
        sampleManager.sampleControls.addMetadataSort(
            sortColumn,
            mdSortDirection == "ascending",
        );

        sortColumn = "";
        mdSortDirection = "ascending";

        sorts = sampleManager.sampleControls.sorts.map((s) => s.name);
        sampleManager.render();
    }
    function handleAddAbundanceSort(event: Event) {
        sampleManager.sampleControls.addAbundanceSort(
            sortTaxon,
            abunSortDirection == "",
        );

        sortTaxon = "";
        abunSortDirection = "";

        sorts = sampleManager.sampleControls.sorts.map((s) => s.name);
        sampleManager.render();
    }
    function handleRemoveSort(event: Event, sortName: string) {
        sampleManager.sampleControls.removeSort(sortName);
        sorts = sampleManager.sampleControls.sorts.map((s) => s.name);
        sampleManager.render();
    }

    function handleDragStart(event: DragEvent, index: number) {
        dragIndex = index;
        event.dataTransfer!.effectAllowed = "move";
    }
    function handleDragOver(event: DragEvent) {
        event.preventDefault();
        event.dataTransfer!.dropEffect = "move";
    }
    async function handleDragDrop(event: DragEvent, dropIndex: number) {
        event.preventDefault();

        if (dragIndex != null && dragIndex != dropIndex) {
            const updated = [...sorts];
            const [moved] = updated.splice(dragIndex, 1);
            updated.splice(dropIndex, 0, moved);
            sorts = updated;
        }

        dragIndex = null;

        sampleManager.sampleControls.updateSortOrder(sorts);
        setTimeout(() => {
            sampleManager.render();
        }, 10);
    }
</script>

<div class="grid auto-rows-min grid-cols-3 gap-2 w-[22em] pb-[0.75rem]">
    <p
        class="row-start-1 col-start-1 col-end-4 justify-self-center text-sm font-bold text-center"
    >
        Sort by Metadata
    </p>

    <label class="row-start-2 col-start-1 justify-self-end" for="sortColumn">
        Column:
    </label>
    <select
        class="row-start-2 col-start-2 select-primary"
        name="sortColumn"
        bind:value={sortColumn}
    >
        {#each sampleManager.sampleControls.metadata.getColumnNames() as name}
            <option value={name}>{name}</option>
        {/each}
    </select>

    <label class="row-start-3 col-start-1 justify-self-end" for="sortDirection">
        Direction:
    </label>
    <select
        class="row-start-3 col-start-2 select-primary w-[12rem]"
        name="sortDirection"
        bind:value={mdSortDirection}
    >
        <option value="ascending">ascending</option>
        <option value="descending">descending</option>
    </select>

    <button
        class="row-start-4 col-start-2 justify-self-center button-primary"
        onclick={handleAddMetadataSort}>Add</button
    >

    <p
        class="p-0 m-0 row-start-5 col-start-1 col-end-4 justify-self-center mt-4 text-sm font-bold leading-none text-center"
    >
        Sort by Taxon Abundance
    </p>

    <label class="row-start-6 col-start-1 justify-self-end" for="sortTaxon">
        Taxon:
    </label>
    <select
        class="row-start-6 col-start-2 select-primary w-[12rem]"
        name="sortTaxon"
        bind:value={sortTaxon}
    >
        {#each viewTaxaNames as name}
            <option value={name}>{name}</option>
        {/each}
    </select>
    <label
        class="row-start-7 col-start-1 justify-self-end"
        for="taxonDirection"
    >
        Direction:
    </label>
    <select
        class="row-start-7 col-start-2 select-primary w-[12rem]"
        name="taxonDirection"
        bind:value={abunSortDirection}
    >
        <option value="ascending">ascending</option>
        <option value="descending">descending</option>
    </select>
    <button
        class="row-start-8 col-start-2 justify-self-center button-primary"
        onclick={handleAddAbundanceSort}
    >
        Add
    </button>

    <p
        class="row-start-9 col-start-2 justify-self-center mt-4 text-sm font-bold"
    >
        Applied Sorts
    </p>
    <div
        class="row-start-10 col-start-1 col-end-4 justify-self-center w-[18rem] h-[7rem] bg-white border-2 border-gray-300 rounded-lg overflow-y-scroll"
    >
        <ul>
            {#each sorts as sort, index}
                <li
                    class="flex justify-between items-center mx-2 mt-1 p-2 bg-white border-2 border-gray-300 rounded-lg cursor-move"
                    draggable="true"
                    ondragstart={(e) => handleDragStart(e, index)}
                    ondragover={handleDragOver}
                    ondrop={(e) => handleDragDrop(e, index)}
                >
                    <p class="text-sm max-w-[15rem] truncate">{sort}</p>
                    <button
                        class="bg-red-400 rounded-lg w-6 h-6 hover:cursor-pointer"
                        onclick={(e) => handleRemoveSort(e, sort)}
                    >
                        X
                    </button>
                </li>
            {/each}
        </ul>
    </div>
</div>
