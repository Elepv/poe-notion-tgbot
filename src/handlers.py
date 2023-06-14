from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

import asyncio

import poe_api
import notion_api
import whisper_api
import utils

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

notion_client = notion_api.NotionClient

# 处理语音信息
async def handle_voice_message_to_short_summary(update: Update, context: CallbackContext):

    try:
        chat_id = update.effective_chat.id
        bot = context.bot

        # if message.reply_to_message:
        #     reply_message = message.reply_to_message
        #     reply_sender = 


        message = update.message

        # send placeholder message to user
        placeholder_message = await bot.send_message(chat_id=chat_id, text="in summary... please waiting...")

        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")


        # if update.message is voice, voice_to_speech. else message
        if update.message.voice or message.audio:
            logging.info("voice message found...")

            # forward voice
            if message.forward_from:
                voice_sender = message.forward_from.username
                voice_timestamp = message.forward_date
                logging.info(f'Forward voice message from {voice_sender} at {voice_timestamp}')

                _message = message.voice or message.audio
                
                file_id = _message.file_id
                logging.info(f'file_id: {file_id}')
                file_unique_id = _message.file_unique_id
                logging.info(f'file_unique_id: {file_unique_id}')

            # sending voice text or file.
            else:
                voice_sender = message.from_user.username
                voice_timestamp = message.date
                logging.info(f'Sender voice message from {voice_sender} at {voice_timestamp}')

                _message = message.voice or message.audio

                file_id = _message.file_id
                logging.info(f'file_id: {file_id}')
                file_unique_id = _message.file_unique_id
                logging.info(f'file_unique_id: {file_unique_id}')


            transcribed_text = await whisper_api.voice_to_speech(file_id, context)
            if len(transcribed_text) < 10:
                await context.bot.send_message(update.effective_chat.id, "你说的话太短了，用不着转译。")
                logger.error("too short...") 
                return

            text_to_poe = transcribed_text
            symbol = "🎤"

        else:
            text_to_poe = update.message.text
            file_unique_id = update.message.text.file_unique_id
            if len(text_to_poe) < 35:
                await context.bot.send_message(update.effective_chat.id, "你说的话太短了，用不着转译。")
                logger.error("too short...") 
                return
            symbol = "📝"
        
        is_exist_in_notion = await notion_client.search_database(file_unique_id=file_unique_id)

        short_summary = await poe_api.get_answer_from_poe("speech2summary", text_to_poe)
        text = f"{symbol} 摘要: <i>{short_summary}</i>"
        

        # await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        parse_mode = ParseMode.HTML
        await context.bot.edit_message_text(text, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=parse_mode)


        # notion recorder

        if is_exist_in_notion:
            error_text = f"该文件已经在notion中记录过了，不要重复记录"
            await bot.send_message(chat_id=chat_id, text=error_text) 
            return

        speech2doc = await poe_api.get_answer_from_poe("speech2doc", transcribed_text)
        block_title_h2 = f"🎤 修正后录音内容："
        block_content = speech2doc
        logging.info(block_content)
        speak_time = utils.shanghai_tz(voice_timestamp)
        user_name = voice_sender
        file_unique_id = file_unique_id
        await notion_client.write_row(
            speak_time=speak_time, 
            abstract=short_summary, 
            user_name=user_name, 
            file_unique_id=file_unique_id, 
            block_title_h2=block_title_h2, 
            block_content=block_content
            )

    except Exception as e:
        error_text = f"在完成的过程中出了点问题。 Reason: {e}"
        logger.error(error_text)
        await bot.send_message(chat_id=chat_id, text=error_text)


# 语音信息总结
async def voice_summary_handle(update: Update, context: CallbackContext):

    logging.info("voice_summary_handle runs")

    message = update.message
    # voice = None

    if message.reply_to_message and message.reply_to_message.voice:
        file_id = message.reply_to_message.voice.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.audio:
        file_id = message.audio.file_id 
    else:
        raise ValueError("No voice message found.")
    

    try:
        bot = context.bot
        chat_id = update.effective_chat.id

        # 发送语音信息内容
        placeholder_message = await bot.send_message(chat_id=chat_id, text="...")
        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")
   
        transcribed_text = await whisper_api.voice_to_speech(file_id, context)
        speech2doc = poe_api.get_answer_from_poe("speech2doc", transcribed_text)
        text = f"🎤 语音信息修正后的内容:\n <i>{speech2doc}</i>"
        await bot.edit_message_text(text, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=ParseMode.HTML)

        # 发送总结内容
        placeholder_message = await bot.send_message(chat_id=chat_id, text="In summary, please wait more than 3 minutes...")
        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")

        # summary = await poe_api.get_summary(transcribed_text)
        speech2analyze = await asyncio.wait_for(poe_api.get_answer_from_poe("speech2analyze", transcribed_text), timeout=360)
        await bot.edit_message_text(speech2analyze, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        error_text = f"在完成的过程中出了点问题。 Reason: {e}"
        logger.error(error_text)
        await context.bot.send_message(chat_id=chat_id, text=error_text)
