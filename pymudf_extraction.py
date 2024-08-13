import fitz
import json
import re

def extract_invoice_details(text):
    data = {}

    # Extraction of  reference / invoice / order details
    data["Reference Number"] = re.search(r'REFERENCE#\s*(\d+)', text).group(1) if re.search(r'REFERENCE#\s*(\d+)', text) else None
    data["Invoice Number"] = re.search(r'INVOICE#\s*(\d+)', text).group(1) if re.search(r'INVOICE#\s*(\d+)', text) else None
    data["Invoice Date"] = re.search(r'INVOICE DATE\s*(\d{2}/\d{2}/\d{4})', text).group(1) if re.search(r'INVOICE DATE\s*(\d{2}/\d{2}/\d{4})', text) else None
    data["Order Number"] = re.search(r'ORDER#\s*(\w+)', text).group(1) if re.search(r'ORDER#\s*(\w+)', text) else None
    data["Customer PO"] = re.search(r'CUSTOMER PO\s*(\d+)', text).group(1) if re.search(r'CUSTOMER PO\s*(\d+)', text) else None

    # Extract of shipping / billing details
    ship_to_match = re.search(r'SHIP TO:\s*(.*?)\s*BILL TO:', text, re.DOTALL)
    bill_to_match = re.search(r'BILL TO:\s*(.*?)(REFERENCE#|INVOICE#)', text, re.DOTALL)

    data["Ship To"] = ship_to_match.group(1).strip() if ship_to_match else None
    data["Bill To"] = bill_to_match.group(1).strip() if bill_to_match else None

    # extraction of balance / payment details
    data["Labor"] = re.search(r'Labor\s*\$?([\d,.]+)', text).group(1) if re.search(r'Labor\s*\$?([\d,.]+)', text) else None
    data["Equipment & Parts"] = re.search(r'Equipment\s*&\s*Parts\s*\$?([\d,.]+)', text).group(1) if re.search(r'Equipment\s*&\s*Parts\s*\$?([\d,.]+)', text) else None
    data["Subtotal"] = re.search(r'SUB\s*TOTAL\s*\$?([\d,.]+)', text).group(1) if re.search(r'SUB\s*TOTAL\s*\$?([\d,.]+)', text) else None
    data["Shipping & Handling"] = re.search(r'Shipping\s*&\s*Handling\s*\$?([\d,.]+)', text).group(1) if re.search(r'Shipping\s*&\s*Handling\s*\$?([\d,.]+)', text) else None
    data["Tax"] = re.search(r'Tax\s*\$?([\d,.]+)', text).group(1) if re.search(r'Tax\s*\$?([\d,.]+)', text) else None
    data["Order Total"] = re.search(r'ORDER\s*TOTAL\s*\$?([\d,.]+)', text).group(1) if re.search(r'ORDER\s*TOTAL\s*\$?([\d,.]+)', text) else None
    data["Less Deposit"] = re.search(r'Less\s*Deposit\s*\$?([\d,.]+)', text).group(1) if re.search(r'Less\s*Deposit\s*\$?([\d,.]+)', text) else None
    data["Balance Due"] = re.search(r'BALANCE\s*DUE\s*\$?([\d,.]+)', text).group(1) if re.search(r'BALANCE\s*DUE\s*\$?([\d,.]+)', text) else None

    # Extract contact information
    data["Customer Service Contact"] = re.search(r'Customer Service\s*(.*?)\n', text).group(1).strip() if re.search(r'Customer Service\s*(.*?)\n', text) else None
    data["Email Contact"] = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', text).group(1) if re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', text) else None

    # Extract items with serial numbers and additional information
    items = []
    item_lines = re.findall(r'(\d+\s+\d+\s+[\w\s,]+?\s+\d+\s+[\d,.]+\s+[\d,.]+)', text)
    for line in item_lines:
        parts = line.split()
        description_end_index = len(parts) - 4  # Position of quantity
        serial_number_match = re.search(r'S/N:\s+([\w-]+)', text)

        item = {
            "Item Number": parts[0],
            "Description": " ".join(parts[2:description_end_index]),
            "Quantity": parts[-4],
            "Unit Price": parts[-3],
            "Total Price": parts[-1],
            "Serial Number": serial_number_match.group(1) if serial_number_match else None
        }
        items.append(item)
    data["Items"] = items

    # Extract payment terms and conditions
    payment_terms_match = re.search(r'For Terms of Sale please visit:\s*(.*?)\n', text)
    if payment_terms_match:
        data["Payment Terms"] = payment_terms_match.group(1).strip()

    # Extract remit to information
    remit_to_match = re.search(r'Please remit payments to:\s*(.*?)\n', text)
    if remit_to_match:
        data["Remit To"] = remit_to_match.group(1).strip()

    return data

def convert_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text") + "\n"
    
    data = extract_invoice_details(text)
    return data

pdf_path = "invoice_sample.pdf"
json_data = convert_with_pymupdf(pdf_path)

# Print the JSON data for verification before saving
# print("Extracted JSON Data:\n", json.dumps(json_data, indent=4))

with open("invoice_pymupdf.json", "w") as f:
    json.dump(json_data, f, indent=4)
