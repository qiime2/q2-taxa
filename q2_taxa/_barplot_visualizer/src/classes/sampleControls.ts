import { Metadata } from "./metadata";
import { Sample } from "./sample";

export class SampleControls {
    metadata: Metadata;
    sorts: SampleSort[];
    filters: SampleFilter[];
    labels: string[];

    constructor() {
        this.metadata = new Metadata();
        this.sorts = [];
        this.filters = [];
        this.labels = ["sampleID"];
    }

    addMetadataSort(column: string, ascending: boolean) {
        const sortFunc = this.metadata.getSortFunc(column, ascending);
        const name = `${column}-${ascending ? "ascending" : "descending"}`;

        const sort: SampleSort = {
            name: name,
            func: sortFunc,
        };

        this.sorts.push(sort);
    }

    addAbundanceSort(viewTaxonId: string, ascending: boolean) {
        const sortFunc = (sample1: Sample, sample2: Sample) => {
            const sample1Abun = sample1.getViewTaxonRelAbun(viewTaxonId);
            const sample2Abun = sample2.getViewTaxonRelAbun(viewTaxonId);

            if (ascending) {
                return sample2Abun - sample1Abun;
            } else {
                return sample1Abun - sample2Abun;
            }
        };

        const name = `${viewTaxonId}-${ascending ? "ascending" : "descending"}`;
        const sort: SampleSort = {
            name: name,
            func: sortFunc,
        };

        this.sorts.push(sort);
    }

    removeSort(name: string) {
        const names = this.sorts.map((s) => s.name);
        const index = names.indexOf(name);
        this.sorts = [
            ...this.sorts.slice(0, index),
            ...this.sorts.slice(index + 1),
        ];
    }

    addCategoricalMetadataFilter(
        column: string,
        levels: string[],
        keep: boolean,
    ) {
        const filterFunc = this.metadata.getCategoricalFilterFunc(
            column,
            levels,
            keep,
        );
        const name = `${column} ${keep ? "IN" : "NOT IN"} ${levels.join(",")}`;

        const filter: SampleFilter = {
            name: name,
            func: filterFunc,
        };

        this.filters.push(filter);
    }

    addNumericMetadataFilter(
        column: string,
        value: number,
        operator: ">" | "<",
    ) {
        const filterFunc = this.metadata.getNumericFilterFunc(
            column,
            value,
            operator,
        );
        const name = `${column} ${operator} ${value}`;

        const filter: SampleFilter = {
            name: name,
            func: filterFunc,
        };

        this.filters.push(filter);
    }

    addAbundanceFilter(
        viewTaxonId: string,
        value: number,
        operator: ">" | "<",
    ) {
        const filterFunc = (sample: Sample) => {
            const viewTaxonAbun = sample.getViewTaxonRelAbun(viewTaxonId);
            if (operator == ">") {
                return !(viewTaxonAbun > value);
            } else {
                return !(viewTaxonAbun < value);
            }
        };

        const name = `${viewTaxonId} ${operator} ${value}`;

        const filter: SampleFilter = {
            name: name,
            func: filterFunc,
        };

        this.filters.push(filter);
    }

    removeFilter(name: string) {
        const names = this.filters.map((s) => s.name);
        const index = names.indexOf(name);
        this.filters = [
            ...this.filters.slice(0, index),
            ...this.filters.slice(index + 1),
        ];
    }

    addLabel(column: string) {
        this.labels.push(column);
    }

    setLabels(labels: string[]) {
        this.labels = labels;
    }

    removeLabel(column: string) {
        const index = this.labels.indexOf(column);
        this.labels = [
            ...this.labels.slice(0, index),
            ...this.labels.slice(index + 1),
        ];
    }

    getSampleLabels(sampleId: string): string[] {
        const sampleLabels: string[] = [];
        for (let label of this.labels) {
            const sampleLabel = this.metadata.getColumnValue(label, sampleId);
            sampleLabels.push(sampleLabel);
        }

        return sampleLabels;
    }

    updateSortOrder(sortNames: string[]) {
        if (this.sorts.length == 0) {
            return;
        }

        const names = this.sorts.map((s) => s.name);
        const shared = sortNames.filter((n) => names.indexOf(n) != -1);
        if (this.sorts.length != shared.length) {
            throw new Error("Sorts arrays were out of sync.");
        }

        const updated: SampleSort[] = [];
        for (let name of sortNames) {
            let sortIndex = names.indexOf(name);
            let sort = this.sorts[sortIndex];
            updated.push(sort);
        }

        this.sorts = updated;
    }

    /**
     * Applies all filters and sorts and returns the final array of rendered
     * samples.
     */
    getRenderedSamples(samples: Sample[]): Sample[] {
        let rendered = [...samples];

        for (let filter of this.filters) {
            rendered = rendered.filter(filter.func);
        }

        const finalBossSortFunc = (sample1: Sample, sample2: Sample) => {
            let diff = this.sorts[0]?.func(sample1, sample2);

            let sortIndex = 1;
            while (diff == 0 && sortIndex < this.sorts.length) {
                diff = this.sorts[sortIndex].func(sample1, sample2);
                sortIndex++;
            }

            return diff;
        };

        if (this.sorts.length > 0) {
            rendered = rendered.sort(finalBossSortFunc);
        }

        return rendered;
    }
}

type SampleSort = {
    name: string;
    func: (s1: Sample, s2: Sample) => number;
};

type SampleFilter = {
    name: string;
    func: (s: Sample) => boolean;
};
