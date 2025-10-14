<script lang="ts">
    import { sampleManager } from "./../classes/sampleManager.svelte";
    import { Taxon } from "./../classes/taxonomy.svelte";

    function handleColorSchemeChange(event: Event) {
        sampleManager.render();
    }

    function handleRemoveColor(taxon: Taxon) {
        return (event: Event) => {
            sampleManager.colors.removeCustomColor(taxon);

            sampleManager.render();
        };
    }

    let show = $state(false);
</script>

<div
    class="grid rows-auto-min grid-cols-[40%_30%_30%] gap-x-[0.5rem] w-[22rem] h-[13rem] bg-gray-100 rounded-lg py-[0.75rem]"
>
    <label class="row-start-1 col-start-1 justify-self-end" for="colorScheme">
        Color Scheme:
    </label>
    <select
        class="row-start-1 col-start-2 select-primary w-[10rem]"
        name="colorScheme"
        bind:value={sampleManager.colors.colorScheme}
        onchange={handleColorSchemeChange}
    >
        {#each sampleManager.colors.getColorSchemeNames() as scheme}
            <option value={scheme}>{scheme}</option>
        {/each}
    </select>
    <p class="row-start-2 col-start-1 col-end-4 widget-subheading">
        Applied Custom Colors
    </p>
    <div
        class="row-start-3 col-start-1 col-end-4 w-[18rem] h-[7rem]
        justify-self-center bg-white border-2 border-gray-300 rounded-sm
        overflow-scroll"
    >
        {#each sampleManager.colors.customColors.entries() as [taxon, color]}
            <div
                class="flex justify-between items-center mx-2 mt-1 p-2 min-h-8 bg-white border-2 border-gray-300 rounded-lg"
            >
                <div class="flex flex-around items-center">
                    <p class="text-sm mr-[0.75rem]">
                        {taxon.name}
                    </p>
                    <span
                        class="w-[1.5rem] h-[1.5rem] rounded-sm"
                        style={`background-color: ${color}`}
                    ></span>
                </div>
                <button
                    class="bg-red-400 justify-self-end rounded-md w-[1.5rem] h-[1.5rem] hover:cursor-pointer"
                    onclick={handleRemoveColor(taxon)}>X</button
                >
            </div>
        {/each}
    </div>
</div>
