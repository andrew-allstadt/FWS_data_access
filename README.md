# FWS_data_access
## Package to simplify loading data from commonly used sources in the USFWS

This (very draft) module aims to make it easy to query and load data from USFWS sources and commonly used sources outside of the Service. Data are returned in Pandas or Geopandas data frames and ready for analysis.

Currently addressed sources within the Service:
- Query the Corporate Master Table (CMT)
- FWS Taxonomy (behind the FWSpecies database operated by NWRS)

Outside data sources:
- Bureau of Indian Affiars data
- ITIS
