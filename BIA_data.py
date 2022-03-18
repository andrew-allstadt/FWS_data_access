import pandas as pd
from fws_utilities import get_geojson


def get_tribal_information(url="https://www.bia.gov/tribal-leaders-json"):
    """
    Retrieve Bureau of Indian Affairs contact information for federally recognized tribes. See
    https://www.bia.gov/tribal-leaders-directory for more information.
    :param url: url to endpoint, typically leave as default
    :return: Pandas data frame of current
    """
    return pd.read_json(url)


def get_bia_regions(url="https://www.bia.gov/sites/bia.gov/files/assets/mapfiles/IARegionPolygonGeo.json",
                    as_esri_sdf=False):
    """
    Retrieve Bureau of Indian Affairs regions as a spatial data frame, or optionally a feature set. See
    https://www.bia.gov/tribal-leaders-directory for more information about the data, and either geopandas package or
    https://developers.arcgis.com/python/api-reference/ for more on the format.
    :param url: url to endpoint, typically leave as default
    :param as_esri_sdf: if False, returns geopandas data frame. If true, returns an ESRI geoaccessor pd.
    :return: Pandas/ArcGIS GeoAccessor spatial data frame, or an ArcGIS feature set
    """
    return get_geojson(url, as_esri_sdf)
