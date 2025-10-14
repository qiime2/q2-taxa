<script lang="ts">
    import { onMount } from "svelte";
    import { sampleManager } from "../classes/sampleManager.svelte";

    onMount(() => {
        sampleManager.render();
    });
</script>

<div class="h-[40rem] overflow-scroll">
    <svg id="barplot" class="h-[39rem]"></svg>
</div>
