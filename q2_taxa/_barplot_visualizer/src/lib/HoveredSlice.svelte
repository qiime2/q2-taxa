<script lang="ts">
    import { sampleManager } from "../classes/sampleManager.svelte";

    sampleManager.eventBus.addEventListener("taxon-hovered", (e) => {
        const sampleID = (e as any).detail.sampleID;
        const viewTaxon = (e as any).detail.viewTaxon;

        sampleManager.hoveredSlice = { sampleID, viewTaxon };
    });
</script>

<div
    class="flex w-[42rem] h-[4.8rem] items-center bg-gray-100 rounded-lg p-[1rem] ml-[2rem] mt-[1rem]"
>
    <div class="flex flex-row items-center w-[16rem] truncate">
        <p class="font-bold text-sm mr-[1rem]">Sample Lables</p>
        <div class="flex flex-col">
            {#if sampleManager.hoveredSlice != null}
                {#each sampleManager.sampleControls.getSampleLabels(sampleManager.hoveredSlice.sampleID) as label}
                    <p class="text-sm">{label}</p>
                {/each}
            {/if}
        </div>
    </div>

    <div class="flex flex-col w-[12rem] ml-[2rem] truncate">
        <p class="font-bold text-sm">Classification</p>
        {#if sampleManager.hoveredSlice != null}
            <p class="text-sm">
                {sampleManager.hoveredSlice.viewTaxon.taxon.name}
            </p>
        {:else}
            <p class="text-sm">-</p>
        {/if}
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
</div>
