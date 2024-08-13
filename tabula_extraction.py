import tabula
import pandas as pd
import json
import re

def clean_dataframe(df):
    df = df.fillna("")  # Replace NaN with empty strings for easier processing
    text = " ".join(df.apply(lambda x: " ".join(x.astype(str)), axis=1).tolist())
    return text

def extract_invoice_details(dfs):
    data = {}
    all_text = ""

    # Iterate over all extracted DataFrames to gather all text
    for df in dfs:
        text = clean_dataframe(df)
        all_text += text + "\n"

    # Now apply the regex patterns on the concatenated text
    data["Reference Number"] = re.search(r'REFERENCE#\s*(\d+)', all_text).group(1) if re.search(r'REFERENCE#\s*(\d+)', all_text) else None
    data["Invoice Number"] = re.search(r'INVOICE#\s*(\d+)', all_text).group(1) if re.search(r'INVOICE#\s*(\d+)', all_text) else None
    data["Invoice Date"] = re.search(r'INVOICE DATE\s*(\d{2}/\d{2}/\d{4})', all_text).group(1) if re.search(r'INVOICE DATE\s*(\d{2}/\d{2}/\d{4})', all_text) else None
    data["Order Number"] = re.search(r'ORDER#\s*(\w+)', all_text).group(1) if re.search(r'ORDER#\s*(\w+)', all_text) else None
    data["Customer PO"] = re.search(r'CUSTOMER PO\s*(\d+)', all_text).group(1) if re.search(r'CUSTOMER PO\s*(\d+)', all_text) else None

    # Extract shipping and billing details
    ship_to_match = re.search(r'SHIP TO:\s*(.*?)\s*BILL TO:', all_text, re.DOTALL)
    bill_to_match = re.search(r'BILL TO:\s*(.*?)(REFERENCE#|INVOICE#)', all_text, re.DOTALL)
    data["Ship To"] = ship_to_match.group(1).strip() if ship_to_match else None
    data["Bill To"] = bill_to_match.group(1).strip() if bill_to_match else None

    # Extract balance and payment details
    data["Labor"] = re.search(r'Labor\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'Labor\s*\$?([\d,.]+)', all_text) else None
    data["Equipment & Parts"] = re.search(r'Equipment\s*&\s*Parts\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'Equipment\s*&\s*Parts\s*\$?([\d,.]+)', all_text) else None
    data["Subtotal"] = re.search(r'SUB\s*TOTAL\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'SUB\s*TOTAL\s*\$?([\d,.]+)', all_text) else None
    data["Shipping & Handling"] = re.search(r'Shipping\s*&\s*Handling\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'Shipping\s*&\s*Handling\s*\$?([\d,.]+)', all_text) else None
    data["Tax"] = re.search(r'Tax\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'Tax\s*\$?([\d,.]+)', all_text) else None
    data["Order Total"] = re.search(r'ORDER\s*TOTAL\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'ORDER\s*TOTAL\s*\$?([\d,.]+)', all_text) else None
    data["Less Deposit"] = re.search(r'Less\s*Deposit\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'Less\s*Deposit\s*\$?([\d,.]+)', all_text) else None
    data["Balance Due"] = re.search(r'BALANCE\s*DUE\s*\$?([\d,.]+)', all_text).group(1) if re.search(r'BALANCE\s*DUE\s*\$?([\d,.]+)', all_text) else None

    # Extract contact information
    data["Customer Service Contact"] = re.search(r'Customer Service\s*(.*?)\n', all_text).group(1).strip() if re.search(r'Customer Service\s*(.*?)\n', all_text) else None
    data["Email Contact"] = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', all_text).group(1) if re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', all_text) else None

    # Extract items
    items = []
    item_lines = re.findall(r'(\d+\s+\d+\s+[\w\s,]+?\s+\d+\s+[\d,.]+\s+[\d,.]+)', all_text)
    for line in item_lines:
        parts = line.split()
        description_end_index = len(parts) - 4  # Position of quantity

        item = {
            "Item Number": parts[0],
            "Description": " ".join(parts[2:description_end_index]),
            "Quantity": parts[-4],
            "Unit Price": parts[-3],
            "Total Price": parts[-1]
        }
        items.append(item)
    data["Items"] = items

    # Extract payment terms and conditions
    payment_terms_match = re.search(r'For Terms of Sale please visit:\s*(.*?)\n', all_text)
    if payment_terms_match:
        data["Payment Terms"] = payment_terms_match.group(1).strip()

    # Extract remit to information
    remit_to_match = re.search(r'Please remit payments to:\s*(.*?)\n', all_text)
    if remit_to_match:
        data["Remit To"] = remit_to_match.group(1).strip()

    return data

def convert_with_tabula(pdf_path):
    # Extract tables from the PDF
    dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    if not dfs or len(dfs) == 0:
        raise ValueError("No tables found in the PDF.")
    
    # Extract relevant information from the tables
    data = extract_invoice_details(dfs)
    return data

pdf_path = "invoice_sample.pdf"
json_data = convert_with_tabula(pdf_path)


with open("invoice_tabula.json", "w") as f:
    json.dump(json_data, f, indent=4)
