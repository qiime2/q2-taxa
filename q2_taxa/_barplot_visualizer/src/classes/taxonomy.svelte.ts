import { csv } from "d3-fetch";
import { SvelteSet } from "svelte/reactivity";

export class Taxonomy {
    rootTaxon: Taxon;
    displayLevel: number;
    expansions: Set<Taxon>;
    featureMap: Map<string, Taxon>;

    constructor() {
        this.rootTaxon = new Taxon("placeholder", null);
        this.displayLevel = $state(1);
        this.expansions = $state(new SvelteSet());
        this.featureMap = new Map();
    }

    /**
     * Parses a taxonomy.csv file into a tree of `Taxon` objects. Initializes
     * `this.rootTaxon` to the root of this tree.
     */
    async parse(filepath: string) {
        const root = new Taxon("root", null);
        this.rootTaxon = root;

        const taxonomyRecords = await csv(filepath);

        for (let taxonRecord of taxonomyRecords) {
            let parentNode = root;

            const featureID = taxonRecord["Feature ID"];
            const levelNames = taxonRecord["Taxon"]
                .split(";")
                .map((n: string) => n.trim())
                .filter((n: string) => n != "");

            for (let [levelIndex, levelName] of levelNames.entries()) {
                const existingChild = this.findChildByName(
                    parentNode,
                    levelName,
                );

                if (existingChild != null) {
                    parentNode = existingChild;
                } else {
                    const newChild = new Taxon(levelName, parentNode);
                    parentNode.children.push(newChild);
                    parentNode = newChild;
                }

                if (levelIndex == levelNames.length - 1) {
                    // the final node is the classification of a feature
                    parentNode.featureIDs.push(featureID);

                    if (this.featureMap.has(featureID)) {
                        throw new Error(`
                            Feature ${featureID} classified to multiple taxa.`);
                    }
                    this.featureMap.set(featureID, parentNode);
                }
            }
        }
    }

    /**
     * Updates `this.displayLevel` as long as the desired level is within the
     * valid range.
     */
    setDisplayLevel(displayLevel: number) {
        const descendants = this.rootTaxon.getDescendants();
        const levels = descendants.map((d) => d.getLevel());
        const maxLevel = Math.max(...levels);

        if (displayLevel < 1) {
            alert("Can not set display level lower than 1.");
        } else if (displayLevel > maxLevel) {
            alert(`Can not set display level to more than ${maxLevel}.`);
        } else {
            this.displayLevel = displayLevel;
        }
    }

    getDepth(): number {
        const allTaxa = this.rootTaxon.getDescendants();
        const levels = allTaxa.map((t) => t.getLevel());
        return Math.max(...levels);
    }

    /**
     *
     */
    addExpandFromAncestor(taxon: Taxon, expandToLevel: number): boolean {
        // ensure taxon level is less than the level to which to expand
        const taxonLevel = taxon.getLevel();
        if (taxonLevel >= expandToLevel) {
            alert("Expansion from-level must be less than to-level.");
            return false;
        }

        // ensure taxon has descendants to which to expand
        const descendantTaxa = taxon.getDescendantsAtLevel(expandToLevel);
        if (descendantTaxa.length == 0) {
            alert(`Taxon has no descendants at level ${expandToLevel}.`);
            return false;
        }

        // scan sub tree to ensure no other expand
        if (!this.isSubTreeClear(taxon, expandToLevel)) {
            alert("Another expansion was detected in the subtree.");
            return false;
        }

        taxon.expandTo = expandToLevel;

        // todo: update data structure tracking expansions & collapses

        return true;
    }

    /**
     * For a given feature ID find the taxon at which it is displayed, taking
     * into account display level, expansions, and collapses. Returns null
     * if the taxon is filtered.
     */
    getDisplayTaxon(featureID: string): Taxon | null {
        // find taxon by feature ID
        const featureTaxon = this.featureMap.get(featureID);
        if (featureTaxon == undefined) {
            throw new Error(`Feature ${featureID} has no classification.`);
        }

        const featureTaxonLevel = featureTaxon.getLevel();

        // map to ancestor if needed
        let taxon: Taxon;
        if (featureTaxonLevel > this.displayLevel) {
            taxon = featureTaxon.getAncestorAtLevel(this.displayLevel);
        } else {
            taxon = featureTaxon;
        }

        // follow expansion if present
        if (taxon.expandTo != null) {
            if (taxon.expandTo <= featureTaxonLevel) {
                taxon = featureTaxon.getAncestorAtLevel(taxon.expandTo);
            }
        }

        return taxon;
    }

