<script lang="ts">
    import { sampleManager } from "../classes/sampleManager.svelte";

    sampleManager.eventBus.addEventListener("taxon-hovered", (e) => {
        const sampleID = (e as any).detail.sampleID;
        const viewTaxon = (e as any).detail.viewTaxon;

        sampleManager.hoveredSlice = { sampleID, viewTaxon };
    });
</script>

<div
    class="flex w-[59rem] h-[4.8rem] items-center bg-gray-100 rounded-lg p-[1rem] ml-[2rem] mt-[1rem]"
>
    <div class="flex flex-row items-center w-[18rem]">
        <p class="font-bold text-sm mr-[1rem] flex-shrink-0">Sample</p>
        <div class="flex flex-col min-w-0">
            {#if sampleManager.hoveredSlice != null}
                {#each Object.entries(sampleManager.sampleControls.getSampleLabels(sampleManager.hoveredSlice.sampleID)) as [label, value]}
                    <p class="text-sm truncate">{label}: {value}</p>
                {/each}
            {/if}
        </div>
    </div>

    <div class="flex flex-col w-[6rem] ml-[2rem]">
        <p class="font-bold text-sm">Abundance</p>
        {#if sampleManager.hoveredSlice != null}
            <p class="text-sm">
                {sampleManager.hoveredSlice.viewTaxon.relAbun.toFixed(4)}
            </p>
        {:else}
            <p class="text-sm">-</p>
        {/if}
    </div>

    <div class="flex flex-row items-center w-[28rem] ml-[2rem]">
        <p class="font-bold text-sm mr-[1rem]">Classification</p>
        {#if sampleManager.hoveredSlice != null}
            {#if sampleManager.taxonomy.displayLevel > 1}
                <p class="text-sm line-clamp-3 break-words">
                    {sampleManager.hoveredSlice.viewTaxon.taxon
                        .getFullTaxonomicString()
                        .slice(5)}
                </p>
            {:else}
                <p class="text-sm line-clamp-3 break-words">root</p>
            {/if}
        {/if}
    </div>
</div>
