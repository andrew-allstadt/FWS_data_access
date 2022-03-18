import geopandas
from importlib import util

# Optionally, if present, load ArcGIS Online module
try_load = util.find_spec("arcgis")
arcgis_loaded = try_load is not None and try_load.name == "arcgis"
if arcgis_loaded:
    import arcgis


def get_geojson(url, as_esri_sdf=False):
    """
    Generic call for a geojson to geopandas object. Option to return as ESRI
    :param url: URL to geojson file
    :param as_esri_sdf: if False, returns geopandas data frame. If true, returns an ESRI geoaccessor pd
    :return:
    """
    return_value = geopandas.read_file(url)
    if as_esri_sdf:
        if not arcgis_loaded:
            raise ModuleNotFoundError("Module \"arcgis\" not found in environment. Install package or run"
                                      "\"get_bia_regions\" and return a geopandas data frame.")
        else:
            return arcgis.features.GeoAccessor.from_geodataframe(return_value)
    else:
        return return_value

