from pathlib import Path
import tempfile
import openai
import pydub

import config

openai.api_key = config.openai_api_key

async def transcribe_audio(audio_file):
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]

# bot_name:
# speech2doc: 语音转文字
# speech2analyze: 文字的分析
# speech2summary: 文字的总结摘要

# from voice_file_id and context to get transcribed_text.
async def voice_to_speech(voice_file_id: str, context) -> str:
    # 临时文件存储录音文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        voice_ogg_path = tmp_dir / "group_voice.ogg"

        # download 下载语音文件
        voice_file = await context.bot.get_file(voice_file_id)
        await voice_file.download_to_drive(voice_ogg_path)

        # convert to mp3
        voice_mp3_path = tmp_dir / "gourp_voice.mp3"
        pydub.AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")

        # transcribe
        with open(voice_mp3_path, "rb") as f:
            transcribed_text = await transcribe_audio(f)

            if transcribed_text is None:
                 transcribed_text = "" 

        return transcribed_text