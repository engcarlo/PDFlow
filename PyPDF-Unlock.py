import io
import zipfile

import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.errors import FileNotDecryptedError

st.set_page_config(
    page_title="PDF Toolkit",
    page_icon="🧰",
    layout="centered",
)

# --- Navegação lateral ----------------------------------------------------
st.sidebar.title("🧰 PDF Toolkit")
pagina = st.sidebar.radio(
    "Funcionalidade",
    ["🔓 Desbloquear", "📎 Juntar", "✂️ Dividir"],
)

st.sidebar.divider()
st.sidebar.caption("Nenhum arquivo é salvo em servidor — o processamento acontece apenas na sessão atual.")


# ===========================================================================
# DESBLOQUEAR
# ===========================================================================
if pagina == "🔓 Desbloquear":
    st.title("🔓 Desbloqueio de PDF")
    st.write(
        "Envie um PDF protegido por senha, informe a senha de acesso e baixe "
        "a versão desbloqueada."
    )

    st.divider()

    arquivo = st.file_uploader("Arquivo PDF protegido", type=["pdf"])
    senha = st.text_input("Senha do PDF", type="password", placeholder="Digite a senha")

    desbloquear = st.button(
        "Desbloquear PDF", type="primary", use_container_width=True, disabled=arquivo is None
    )

    st.divider()

    if desbloquear:
        if arquivo is None:
            st.warning("Envie um arquivo PDF antes de continuar.")
        else:
            try:
                reader = PdfReader(arquivo)

                if reader.is_encrypted:
                    if not senha:
                        st.error("Este PDF está protegido. Informe a senha para continuar.")
                        st.stop()

                    resultado = reader.decrypt(senha)

                    # decrypt() retorna 0 quando a senha está incorreta
                    if resultado == 0:
                        st.error("Senha incorreta. Verifique e tente novamente.")
                        st.stop()
                else:
                    st.info("Este PDF não está protegido por senha — gerando cópia sem alterações.")

                writer = PdfWriter()
                for p in reader.pages:
                    writer.add_page(p)

                buffer_saida = io.BytesIO()
                writer.write(buffer_saida)
                buffer_saida.seek(0)

                nome_saida = f"UNLOCKED-{arquivo.name}"

                st.success(f"PDF desbloqueado com sucesso! ({len(reader.pages)} páginas)")

                st.download_button(
                    label="⬇️ Baixar PDF desbloqueado",
                    data=buffer_saida,
                    file_name=nome_saida,
                    mime="application/pdf",
                    use_container_width=True,
                )

            except FileNotDecryptedError:
                st.error("Não foi possível desbloquear o PDF com a senha informada.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o PDF: {e}")


# ===========================================================================
# JUNTAR (MERGE)
# ===========================================================================
elif pagina == "📎 Juntar":
    st.title("📎 Juntar PDFs")
    st.write("Envie dois ou mais PDFs e combine-os em um único arquivo, na ordem escolhida.")

    st.divider()

    arquivos = st.file_uploader(
        "Arquivos PDF para juntar", type=["pdf"], accept_multiple_files=True
    )

    if arquivos and len(arquivos) > 1:
        st.caption("Ordem de junção (arraste os nomes na lista para reordenar não é suportado — "
                   "use o seletor abaixo para definir a ordem):")
        nomes = [a.name for a in arquivos]
        ordem = st.multiselect(
            "Ordem final dos arquivos",
            options=nomes,
            default=nomes,
            help="Clique para remover e adicionar novamente na ordem desejada.",
        )
    else:
        ordem = [a.name for a in arquivos] if arquivos else []

    juntar = st.button(
        "Juntar PDFs",
        type="primary",
        use_container_width=True,
        disabled=not arquivos or len(arquivos) < 2,
    )

    st.divider()

    if juntar:
        if not arquivos or len(arquivos) < 2:
            st.warning("Envie pelo menos dois arquivos PDF.")
        else:
            try:
                mapa_arquivos = {a.name: a for a in arquivos}
                lista_final = ordem if ordem else [a.name for a in arquivos]

                writer = PdfWriter()
                for nome in lista_final:
                    arquivo = mapa_arquivos[nome]
                    arquivo.seek(0)
                    writer.append(arquivo)

                buffer_saida = io.BytesIO()
                writer.write(buffer_saida)
                writer.close()
                buffer_saida.seek(0)

                st.success(f"{len(lista_final)} arquivos combinados com sucesso!")

                st.download_button(
                    label="⬇️ Baixar PDF combinado",
                    data=buffer_saida,
                    file_name="combined_output.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Ocorreu um erro ao juntar os PDFs: {e}")


# ===========================================================================
# DIVIDIR (SPLIT)
# ===========================================================================
elif pagina == "✂️ Dividir":
    st.title("✂️ Dividir PDF")
    st.write("Envie um PDF e baixe cada página como um arquivo separado, dentro de um .zip.")

    st.divider()

    arquivo = st.file_uploader("Arquivo PDF para dividir", type=["pdf"])

    dividir = st.button(
        "Dividir PDF", type="primary", use_container_width=True, disabled=arquivo is None
    )

    st.divider()

    if dividir:
        if arquivo is None:
            st.warning("Envie um arquivo PDF antes de continuar.")
        else:
            try:
                reader = PdfReader(arquivo)
                nome_base = arquivo.name.replace(".pdf", "")

                buffer_zip = io.BytesIO()
                with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for index, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)

                        buffer_pagina = io.BytesIO()
                        writer.write(buffer_pagina)
                        buffer_pagina.seek(0)

                        nome_pagina = f"{nome_base}_page_{index + 1}.pdf"
                        zip_file.writestr(nome_pagina, buffer_pagina.read())

                buffer_zip.seek(0)

                st.success(f"{len(reader.pages)} páginas geradas com sucesso!")

                st.download_button(
                    label="⬇️ Baixar páginas (.zip)",
                    data=buffer_zip,
                    file_name=f"{nome_base}_paginas.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Ocorreu um erro ao dividir o PDF: {e}")