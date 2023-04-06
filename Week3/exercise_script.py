import os
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file(os.path.abspath('data_files/Counties.shp'))
wards = gpd.read_file(os.path.abspath('data_files/NI_Wards.shp'))

print(counties.crs)
print(wards.crs)
print(counties.crs == wards.crs)
print(wards)

counties.to_crs(epsg='4807')
wards.to_crs(epsg='4807')

# your analysis goes here...
wards_reppoint = wards.copy()
wards_reppoint['geometry'] = wards_reppoint['geometry'].representative_point()

join = gpd.sjoin(counties, wards_reppoint, how='inner', lsuffix='left', rsuffix='right')
join.shape
print(join)
join_total = join['Population'].sum()
wards_total = wards['Population'].sum()
print(join.groupby(['CountyName', 'Ward'])['Population'].sum())
print('Population in wards item is: ', wards_total)
print('Population from joined table is: ', join_total)
print(wards_total == join_total)

County_populations = dict()

for county in counties['CountyName'].unique():  #loop to display county names and populations
    County_pop = join.loc[join['CountyName'] == county, 'Population'].sum()
    County_populations.update({county: County_pop})

print(County_populations)
print




# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
print(myCRS)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = True
gridlines.bottom_labels = True

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

#ward_reppoint_plot = wards_reppoint.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                     #  legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='g', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='g')]

ax.legend(county_handles, ['County Lines'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('sample_map.png', dpi=300, bbox_inches='tight')
