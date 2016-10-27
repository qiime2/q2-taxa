import { select, selectAll } from 'd3';
import { transitionDur } from './init';


function _swatchColor(sel, z, stackOrder) {
  sel.transition().duration(transitionDur)
    .style('fill', d => z(stackOrder.indexOf(d)));
}

export default function plotLegend(svg, chart, keys, width, z) {
  // Legend
  const stackOrder = svg.property('stackOrder');
  chart.selectAll('.legend').remove();
  const legendUpdate = chart.selectAll('.legend').data(stackOrder);
  const legendEnter = legendUpdate.enter().append('g')
    .attr('class', 'legend')
    .attr('id', d => `id${d}`)
    .style('font', '10px sans-serif');
  let legend = legendUpdate.merge(legendEnter)
    .attr('transform', (_, i) => `translate(10,${((keys.length - i - 1) * 20)})`);

  // Swatches
  legendEnter.append('rect')
    .attr('width', 18)
    .attr('height', 18);
  legend.selectAll('rect')
    .attr('x', width)
    .call(_swatchColor, z, stackOrder)
    .on('mouseover', function pointer() { select(this).style('cursor', 'pointer'); })
    .on('click', (d) => {
      const clickedLegend = select(`#id${d}`);
      const clickedSwatch = clickedLegend.select('rect');
      const isSelected = clickedSwatch.classed('selected');

      clickedSwatch.classed('selected', !isSelected)
        .style('stroke', () => (isSelected ? null : 'black'))
        .style('stroke-width', () => (isSelected ? null : 2));

      const selectedTaxa = selectAll('.legend .selected')
        .nodes().map(k => keys[select(k).datum()]);

      selectAll('.layer')
        .attr('visibility', (datum) => {
          if (selectedTaxa.length === 0) { return null; }
          return selectedTaxa.indexOf(datum.key.trim()) > -1 ? null : 'hidden';
        });
    });

  // Labels
  legendEnter.append('text')
    .attr('y', 9)
    .attr('dy', '.35em')
    .attr('text-anchor', 'start');
  legend = legend.selectAll('text')
    .attr('x', width + 24)
    .text(d => keys[d]);

  let maxLabelLegendWidth = 0;
  legend.each(function getMaxWidth() {
    const textWidth = this.getComputedTextLength();
    if (textWidth > maxLabelLegendWidth) maxLabelLegendWidth = textWidth;
  });

  return maxLabelLegendWidth;
}
