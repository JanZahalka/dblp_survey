# dblp_survey
Iterates over the entire DBLP database of scientific papers, creating CSV(s) of papers from the given year or newer and from the given conferences/journals, whose title contains any of the given keywords. The CSV output contains the paper title, conference/journal, year, and a URL to the paper. Useful for scientific surveys.

## Usage
1. Install the required Python packages by `pip install -r requirements.txt`
2. Download the DBLP database to the root directory of the repo from [this link](https://dblp.org/xml/) (if it's dead, let me know, going to [dblp.org](https://dblp.org/)->XML Data->"raw dblp data in a single XML file" should work). Download both the `dblp.xml.gz` file (unpack to `dblp.xml`) and the `dblp.dtd` file.
