import arcpy
import pandas as pd
import os
def getParameterInfo():
    # First parameter
    param0 = arcpy.Parameter(
        displayName="Workspace",
        name="in_workspace",
        datatype="DEWorkspace",
        parameterType="Required",
        direction="Input")
    
    # Second parameter
    param1 = arcpy.Parameter(
        displayName="Class Name",
        name="class_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
    
    # Third parameter
    param2 = arcpy.Parameter(
        displayName="Class Value",
        name="class_value",
        datatype="GPLong",
        parameterType="Required",
        direction="Input")
    
    # Fourth parameter
    param3 = arcpy.Parameter(
        displayName="Output Folder",
        name="out_file",
        datatype="DEFile",
        parameterType="Required",
        direction="Output")
    param3.filter.list = ['txt', 'csv']
    
    params = [param0, param1, param2, param3]
    return params
def count_pixels_for_class(raster,class_name, class_value, output_csv):
    # Convert raster to a table with pixel counts using RasterToTable
    output_table = os.path.join(arcpy.env.workspace, f"{raster}")
    
    
    # List to store results
    pixel_count = []
    
    # Query the table to find pixel counts for the class
    with arcpy.da.SearchCursor(output_table, [class_name, "Count"]) as cursor:
        for row in cursor:
            if row[0] == class_value:
                pixel_count.append({"Raster": raster, "Class": row[0], "Pixel Count": row[1]})
    
    # Convert results to a DataFrame
    df = pd.DataFrame(pixel_count)
    
    # If there are results, append to CSV file
    if not df.empty:
        df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
        print(f"Pixel count for {raster} exported to {output_csv}")
    else:
        print(f"No pixels found for class {class_value} in {raster}")
# Get parameter values from ArcGIS
workspace = arcpy.GetParameterAsText(0)  # Workspace input
class_name = arcpy.GetParameterAsText(1)  # Class name input
class_value = int(arcpy.GetParameterAsText(2))  # Class value input
output_csv = arcpy.GetParameterAsText(3)  # Output CSV file
    
# Set the workspace for ArcPy
arcpy.env.workspace = workspace
    
# Clear the CSV file if it already exists
if os.path.exists(output_csv):
	os.remove(output_csv)
# Get a list of raster datasets in the workspace
rasters = arcpy.ListRasters()
# Loop through each raster in the list
for raster in rasters:
	count_pixels_for_class(raster, class_name, class_value, output_csv)
