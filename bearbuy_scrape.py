from bs4 import BeautifulSoup
import copy
import os
import sys
import json as js
import csv
import glob 

# Author Liam McKay

def match_class(target):
    def do_match(tag):
        try:
            classes = dict(tag.attrs)["class"]
        except KeyError:
            classes = ""
        return all(c in classes for c in target)
    return do_match

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigating-the-tree
def has_class(tag):
    return tag.has_attr('class')


def main():
    html_files = glob.glob("*.html")
    output_tsv = ""
    for file_name in html_files:
        with open(file_name, "r") as html_doc:
            soup = BeautifulSoup("".join(html_doc.readlines()), 'html.parser')

            # the magic location of the info (hopefully BearBuy doesn't update their HTML soon)
            company_boxes = soup.find(['div', 'table', 'tbody', 'tr', 'td', 'div', 'div', 'div', 'table', 'tbody', 'tr', 'td'], recursive=True, attrs="ForegroundPanel")
            # company_boxes = soup.find('td', attrs="ForegroundPanel")
            # print(mettlerToledo)
            # print([a for a in company_boxes.contents[1].children])
            try:
                findmysiblings = copy.copy(company_boxes.div.div.find('a', 'SupplierName'))
            except AttributeError as e:
                print(e)
                continue

            json = {}
            for child in company_boxes.div.div.children:
                splitRows=False
                company = child.find("a")
                if child.find("a") != -1:
                    if "Subtotal" in company.string:
                        continue
                    if "Hide line details" not in company.string:
                        json[company.string] = {}
                        row = []
                        for i,td in enumerate(child.find_all("td", "LineSixPack")):
                            for a in td.stripped_strings:
                                if "more info..." not in a:
                                    row.append(a.replace("\xa0",'').replace('USD','').replace('\n','/'))
                            if i > 10:
                                splitRows=True
                        if splitRows:
                            list_rows = []
                            indices = [0]
                            for i,item in enumerate(row):
                                if "addLineData" in item:
                                    indices.append(i+1)
                            for i in range(len(indices)-1):
                                list_rows.append(row[indices[i]:indices[i+1]-1])
                            if list_rows:
                                json[company.string]={row[0]:row[1:] for row in list_rows}
                        else:
                            if row:
                                json[company.string]={row[0]:row[1:-1]}
                        print(row[:5])
                        

        with open("data"+file_name.replace("html",'json'), 'w') as json_file_out:
            js.dump(json, json_file_out)
        if json:
            print("wrote to "+"data"+file_name.replace("html",'json'))
        else:
            print("json is empty for "+"data"+file_name.replace("html",'json'))


        # add data to output_tsv string
        for company, row in json.items():
            for number, item in row.items():
                output_tsv += file_name+"\t"+file_name.replace("Summary - Requisition ","").replace(".html","")+"\t"+company+"\t"+number+"\t"
                output_tsv += item[0]+"\t"
                if "/EA" not in item[1]:
                    output_tsv += item[1]+"\t"
                else:
                    output_tsv += "\t"

                output_tsv += item[-4]+"\t"
                output_tsv += item[-3]+"\t"
                output_tsv += item[-2]+"\t"
                output_tsv += item[-1]+"\t"
                output_tsv += "\n"
    
    # output_tsv to allRequisitions.tsv
    with open("allRequisitions.tsv", 'w') as tsvout:
        tsvout.write("Requisition\tRequisition Number\tCompany\tNumber\tItem Description\tCatalog Number\tSize / Packaging\tUnit Price\tQuantity\tExt. Price\n")
        tsvout.write(output_tsv)
    print("wrote to allRequisitions.tsv")
if __name__ == '__main__':
    main()
