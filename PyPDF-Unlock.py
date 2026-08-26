from pypdf import PdfReader, PdfWriter

# Caminho do arquivo protegido e a senha de acesso
input_file = "Manual de direito para engenheiros e arquitetos, Senado Federal-protegido"+".pdf"
output_file = "UNLOCKED-"+input_file
senha = "CG"

# Realiza a leitura do PDF
reader = PdfReader(input_file)

# Verifica se o arquivo está criptografado e aplica a senha
if reader.is_encrypted:
    reader.decrypt(senha)

writer = PdfWriter()

# Adiciona todas as páginas ao escritor
for page in reader.pages:
    writer.add_page(page)

# Salva o novo arquivo sem senha
with open(output_file, "wb") as f:
    writer.write(f)

print("PDF desbloqueado com sucesso!")
print(output_file)