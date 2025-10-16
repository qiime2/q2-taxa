import { Sample } from "./sample";
import { SampleControls } from "./sampleControls";
import { type SampleManager } from "./sampleManager.svelte";

export class Plot {
    dims: PlotDimensions;
    dynamicAxis: boolean;
    showFiltered: boolean;

    constructor() {
        this.dims = {
            barWidth: 25,
            barPadding: 2,
            marginTop: 25,
            marginRight: 50,
            marginBottom: 100,
            marginLeft: 75,
            axisOffset: 10,
        };
        this.dynamicAxis = false;
        this.showFiltered = false;
    }

    getPlotHeight(): number {
        const svgElem = document.querySelector("#barplot")!;
        const rect = svgElem.getBoundingClientRect();

        return rect.height - this.dims.marginTop - this.dims.marginBottom;
    }

    /**
     *
     */
    async drawSamples(sampleManager: SampleManager) {
        // clear <svg> content
        const svgElem = document.querySelector("#barplot")!;
        const rectElems = document.querySelectorAll(".taxonRect");
        if (rectElems.length > 0) {
            for (let rectElem of rectElems) {
                const r = rectElem as SVGRectElement;
                requestAnimationFrame(() => (r.style.opacity = "0"));
            }
            await new Promise((r) => setTimeout(r, 800));
        }

        svgElem.innerHTML = "";

        const samples = sampleManager.renderedSamples;

        // resize svg
        const width =
            this.dims.marginLeft +
            this.dims.marginRight +
            samples.length * this.dims.barWidth;
        svgElem.setAttribute("width", width.toString());

        // find axis scaler
        const relAbunSums: number[] = samples.map((s) => s.getRelAbunSum());
        const maxRelAbunSum = Math.max(...relAbunSums);

        let heightAdjustor: number;
        if (this.dynamicAxis) {
            heightAdjustor = maxRelAbunSum;
        } else {
            heightAdjustor = 1;
        }

        // draw each sample
        for (let [index, sample] of samples.entries()) {
            const x0 = this.dims.marginLeft + index * this.dims.barWidth;
            const y0 = this.dims.marginTop + this.getPlotHeight();
            sample.draw(
                x0,
                y0,
                this.dims.barWidth - this.dims.barPadding,
                this.getPlotHeight(),
                heightAdjustor,
                sampleManager,
            );
        }

        this.drawYAxis(sampleManager.renderedSamples);
        this.drawXAxis(
            sampleManager.renderedSamples,
            sampleManager.sampleControls,
        );
    }

    /**
     *
     */
    drawYAxis(samples: Sample[]) {
        const plotHeight = this.getPlotHeight();

        // draw axis
        this.drawSvgLine(
            this.dims.marginLeft - this.dims.axisOffset,
            this.dims.marginLeft - this.dims.axisOffset,
            this.dims.marginTop,
            this.dims.marginTop + plotHeight,
            2,
        );

        // draw axis ticks
        const relAbunSums: number[] = samples.map((s) => s.getRelAbunSum());
        const maxRelAbunSum = Math.max(...relAbunSums);

        let tickInterval: number;
        let numTicks: number;
        if (this.dynamicAxis) {
            tickInterval = this.getYAxisTickInterval(maxRelAbunSum);
            numTicks = Math.floor(maxRelAbunSum / tickInterval);
        } else {
            tickInterval = 0.1;
            numTicks = 10;
        }

        let yPosition;
        while (numTicks >= 0) {
            const tickValue = Number((numTicks * tickInterval).toFixed(3));
            if (this.dynamicAxis) {
                yPosition =
                    this.dims.marginTop +
                    (plotHeight - (tickValue * plotHeight) / maxRelAbunSum);
            } else {
                yPosition =
                    this.dims.marginTop + (plotHeight - tickValue * plotHeight);
            }

            // tick
            this.drawSvgLine(
                this.dims.marginLeft - this.dims.axisOffset,
                this.dims.marginLeft - this.dims.axisOffset - 5,
                yPosition,
                yPosition,
                2,
            );

            // tick number
            this.drawSvgText(
                [tickValue.toString()],
                this.dims.marginLeft - this.dims.axisOffset - 10,
                yPosition,
                "y",
            );

            numTicks--;
        }
    }

    getYAxisTickInterval(yAxisMax: number): number {
        let tickInterval = 0.1;
        while (Math.floor(yAxisMax / tickInterval) < 10) {
            tickInterval = tickInterval / 2;
        }

        return tickInterval;
    }

