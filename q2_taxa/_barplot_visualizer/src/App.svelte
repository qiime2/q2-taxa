<script lang="ts">
    import Hideable from "./lib/Hideable.svelte";
    import Plot from "./lib/Plot.svelte";
    import PlotControls from "./lib/PlotControls.svelte";
    import Legend from "./lib/Legend.svelte";
    import FeatureSort from "./lib/feature-controls/FeatureSort.svelte";
    import FeatureFilters from "./lib/feature-controls/FeatureFilters.svelte";
    import SampleSorts from "./lib/sample-controls/SampleSorts.svelte";
    import SampleFilters from "./lib/sample-controls/SampleFilters.svelte";
    import SampleLabels from "./lib/sample-controls/SampleLabels.svelte";
    import SelectedTaxon from "./lib/SelectedTaxon.svelte";
    import HoveredSlice from "./lib/HoveredSlice.svelte";
    import ColorControls from "./lib/ColorControls.svelte";
    import { sampleManager } from "./classes/sampleManager.svelte";

    const smPromise = sampleManager.parseFeatureTable("table.csv");

    const parsedPromise = smPromise.then((r) => {
        const tPromise = sampleManager.taxonomy.parse("taxonomy.csv");
        const mdPromise =
            sampleManager.sampleControls.metadata.parse("metadata.csv");
        const cPromise = sampleManager.colors.parse("colors.csv");

        return Promise.all([tPromise, mdPromise, cPromise]);
    });

    let showTaxaControls = $state(false);
    let showSampleControls = $state(false);
</script>

{#await parsedPromise}
    <p>Loading...</p>
{:then}
    <div class="grid grid-cols-4 gap-x-[2rem] w-[95%] p-[1rem]">
        <div class="col-start-1 col-end-5">
            <PlotControls />
        </div>
        <div class="col-start-1 col-end-5">
            <HoveredSlice />
        </div>
        <div class="col-start-1 col-end-4">
            <Plot />
        </div>
        <div class="col-start-4 col-end-5">
            <Legend />
        </div>
    </div>
    <div class="grid grid-cols-3 w-[68rem] gap-x-[1rem] ml-[2rem] pb-[2rem]">
        <div
            class="col-start-1 col-end-2 flex flex-col gap-[0.5rem] mr-[0.5rem]"
        >
            <Hideable title="Selected Taxon">
                <SelectedTaxon />
            </Hideable>
            <Hideable title="Color Controls">
                <ColorControls />
            </Hideable>
        </div>
        <div
            class="col-start-2 col-end-3 flex flex-col gap-[0.5rem] mr-[0.5rem]"
        >
            <Hideable title="Sort Taxa">
                <FeatureSort />
            </Hideable>
            <Hideable title="Filter Taxa">
                <FeatureFilters />
            </Hideable>
        </div>
        <div class="col-start-3 col-end-4 flex flex-col gap-[0.5rem]">
            <Hideable title="Sort Samples">
                <SampleSorts />
            </Hideable>
            <Hideable title="Filter Samples">
                <SampleFilters />
            </Hideable>
            <Hideable title="Label Samples">
                <SampleLabels />
            </Hideable>
        </div>
    </div>
{:catch error}
    <p>An error occured: {error}</p>
{/await}