    /**
     * Checks a subtree in the taxonomy extending from `ancestor` down to
     * `descendantLevel` for any taxa marked as expanded or collapsed. If any
     * are found, false is returned; if none are found true is returned.
     */
    private isSubTreeClear(ancestor: Taxon, descendantLevel: number): boolean {
        const descendants = ancestor.getDescendants();
        const violators = descendants.filter((d) => {
            const inSubTree = d.getLevel() <= descendantLevel;
            const isExpanded = d.expandTo != null;

            return inSubTree && isExpanded;
        });

        return violators.length == 0;
    }

    /**
     * Searches all children of `parent` for a child with name `name`. Returns
     * the child if found, or null if no matching child is found.
     */
    private findChildByName(parent: Taxon, name: string): Taxon | null {
        let matchingChildren = parent.children.filter((child) => {
            return child.name == name;
        });

        if (matchingChildren.length > 1) {
            throw new Error("More than one matching child found.");
        }
        if (matchingChildren.length == 0) {
            return null;
        }

        return matchingChildren[0];
    }
}

export class Taxon {
    name: string;
    parent: Taxon | null;
    children: Taxon[];
    filtered: boolean;
    expandTo: number | null;
    color: string;
    featureIDs: string[];

    constructor(name: string, parent: Taxon | null) {
        this.name = name;
        this.parent = parent;
        this.children = [];
        this.filtered = $state(false);
        this.expandTo = $state(null);
        this.color = $state("");
        this.featureIDs = [];
    }

    /**
     *
     */
    getLevel(): number {
        if (this.parent == null) {
            return 1;
        }

        return this.parent.getLevel() + 1;
    }

    /**
     * Return all descendants of the taxon, including the taxon itself.
     */
    getDescendants(): Taxon[] {
        const descendants: Taxon[] = [this];

        for (let child of this.children) {
            descendants.push(...child.getDescendants());
        }

        return descendants;
    }

    /**
     * Returns the descendants of the taxon at `level` or an empty array if
     * there are none.
     */
    getDescendantsAtLevel(level: number): Taxon[] {
        const descendants = this.getDescendants();
        if (descendants.length == 0) {
            return descendants;
        }

        return descendants.filter((descendant) => {
            return descendant.getLevel() == level;
        });
    }

    /**
     * Returns all ancestors of the taxon, including the taxon itself.
     */
    getAncestors(): Taxon[] {
        if (this.parent == null) {
            return [this];
        }

        return [...this.parent.getAncestors(), this];
    }

    /**
     * Returns the ancestor of the taxon at level `level`.
     */
    getAncestorAtLevel(level: number): Taxon {
        if (this.getLevel() < level) {
            throw new Error("Taxon level less than ancestor level.");
        }

        const ancestors = this.getAncestors();

        const ancestorsAtLevel = ancestors.filter((ancestor) => {
            return ancestor.getLevel() == level;
        });

        if (ancestorsAtLevel.length > 1) {
            throw new Error("Multiple ancestors.");
        }
        if (ancestorsAtLevel.length < 1) {
            throw new Error("No ancestor found.");
        }

        return ancestorsAtLevel[0];
    }

    /**
     * Returns the full taxonomic string of the taxon. Serves as a unique id.
     */
    getFullTaxonomicString(): string {
        return this.getAncestors()
            .map((a) => a.name)
            .join(";");
    }
}

export class ViewTaxon {
    taxon: Taxon;
    features: Feature[];
    abundance: number;
    relAbun: number;
    meanRelAbun: number;
    preval: number;
    prevalProp: number;
    expanded: boolean;

    constructor(taxon: Taxon) {
        this.taxon = taxon;
        this.features = [];
        this.abundance = 0;
        this.relAbun = -1;
        this.meanRelAbun = -1;
        this.preval = -1;
        this.prevalProp = -1;
        this.expanded = false;
    }
}

export class Feature {
    featureID: string;
    abundance: number;

    constructor(featureID: string, abundance: number) {
        this.featureID = featureID;
        this.abundance = abundance;
    }
}
