import { select } from 'd3';
import * as d3chromo from 'd3-scale-chromatic';

import init from './init';
import render from './render';
import { sort } from './data';
import plotLegend from './legend';


export const availableColorSchemes = [
  { name: 'schemeAccent', scheme: d3chromo.schemeAccent, type: 'o' },
  { name: 'schemeDark2', scheme: d3chromo.schemeDark2, type: 'o' },
  { name: 'schemePaired', scheme: d3chromo.schemePaired, type: 'o' },
  { name: 'schemePastel1', scheme: d3chromo.schemePastel1, type: 'o' },
  { name: 'schemePastel2', scheme: d3chromo.schemePastel2, type: 'o' },
  { name: 'schemeSet1', scheme: d3chromo.schemeSet1, type: 'o' },
  { name: 'schemeSet2', scheme: d3chromo.schemeSet2, type: 'o' },
  { name: 'schemeSet3', scheme: d3chromo.schemeSet3, type: 'o' },
  { name: 'PRGn', scheme: d3chromo.interpolatePRGn, type: 's' },
  { name: 'BrBG', scheme: d3chromo.interpolateBrBG, type: 's' },
  { name: 'PiYG', scheme: d3chromo.interpolatePiYG, type: 's' },
  { name: 'PuOr', scheme: d3chromo.interpolatePuOr, type: 's' },
  { name: 'RdBu', scheme: d3chromo.interpolateRdBu, type: 's' },
  { name: 'RdGy', scheme: d3chromo.interpolateRdGy, type: 's' },
  { name: 'RdYlBu', scheme: d3chromo.interpolateRdYlBu, type: 's' },
  { name: 'RdYlGn', scheme: d3chromo.interpolateRdYlGn, type: 's' },
  { name: 'Spectral', scheme: d3chromo.interpolateSpectral, type: 's' },
];

// HELPERS
function _getSort(sel, svg, data, dataMeta) {
  const sorts = sel.selectAll('.xCtrl').nodes().map(d => d.options[d.selectedIndex].value);
  const orders = sel.selectAll('.xOrder').nodes().map(d => d.options[d.selectedIndex].value);
  const labels = sel.selectAll('.xLabel').nodes().map(d => (d.type === 'hidden' ? false : d.checked));
  return sort(data, sorts, orders, labels, dataMeta);
}

function _updateSort(sel, svg, data, dataMeta) {
  const xOrdering = _getSort(sel, svg, data, dataMeta);
  render(svg, svg.property('colorScheme'), xOrdering, dataMeta);
}

function _appendSortByPicker(sel, svg, data, dataMeta) {
  const row = sel.append('div').attr('class', 'row');
  const lcol = row.append('div').attr('class', 'col-xs-7 col-md-4');
  const mcol = row.append('div').attr('class', 'col-xs-4 col-md-4');
  const rcol = row.append('div').attr('class', 'col-xs-1 col-md-4');

  const sortBySelect = lcol.append('select').attr('class', 'xCtrl form-control')
    .on('change', function sortChange() {
      rcol.select('label').remove();

      const currentSelect = select(this).node();
      const key = currentSelect.options[currentSelect.selectedIndex].value;
      const keyIsMetaData = dataMeta.metaData.indexOf(key) > -1;

      rcol.append('label')
        .text(() => (keyIsMetaData ? 'Relabel X? ' : ''))
        .append('input')
        .attr('class', 'xLabel')
        .attr('type', () => (keyIsMetaData ? 'checkbox' : 'hidden'))
        .property('checked', true)
        .on('change', () => {
          _updateSort(sel, svg, data, dataMeta);
        });

      _updateSort(sel, svg, data, dataMeta);
    });
  const ordering = ['Ascending', 'Descending'];
  mcol.append('select').attr('class', 'xOrder form-control')
    .on('change', () => { _updateSort(sel, svg, data, dataMeta); })
    .selectAll('option')
    .data(ordering)
    .enter()
      .append('option')
      .attr('value', d => d)
      .text(d => d);
  if (sel.selectAll('.row').size() > 1) {
    rcol.append('a')
        .on('click', () => { row.remove(); _updateSort(sel, svg, data, dataMeta); })
      .append('span')
        .attr('class', 'glyphicon glyphicon-minus-sign text-danger')
        .attr('style', 'padding-top: 8px; margin-left: -10px; cursor: pointer; cursor: hand;');
  }
  return sortBySelect;
}

function _sortBySelectOptions(sel, metaData, sortedKeysReverse, defaultOptionName) {
  const optGroups = [
    { label: 'Sample Metadata', keys: metaData },
    { label: 'Taxonomic Abundance', keys: sortedKeysReverse },
  ];
  const updateGroup = sel.selectAll('optgroup').data(optGroups);
  updateGroup.exit().remove();
  const enterGroup = updateGroup.enter().append('optgroup');
  const optgroups = updateGroup.merge(enterGroup)
    .attr('label', d => d.label);

  const updateOpt = optgroups.selectAll('option').data(d => d.keys);
  updateOpt.exit().remove();
  const enterOpt = updateOpt.enter().append('option');
  return updateOpt.merge(enterOpt)
    .attr('value', d => d)
    .property('selected', d => (d === defaultOptionName))
    .text(d => d);
}

