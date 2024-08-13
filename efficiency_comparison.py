import time
import pymudf_extraction
import pdfplumber_extraction
import tabula_extraction

pdf_path = "invoice_sample.pdf"

# time function
def time_function(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time


pymupdf_text, pymupdf_time = time_function(pymudf_extraction.convert_with_pymupdf, pdf_path)
pdfplumber_text, pdfplumber_time = time_function(pdfplumber_extraction.convert_with_pdfplumber, pdf_path)
tabula_text, tabula_time = time_function(tabula_extraction.convert_with_tabula, pdf_path)


# execution times
print(f"PyMuPDF Execution Time: {pymupdf_time:.4f} seconds")
print(f"pdfplumber Execution Time: {pdfplumber_time:.4f} seconds")
print(f"tabula-py Execution Time: {tabula_time:.4f} seconds")
