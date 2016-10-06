def _extract_to_level(taxonomy, table, max_level=None):
    # Assemble the taxonomy data
    taxa = {}
    max_obs_lvl = 0
    for k, v in taxonomy.iteritems():
        levels = [x.strip() for x in v.split(';')]
        max_obs_lvl = len(levels) if len(levels) > max_obs_lvl else max_obs_lvl
        taxa[k] = {'taxonomy': levels}
    table.add_metadata(taxa, axis='observation')

    if max_level is None:
        max_level = max_obs_lvl

    if max_level > max_obs_lvl:
        raise ValueError('Requested max_level of %d is larger than max_level '
                         'available in taxonomy data (%d).' % (max_level,
                                                               max_obs_lvl))

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_level + 1):
        def bin_f(id_, x):
            if len(x['taxonomy']) < max_obs_lvl:
                padding = ['__'] * (max_obs_lvl - len(x['taxonomy']))
                x['taxonomy'].extend(padding)
            return ';'.join(x['taxonomy'][:level])
        collapsed_tables.append(table.collapse(bin_f, norm=False,
                                               min_group_size=1,
                                               axis='observation'))

    return collapsed_tables
