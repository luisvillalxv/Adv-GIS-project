#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Script Objectives and work plan
#Task: Create a CSV file with data and coordinates to automate onto a map. 
    ## Create a CSV file with data at locations and artifacts found at each hole. 


# In[1]:


pip install geopandas


# In[16]:


pip install fiona


# In[30]:


import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px


# In[104]:


# CSV file data
## See the CSV file data with python
df = pd.read_csv("H:\Kwon\Perry\Assignment7_finalAsgmt\data\PointData_better3.csv")
print(df)


# In[106]:


# CSV to points on a DataFrame
# CSV file
df = pd.read_csv("H:\Kwon\Perry\Assignment7_finalAsgmt\data\PointData_better3.csv")

# Scatterplot
fig = px.scatter_mapbox(df, lat="x", lon="y", hover_name="position", zoom=15, height=500)
# replace "lat", "Lon", and "hoover_name" with your csv file's latitude, logitude, and the collumn you want to represent the points.

# set style to display map
fig.update_layout(mapbox_style="open-street-map")
fig.show()


# In[ ]:


# Future work plan
## I would like to turn the CSV file into a heatmap or buble map using plotly to show all the artifacts at each hole.


# In[ ]:


#CSV to heatmap (show aggegratation of artifacts found from CSV file per hole)

