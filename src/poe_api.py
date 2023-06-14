import config
import poe
import logging

poe.logger.setLevel(logging.INFO)

# send a message and immediately delete it
# bot_name:
# speech2doc: 语音转文字
# speech2analyze: 文字的分析
# speech2summary: 文字的总结摘要

token = config.poe_api_token
logging.info(token)
proxy = config.socks5
# client = poe.Client(token)
client = poe.Client(token, proxy)

# for chunk in client.send_message("voicesummary", message, with_chat_break=True,timeout = 180):
#   print(chunk["text_new"], end="", flush=True)  # 逐句打印

async def get_answer_from_poe(bot_name, text):
   
    message = text

    logging.info("now sending question to poe")

    for chunk in client.send_message(bot_name, message, with_chat_break=True, timeout=360):
        pass # 不逐句打印
        answer = chunk["text"]   # 不逐句打印

    logging.info("Now return answer from poe.") 
    
    return answer