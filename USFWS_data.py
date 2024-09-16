from importlib import util
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import requests


def get_cmt_main_table(legacy_regions=None, as_geopandas=False,
                       url="https://systems.fws.gov/cmt/getCMTBasic.do?REGION=",
                       encoding_errors='strict'):
    """
    Return the main USFWS Corporate Master Table
    or as a geopandas
    NOTE: You MUST be on the USFWS network for this function to work.

    :param legacy_regions: A list or set of integer USFWS legacy region #s, valid in [0,9]
    :param as_geopandas: Returns same information, but as geopandas data frame with points set to lat/long
    :param url: url to endpoint, typically leave as default
    :param encoding_errors: CMT often has encoding errors in it. Change to ignore if function won't run.
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
    cmt = pd.read_json(url + region_text, encoding_errors)

    # If necessary turn to geopandas, and either way return
    if as_geopandas:
        geo_cmt = geopandas.GeoDataFrame(cmt, geometry=geopandas.points_from_xy(cmt.LONG, cmt.LAT),
                                         crs="EPSG:4326")
        return geo_cmt
    else:
        return cmt


def plot_cmt(legacy_regions=None):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    geo_cmt = get_cmt_main_table(legacy_regions=None, as_geopandas=True)
    ax = world.plot(color='white', edgecolor='black')
    geo_cmt.plot(ax=ax, color="red")


# Function to look up FWS Taxon code
def get_fws_taxon_code(sci_name, url="https://ecos.fws.gov/ServCatServices/v2/rest/taxonomy/searchByScientificName/"):
    print(sci_name)
    sci_name_ = sci_name.replace(" spp.", "").replace(" ", "%20")
    result = requests.get(url+sci_name_+"?format=JSON")
    sci_names = {x['ScientificName']: x['TaxonCode'] for x in result.json()}
    if sci_name in sci_names.keys():
        return sci_names[sci_name]
    else:
        return None
