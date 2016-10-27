export const labelOffset = 30;

export function setupXAxis(svg, chart, width, height, xAxis) {
  let maxLabelX = 0;

  svg.select('.x.axis')
    .attr('transform', `translate(0,${height})`)
    .call(xAxis)
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '-0.5em')
      .attr('transform', function setHeight() {
        const textHeight = this.getComputedTextLength();
        if (textHeight > maxLabelX) maxLabelX = textHeight;
        return 'rotate(-90)';
      });

  chart.select('#x-label')
    .attr('transform', `translate(${(width / 2)},${(height + maxLabelX + labelOffset)})`);

  return maxLabelX;
}

export function setupYAxis(svg, chart, height, yAxis) {
  svg.select('.y.axis').call(yAxis);

  chart.select('#y-label')
    .attr('transform', `translate(-${labelOffset},${(height / 2)})rotate(-90)`);
}
