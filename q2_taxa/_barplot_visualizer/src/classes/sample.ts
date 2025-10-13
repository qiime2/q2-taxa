import { Taxonomy, Taxon, Feature, ViewTaxon } from "./taxonomy.svelte";
import { Colors } from "./colors.svelte";
import type { FeatureFilter, FeatureSort } from "./featureControls.svelte";
import { type SampleManager } from "./sampleManager.svelte";

export class Sample {
    sampleID: string;
    features: Feature[];
    viewTaxa: ViewTaxon[];

    constructor(sampleID: string) {
        this.sampleID = sampleID;
        this.features = [];
        this.viewTaxa = [];
    }

    /**
     * Maps a sample's features to a set of "view taxa", which are the taxa
     * that the features are displayed as in the stacked bar chart. Updates
     * (and overwrites) `this.viewTaxa`.
     */
    async mapToViewTaxa(taxonomy: Taxonomy) {
        const viewTaxaMap: Map<Taxon, ViewTaxon> = new Map();

        for (let feature of this.features) {
            const displayTaxon = taxonomy.getDisplayTaxon(feature.featureID);

            if (displayTaxon == null) {
                continue;
            }

            if (viewTaxaMap.get(displayTaxon) == null) {
                const newViewTaxon = new ViewTaxon(displayTaxon);
                viewTaxaMap.set(displayTaxon, newViewTaxon);
            }

            const viewTaxon = viewTaxaMap.get(displayTaxon)!;
            viewTaxon.abundance += feature.abundance;
            viewTaxon.features.push(feature);
        }

        this.viewTaxa = [...viewTaxaMap.values()];
    }

    /**
     * Calculates and assigns the relative abundance of each taxon in
     * `this.viewTaxa`.
     */
    calcRelAbun() {
        const totalAbundance = this.viewTaxa.reduce((sum, taxon) => {
            return (sum += taxon.abundance);
        }, 0);

        for (let viewTaxon of this.viewTaxa) {
            viewTaxon.relAbun = viewTaxon.abundance / totalAbundance;
        }
    }

    /**
     * Tallies prevalence and relative abundance of each of the taxa in
     * `this.viewTaxa`.
     */
    tallyGlobalStats(
        prevalMap: Map<Taxon, number>,
        relAbunMap: Map<Taxon, number>,
    ) {
        for (let viewTaxon of this.viewTaxa) {
            const taxon = viewTaxon.taxon;

            if (!prevalMap.get(taxon)) {
                prevalMap.set(taxon, 1);
            } else {
                const prevalence = prevalMap.get(taxon)!;
                prevalMap.set(taxon, prevalence + 1);
            }

            if (!relAbunMap.get(taxon)) {
                relAbunMap.set(taxon, viewTaxon.relAbun);
            } else {
                const relAbunSum = relAbunMap.get(taxon)!;
                relAbunMap.set(taxon, relAbunSum + viewTaxon.relAbun);
            }
        }
    }

    /**
     * Uses  populated prevalence and relative abundance maps to record the
     * prevalence, prevalence proportion, and mean relative abundance of each
     * view taxon in `this.viewTaxa`.
     */
    calcGlobalStats(
        prevalMap: Map<Taxon, number>,
        relAbunMap: Map<Taxon, number>,
        numSamples: number,
    ) {
        for (let viewTaxon of this.viewTaxa) {
            const taxon = viewTaxon.taxon;

            const prevalence = prevalMap.get(taxon)!;
            viewTaxon.preval = prevalence;
            viewTaxon.prevalProp = prevalence / numSamples;

            const relAbunSum = relAbunMap.get(taxon)!;
            viewTaxon.meanRelAbun = relAbunSum / numSamples;
        }
    }

    /**
     *
     */
    getViewTaxonRelAbun(viewTaxonId: string): number {
        const matches = this.viewTaxa.filter((vt) => {
            return vt.taxon.getFullTaxonomicString() == viewTaxonId;
        });

        if (matches.length == 0) {
            return 0;
        } else if (matches.length == 1) {
            return matches[0].relAbun;
        } else {
            throw new Error("Found more than one view taxon match.");
        }
    }

    /**
     * Returns the sum of the relative abundances of the view taxa of the
     * sample. Useful to know for displaying the abundance axis after taxon
     * filtering has been performed.
     */
    getRelAbunSum(): number {
        return this.viewTaxa.reduce(
            (sum: number, vt: ViewTaxon) => sum + vt.relAbun,
            0,
        );
    }

    filterViewTaxa(filters: FeatureFilter[]) {
        for (let filter of filters) {
            this.viewTaxa = this.viewTaxa.filter(filter.func);
        }
    }

    sortViewTaxa(sort: FeatureSort) {
        this.viewTaxa = this.viewTaxa.sort(sort.func);
    }

    /**
     *
     */
    draw(
        x0: number,
        y0: number,
        barWidth: number,
        barHeight: number,
        heightAdjustor: number,
        sampleManager: SampleManager,
    ) {
        // draw from bottom
        const viewTaxaReversed = this.viewTaxa.slice().reverse();

        let i = 0;
        let sumAbun = 0;
        for (let viewTaxon of viewTaxaReversed) {
            // create and append rect
            const rectHeight = (viewTaxon.relAbun * barHeight) / heightAdjustor;
            y0 = y0 - rectHeight;

            this.drawRect(
                viewTaxon,
                x0,
                y0,
                barWidth,
                rectHeight,
                sampleManager,
            );

            sumAbun += viewTaxon.relAbun;
        }

        if (sampleManager.plot.showFiltered && sumAbun != 1) {
            const rectHeight = ((1 - sumAbun) * barHeight) / heightAdjustor;
            y0 = y0 - rectHeight;
            this.drawRect(null, x0, y0, barWidth, rectHeight, sampleManager);
        }
    }

    drawRect(
        viewTaxon: ViewTaxon | null,
        x: number,
        y: number,
        width: number,
        height: number,
        sampleManager: SampleManager,
    ) {
        const svgElem = document.querySelector("#barplot")!;
        const svgNamespace = "http://www.w3.org/2000/svg";

        const rect = document.createElementNS(svgNamespace, "rect");

        rect.setAttribute("x", x.toString());
        rect.setAttribute("y", y.toString());
        rect.setAttribute("width", width.toString());
        rect.setAttribute("height", height.toString());
        rect.setAttribute("class", "taxonRect");

        if (viewTaxon != null) {
            viewTaxon.taxon.color = sampleManager.colors.colorTaxon(
                viewTaxon.taxon,
                1,
            );
            rect.setAttribute("fill", viewTaxon.taxon.color);

            rect.addEventListener("click", () => {
                const payload = { viewTaxon: viewTaxon };
                sampleManager.eventBus.dispatchEvent(
                    new CustomEvent("taxon-selected", { detail: payload }),
                );
            });
        } else {
            // filtered rect
            rect.setAttribute("fill", "#adadad");
        }

        rect.style.opacity = "0";
        svgElem.appendChild(rect);
        requestAnimationFrame(() => (rect.style.opacity = "1"));
    }
}
