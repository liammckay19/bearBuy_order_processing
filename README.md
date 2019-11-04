# bearBuy_order_processing
Web scraper for BearBuy orders at UCSF

## Prerequisites

- Needs Python 3, pip

## Quick how to set up

- Download bearbuy_scrape.py - put it in its own folder

- Make a virtual environment for this script. 

`python3 -m venv ./../bearBuy_env`

`source ../bearBuy_env/bin/activate`

- Download requirements.txt

- Run `pip install -r requirements.txt`

- When you load a requisition, save the Summary page as an HTML file in the same dir as bearbuy_scrape.py

- Run `python bearbuy_scrape.py`

- Copy and paste allRequisitions.tsv into your favorite spreadsheet


## How to save and parse a bearBuy Requisition:

### On BearBuy:

1. Documents>Search Documents>My Requisitions
2. Click on the requisition no. link
3. On the Summary tab page, Hit Ctrl-S, save webpage as HTML in same dir as bearbuy_scrape.py
4. Run `python bearbuy_scrape.py`
5. Output should have populated a allRequisitions.tsv file 