    drawXAxis(samples: Sample[], sampleControls: SampleControls) {
        const plotWidth = samples.length * this.dims.barWidth;
        const plotHeight = this.getPlotHeight();

        // draw axis
        this.drawSvgLine(
            this.dims.marginLeft,
            this.dims.marginLeft + plotWidth,
            this.dims.marginTop + plotHeight + this.dims.axisOffset,
            this.dims.marginTop + plotHeight + this.dims.axisOffset,
            2,
        );

        // draw axis ticks
        for (let [i, sample] of samples.entries()) {
            const xPosition =
                this.dims.marginLeft +
                i * this.dims.barWidth +
                this.dims.barWidth / 2;

            // tick
            this.drawSvgLine(
                xPosition,
                xPosition,
                this.dims.marginTop + plotHeight + this.dims.axisOffset,
                this.dims.marginTop + plotHeight + this.dims.axisOffset + 5,
                2,
            );

            // labels
            const labels = sampleControls.getSampleLabels(sample.sampleID);
            this.drawSvgText(
                labels,
                xPosition,
                this.dims.marginTop + plotHeight + this.dims.axisOffset + 10,
                "x",
            );
        }
    }

    drawSvgLine(
        x1: number,
        x2: number,
        y1: number,
        y2: number,
        strokeWidth: number,
    ) {
        const svgElem = document.querySelector("#barplot")!;
        const svgNamespace = "http://www.w3.org/2000/svg";

        const line = document.createElementNS(svgNamespace, "line");

        line.setAttribute("x1", x1.toString());
        line.setAttribute("x2", x2.toString());
        line.setAttribute("y1", y1.toString());
        line.setAttribute("y2", y2.toString());
        line.setAttribute("stroke-width", strokeWidth.toString());
        line.setAttribute("stroke", "black");
        line.setAttribute("stroke-linecap", "round");

        svgElem.appendChild(line);
    }

    drawSvgText(content: string[], x: number, y: number, axis: "x" | "y") {
        const svgElem = document.querySelector("#barplot")!;
        const svgNamespace = "http://www.w3.org/2000/svg";

        const fontSize = this.getRemInPixels(0.9 / content.length);

        const group = document.createElementNS(svgNamespace, "g");
        for (let [i, textItem] of content.entries()) {
            const text = document.createElementNS(svgNamespace, "text");
            text.innerHTML = textItem;
            text.setAttribute("x", x.toString());
            text.setAttribute("y", (y + i * fontSize).toString());
            text.setAttribute("font-size", `${fontSize}`);
            text.setAttribute("text-anchor", "end");
            text.setAttribute("dominant-baseline", "middle");

            group.appendChild(text);
        }

        if (axis == "x") {
            group.setAttribute("transform", `rotate(270, ${x}, ${y})`);
        }

        svgElem.appendChild(group);
    }

    getRemInPixels(rem: number): number {
        const computedStyle = getComputedStyle(document.documentElement);
        const rootRemPixels = parseFloat(computedStyle.fontSize);

        return rem * rootRemPixels;
    }

    downloadSVG() {
        const svgElem = document.querySelector("#barplot");

        const svgData = new XMLSerializer().serializeToString(svgElem as Node);
        const blob = new Blob([svgData], {
            type: "image/svg+xml;charset=utf-8",
        });

        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "taxa-barplot.svg";
        a.click();

        URL.revokeObjectURL(url);
    }

    downloadPNG() {
        const svgElem = document.querySelector("#barplot");

        const clone = svgElem.cloneNode(true) as SVGSVGElement;

        const bbox = svgElem.getBBox();
        const width = svgElem.width.baseVal.value || bbox.width;
        const height = svgElem.height.baseVal.value || bbox.height;

        clone.setAttribute("width", `${width}px`);
        clone.setAttribute("height", `${height}px`);

        const svgData = new XMLSerializer().serializeToString(clone);
        const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
        const url = URL.createObjectURL(svgBlob);

        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext("2d")!;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, width, height);
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                if (!blob) return;
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "taxa-barplot.png";
                a.click();
                URL.revokeObjectURL(a.href);
            }, "image/png");

            URL.revokeObjectURL(url);
        };

        img.crossOrigin = "anonymous";
        img.src = url;
    }

    downloadCSV() {}
}

type PlotDimensions = {
    barWidth: number;
    barPadding: number;
    marginTop: number;
    marginRight: number;
    marginBottom: number;
    marginLeft: number;
    axisOffset: number;
};
