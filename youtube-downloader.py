import streamlit as st
import yt_dlp
from pydub import AudioSegment
import os

# Barra de progresso global
progresso_download = None

# Função para download usando yt-dlp
def download_video(url, max_videos=5):
    folder_path = "./downloads"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Criar a pasta se ela não existir

    global progresso_download

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder_path, "%(title)s.%(ext)s"),
            "playlist_items": f"1-{max_videos}",  # Limitar número de vídeos
            "progress_hooks": [progress_hook],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # st.write("Iniciando o download...")
            progresso_download = st.progress(0)  # Inicializa barra de progresso
            info = ydl.extract_info(url, download=True)
            progresso_download.empty()  # Remove a barra após o término
            return info["entries"] if "entries" in info else [info]
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {e}")
        return None

# Callback para exibir progresso
def progress_hook(d):
    global progresso_download
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes", 1)
        percentage = (downloaded / total)
        if progresso_download:
            progresso_download.progress(percentage)

# Função para converter para MP3
def convert_to_mp3(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        mp3_path = file_path.rsplit(".", 1)[0] + ".mp3"
        audio.export(mp3_path, format="mp3")
        return mp3_path
    except Exception as e:
        print(e)
        return None

# Função para listar os arquivos na pasta e permitir download/conversão
def listar_arquivos_na_pasta(folder_path):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Criar a pasta se não existir
        arquivos = os.listdir(folder_path)
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(folder_path, arquivo)
            if arquivo.endswith(".webm"):
                # st.write(f"Convertendo {arquivo} para MP3...")
                mp3_path = convert_to_mp3(caminho_arquivo)
                if mp3_path:
                    os.remove(caminho_arquivo)  # Remove o arquivo .webm original
                    caminho_arquivo = mp3_path
            with open(caminho_arquivo, "rb") as f:
                st.download_button(
                    label=f"Baixar {arquivo}",
                    data=f,
                    file_name=arquivo,
                    mime="audio/mpeg" if arquivo.endswith(".mp3") else "application/octet-stream",
                )
    except Exception as e:
        # st.error(f"Erro ao listar os arquivos: {e}")
        st.error("Por favor atualize a página, os arquivos ainda estão sendo convertidos.")

# Interface do Streamlit
st.title("YouTube Downloader e Conversor para MP3")

# Input para URL do vídeo ou playlist
video_url = st.text_input("Insira a URL do vídeo ou playlist do YouTube:")

# Botão para iniciar o download e conversão
if st.button("Baixar e Converter"):
    if video_url:
        folder_path = "./downloads"
        max_videos = 5  # Limite de vídeos da playlist

        video_entries = download_video(video_url, max_videos)
        if video_entries:
            for entry in video_entries:
                file_path = os.path.join(folder_path, f"{entry['title']}.{entry['ext']}")
                # st.success(f"Download concluído: {file_path}")

                # Converter para MP3
                # st.write(f"Convertendo {entry['title']} para MP3...")
                mp3_path = convert_to_mp3(file_path)
                if mp3_path:
                    # st.success(f"Conversão concluída: {mp3_path}")

                    # Disponibilizar o arquivo MP3 para download
                    with open(mp3_path, "rb") as mp3_file:
                        st.download_button(
                            label=f"Baixar {entry['title']} (MP3)",
                            data=mp3_file,
                            file_name=os.path.basename(mp3_path),
                            mime="audio/mpeg",
                        )
    else:
        st.warning("Por favor, insira uma URL válida.")

# Exibir arquivos já baixados
st.header("Arquivos Já Baixados")
listar_arquivos_na_pasta("./downloads")
