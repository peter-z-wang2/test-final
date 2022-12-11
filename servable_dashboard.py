# %%
import pandas as pd
import numpy as np
import panel as pn

pn.extension('tabulator')

import geoviews as gv
from geoviews import dim

gv.extension('bokeh')

import holoviews as hv
import hvplot.pandas

# %%
# FUNCTIONING DROPDOWN MENU

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import hvplot.pandas 

FILE_NAME = "countincidents.csv"
 
df = pd.read_csv(
    FILE_NAME, delimiter=",", encoding="ISO-8859-1")

gdf = gpd.GeoDataFrame(df, 
    geometry = gpd.points_from_xy(df.Longitude, df.Latitude),
    crs = 'EPSG:4326')

dropdown = pn.widgets.Select(name='dropdown', options=['# incidents', '# incidents/100k people'])

plot = gdf.hvplot(geo=True, tiles=True, size=dropdown, color=dropdown, cmap='viridis', xlabel='Longitude', 
           ylabel='Latitude', global_extent=True, groupby='Year')

plot2 = gdf.hvplot(geo=True, tiles=True, size=dropdown, color=dropdown, cmap='viridis', xlabel='Longitude', 
           ylabel='Latitude', global_extent=True, groupby='Year')

pn.Column(pn.WidgetBox(dropdown), plot, plot2)

# %%
terror = pd.read_csv('globalterrorism.csv', encoding="ISO-8859-1", low_memory=False)

# %%
filter_terror = terror.loc[terror['iyear'] >= 1994].loc[terror['longitude'].notnull()].loc[terror['latitude'].notnull()]

# %%
filter_terror['weaptype1_txt'] = filter_terror['weaptype1_txt'].replace('Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)', 'Vehicle')

# %%
country_df = filter_terror \
    .groupby(['country_txt', 'iyear', 'weaptype1_txt'], as_index = False) \
    .agg(
        latitude = ('latitude', 'mean'),
        longitude =('longitude', 'mean'),
        num_incidents = ('iyear', "count"),
        total_killed = ("nkill", "sum")
    )


region_df = filter_terror \
    .groupby(['region_txt', 'iyear', 'weaptype1_txt'], as_index = False) \
    .agg(
        latitude = ('latitude', 'mean'),
        longitude =('longitude', 'mean'),
        num_incidents = ('iyear', "count"),
        total_killed = ("nkill", "sum")
    )
    

# %%

country_gdf = gpd.GeoDataFrame(region_df, 
    geometry = gpd.points_from_xy(region_df.longitude, region_df.latitude),
    crs = 'EPSG:4326')

statistic_dropdown = pn.widgets.Select(name='Statistic', options=['num_incidents', 'total_killed'])

country_plot = country_gdf.hvplot(
    geo=True,
    tiles=True,
    size=statistic_dropdown,
    color=statistic_dropdown,
    cmap='viridis',
    xlabel='Longitude',
    ylabel='Latitude',
    global_extent=True,
    groupby=['iyear', 'weaptype1_txt']
    )


pn.Column(pn.WidgetBox(statistic_dropdown), country_plot)

# %%
statistic_dropdown = pn.widgets.Select(name='Statistic', options=['num_incidents', 'total_killed'])

weapons_by_country = country_df.hvplot(
    x="iyear",
    y=statistic_dropdown,
    kind='line',
    groupby=['country_txt', 'weaptype1_txt'],
    widgets = {
        "country_txt": pn.widgets.Select,
#         "Weapon Type": pn.widgets.Select,
    },
    widget_location = "left_top"
    
)
pn.Column(pn.WidgetBox(statistic_dropdown), weapons_by_country)


# %%
statistic_dropdown = pn.widgets.Select(name='Statistic', options=['num_incidents', 'total_killed'])

weapons_by_region = region_df.hvplot(
    x="iyear",
    y=statistic_dropdown,
    kind='line',
    groupby=['region_txt', 'weaptype1_txt'],
    widget_location = "left_top"
)
pn.Row(weapons_by_region)

# New weapon_df (resets the index)
weapon_df = (filter_terror
         .groupby(["country_txt", "weaptype1_txt"])
         .agg(num_incidents=('weaptype1_txt', 'count'), total_killed=('nkill', 'sum'))
         .reset_index()
        )

statistic_dropdown = pn.widgets.Select(name='Statistic', options=['num_incidents', 'total_killed'])
# Manually-added country dropdown
country_list = sorted(weapon_df["country_txt"].unique())
country_dropdown = pn.widgets.Select(name='Country', options=country_list)

