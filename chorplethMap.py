import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# Streamlit app title
st.title("Washington State Counties - Muslim Population")

# Load processed data
data_path = "county_counts.csv"  # Replace with your data file path
data = pd.read_csv(data_path)

# Ensure County column matches GeoJSON field
data["County"] = data["County"].str.strip().str.title()

# Load GeoJSON file for Counties
geojson_path = "WA_County_Boundaries.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Extract county centroids for labeling
county_centroids = []
for feature in geojson_data["features"]:
    # Get the county name and calculate the center of the polygon
    county_name = feature["properties"]["JURISDICT_NM"]
    coordinates = feature["geometry"]["coordinates"]

    # For MultiPolygon, use the first polygon's centroid
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Calculate the centroid (average of all coordinates)
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])

    # Add to centroids list
    county_centroids.append({"county": county_name, "lon": lon, "lat": lat})

# Create a DataFrame for centroids
centroid_df = pd.DataFrame(county_centroids)

# Create a Choropleth map with an updated color scale
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["County"],  # Match data column
    z=data["Count"],  # Column for coloring
    featureidkey="properties.JURISDICT_NM",  # Match GeoJSON key
    colorscale="Plasma",  # Use a visually appealing color scale
    marker_opacity=0.8,  # Set transparency
    marker_line_width=1.2  # Set boundary width for better clarity
))

# Add county labels as text
for _, row in centroid_df.iterrows():
    fig.add_trace(go.Scattermapbox(
        lon=[row["lon"]],  # Longitude of the centroid
        lat=[row["lat"]],  # Latitude of the centroid
        mode="text",  # Only text
        text=row["county"],  # County name
        textfont=dict(size=10, color="black"),  # Adjust font size and color
        hoverinfo="text",
        showlegend=False  # Hide legend for text
    ))

# Adjust map layout for Washington State
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Zoom level for WA
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on WA
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(
        title="Muslim Population",  # Add a clear title
        tickprefix="",  # Optional: Add prefix if needed
        ticksuffix="",  # Optional: Add suffix if needed
    )
)

# Display map in Streamlit
st.plotly_chart(fig, use_container_width=True)
############ City #########

# Streamlit app title
st.title("Washington State Cities - Population")

# Load the data
data_path = "preprocessed_ld_data_City.csv"  # Replace with your CSV file path
data = pd.read_csv(data_path)
data["City"] = data["City"].str.title()
# Debug: Check data structure
print(data.head())

# Load GeoJSON file for cities
geojson_path = "CityLimits.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Create a Choropleth map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["City"],  # Column from CSV
    z=data["total_population"],  # Column for coloring
    featureidkey="properties.CITY_NM",  # Match GeoJSON key
    colorscale="Viridis",  # Adjust the color scale
    marker_opacity=0.8,  # Adjust transparency
    marker_line_width=0.5  # Boundary width
))

# Adjust map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Adjust zoom level
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center the map on Washington State
    margin={"r": 0, "t": 0, "l": 0, "b": 0}  # Remove margins
)

# Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)

##### School district information   #################################

# Streamlit app title
st.title("Washington State School Districts - Muslim Population")

# Step 1: Load CSV data
data_path = "district_muslim_count.csv"  # Replace with your CSV file path
data = pd.read_csv(data_path)

# Ensure School District column matches GeoJSON field
data["School District"] = data["School District"].str.strip().str.title()

# Step 2: Load GeoJSON for School Districts
geojson_path = "Washington_School_Districts_2024.geojson"  # Replace with your GeoJSON file path
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Step 3: Create the Choropleth map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["School District"],  # Match data column
    z=data["Muslim Count"],  # Column for coloring
    featureidkey="properties.LEAName",  # Match GeoJSON key for school districts
    colorscale="Blues",  # Use an appealing color scale
    marker_opacity=0.8,  # Set transparency
    marker_line_width=1.2  # Set boundary width
))

# Step 4: Add School District Labels
# Extract centroids for labeling
district_centroids = []
for feature in geojson_data["features"]:
    district_name = feature["properties"]["LEAName"]
    coordinates = feature["geometry"]["coordinates"]

    # For MultiPolygon, use the first polygon's centroid
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Calculate the centroid (average of all coordinates)
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])

    # Add to centroids list
    district_centroids.append({"district": district_name, "lon": lon, "lat": lat})

# Create a DataFrame for centroids
centroid_df = pd.DataFrame(district_centroids)

# Add district labels as text
for _, row in centroid_df.iterrows():
    fig.add_trace(go.Scattermapbox(
        lon=[row["lon"]],  # Longitude of the centroid
        lat=[row["lat"]],  # Latitude of the centroid
        mode="text",  # Only text
        text="",  # District name
        textfont=dict(size=9, color="black"),  # Adjust font size and color
        hoverinfo="text",
        showlegend=False  # Hide legend for text
    ))

# Step 5: Adjust map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,  # Zoom level for WA
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on WA
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(
        title="Muslim Population",  # Add a clear title
        tickprefix="",  # Optional: Add prefix if needed
        ticksuffix="",  # Optional: Add suffix if needed
    )
)

# Step 6: Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)


#############3 LD  ################

# Streamlit app title
st.title("Choropleth Map for Muslim Population by Legislative District")

