import { select } from 'd3';

import render from './render';
import {
  availableColorSchemes,
  addTaxaPicker,
  addWidthSlider,
  addColorPicker,
  addSortByPicker,
  addDownloadLinks,
} from './toolbar';
import { setupData, sort } from './data';
import plotLegend from './legend';


export default function init(level) {
  /* global d */
  const data = d[level].data;

  // DOM
  const body = select('body .container-fluid');
  const vizRow = body.append('div').attr('class', 'viz row');
  const vizDiv = vizRow.append('div').attr('class', 'col-lg-12');
  const controlsRow = vizDiv.append('div').attr('class', 'controls row');
  const controls = controlsRow.append('div').attr('class', 'col-lg-12');
  const detailsRow = vizDiv.append('div').attr('class', 'details row');
  detailsRow.append('div').attr('class', 'col-lg-12');
  const plotRow = vizDiv.append('div').attr('class', 'plot row');
  const barCol = plotRow.append('div').attr('class', 'bars');

  const svgBar = barCol.append('svg');
  const bars = svgBar.append('g');
  bars.append('g').attr('class', 'x axis');
  bars.append('g').attr('class', 'y axis');

  const legendCol = plotRow.append('div').attr('class', 'legend');
  legendCol.append('svg');

  bars.append('text')
    .attr('id', 'y-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Relative Frequency');

  bars.append('text')
    .attr('id', 'x-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Sample');

  const initialColorScheme = availableColorSchemes[0].name;
  const dataMeta = setupData(d[level], svgBar);
  const { sortedKeysReverse, levels } = dataMeta;

  const initialSort = sort(data, [sortedKeysReverse[0]], ['Ascending'], [false], dataMeta);
  const chartInfo = render(svgBar, initialColorScheme, initialSort, dataMeta);

  plotLegend(legendCol, chartInfo);

  // Controls
  const ctrlRowOne = controls.append('div').attr('class', 'row');
  addDownloadLinks(ctrlRowOne, svgBar, legendCol.select('svg'), level + 1);
  addTaxaPicker(ctrlRowOne, levels, level + 1);
  addColorPicker(ctrlRowOne, svgBar, legendCol, data, dataMeta);
  addSortByPicker(ctrlRowOne, svgBar, data, dataMeta);
  addWidthSlider(ctrlRowOne, svgBar, data, dataMeta);
}
