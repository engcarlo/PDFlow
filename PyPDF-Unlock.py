import io

import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.errors import FileNotDecryptedError

st.set_page_config(
    page_title="Desbloqueio de PDF",
    page_icon="🔓",
    layout="centered",
)

st.title("🔓 Desbloqueio de PDF")
st.write(
    "Envie um PDF protegido por senha, informe a senha de acesso e baixe "
    "a versão desbloqueada — tudo em poucos cliques."
)

st.divider()

# --- Entradas do usuário -----------------------------------------------
arquivo = st.file_uploader("Arquivo PDF protegido", type=["pdf"])

#col1, col2 = st.columns([3, 1])
#with col1:
senha = st.text_input("Senha do PDF", type="password", placeholder="Digite a senha")
#with col2:
#    mostrar_senha = st.checkbox("Mostrar")
#    if mostrar_senha and senha:
#        st.caption(f"Senha: `{senha}`")

desbloquear = st.button("Desbloquear PDF", type="primary", use_container_width=True, disabled=arquivo is None)

st.divider()

# --- Processamento -------------------------------------------------------
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
            for pagina in reader.pages:
                writer.add_page(pagina)

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

st.caption("Nenhum arquivo é salvo em servidor — o processamento acontece apenas na sessão atual.")