# Aquifer properties function
## Objetive
Develop a code that shows some of the relevant characteristics of an aquifer (water table altitude and vadose zone thickness) and creates a geodatabase that contains the layers with this information. As inputs for this code, the user needs to supply well points with the depth to water and a Digital Elevation Model (DEM). The output layers are intended to generate a quick visualization of the aquifer conditions, but the results should be verified because the code uses a generic interpolation model that may not adjust in a valid way to the input data. For this reason, the results for this script also include a Standard Error Map that shows the user the accuracy of the interpolation model.
## Relevance
Generally, the analysis of the conditions of an aquifer starts with the collection of data such as the depth to the water level. However, this information is difficult to interpret quickly because the topographic altitude is generally not linked to the altitude of the water level, and it is necessary to perform spatial interpolation analysis to approximate the conditions of the aquifer, which is usually time-consuming and resource-intensive. Therefore, a model that helps visualize and generate data on the conditions of the aquifer quickly is very useful for generating deeper analysis or identifying areas where more data is needed.
## Link for download the aquifer properties function
[Adv. GIS functions](https://github.com/luisvillalxv/Adv-GIS-project.git)
## Flow process

### Analyze the spatial reference for the input layers
- Review if the coordinate system for both layers is the same.
  - If the coordinate system is different, ask the user for an EPSG code to reproject the layers and save these layers in the output geodatabase.


```python
desc_fc = arcpy.Describe(wellData)
desc_raster = arcpy.Raster(DEM)
if desc_fc.spatialReference.factoryCode != desc_raster.spatialReference.factoryCode:
    print(f"The coordinate system for the Well data points is: {desc_fc.spatialReference.name} ({desc_fc.spatialReference.factoryCode}) and the coordinate system for the DEM is: {desc_raster.spatialReference.name} ({desc_raster.spatialReference.factoryCode})")
    print("A reprojection is needed for develop this analysis")
    CS = int(input("Enter the EPSG code to project both layers: "))
    arcpy.management.Project(wellData,"AquiferProperties.gdb\\welldData_RP",arcpy.SpatialReference(CS))
    arcpy.management.ProjectRaster(DEM, "AquiferProperties.gdb\\DEM_RP", arcpy.SpatialReference(CS))
    wellData = "AquiferProperties.gdb\\welldData_RP"
    DEM = "AquiferProperties.gdb\\DEM_RP"
    print("-------------------------------------------------------------------------")
```
<p align="center">Script 1. Analyze the spatial reference for the input layers and reproject if needed.</p>

 
![image](https://github.com/user-attachments/assets/8f937ea6-b22b-4c2e-b95f-322a084ea1a3)
<p align="center">Figure 1. Example output when the input layers have different coordinate systems.</p>
 
### Calculate the water table altitude for each well point
- List the fields in the well data points layer to select the field that contains the water depth.
- Add the altitude from the DEM to each well data point.
- Subtract well altitude from the water depth to obtain the water table altitude.

```python
# List the fields in Well data points layer.
  fields = arcpy.ListFields(wellData)
  print(f"The field names in the layer {wellData} are:")
  
  # Print the name for each field in the layer.
  for field in fields:
      print(field.name, end = ", ")

  # Ask the user to enter the field that contains the well depth to water.
  wellDepthField = input("Enter the field that contains the well depth to water: ")

  # Extracts DEM values to the well data points to create a new feature class.
  arcpy.sa.ExtractValuesToPoints(wellData, DEM, "AquiferProperties.gdb\\welldData_v2")
  wellData2 = "AquiferProperties.gdb\\welldData_v2"
```
<p align="center">Script 2. Calculate the water table altitude for each well point.</p>

 
![image](https://github.com/user-attachments/assets/d32ac6df-c760-47aa-8ec4-841bd2f95d7a)
<p align="center">Figure 2. Example output to show the user the fields in the attribute table of the well points layer</p>
 
### Calculate the water table altitude surface and its standard error
The script uses an Empirical Bayesian Kriging interpolation model with a generic configuration to calculate the water table altitude surface and its standard error from the water table altitude points, following this logic:
- Set the local variables for the interpolation.
- Set the neighborhood search variables.
- Calculate the interpolation prediction for the water table altitude using the Empirical Bayesian Kriging model.
- Calculate the interpolation standard error.
- Add additional basemaps.
- Show the resultant map.

```python
# Set local variables for the interpolation.
inPointFeatures = "welldData_v2"
zField = "WaterAltitude"
outLayer = "outEBK_GA"
outRaster = "EBK_predict"
transformation = "NONE"
maxLocalPoints = 30
overlapFactor = 0.5
numberSemivariograms = 100

# Set variables for search neighborhood.
radius = 50000
smooth = 0.4
searchNeighbourhood = arcpy.SearchNeighborhoodSmoothCircular(radius, smooth)
outputType = "PREDICTION"
quantileValue = ""
thresholdType = ""
probabilityThreshold = ""
semivariogram = "POWER"

# Execute Empirical Bayesian Kriging for calculate the prediction.
arcpy.EmpiricalBayesianKriging_ga(inPointFeatures, zField, outLayer, outRaster,
                                  cellSize, transformation, maxLocalPoints, overlapFactor, numberSemivariograms,
                                  searchNeighbourhood, outputType, quantileValue, thresholdType, probabilityThreshold,
                                  semivariogram)

# Execute Empirical Bayesian Kriging for calculate the prediction standard error.
outRaster = "EBK_SE"
outputType = "PREDICTION_STANDARD_ERROR"
arcpy.EmpiricalBayesianKriging_ga(inPointFeatures, zField, outLayer, outRaster,
                                  cellSize, transformation, maxLocalPoints, overlapFactor, numberSemivariograms,
                                  searchNeighbourhood, outputType, quantileValue, thresholdType, probabilityThreshold,
                                  semivariogram)
```
<p align="center">Script 3. Calculate the water table altitude surface and its standard error.</p>

### Caluculate the Vadose Zone Tickness
- Subtract the water table altitude surface from the DEM.

```python
vzt = arcpy.sa.RasterCalculator([DEM, "AquiferProperties.gdb\\EBK_predict"], ["x", "y"], "x-y", "LastOf", "LastOf")
vzt.save(directoryPath + "\\AquiferProperties.gdb\\VZT")
```
<p align="center">Script 3. Calculate the Vadose Zone Thickness.</p>

### Generate the visualization of the result layers with Folium
- Create a Folium map.
- Reproject each layer to the WGS 1984 Geographic Coordinate System.
- Add the layers to the Folium map.
- Create a legend for each map.
- Add a layer control.
- Show the Folium map with the layers.

```python
#Add the Water table altitude layer to the folium map for create a results visualization
png_route_wta = directoryPath + "\\WaterTableAltitude.png"

arcpy.management.ProjectRaster("\\AquiferProperties.gdb\\EBK_predict", "\\AquiferProperties.gdb\\raster_wgs84", arcpy.SpatialReference(4326))
raster_obj = arcpy.Raster("\\AquiferProperties.gdb\\raster_wgs84")

val_min = raster_obj.minimum
val_max = raster_obj.maximum
array_raster = arcpy.RasterToNumPyArray(raster_obj)
masked_array = np.ma.masked_where(array_raster == raster_obj.noDataValue, array_raster)

colors = plt.cm.terrain(np.linspace(0, 1, 256))
cmap = ListedColormap(colors)

norm = plt.Normalize(vmin=val_min, vmax=val_max)
colored_array = cmap(norm(masked_array))

plt.imsave(png_route_wta, colored_array)

extent = raster_obj.extent
bounds = [[extent.YMin, extent.XMin], [extent.YMax, extent.XMax]]

m = folium.Map(location=[(extent.YMin + extent.YMax) / 2, (extent.XMin + extent.XMax) / 2], zoom_start=7)

folium.raster_layers.ImageOverlay(
    image=png_route_wta,
    bounds=bounds,
    opacity=0.7,
    name="Water Table Altitude"
).add_to(m)



# Add the DEM layer to the folium map.
png_route_dem = directoryPath + "\\dem.png"

arcpy.management.ProjectRaster(DEM, "\\AquiferProperties.gdb\\raster_wgs84", arcpy.SpatialReference(4326))
raster_obj = arcpy.Raster("\\AquiferProperties.gdb\\raster_wgs84")

val_min = raster_obj.minimum
val_max = raster_obj.maximum
array_raster = arcpy.RasterToNumPyArray(raster_obj)
masked_array = np.ma.masked_where(array_raster == raster_obj.noDataValue, array_raster)

colors = plt.cm.terrain(np.linspace(0, 1, 256))
cmap = ListedColormap(colors)

norm = plt.Normalize(vmin=val_min, vmax=val_max)
colored_array = cmap(norm(masked_array))

plt.imsave(png_route_dem, colored_array)

extent = raster_obj.extent
bounds = [[extent.YMin, extent.XMin], [extent.YMax, extent.XMax]]

m = folium.Map(location=[(extent.YMin + extent.YMax) / 2, (extent.XMin + extent.XMax) / 2], zoom_start=7)

folium.raster_layers.ImageOverlay(
    image=png_route_dem,
    bounds=bounds,
    opacity=0.7,
    name="DEM"
).add_to(m)


# Add the well data points layer to the folium map.
arcpy.conversion.FeaturesToJSON(wellData2, "WellData.geojson", "FORMATTED", "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON", "WGS84")
folium.GeoJson(directoryPath + "\\WellData.geojson", name = "Well points", popup = folium.GeoJsonPopup(fields=["WaterDepth"]), tooltip = "Click for details").add_to(m)


# Add the standard error layer to the folium map.
png_route_se = directoryPath + "\\InterpolationError.png"

arcpy.management.ProjectRaster("\\AquiferProperties.gdb\\EBK_SE", "\\AquiferProperties.gdb\\raster_wgs84", arcpy.SpatialReference(4326))
raster_obj = arcpy.Raster("\\AquiferProperties.gdb\\raster_wgs84")

val_min = raster_obj.minimum
val_max = raster_obj.maximum
array_raster = arcpy.RasterToNumPyArray(raster_obj)
masked_array = np.ma.masked_where(array_raster == raster_obj.noDataValue, array_raster)

colors = plt.cm.bwr(np.linspace(0, 1, 256))
cmap = ListedColormap(colors)

norm = plt.Normalize(vmin=val_min, vmax=val_max)
colored_array = cmap(norm(masked_array))

plt.imsave(png_route_se, colored_array)

extent = raster_obj.extent
bounds = [[extent.YMin, extent.XMin], [extent.YMax, extent.XMax]]


folium.raster_layers.ImageOverlay(
    image=png_route_se,
    bounds=bounds,
    opacity=0.7,
    name="Interpolation standard error"
).add_to(m)



# Add the Vadose Zone Thickness layer to the folium map.
png_route_vzt = directoryPath + "\\Vadose Zone Thickness.png"
arcpy.management.ProjectRaster("\\AquiferProperties.gdb\\VZT", "\\AquiferProperties.gdb\\raster_wgs84", arcpy.SpatialReference(4326))
raster_obj = arcpy.Raster("\\AquiferProperties.gdb\\raster_wgs84")
array_raster = arcpy.RasterToNumPyArray(raster_obj)
masked_array = np.ma.masked_where(array_raster == raster_obj.noDataValue, array_raster)

ranks = [-0.1, 0, 3, 5, 10, 15, 20, 30, 50, 100] 
colors = ["#000000", "#f7fcfd", "#e0ecf4", "#bfd3e6", "#9ebcda", "#8c96c6", "#8c6bb1", "#88419d", "#810f7c", "#4d004b"]
cmap = ListedColormap(colors)

ranks_array = np.digitize(masked_array, ranks, right=True) - 1
colored_array = cmap(ranks_array)

plt.imsave(png_route_vzt, colored_array)

extent = raster_obj.extent
bounds = [[extent.YMin, extent.XMin], [extent.YMax, extent.XMax]]

folium.raster_layers.ImageOverlay(
    image=png_route_vzt,
    bounds=bounds,
    opacity=0.7,
    name="Vadose Zone Thickness"
).add_to(m)


# Add the layers legend to the folium map.
legend_html_vzt = """
 <div style="position: fixed; 
             bottom: 0px; left: 0px; width: 150px; height: auto; 
             border:2px solid grey; background-color: white; z-index:9999;
             font-size:14px;">
 &nbsp; <b>Vadose Zone Thickness</b> <br>
 """

for i in range(len(ranks) - 1):
    legend_html_vzt += f'&nbsp; <i style="background-color:{colors[i]}; width: 30px; height: 20px; display: inline-block;"></i> {ranks[i]:.1f} - {ranks[i + 1]:.1f} <br>'

legend_html_vzt += "</div>"


# Water Table Altitude legend.
legend_html_wta = """
     <div style="position: fixed; 
                 bottom: 0px; left: 150px; width: 150px; height: auto; 
                 border:2px solid grey; background-color: white; z-index:9999;
                 font-size:14px;">
     &nbsp; <b>Water Table Altitude (masl)</b> <br>
     """

num_colors = 9 
for i in range(num_colors):
    color = plt.cm.terrain(i / num_colors)
    legend_html_wta += f'&nbsp; <i style="background-color:rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)}); width: 30px; height: 20px; display: inline-block;"></i> {val_min + i * (val_max - val_min) / num_colors:.1f} - {val_min + (i + 1) * (val_max - val_min) / num_colors:.1f} <br>'

legend_html_wta += "</div>"


# DEM legend.
legend_html_dem = """
     <div style="position: fixed; 
                 bottom: 0px; left: 300px; width: 150px; height: auto; 
                 border:2px solid grey; background-color: white; z-index:9999;
                 font-size:14px;">
     &nbsp; <b>DEM (masl)</b> <br>
     """

num_colors = 9 
for i in range(num_colors):
    color = plt.cm.terrain(i / num_colors)
    legend_html_dem += f'&nbsp; <i style="background-color:rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)}); width: 30px; height: 20px; display: inline-block;"></i> {val_min + i * (val_max - val_min) / num_colors:.1f} - {val_min + (i + 1) * (val_max - val_min) / num_colors:.1f} <br>'


legend_html_dem += "</div>"



# Standard error legend.
legend_html_se = """
     <div style="position: fixed; 
                 bottom: 0px; left: 450px; width: 150px; height: auto; 
                 border:2px solid grey; background-color: white; z-index:9999;
                 font-size:14px;">
     &nbsp; <b>Standard error</b> <br>
     """

num_colors = 9 
for i in range(num_colors):
    color = plt.cm.bwr(i / num_colors)
    legend_html_se += f'&nbsp; <i style="background-color:rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)}); width: 30px; height: 20px; display: inline-block;"></i> {val_min + i * (val_max - val_min) / num_colors:.1f} - {val_min + (i + 1) * (val_max - val_min) / num_colors:.1f} <br>'

legend_html_se += "</div>"


m.get_root().html.add_child(folium.Element(legend_html_vzt))
m.get_root().html.add_child(folium.Element(legend_html_wta))
m.get_root().html.add_child(folium.Element(legend_html_dem))
m.get_root().html.add_child(folium.Element(legend_html_se))


# Add additional base maps to the folium map.
TileLayer("CartoDB positron", name="CartoDB Positron").add_to(m)  
TileLayer("CartoDB dark_matter", name="CartoDB Dark Matter").add_to(m) 
folium.LayerControl().add_to(m)

#Display the folium map
display(m)
```
<p align="center">Script 3. Add the layers, legends, additional basemaps, and layer control to the Folium map.</p>

### Delete the temporary data
- Clean the resultant geodatabase that contains the resultant layers.
- Clean the base workspace.

```python
arcpy.management.Delete("dem.png")
arcpy.management.Delete("InterpolationError.png")
arcpy.management.Delete("Vadose Zone Thickness.png")
arcpy.management.Delete("WaterTableAltitude.png")
arcpy.management.Delete("\\AquiferProperties.gdb\\raster_wgs84")
os.remove(directoryPath + "\\WellData.geojson")
```
<p align="center">Script 3. Delete the temporary data.</p>

## Interactive map
- As a result of the execution of the function, an interactive map is generated in which the resulting layers are presented.

<iframe src="ExampleOfResultsInteractiveMap.html" width="100%" height="800" style="border: none;"></iframe>
