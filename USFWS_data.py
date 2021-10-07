from importlib import util
import pandas as pd
import geopandas


# Optionally, if present, load ArcGIS Online module
try_load = util.find_spec("arcgis")
if try_load is not None and try_load.name == "arcgis":
    import arcgis
    arcgis_loaded = True


def get_cmt_main_table(legacy_regions=None, as_geopandas=False, url="https://systems.fws.gov/cmt/getCMTBasic.do?REGION="):
    """
    Return the main USFWS Corporate Master Table
    or as a geopandas
    NOTE: You MUST be on the USFWS network for this function to work.

    :param legacy_regions: A list or set of integer USFWS legacy region #s, valid in [0,9]
    :param as_geopandas: Returns same information, but as geopandas data frame with points set to lat/long
    :param url: url to endpoint, typically leave as default
    :return:
    """
    # Check regions parameter
    all_regions = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    if legacy_regions is None:
        regions_ = all_regions
    else:
        if isinstance(legacy_regions, set):
            regions_ = legacy_regions.copy()
        else:
            regions_ = set(legacy_regions)
        if not regions_.issubset(all_regions):
            raise ValueError("One or more invalid region values provided. Here is the set: " + str(regions_))

    # Create and perform query
    region_text = ",".join([str(x) for x in regions_])
    cmt = pd.read_json(url + region_text)

    # If necessary turn to geopandas, and either way return
    if as_geopandas:
        geo_cmt = geopandas.GeoDataFrame(cmt, geometry=geopandas.points_from_xy(cmt.LONG, cmt.LAT))\
            .set_crs("EPSG:4326")
        return geo_cmt
    else:
        return cmt
