from importlib import util
import pandas as pd
import geopandas

# Optionally, if present, load ArcGIS Online module
try_load = util.find_spec("arcgis")
if try_load is not None and try_load.name == "arcgis":
    import arcgis
    arcgis_loaded = True


def get_tribal_information(url="https://www.bia.gov/tribal-leaders-json"):
    """
    Retrieve Bureau of Indian Affairs contact information for each federally recognized tribe. See
    https://www.bia.gov/tribal-leaders-directory for more information.
    :param url: url to endpoint, typically leave as default
    :return: Pandas data frame of current
    """
    return pd.read_json(url)


def get_bia_regions(url="https://www.bia.gov/sites/bia.gov/files/assets/mapfiles/IARegionPolygonGeo.json",
                    as_esri_sdf=False):
    """
    Retrieve Bureau of Indian Affairs regions as a spatial dataframe, or optionally a feature set. See
    https://www.bia.gov/tribal-leaders-directory for more information about the data, and either geopandas package or
    https://developers.arcgis.com/python/api-reference/ for more on the format.
    :param url: url to endpoint, typically leave as default
    :param as_esri_sdf: if False, returns Geopandas data frame. If true, returns an ESRI geoaccessor pd.
    :return: Pandas/ArcGIS GeoAccessor spatial data frame, or an ArcGIS feature set
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
