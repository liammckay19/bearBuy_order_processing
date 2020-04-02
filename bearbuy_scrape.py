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

def po_information_tags(tag):
    return tag.has_attr('class') and tag.has_attr('href') and tag.has_attr('tabindex') and "ElementValue" in tag['class']


def main():
    html_files = glob.glob("*.html")
    output_tsv = ""
    for file_name in html_files:
        rows_processed = 0

        with open(file_name, "r") as html_doc:
            soup = BeautifulSoup("".join(html_doc.readlines()), 'html.parser')

            # the magic location of the info (hopefully BearBuy doesn't update their HTML soon)
            company_boxes = soup.find(['div', 'table', 'tbody', 'tr', 'td', 'div', 'div', 
                'div', 'table', 'tbody', 'tr', 'td'], recursive=True, attrs="ForegroundPanel")
            
            try:
                date_completed = soup.find(['td','div','table','tbody','td','div'], recursive=True, attrs=["TabbedBackgroundPanel","tabpanel"])
                date_completed_further = [a.find('div') for a in date_completed.contents[3].table.tbody.children][4]
                date = [a.find('div') for a in date_completed_further.table.tbody.children][2]
                date_str = date.div.string.rstrip().replace("\n",'').replace('(','').replace(')','')
            except AttributeError as e:
                print("Couldn't find date for "+file_name)
                date_str=''
                continue
            text_in_general_box = [a.string for a in soup.find_all(po_information_tags)]
            purchase_orders = []
            for t in text_in_general_box:
                if t:
                    if len(t)>0:
                        if "B0" in t:
                            purchase_orders.append(t)
            print("purchase orders:",*purchase_orders)
            try:
                findmysiblings = copy.copy(company_boxes.div.div.find('a', 'SupplierName'))
            except AttributeError as e:
                print(e)
                continue

            po_idx = 0
            json = {}
            for child in company_boxes.div.div.children:
                splitRows=False
                company = child.find("a")
                if child.find("a") != -1:
                    if "Subtotal" in company.string:
                        continue
                    if "Hide line details" not in company.string:
                        json[company.string] = {purchase_orders[po_idx]:{}}
                        row = []
                        for i,td in enumerate(child.find_all("td", "LineSixPack")): # item bought information
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
                                json[company.string][purchase_orders[po_idx]]={row[0]:row[1:] for row in list_rows}
                        else:
                            if row:
                                json[company.string][purchase_orders[po_idx]]={row[0]:row[1:-1]}
                        po_idx+=1
                rows_processed+=1



        # add data to output_tsv string
        for company, things_bought in json.items():
            for po, row in things_bought.items():
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
                    output_tsv += date_str+"\t"
                    output_tsv += po+"\t"
                    output_tsv += "\n"

        json['Date']=date_str

        with open("data"+file_name.replace("html",'json'), 'w') as json_file_out:
            js.dump(json, json_file_out)
        if json:
            print("wrote to "+"data"+file_name.replace("html",'json')+"\t Lines Found = "+str(rows_processed))
        else:
            print("json is empty for "+"data"+file_name.replace("html",'json'))


    # output_tsv to allRequisitions.tsv
    with open("allRequisitions.tsv", 'w') as tsvout:
        tsvout.write("Requisition\tRequisition Number\tCompany\tNumber\tItem Description\tCatalog Number\tSize / Packaging\tUnit Price\tQuantity\tExt. Price\tDate Complete\tPurchase Order\n")
        tsvout.write(output_tsv)
    print("wrote to allRequisitions.tsv")
if __name__ == '__main__':
    main()