export function addTaxaPicker(row, levels, selectedLevel) {
  const grp = row.append('div').attr('class', 'col-lg-2 form-group taxaPicker');
  grp.append('label').text('Taxonomic Level');
  grp.append('select')
    .attr('class', 'form-control')
    .on('change', function appendTaxaPicker() {
      const container = select('.container-fluid');
      container.select('.viz.row').remove();
      init(this.selectedIndex);
    })
    .selectAll('option')
    .data(levels)
    .enter()
      .append('option')
        .attr('value', d => d)
        .text(d => `Level ${d}`)
        .property('selected', d => (d === selectedLevel));
  return grp;
}

/* Adds a slider to let users control the width of the barplot's bars.
 *
 * This function was cobbled together from parts of code from
 * addColorPicker(), addSortByPicker(), and _updateSort().
 */
export function addWidthSlider(row, svg, data, dataMeta) {
  const grp = row.append('div').attr('class', 'col-lg-2 form-group widthSlider');
  grp.append('label').text('Bar Width');
  grp.append('input')
    .attr('type', 'range')
    .attr('id', 'barWidthSlider')
    .attr('min', '5')
    .attr('max', '50')
    .attr('value', '10')
    .attr('class', 'form-control')
    .on('input', () => {
      const xOrdering = _getSort(row, svg, data, dataMeta);
      // This line derived from https://stackoverflow.com/a/20154105/10730311.
      const newVal = select('#barWidthSlider').node().value;
      render(svg, svg.property('colorScheme'), xOrdering, dataMeta, newVal);
    });
  return grp;
}

export function addColorPicker(row, svg, legendCol, data, dataMeta) {
  const grp = row.append('div').attr('class', 'col-lg-2 form-group colorPicker');
  grp.append('label').text('Color Palette');
  grp.append('a')
      .attr('style', 'padding-left: 5px;')
      .attr('href', 'https://github.com/d3/d3-scale-chromatic#api-reference')
      .attr('title', 'Click here for more information on the color schemes.')
      .attr('target', '_blank')
      .attr('rel', 'noopener noreferrer')
    .append('span')
      .attr('class', 'glyphicon glyphicon-info-sign');
  const sel = grp.append('select')
    .attr('class', 'form-control')
    .on('change', function changeColorPicker() {
      const colorScheme = this.options[this.selectedIndex].value;
      const xOrdering = _getSort(row, svg, data, dataMeta);
      const chartInfo = render(svg, colorScheme, xOrdering, dataMeta);
      plotLegend(legendCol, chartInfo);
    });

  const discrete = availableColorSchemes.filter(d => d.type === 'o');
  const continuous = availableColorSchemes.filter(d => d.type === 's');
  const optGroups = [
    { label: 'Discrete', keys: discrete },
    { label: 'Continuous', keys: continuous },
  ];

  const updateGroup = sel.selectAll('optgroup').data(optGroups);
  updateGroup.exit().remove();
  const enterGroup = updateGroup.enter().append('optgroup');
  const optgroups = updateGroup.merge(enterGroup)
    .attr('label', d => d.label);

  const updateOpt = optgroups.selectAll('option').data(d => d.keys);
  updateOpt.exit().remove();
  const enterOpt = updateOpt.enter().append('option');
  updateOpt.merge(enterOpt)
    .attr('value', d => d.name)
    .text(d => d.name);

  return grp;
}

export function addSortByPicker(row, svg, data, dataMeta) {
  const { metaData, sortedKeysReverse } = dataMeta;
  const grp = row.append('div').attr('class', 'col-lg-5 form-group sortByPicker');
  grp.append('label').text('Sort Samples By');
  grp.append('a')
      .on('click', () => {
        const selects = grp.selectAll('.xCtrl');
        if (selects.size() === metaData.length + sortedKeysReverse.length + 1) { return; }
        const sel = _appendSortByPicker(grp, svg, data, dataMeta);
        _sortBySelectOptions(sel, metaData, sortedKeysReverse, sortedKeysReverse[0]);
      })
    .append('span')
      .attr('class', 'glyphicon glyphicon-plus-sign')
      .attr('style', 'padding-left: 5px; cursor: pointer; cursor: hand;');

  // Add initial 'Sort By' to sortByGroup
  const sel = _appendSortByPicker(grp, svg, data, dataMeta);
  _sortBySelectOptions(sel, metaData, sortedKeysReverse, sortedKeysReverse[0]);
  return grp;
}

export function addDownloadLinks(sel, svgPlot, svgLegend, level) {
  function _serializer(svg, label) {
    return () => {
      /* global XMLSerializer */
      const serializer = new XMLSerializer();
      let src = serializer.serializeToString(svg.node());
      src = `<?xml version="1.0" standalone="no"?>\r\n${src}`;
      const url = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`;

      /* global document */
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `level-${level}-${label}.svg`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };
  }
  const col = sel.append('div').attr('class', 'col-lg-3');
  col.append('label').html('Download');
  const grp = col.append('div').append('span').attr('class', 'btn-group');
  grp.append('a')
    .text('SVG (bars)')
    .attr('class', 'btn btn-default')
    .on('click', _serializer(svgPlot, 'bars'));
  grp.append('a')
    .text('SVG (legend)')
    .attr('class', 'btn btn-default')
    .on('click', _serializer(svgLegend, 'legend'));
  grp.append('a')
    .text('CSV')
    .attr('href', `level-${level}.csv`)
    .attr('class', 'btn btn-default');
}
