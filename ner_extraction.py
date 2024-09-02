import pdfplumber
import spacy
import re
import json

# Load spaCy's NER model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


# Uses regex patterns to extract specific entities from the text.
def extract_entities_with_regex(text):
   
    entities = {
        "Reference Number": None,
        "Invoice Number": None,
        "Invoice Date": None,
        "Order Number": None,
        "Customer PO": None,
        "Ship To": None,
        "Bill To": None,
        "Labor": None,
        "Equipment & Parts": None,
        "Subtotal": None,
        "Shipping & Handling": None,
        "Tax": None,
        "Order Total": None,
        "Less Deposit": None,
        "Balance Due": None,
        "Customer Service Contact": None,
        "Email Contact": None,
        "Items": [],
        "Payment Terms": None,
        "Remit To": None
    }

    # Regular expression patterns
    patterns = {
        "Reference Number": re.compile(r'REFERENCE#\s*(\d+)'),
        "Invoice Number": re.compile(r'INVOICE#\s*(\d+)'),
        "Invoice Date": re.compile(r'INVOICE DATE\s*(\d{2}/\d{2}/\d{4})'),
        "Order Number": re.compile(r'ORDER#\s*(\S+)'),
        "Customer PO": re.compile(r'CUSTOMER PO\s*(\d+)'),
        "Ship To": re.compile(r'SHIP TO:\s*(.*?)\s*BILL TO:', re.DOTALL),
        "Bill To": re.compile(r'BILL TO:\s*(.*?)\n', re.DOTALL),
        "Labor": re.compile(r'Labor\s*\$?([\d,.]+)'),
        "Equipment & Parts": re.compile(r'Equipment\s*&\s*Parts\s*\$?([\d,.]+)'),
        "Subtotal": re.compile(r'SUBTOTAL\s*\$?([\d,.]+)'),
        "Shipping & Handling": re.compile(r'Shipping\s*&\s*Handling\s*\$?([\d,.]+)'),
        "Tax": re.compile(r'Tax\s*\$?([\d,.]+)'),
        "Order Total": re.compile(r'ORDER\s*TOTAL\s*\$?([\d,.]+)'),
        "Less Deposit": re.compile(r'Less\s*Deposit\s*\$?([\d,.]+)'),
        "Balance Due": re.compile(r'BALANCE\s*DUE\s*\$?([\d,.]+)'),
        "Customer Service Contact": re.compile(r'Customer Service Contact:\s*(.*?)\n', re.DOTALL),
        "Email Contact": re.compile(r'Email:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'),
        "Payment Terms": re.compile(r'Payment Terms:\s*(.*?)\n', re.DOTALL),
        "Remit To": re.compile(r'Please remit payments to:\s*(.*?)\n', re.DOTALL),
    }

    # Extract using regex
    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            entities[key] = match.group(1).strip()

    # Extract items
    item_pattern = re.compile(r'(\d+)\s+([\w\s,]+?)\s+(\d+)\s+([\d,.]+)\s+([\d,.]+)\s+(\S+)', re.DOTALL)
    items = item_pattern.findall(text)
    for item in items:
        entities["Items"].append({
            "Item Number": item[0],
            "Description": item[1].strip(),
            "Quantity": item[2],
            "Unit Price": item[3],
            "Total Price": item[4],
            "Serial Number": item[5]
        })

    return entities


#NER to extract entities from the text.
def extract_entities_with_ner(text):
    
    doc = nlp(text)
    entities = extract_entities_with_regex(text)

    for ent in doc.ents:
        if ent.label_ == "DATE" and not entities["Invoice Date"]:
            entities["Invoice Date"] = ent.text
        elif ent.label_ == "MONEY" and not entities["Balance Due"]:
            entities["Balance Due"] = ent.text
        elif ent.label_ == "ORG" and not entities["Bill To"]:
            entities["Bill To"] = ent.text
        elif ent.label_ == "EMAIL" and not entities["Email Contact"]:
            entities["Email Contact"] = ent.text

    return entities


def convert_pdf_to_json(pdf_path):
    
    # Step 1: Extract text
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Extract entities using NER and regex
    entities = extract_entities_with_ner(text)
    
    # Step 3: Convert the extracted entities to JSON
    json_data = json.dumps(entities, indent=4)
    
    return json_data


if __name__ == "__main__":
    
    pdf_path = "invoice_sample.pdf"
    
    json_result = convert_pdf_to_json(pdf_path)
    
    
    # Save the result to a JSON file (optional)
    with open("invoice_ner_output.json", "w") as json_file:
        json_file.write(json_result)
