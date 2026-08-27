import io
import zipfile
from pathlib import Path

import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.errors import FileNotDecryptedError

ICON_PATH = Path(__file__).parent / "assets" / "icon.png"

st.set_page_config(
    page_title="PDFlow",
    page_icon=str(ICON_PATH) if ICON_PATH.exists() else "🗂️",
    layout="centered",
)

# --- Navegação lateral ----------------------------------------------------
if ICON_PATH.exists():
    st.sidebar.image(str(ICON_PATH), width=64)
st.sidebar.title("PDFlow")
st.sidebar.caption("Ferramentas para desbloquear, juntar e dividir PDFs.")
pagina = st.sidebar.radio(
    "Funcionalidade",
    ["🔓 Desbloquear", "📎 Juntar", "✂️ Dividir"],
)

st.sidebar.divider()
st.sidebar.caption("Nenhum arquivo é salvo em servidor — o processamento acontece apenas na sessão atual.")

# --- Banner de topo --------------------------------------------------------
BANNER_PATH = Path(__file__).parent / "assets" / "banner.png"
if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), width='stretch')


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
    st.write("Envie um PDF e escolha como deseja dividi-lo.")

    st.divider()

    arquivo = st.file_uploader("Arquivo PDF para dividir", type=["pdf"])

    total_paginas = None
    if arquivo is not None:
        try:
            reader_preview = PdfReader(arquivo)
            total_paginas = len(reader_preview.pages)
            st.caption(f"O arquivo enviado tem **{total_paginas}** página(s).")
        except Exception as e:
            st.error(f"Não foi possível ler o PDF: {e}")

    modo = st.radio(
        "Modo de divisão",
        [
            "Todas as páginas (uma por arquivo)",
            "Um único intervalo",
            "Múltiplos intervalos personalizados",
        ],
    )

    intervalo_unico = None
    intervalos_texto = ""

    if modo == "Um único intervalo" and total_paginas:
        col1, col2 = st.columns(2)
        with col1:
            pagina_inicio = st.number_input(
                "Página inicial", min_value=1, max_value=total_paginas, value=1
            )
        with col2:
            pagina_fim = st.number_input(
                "Página final", min_value=1, max_value=total_paginas, value=total_paginas
            )
        intervalo_unico = (pagina_inicio, pagina_fim)

    elif modo == "Múltiplos intervalos personalizados":
        intervalos_texto = st.text_input(
            "Intervalos (separados por vírgula)",
            placeholder="Ex: 1-3, 5, 8-10",
            help="Cada intervalo ou página avulsa vira um arquivo PDF separado dentro do .zip.",
        )
        st.caption("Use páginas avulsas (ex: `5`) ou faixas (ex: `8-10`), separadas por vírgula.")

    st.divider()

    def _parse_intervalos(texto, total):
        """Converte uma string como '1-3, 5, 8-10' em uma lista de tuplas (inicio, fim), 1-indexado."""
        intervalos = []
        partes = [p.strip() for p in texto.split(",") if p.strip()]

        if not partes:
            raise ValueError("Nenhum intervalo foi informado.")

        for parte in partes:
            if "-" in parte:
                inicio_str, fim_str = parte.split("-", 1)
                inicio, fim = int(inicio_str.strip()), int(fim_str.strip())
            else:
                inicio = fim = int(parte.strip())

            if inicio < 1 or fim < 1 or inicio > total or fim > total:
                raise ValueError(f"O intervalo '{parte}' está fora do intervalo válido (1-{total}).")
            if inicio > fim:
                raise ValueError(f"O intervalo '{parte}' é inválido (início maior que o fim).")

            intervalos.append((inicio, fim))

        return intervalos

    dividir = st.button(
        "Dividir PDF", type="primary", use_container_width=True, disabled=arquivo is None
    )

    if dividir:
        if arquivo is None:
            st.warning("Envie um arquivo PDF antes de continuar.")
        else:
            try:
                arquivo.seek(0)
                reader = PdfReader(arquivo)
                total = len(reader.pages)
                nome_base = arquivo.name.replace(".pdf", "")

                # --- Define os intervalos a extrair, conforme o modo escolhido ---
                if modo == "Todas as páginas (uma por arquivo)":
                    intervalos = [(i + 1, i + 1) for i in range(total)]

                elif modo == "Um único intervalo":
                    intervalos = [intervalo_unico]

                else:  # Múltiplos intervalos personalizados
                    intervalos = _parse_intervalos(intervalos_texto, total)

                # --- Caso especial: um único resultado -> baixa direto o PDF, sem zip ---
                if len(intervalos) == 1:
                    inicio, fim = intervalos[0]
                    writer = PdfWriter()
                    for p in range(inicio - 1, fim):
                        writer.add_page(reader.pages[p])

                    buffer_saida = io.BytesIO()
                    writer.write(buffer_saida)
                    buffer_saida.seek(0)

                    sufixo = f"p{inicio}" if inicio == fim else f"p{inicio}-{fim}"
                    st.success(f"PDF gerado com sucesso! ({fim - inicio + 1} página(s))")

                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=buffer_saida,
                        file_name=f"{nome_base}_{sufixo}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                # --- Múltiplos resultados -> empacota em um .zip ---
                else:
                    buffer_zip = io.BytesIO()
                    with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for inicio, fim in intervalos:
                            writer = PdfWriter()
                            for p in range(inicio - 1, fim):
                                writer.add_page(reader.pages[p])

                            buffer_pagina = io.BytesIO()
                            writer.write(buffer_pagina)
                            buffer_pagina.seek(0)

                            sufixo = f"page_{inicio}" if inicio == fim else f"pages_{inicio}-{fim}"
                            zip_file.writestr(f"{nome_base}_{sufixo}.pdf", buffer_pagina.read())

                    buffer_zip.seek(0)

                    st.success(f"{len(intervalos)} arquivo(s) gerado(s) com sucesso!")

                    st.download_button(
                        label="⬇️ Baixar arquivos (.zip)",
                        data=buffer_zip,
                        file_name=f"{nome_base}_dividido.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Ocorreu um erro ao dividir o PDF: {e}")