# # New code: uses manually-added country dropdown
weapon_idf = weapon_df.interactive()
weapon_pipeline = (
    weapon_idf
    .loc[weapon_idf["country_txt"] == country_dropdown]
    .loc[weapon_idf[statistic_dropdown] != 0]
    .groupby(["weaptype1_txt"])[statistic_dropdown]
    .nlargest(5) # why doesn't this work??? and why does it throw an error when I remove it???
    .reset_index()
    .sort_values(by=statistic_dropdown)  
)

weapon_plot = weapon_pipeline.hvplot(
    kind="bar",
    x="weaptype1_txt",
    y=statistic_dropdown,
    width=1000,
).output()


country_targ_df = filter_terror \
    .groupby(['country_txt', 'targtype1_txt'], as_index = False) \
    .agg(
        num_incidents = ('targtype1_txt', "count"),
        total_killed = ("nkill", "sum")
    )

country_targ_idf = country_targ_df.interactive()
country_targ_pipeline = (
    country_targ_idf
    .loc[country_targ_idf["country_txt"] == country_dropdown]
    .loc[country_targ_idf[statistic_dropdown] != 0]
    .groupby(["targtype1_txt"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(7)
)

country_targ_plot = country_targ_pipeline.hvplot(
    kind="bar",
    x="targtype1_txt",
    y=statistic_dropdown,
    width=1000,
).opts(
    fontsize = {"xticks": 8},
).output()



group_df = filter_terror \
    .groupby(['country_txt', 'gname'], as_index = False) \
    .agg(
        num_incidents = ('gname', "count"),
        total_killed = ("nkill", "sum")
    )

group_idf = group_df.interactive()
group_pipeline = (
    group_idf
    .loc[group_idf["country_txt"] == country_dropdown]
    .loc[group_idf[statistic_dropdown] != 0]
    .groupby(["gname"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(5)
)


group_plot = group_pipeline.hvplot(
    kind="bar",
    x="gname",
    y=statistic_dropdown,
    width=1000,
).opts(
    fontsize = {"xticks": 8},
).output()


natlty_df = filter_terror \
    .groupby(['country_txt', 'natlty1_txt'], as_index = False) \
    .agg(
        num_incidents = ('gname', "count"),
        total_killed = ("nkill", "sum")
    )

natlty_idf = natlty_df.interactive()
natlty_pipeline = (
    natlty_idf
    .loc[natlty_idf["country_txt"] == country_dropdown]
    .loc[natlty_idf[statistic_dropdown] != 0]
    .groupby(["natlty1_txt"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(5)
)

natlty_plot = natlty_pipeline.hvplot(
    kind="bar",
    x="natlty1_txt",
    y=statistic_dropdown,
    width=1000,
).output()

pn.Column(country_dropdown, statistic_dropdown, pn.Row(weapon_plot, group_plot), pn.Row(country_targ_plot, natlty_plot))


# %%
# New region_region_weapon_df (resets the index)
region_region_weapon_df = (filter_terror
         .groupby(["region_txt", "weaptype1_txt"])
         .agg(num_incidents=('weaptype1_txt', 'count'), total_killed=('nkill', 'sum'))
         .reset_index()
        )

statistic_dropdown = pn.widgets.Select(name='Statistic', options=['num_incidents', 'total_killed'])
# Manually-added region dropdown
region_list = sorted(region_region_weapon_df["region_txt"].unique())
region_dropdown = pn.widgets.Select(name='region', options=region_list)

# # New code: uses manually-added region dropdown
region_weapon_idf = region_region_weapon_df.interactive()
region_weapon_pipeline = (
    region_weapon_idf
    .loc[region_weapon_idf["region_txt"] == region_dropdown]
    .loc[region_weapon_idf[statistic_dropdown] != 0]
    .groupby(["weaptype1_txt"])[statistic_dropdown]
    .nlargest(5) # why doesn't this work??? and why does it throw an error when I remove it???
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(7)
)

region_weapon_plot = region_weapon_pipeline.hvplot(
    kind="bar",
    x="weaptype1_txt",
    y=statistic_dropdown,
    width=1000,
).opts(
    fontsize = {"xticks": 8},
).output()


region_targ_df = filter_terror \
    .groupby(['region_txt', 'targtype1_txt'], as_index = False) \
    .agg(
        num_incidents = ('targtype1_txt', "count"),
        total_killed = ("nkill", "sum")
    )

region_targ_idf = region_targ_df.interactive()
region_targ_pipeline = (
    region_targ_idf
    .loc[region_targ_idf["region_txt"] == region_dropdown]
    .loc[region_targ_idf[statistic_dropdown] != 0]
    .groupby(["targtype1_txt"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(7)
)

region_targ_plot = region_targ_pipeline.hvplot(
    kind="bar",
    x="targtype1_txt",
    y=statistic_dropdown,
    width=1000,
).output()



region_group_df = filter_terror \
    .groupby(['region_txt', 'gname'], as_index = False) \
    .agg(
        num_incidents = ('gname', "count"),
        total_killed = ("nkill", "sum")
    )

region_group_idf = region_group_df.interactive()
region_group_pipeline = (
    region_group_idf
    .loc[region_group_idf["region_txt"] == region_dropdown]
    .loc[region_group_idf[statistic_dropdown] != 0]
    .groupby(["gname"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(5)
)


region_group_plot = region_group_pipeline.hvplot(
    kind="bar",
    x="gname",
    y=statistic_dropdown,
    width=1000,
).opts(
    fontsize = {"xticks": 8},
).output()


region_natlty_df = filter_terror \
    .groupby(['region_txt', 'natlty1_txt'], as_index = False) \
    .agg(
        num_incidents = ('gname', "count"),
        total_killed = ("nkill", "sum")
    )

region_natlty_idf = region_natlty_df.interactive()
region_natlty_pipeline = (
    region_natlty_idf
    .loc[region_natlty_idf["region_txt"] == region_dropdown]
    .loc[region_natlty_idf[statistic_dropdown] != 0]
    .groupby(["natlty1_txt"])[statistic_dropdown]
    .nlargest(5)
    .reset_index()
    .sort_values(by=statistic_dropdown)
    .tail(5)
)

region_natlty_plot = region_natlty_pipeline.hvplot(
    kind="bar",
    x="natlty1_txt",
    y=statistic_dropdown,
    width=1000,
).output()


pn.Column(region_dropdown, statistic_dropdown, pn.Row(region_weapon_plot, region_group_plot), pn.Row(region_targ_plot, region_natlty_plot))

# %%
# Incidents per country per year (map visualization)

incident_data = pd.read_csv('countincidents.csv', encoding="ISO-8859-1", low_memory=False)

country_incidents = gv.Dataset(incident_data, kdims=['Year'])
points = country_incidents.to(gv.Points, ['Longitude', 'Latitude'], ['# incidents/100k people', '# incidents', 'Country'])

tiles = gv.tile_sources.Wikipedia

map_plot = pn.panel(tiles * points.opts(
    color='# incidents', cmap='viridis', size=dim('# incidents')*0.005,
    tools=['hover'], global_extent=True, width=600, height=600))

map_plot

# %%
y_vals = ['Private Citizens & Property',
          'Military',
          'Police',
          'Government (General)',
          'Business',
          'Religious Figures/Institutions',
          'Educational Institution',
          'Violent Political Party',
          'Tourists',
          'Journalists & Media',
         ]

top10_targ = filter_terror \
    .groupby(['targtype1_txt', 'iyear']) \
    .agg(
        num_incidents = ('targtype1_txt', 'count'),
        total_killed = ('nkill', 'sum')
    ).reset_index() \

top10_targ = top10_targ.loc[top10_targ['targtype1_txt'].isin(y_vals)] \
    


pn.Column(
    top10_targ.hvplot.line(x='iyear', y='num_incidents', by='targtype1_txt', height=500, width=1000),
    top10_targ.hvplot.line(x='iyear', y='total_killed', by='targtype1_txt', height=500, width=1000)
)

# %%
# Top 10 countries by # incidents/100k people line graph

top10 = pd.read_csv("top10incidents.csv", encoding="ISO-8859-1", low_memory=False)

top10.hvplot.line(x='Year', y=['Iraq', 'West Bank and Gaza Strip', 'Afghanistan', 'Libya', 'Somalia', 'Israel', 'Bahrain', 'Lebanon', 'Syria', 'Yemen'], 
                value_label='# incidents/100k people', legend='right', title='Top 10 Countries by # incidents/100k people', height=500, width=1000)

# %%
# Build interactive dashboard

template = pn.template.FastListTemplate(
    title='insert title here',
    background_color='#63d8ff',
    neutral_color='#F08080',
    header_background='#0072B5',
    main=[pn.Row(pn.Column(pn.pane.Markdown('insert markdown here'), background='#0072B5')),
          pn.Row(pn.Column(map_plot)),
          pn.Row(pn.pane.Str('test1', background='#f0f0f0', height=100, sizing_mode='stretch_width'), width_policy='max', height=200),
          pn.Row(pn.layout.HSpacer(), '* Item 1\n* Item2', pn.layout.HSpacer(), '1. First\n2. Second', pn.layout.HSpacer()),
          pn.Row(pn.pane.HTML(background='#f307eb', width=100, height=100))
         ]
)
template.servable();


