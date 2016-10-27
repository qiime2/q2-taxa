import { select, mouse } from 'd3';

import { transitionDur } from './init';


function _barGroupColor(sel, z) {
  sel.transition().duration(transitionDur)
    .style('fill', d => z(d.index));
}

export default function plotBars(chart, x, y, z, dataMeta, sortMap) {
  // Tooltip
  chart.selectAll('#tooltip').remove();
  const tooltip = chart.append('g').style('display', 'none').attr('id', 'tooltip');
  tooltip.append('rect')
    .attr('height', 50)
    .attr('fill', 'white');
  const tttext = tooltip.append('text')
    .style('text-anchor', 'middle')
    .attr('font-size', '12px')
    .attr('font-weight', 'bold');
  tttext.append('tspan')
    .attr('id', 'ttxlabel')
    .attr('dy', '1.2em');
  tttext.append('tspan')
    .attr('id', 'taxalabel')
    .attr('dy', '1.2em');
  tttext.append('tspan')
    .attr('id', 'abunlabel')
    .attr('dy', '1.2em');

  // Color groups
  const layerUpdate = chart.selectAll('.layer').data(dataMeta.layers);
  layerUpdate.exit().remove();
  const layerEnter = layerUpdate.enter().append('g').attr('class', 'layer');
  const layer = layerUpdate.merge(layerEnter)
    .call(_barGroupColor, z)
    .attr('visibility', null)
    .property('taxa', d => d.key);

  // Rectangles
  const rectUpdate = layer.selectAll('rect').data(d => d);
  rectUpdate.exit().remove();
  const rectEnter = rectUpdate.enter().append('rect');
  rectUpdate.merge(rectEnter)
    .attr('x', d => x(d.data[dataMeta.first]))
    .attr('y', d => y(d[1]))
    .attr('height', d => y(d[0]) - y(d[1]))
    .attr('width', x.bandwidth())
    .on('mouseover', () => { tooltip.style('display', null); })
    .on('mouseout', () => { tooltip.style('display', 'none'); })
    .on('mousemove', function mouseMove(d) {
      const text = tooltip.select('text');
      const hoveredTaxa = select(this.parentNode).property('taxa');
      const txlabel = text.select('#ttxlabel');
      const taxalabel = text.select('#taxalabel');
      const abunlabel = text.select('#abunlabel');

      txlabel.text(() => sortMap[d.data[dataMeta.first]]);
      taxalabel.text(() => hoveredTaxa);
      abunlabel.text(() => `${((d[1] - d[0]) * 100).toFixed(3)}%`);

      const textWidth = text.node().getBBox().width;
      const midpoint = (textWidth / 2) + 5;

      txlabel.attr('x', midpoint);
      taxalabel.attr('x', midpoint);
      abunlabel.attr('x', midpoint);

      tooltip.select('rect').attr('width', textWidth + 10);

      const xPosition = mouse(this)[0];
      const yPosition = mouse(this)[1] - 25;
      tooltip.attr('transform', `translate(${xPosition},${yPosition})`);
    });
}
