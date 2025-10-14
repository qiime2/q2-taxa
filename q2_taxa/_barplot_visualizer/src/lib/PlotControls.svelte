<script lang="ts">
    import { sampleManager } from "../classes/sampleManager.svelte";

    let displayLevel: number = $state(1);
    let dynamicAxis: boolean = $state(false);
    let showFiltered: boolean = $state(false);

    let levels: number[] = $state([]);
    for (let i = 1; i <= sampleManager.taxonomy.getDepth(); i++) {
        levels.push(i);
    }

    function handleDisplayLevelChange(event: Event) {
        sampleManager.taxonomy.displayLevel = displayLevel;
        sampleManager.render();
    }

    function decreaseBarWidth() {
        sampleManager.plot.dims.barWidth *= 0.9;
        sampleManager.render();
    }
    function increaseBarWidth() {
        sampleManager.plot.dims.barWidth *= 1.1;
        sampleManager.render();
    }

    function handleDynamicAxisChange() {
        sampleManager.plot.dynamicAxis = dynamicAxis;

        if (dynamicAxis && showFiltered) {
            sampleManager.plot.showFiltered = false;
            showFiltered = false;
        }

        sampleManager.render();
    }

    function handleShowFilteredChange() {
        sampleManager.plot.showFiltered = showFiltered;

        if (showFiltered && dynamicAxis) {
            sampleManager.plot.dynamicAxis = false;
            dynamicAxis = false;
        }

        sampleManager.render();
    }
</script>

<div class="flex w-fit items-center py-[1rem] bg-gray-100 rounded-lg">
    <label class="ml-[1rem] mr-[0.5rem]" for="displayLevel">
        Display Level:
    </label>
    <select
        class="select-primary w-[4rem] mr-[1rem]"
        name="displayLevel"
        bind:value={displayLevel}
        onchange={handleDisplayLevelChange}
    >
        {#each levels as level}
            <option value={level}>{level}</option>
        {/each}
    </select>

    <p class="mr-[0.5rem]">Bar Width:</p>
    <div class="flex items-center mr-[1rem]">
        <button
            class="flex items-center justify-center w-[1.9rem] h-[1.9rem]! mr-[0.5rem] button-primary"
            onclick={decreaseBarWidth}
        >
            -
        </button>
        <button
            class="flex items-center justify-center w-[1.9rem] h-[1.9rem]! button-primary"
            onclick={increaseBarWidth}
        >
            +
        </button>
    </div>

    <label class="mr-[0.5rem]" for="dynamicAxis"> Dynamic Y-axis: </label>
    <input
        class="checkbox-primary mr-[1rem]"
        name="dynamicAxis"
        type="checkbox"
        bind:checked={dynamicAxis}
        onchange={handleDynamicAxisChange}
    />

    <label class="mr-[0.5rem]" for="showFiltered"> Show Filtered: </label>
    <input
        class="checkbox-primary mr-[1rem]"
        name="showFiltered"
        type="checkbox"
        bind:checked={showFiltered}
        onchange={handleShowFilteredChange}
    />

    <button
        class="button-primary mr-[1rem]"
        onclick={sampleManager.plot.downloadSVG}
    >
        Download SVG
    </button>
    <button
        class="button-primary mr-[1rem]"
        onclick={sampleManager.plot.downloadPNG}
    >
        Download PNG
    </button>
</div>
