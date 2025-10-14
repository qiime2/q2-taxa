<script lang="ts">
    import { slide } from "svelte/transition";

    let { title, children } = $props();

    let show = $state(false);
</script>

<div class="bg-gray-100 rounded-lg w-[22rem] min-h-[3rem] py-[0.5rem]">
    <div class="grid grid-cols-5 my-[0.5rem]">
        <h1 class="col-start-2 col-end-5 justify-self-center text-lg font-bold">
            {title}
        </h1>
        <button
            class="col-start-5 hover:cursor-pointer font-bold"
            onclick={() => (show = !show)}
        >
            {show ? "-" : "+"}
        </button>
    </div>
    {#if show}
        <div transition:slide>
            {@render children?.()}
        </div>
    {/if}
</div>