# Load data
data_path = "preprocessed_ld_data.csv"  # Replace with your CSV file
data = pd.read_csv(data_path)

# Ensure columns are correct
data["Legislative District"] = data["Legislative District"].apply(
    lambda x: f"Legislative (House) District {int(float(x))}" if pd.notna(x) else None
)
data["non_voters"] = data["total_population"] - data["voters"]

# Load GeoJSON file
geojson_path = "wa_legislative_districts.geojson"  # Replace with your GeoJSON file
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Calculate centroids for districts
centroids = []
for feature in geojson_data["features"]:
    district_name = feature["properties"]["NAMELSAD"]
    coordinates = feature["geometry"]["coordinates"]

    # Handle MultiPolygon
    if feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0]

    # Centroid calculation
    lon = sum([point[0] for point in coordinates[0]]) / len(coordinates[0])
    lat = sum([point[1] for point in coordinates[0]]) / len(coordinates[0])
    centroids.append({"district": district_name, "lon": lon, "lat": lat})

centroid_df = pd.DataFrame(centroids)

# Create a choropleth map for the Muslim population
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["Legislative District"],  # Match column in data
    z=data["total_population"],  # Population coloring
    featureidkey="properties.NAMELSAD",  # Match GeoJSON key
    colorscale="Viridis",
    marker_opacity=0.6,
    marker_line_width=0.5,
    name="Population"
))

# Add scatter points for voters (green) and non-voters (red)
for _, row in centroid_df.iterrows():
    ld = row["district"]
    if ld in data["Legislative District"].values:
        voter_count = data.loc[data["Legislative District"] == ld, "voters"].values[0]
        non_voter_count = data.loc[data["Legislative District"] == ld, "non_voters"].values[0]

        # Green dot for voters
        fig.add_trace(go.Scattermapbox(
            lon=[row["lon"]],
            lat=[row["lat"]],
            mode="markers",
            marker=dict(size=8, color="green"),
            name="Voters",
            text=f"Voters: {voter_count}",
            hoverinfo="text",
            showlegend=False
        ))

        # Red dot for non-voters
        fig.add_trace(go.Scattermapbox(
            lon=[row["lon"] + 0.05],  # Slight shift to avoid overlap
            lat=[row["lat"]],
            mode="markers",
            marker=dict(size=8, color="red"),
            name="Non-Voters",
            text=f"Non-Voters: {non_voter_count}",
            hoverinfo="text",
            showlegend=False
        ))

# Update map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,
    mapbox_center={"lat": 47.7511, "lon": -120.7401},
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    legend=dict(orientation="h")
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

############### CD MAPPING #############

# Streamlit app title
st.title("Washington State Congressional Districts - Population")

# Load CSV data
csv_path = "preprocessed_ld_data_Congressional District.csv"  # Replace with your CSV file
data = pd.read_csv(csv_path)

# Load GeoJSON data
geojson_path = "Congressional District.geojson"  # Replace with your GeoJSON file
with open(geojson_path, "r") as file:
    geojson_data = json.load(file)

# Debug to verify matching keys
geojson_keys = [feature["properties"]["NAMELSAD"] for feature in geojson_data["features"]]
data_keys = data["Congressional District"].unique()
if not set(data_keys).issubset(set(geojson_keys)):
    st.write("Warning: Mismatch between CSV and GeoJSON district names.")
    st.write(f"CSV Keys: {data_keys}")
    st.write(f"GeoJSON Keys: {geojson_keys}")

# Create the map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    locations=data["Congressional District"],  # Column in the CSV
    z=data["total_population"],  # Population column for color scale
    featureidkey="properties.NAMELSAD",  # GeoJSON key to match with locations
    colorscale="Viridis",  # Adjust color scheme
    colorbar_title="Population",  # Title for the color bar
    marker_opacity=0.7,  # Adjust opacity
    marker_line_width=1  # Boundary width
))

# Add district labels (optional)
district_labels = []
for feature in geojson_data["features"]:
    name = feature["properties"]["NAMELSAD"]
    coordinates = feature["geometry"]["coordinates"]

    # Handle both Polygon and MultiPolygon
    if feature["geometry"]["type"] == "Polygon":
        coordinates = coordinates[0]
    elif feature["geometry"]["type"] == "MultiPolygon":
        coordinates = coordinates[0][0]

    # Calculate the centroid
    lon = sum([point[0] for point in coordinates]) / len(coordinates)
    lat = sum([point[1] for point in coordinates]) / len(coordinates)

    # Add to district_labels
    district_labels.append({"district": name, "lon": lon, "lat": lat})

# Add district labels to the map
for label in district_labels:
    fig.add_trace(go.Scattermapbox(
        lon=[label["lon"]],
        lat=[label["lat"]],
        mode="text",
        text=label["district"].split()[-1],  # Display only the district number
        textfont=dict(size=12, color="black"),
        hoverinfo="text",
        showlegend=False
    ))

# Update map layout
fig.update_layout(
    mapbox_style="carto-positron",  # Map style
    mapbox_zoom=6,  # Zoom level
    mapbox_center={"lat": 47.7511, "lon": -120.7401},  # Center on Washington State
    margin={"r": 0, "t": 0, "l": 0, "b": 0}  # Remove margins
)

# Display the map
st.plotly_chart(fig, use_container_width=True)
