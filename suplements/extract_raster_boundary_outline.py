import rasterio
from rasterio import features
import fiona
from shapely.geometry import shape

def extract_boundary(input_geotiff, output_shapefile):
    # Open the GeoTIFF file
    with rasterio.open(input_geotiff) as src:
        # Read the raster data
        raster_data = src.read(1)

        # Extract shapes from the raster data
        shapes = features.shapes(raster_data, transform=src.transform)

        # Create a schema for the shapefile
        schema = {
            'geometry': 'Polygon',
            'properties': {'id': 'int'},
        }

        # Create the shapefile with the specified schema
        with fiona.open(output_shapefile, 'w', 'ESRI Shapefile', schema) as dst:
            # Iterate through shapes and add them to the shapefile
            for i, (geom, val) in enumerate(shapes):
                geom = shape(geom)
                if geom.is_empty:
                    continue

                # Create a feature for the shapefile
                feature = {
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [list(geom.exterior.coords)],
                    },
                    'properties': {
                        'id': i + 1,
                    },
                }

                # Write the feature to the shapefile
                dst.write(feature)

if __name__ == "__main__":
    # Replace 'input.tif' with the path to your GeoTIFF file
    input_geotiff = r"F:\OneDrive - str.ucture GmbH\CoKLIMAx\_Palm_DataPreparation\_Raster\DGM_Data_Stadt_Konstanz - DTM , ALKIS\DGM_Konstanz - DTM (Digitale Geländemodelle)\DGM_Konstanz_1m.tif"

    # Replace 'output.shp' with the desired path for the output shapefile
    output_shapefile = r"F:\test.shp"

    extract_boundary(input_geotiff, output_shapefile)
