from pypdf import PdfReader, PdfWriter

def split_pdf(input_path):
    # Load the PDF file
    reader = PdfReader(input_path)
    
    # Loop through each page and save it individually
    for index, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        
        # Output filename: input_page_1.pdf, input_page_2.pdf, etc.
        output_filename = f"{input_path.replace('.pdf', '')}_page_{index + 1}.pdf"
        
        with open(output_filename, "wb") as output_file:
            writer.write(output_file)
            
    print(f"Successfully split {len(reader.pages)} pages.")

# Example usage
split_pdf("sample.pdf")