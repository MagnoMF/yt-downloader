import streamlit as st
import yt_dlp
from pydub import AudioSegment
import os

# Barra de progresso global
progresso_download = None

# Função para download e conversão direto para MP3
def download_and_convert_to_mp3(url, max_videos=5):
    folder_path = "./downloads"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Cria a pasta se ela não existir

    global progresso_download

    try:
        # Configurações para yt-dlp
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder_path, "%(title)s.%(ext)s"),
            "playlist_items": f"1-{max_videos}",  # Limitar número de vídeos
            "progress_hooks": [progress_hook],
        }

        progresso_download = st.progress(0)  # Inicializa a barra de progresso

        # Baixa o áudio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            progresso_download.empty()  # Remove a barra após o término

            # Converte para MP3 imediatamente após o download
            entries = info["entries"] if "entries" in info else [info]
            mp3_files = []
            for entry in entries:
                original_path = os.path.join(folder_path, f"{entry['title']}.{entry['ext']}")
                mp3_path = convert_to_mp3(original_path)
                if mp3_path:
                    mp3_files.append(mp3_path)
            return mp3_files
    except Exception as e:
        st.error(f"Erro ao baixar e converter o áudio: {e}")
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
        os.remove(file_path)  # Remove o arquivo original após a conversão
        return mp3_path
    except Exception as e:
        st.error(f"Erro ao converter {file_path}: {e}")
        return None

# Interface do Streamlit
st.title("YouTube Downloader e Conversor para MP3")

# Input para URL do vídeo ou playlist
video_url = st.text_input("Insira a URL do vídeo ou playlist do YouTube:")

# Botão para iniciar o download e conversão
if st.button("Baixar e Converter"):
    if video_url:
        max_videos = 5  # Limite de vídeos da playlist
        mp3_files = download_and_convert_to_mp3(video_url, max_videos)

        if mp3_files:
            st.success("Download e conversão concluídos!")
            for mp3_path in mp3_files:
                file_name = os.path.basename(mp3_path)
                with open(mp3_path, "rb") as f:
                    st.download_button(
                        label=f"Baixar {file_name}",
                        data=f,
                        file_name=file_name,
                        mime="audio/mpeg",
                    )
    else:
        st.warning("Por favor, insira uma URL válida.")
