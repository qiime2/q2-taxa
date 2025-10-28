import { csv } from "d3-fetch";
import { Sample } from "./sample";

export class Metadata {
    rows: MetadataRow[];
    columnTypes: Map<string, "categorical" | "numeric">;

    constructor() {
        this.rows = [];
        this.columnTypes = new Map();
    }

    /**
     * Parses a metadata.csv file into an array of row objects and initializes
     * `this.metadata` and `this.columnTypes`.
     */
    async parse(filepath: string) {
        let metadataRowsD3 = await csv(filepath);

        let metadataRows: MetadataRow[] = [];
        for (let row of metadataRowsD3) {
            metadataRows.push(row);
        }

        // get metadata type row, create column type map
        const typesRow = metadataRows[0];
        if (typesRow.sampleID != "#q2:types") {
            throw new Error("Expected types row in metadata.");
        }

        for (let column in typesRow) {
            if (column == "sampleID") {
                continue;
            }

            this.columnTypes.set(
                column,
                typesRow[column] as "categorical" | "numeric",
            );
        }

        // remove types row
        this.rows = metadataRows.slice(1);

        // ensure categorical columns are strings; numeric are numbers
        for (let row of this.rows) {
            for (let column in row) {
                if (column == "sampleID") {
                    row[column] = String(row[column]);
                    continue;
                }

                const columnType = this.columnTypes.get(column);
                if (columnType == "categorical") {
                    row[column] = String(row[column]);
                } else {
                    row[column] = Number(row[column]);
                }
            }
        }
    }

    /**
     * Returns an array of all metadata column names.
     */
    getColumnNames(): string[] {
        return Object.keys(this.rows[0]);
    }

    getColumnNamesOfType(type: "categorical" | "numeric"): string[] {
        const columnNames = this.getColumnNames();
        return columnNames.filter((cn) => this.columnTypes.get(cn) == type);
    }

    getColumnValue(column: string, sampleId: string): string {
        const sampleRows = this.rows.filter((s) => s.sampleID == sampleId);

        if (sampleRows.length != 1) {
            throw new Error("Found more or less than 1 matching sample row.");
        }

        const sampleRow = sampleRows[0];

        return sampleRow[column].toString();
    }

    /**
     */
    getCategoricalColumnLevels(column: string): string[] {
        if (this.columnTypes.get(column) != "categorical") {
            throw new Error("Tried to get levels for non-categorical column.");
        }

        const levels = new Set<string>();
        for (let row of this.rows) {
            levels.add(row[column] as string);
        }

        return [...levels];
    }

    /**
     * Given a `Sample` object returns the corresponding metadata row.
     */
    private getRow(sample: Sample): MetadataRow {
        const matches = this.rows.filter((r) => r.sampleID == sample.sampleID);
        if (matches.length > 1) {
            throw new Error("Found more than one match by sample ID.");
        } else if (matches.length == 0) {
            throw new Error("Found no matches by sample ID.");
        } else {
            return matches[0];
        }
    }

    /**
     * Returns a sample-sorting function. If the sorting column
     * is categorical then levels are sorted in alphabetical order.
     */
    getSortFunc(column: string, ascending: boolean) {
        const columnType = this.columnTypes.get(column);
        let sortFunc;

        if (columnType == "categorical") {
            sortFunc = (sample1: Sample, sample2: Sample) => {
                const row1 = this.getRow(sample1);
                const row2 = this.getRow(sample2);

                if (row1[column] < row2[column]) {
                    if (ascending) {
                        return -1;
                    } else {
                        return 1;
                    }
                } else if (row1[column] > row2[column]) {
                    if (ascending) {
                        return 1;
                    } else {
                        return -1;
                    }
                } else {
                    return 0;
                }
            };
        } else {
            sortFunc = (sample1: Sample, sample2: Sample) => {
                const row1 = this.getRow(sample1);
                const row2 = this.getRow(sample2);
                if (ascending) {
                    return (row1[column] as number) - (row2[column] as number);
                } else {
                    return (row2[column] as number) - (row1[column] as number);
                }
            };
        }

        return sortFunc;
    }

    /**
     * Returns a categorical metadata filter function.
     */
    getCategoricalFilterFunc(column: string, levels: string[], keep: boolean) {
        let filterFunc;
        if (keep) {
            filterFunc = (sample: Sample) => {
                const row = this.getRow(sample);
                return levels.indexOf(row[column] as string) != -1;
            };
        } else {
            filterFunc = (sample: Sample) => {
                const row = this.getRow(sample);
                return levels.indexOf(row[column] as string) == -1;
            };
        }

        return filterFunc;
    }

    /**
     * Returns a numeric metadata column filter function.
     */
    getNumericFilterFunc(column: string, value: number, operator: ">" | "<") {
        let filterFunc;
        if (operator == ">") {
            filterFunc = (sample: Sample) => {
                const row = this.getRow(sample);
                return (row[column] as number) > value;
            };
        } else {
            filterFunc = (sample: Sample) => {
                const row = this.getRow(sample);
                return (row[column] as number) < value;
            };
        }

        return filterFunc;
    }
}

type MetadataRow = { [key: string]: string | number };
