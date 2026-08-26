from pypdf import PdfMerger

def merge_pdfs(pdf_list, output_path):
    merger = PdfMerger()
    
    # Append each PDF file to the merger object
    for pdf in pdf_list:
        merger.append(pdf)
        
    # Write the combined pages to the final output file
    with open(output_path, "wb") as output_file:
        merger.write(output_file)
        
    # Close the merger to free up system resources
    merger.close()
    print(f"Successfully merged files into {output_path}")

# Example usage
files_to_merge = ["file1.pdf", "file2.pdf", "file3.pdf"]
merge_pdfs(files_to_merge, "combined_output.pdf")