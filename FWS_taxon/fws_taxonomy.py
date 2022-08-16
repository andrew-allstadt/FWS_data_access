# Author: A. Allstadt
# Last updated: 8/15/2022

# Notes:
# User functions are named for the API they reference and don't follow PEP8
# Camel case, all JSON calls, but user will just see pandas data frames returned.
# Copied logging pattern from ITIS package: https://github.com/nelas/itis.py/blob/master/itis.py

import requests
import logging
import re
import pandas as pd
from numpy import isnan
from requests.utils import requote_uri

# Create logger.
logger = logging.getLogger('fwsTaxonomy')
logger.setLevel(logging.DEBUG)
logger.propagate = False
formatter = logging.Formatter('[%(levelname)s] %(asctime)s @ %(module)s %(funcName)s (l%(lineno)d): %(message)s')

# Console handler for logger.
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


class fwsTaxonomy:

    def __init__(self):
        """
        Initialization function. Set some constants for later use and check that connection can be made. Throws
        connection error if connection cannot be made.
        :param: None
        :return: None
        """

        # Constants for use in this class
        self.baseURL = 'https://ecos.fws.gov/ServCatServices/v2/rest/taxonomy/'

        # Implemented services
        self.implementedServices = ['searchByScientificName', 'searchByCodes']

        # List of all services in FWSpecies
        self.allServices = ['searchByScientificName', 'searchByCodes']

        # Services that end in "&format=JSON" rather than "?format=JSON"
        self.json_extension = ['searchByCodes']

        # Test we can connect with simple query from example document
        logger.info('Initiating contact with FWS Taxonomy...')

        if requests.get(self.baseURL + "searchByScientificName/Branta%20canadensis?format=JSON").status_code == 200:
            logger.info('Connected to ITIS web services.')
        else:
            raise ConnectionError("Error connecting to FWS Taxonomy. Check your connection and that you "
                                  "are on the FWS network or VPN.")
        logger.info('FWS taxonomy initialized.')

    def searchByScientificName(self, scientific_name: str):
        """
        Search FWS Taxonomy by a scientific name. These terms are stripped from the end
        of the string if present and preceded by a space: spp., spp, sp, sp.
        :param scientific_name: string, species name.
        :return: Returns data frame with the search results, including an empty data frame with the expected columns if
        no results were returned.
        """
        # Check species name is a string and is not blank.
        if type(scientific_name) != str or scientific_name == "":
            raise TypeError("scientific_name must be a string and cannot be blank.")
        # Strip species abbreviations, in place of a genus for example.
        # Also strip whitespace
        sci_name = scientific_name.strip()
        sci_name = re.sub('[\s+]', ' ', sci_name)
        for rm in ['\s+spp+\.$', '\s+spp$', '\s+sp+\.$', '\s+sp$']:
            sci_name = re.sub(rm, "", sci_name, flags=re.IGNORECASE)
        sci_name = sci_name.strip()

        # Perform query
        # TODO: Bring back for some basic processing before returning.
        return self._call_taxon("searchByScientificName", sci_name)

    def searchByTaxonCodes(self, taxoncodes: list = None):
        """
        Search FWS Taxonomy by FWS Taxon codes (not to be confused with ITIS TSNs.
        :param taxoncodes: list of codes, in int form or strings convertable to int
        :return: Returns data frame with the search results, including an empty data frame with the expected columns if
        no results were returned.
        """
        # Return if nothing. If a single int or string convert to list.
        if taxoncodes is None:
            return None
        if type(taxoncodes) == str or type(taxoncodes) == int:
            taxoncodes = list(taxoncodes)
        elif type(taxoncodes) != list:
            raise TypeError("taxoncodes must be a list, or a single int or string.")

        # Convert to ints to make sure they're valid. Then back to string.
        for i in range(0, len(taxoncodes)):
            taxoncodes[i] = int(taxoncodes[i])
            taxoncodes[i] = str(taxoncodes[i])

        query = "taxoncode?codes=" + ",".join(taxoncodes)

        # Perform query
        # TODO: Bring back for some basic processing before returning.
        return self._call_taxon("searchByCodes", query)

    def _construct_call(self, function_name: str, query: str):
        """
        Puts together base URL, the proper function, query together into a format to return. Raises error if function
        is not in the implemented list.
        :param function_name:
        :param query:
        :return:
        """
        if function_name not in self.implementedServices:
            if function_name in self.allServices:
                raise NotImplementedError("Function: " + function_name +
                                          " is part of FWS Taxomonmy web serivces, but is not yet implemented in"
                                          " this package.")
            else:
                raise ValueError("Function: is not part of FWS Taxonomy web services. Please check your input.")

        json_extension = "?format=JSON"
        if function_name in self.json_extension:
            json_extension = "&format=JSON"

        # print(self.baseURL + function_name + "/" + requests.utils.requote_uri(query) + json_extension)
        return self.baseURL + function_name + "/" + requests.utils.requote_uri(query) + json_extension

    def _call_taxon(self, function, query):
        url = self._construct_call(function, query)
        return pd.read_json(url)

    def best_match_sci_name(self, scientific_name: str, kingdom: str = None,
                            NPSpeciesCategory: list = None):
        print(scientific_name)

        # Is provided name a genus or higher (ends with spp. or similar, or has only 1 word), or
        # a species or lower (two or more words, contains "var.").
        genus_or_higher = False
        lower_than_species = False

        # Start cleaning, look for genus.
        sci_name = scientific_name.strip()
        sci_name = re.sub('[\s+]', ' ', sci_name)
        for rm in ['\s+spp+\.$', '\s+spp$', '\s+sp+\.$', '\s+sp$']:
            # print(rm + " " + sci_name)
            if re.search(rm, sci_name, flags=re.IGNORECASE) is not None:
                # print("FIXED: " + rm + " " + sci_name)
                genus_or_higher = True
                sci_name = re.sub(rm, "", sci_name, flags=re.IGNORECASE)
        sci_name = sci_name.strip()

        # If down to one word, it's a genus or higher. If more than two words, it's probably a variety
        # unless it includes syn. Could be a varitey with syn., but we can't get everything.
        # num_words = len(re.findall('\w+', sci_name)) # removed, separates dashes sometimes in names
        num_words = len(re.findall('\s', sci_name)) + 1

        if num_words == 1:
            genus_or_higher = True
        elif num_words > 2:
            if re.search('\s+syn+\.+\s', sci_name, flags=re.IGNORECASE) is None and \
                    re.search('\s+syn+\s', sci_name, flags=re.IGNORECASE) is None:
                lower_than_species = True
            else:
                # Trim down to first two words, don't know if FWSpecies can handle syn.
                sci_name = sci_name.split(" ")[0] + " " + sci_name.split(" ")[1]

        # Grab results
        results = self.searchByScientificName(scientific_name).assign(given_sci_name=scientific_name,
                                                                      clean_name=sci_name,
                                                                      genus_or_higher=genus_or_higher,
                                                                      lower_than_species=lower_than_species)

        # If no results, return search string.
        if len(results) == 0:
            return pd.DataFrame([{'given_sci_name': scientific_name,
                                  'clean_name': sci_name,
                                  'genus_or_higher': genus_or_higher,
                                  'lower_than_species': lower_than_species}])

        # Get accepted taxon codes if it exists
        if 'AcceptedTaxa' in results.columns:
            results = results.assign(AcceptedTaxonCode=lambda y: y.apply(
                lambda x: x.AcceptedTaxa[0]['TaxonCode'] if type(x.AcceptedTaxa) == list else None, axis=1))

        # Get ITIS TSN if it exists.
        if 'ClassificationSource' in results.columns:
            results = results.assign(TSN=lambda y: y.apply(
                lambda x: x.ClassificationSource['Detail']['Code'] if type(x.ClassificationSource) == dict else None,
                axis=1))

        # Match by NPSpecies Category if provided. No option around.
        if NPSpeciesCategory is not None:
            results = results.loc[results.NPSpeciesCategory.isin(NPSpeciesCategory)]

        # Match by Kingdom
        # TODO: Match by kingdom, if specified. To avoid insect in plant results, for example.
        # if kingdom is not None:

        # If only one result, return. Or no results.
        if len(results) < 2:
            return results

        # If multiple results, filter based on Ranks we're looking for.
        # print("Filtering by rough taxon rank we are looking for.")
        if not genus_or_higher and not lower_than_species:
            results = results.loc[results.Rank == "Species"]
        elif genus_or_higher:
            results = results.loc[results.Rank.isin(['Domain', 'Kingdom', 'Phylum', 'Class', 'Order',
                                                     'Family', 'Genus'])]
        else:
            results = results.loc[results.Rank.isin(['Variety', 'Subspecies', 'Form', 'Cultivar'])]

        # If only one result, return. Or no results.
        if len(results) < 2:
            return results

        # Check for exact value in Scientific Name
        # print("Filtering by scientific name, if there's at least one match.")
        if sum(results.ScientificName == scientific_name) > 0:
            results = results.loc[results.ScientificName == scientific_name]

        # If only one result, return. Or no results.
        if len(results) < 2:
            return results

        # Check remove any invalid entries.
        # print("If there's at least one valid, removing all invalid values.")
        if any(results.Usage.isin(["valid", 'accepted'])):
            results = results.loc[results.Usage.isin(["valid", 'accepted'])]

        # TODO: Whittle down by prioritizing species over subspecies or higher levels

        return results
