import { csv } from "d3-fetch";
import { Taxonomy, Taxon, ViewTaxon, Feature } from "./taxonomy.svelte";
import { Sample } from "./sample";
import { SampleControls } from "./sampleControls";
import { FeatureControls } from "./featureControls.svelte";
import { Colors } from "./colors.svelte";
import { Plot } from "./plot";

export class SampleManager {
    samples: Sample[];
    renderedSamples: Sample[];
    sampleControls: SampleControls;
    featureControls: FeatureControls;
    taxonomy: Taxonomy;
    colors: Colors;
    plot: Plot;
    eventBus: EventTarget;
    selectedTaxon: ViewTaxon | null;

    constructor() {
        this.samples = [];
        this.renderedSamples = [];
        this.sampleControls = new SampleControls();
        this.featureControls = new FeatureControls();
        this.taxonomy = new Taxonomy();
        this.colors = new Colors();
        this.plot = new Plot();
        this.eventBus = new EventTarget();
        this.selectedTaxon = $state(null);
    }

    /**
     * Parses a feature table saved as a tsv file (with samples as columns,
     * rows as features) into `Sample` and `Feature` objects, and stores the
     * created samples in `this.samples`.
     */
    async parseFeatureTable(filepath: string) {
        let tableLines = await csv(filepath);

        const featureHeader = tableLines.shift();

        for (let row of tableLines) {
            const sampleID = row.sampleID;
            const sample = new Sample(sampleID);

            for (let featureID in featureHeader) {
                if (featureID == "sampleID") {
                    continue;
                }

                const abundance = Number(row[featureID]);
                if (abundance > 0) {
                    const feature = new Feature(featureID, abundance);
                    sample.features.push(feature);
                }
            }

            this.samples.push(sample);
        }
    }

    /**
     * Calculates relative abundance, prevalence, prevalence proportion, and
     * mean relative abundance for each view taxon in each sample.
     */
    calcTaxaStats() {
        const prevalMap: Map<Taxon, number> = new Map();
        const relAbunMap: Map<Taxon, number> = new Map();

        for (let sample of this.samples) {
            sample.calcRelAbun();
            sample.tallyGlobalStats(prevalMap, relAbunMap);
        }
        for (let sample of this.samples) {
            sample.calcGlobalStats(prevalMap, relAbunMap, this.samples.length);
        }
    }

    /**
     *
     */
    getAllViewTaxa(): ViewTaxon[] {
        const allViewTaxa: Set<ViewTaxon> = new Set();
        for (let sample of this.renderedSamples) {
            for (let viewTaxon of sample.viewTaxa) {
                allViewTaxa.add(viewTaxon);
            }
        }

        return [...allViewTaxa];
    }

    /**
     * Performs an entire render cycle of the barplot, including calculating
     * the set of view taxa, calculating stats for each view taxon, sample
     * filtering & sorting, view taxon filtering & sorting, and sample drawing.
     */
    async render() {
        // find view taxa
        for (let sample of this.samples) {
            sample.mapToViewTaxa(this.taxonomy);
        }

        // calculate taxa stats
        this.calcTaxaStats();

        // filter and sort samples
        this.renderedSamples = this.sampleControls.getRenderedSamples(
            this.samples,
        );

        // filter and sort view taxa per sample
        for (let sample of this.renderedSamples) {
            sample.filterViewTaxa(this.featureControls.filters);
            sample.sortViewTaxa(this.featureControls.sort);
        }

        // draw samples
        this.colors.reset();

        this.plot.drawSamples(this);
    }
}

export const sampleManager = new SampleManager();
