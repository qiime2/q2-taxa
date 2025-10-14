<script lang="ts">
    import { sampleManager } from "../classes/sampleManager.svelte";
    import { ViewTaxon } from "../classes/taxonomy.svelte";

    let legendRecords = $derived.by(() => {
        return sampleManager.colors.getLegendData(
            sampleManager,
            sampleManager.colors.assignedColors,
            sampleManager.colors.customColors,
        );
    });

    function handleLegendClick(viewTaxon: ViewTaxon) {
        return () => {
            sampleManager.selectedTaxon = viewTaxon;
        };
    }
</script>

<div
    class="flex flex-col items-center w-[20rem] h-[35rem] overflow-y-scroll bg-gray-100 rounded-lg mt-[25px] py-[0.6rem]"
>
    {#each legendRecords as legendRecord}
        <div
            class="flex w-[18rem] bg-white rounded-lg hover:cursor-pointer mb-[0.5rem] p-[0.35rem]"
            onclick={handleLegendClick(legendRecord[0])}
            role="button"
            tabindex="0"
            onkeydown={() => {}}
        >
            <div
                class="w-[1.5rem] h-[1.5rem] rounded-md mr-[0.5rem]"
                style="background-color: {legendRecord[1]};"
            ></div>
            <p class="w-[16rem] truncate">{legendRecord[0].taxon.name}</p>
        </div>
    {/each}
</div>
