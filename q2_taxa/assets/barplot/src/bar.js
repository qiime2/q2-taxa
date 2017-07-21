import { select } from 'd3';

import { transitionDur } from './init';


function _barGroupColor(sel, z) {
  sel.transition().duration(transitionDur)
    .style('fill', d => z(d.index));
}

export default function plotBars(chart, x, y, z, dataMeta, sortMap) {
  // Details
  const details = select('.details > div');
  details.selectAll('#details').remove();
  const info = details.append('p').attr('id', 'details')
    .html('Hover over the plot to learn more');

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
    .on('mouseover', function mouseOver(d) {
      const txlabel = sortMap[d.data[dataMeta.first]];
      const taxalabel = select(this.parentNode).property('taxa');
      const abunlabel = `${((d[1] - d[0]) * 100).toFixed(3)}%`;
      info.html(`${txlabel} | ${taxalabel} | ${abunlabel}`);
    });
}
