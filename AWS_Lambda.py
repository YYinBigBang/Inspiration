# -*- coding: utf-8 -*-

import os
import json
import random
import time
from pathlib import Path

# LINE Bot SDK
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ShowLoadingAnimationRequest,
    ReplyMessageRequest,
    TextMessage
)


def read_the_book_of_answers():
    """Load the book of answers from the JSON file."""
    current_dir = Path(__file__).parent
    json_file_path = current_dir / 'the_book_of_answers.json'
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


# Load the necessary data
inspiration_database = read_the_book_of_answers()
line_bot_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
line_bot_config = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])


def draw_straw(line_bot_api, line_user_id):
    """Draw a straw from the inspiration database."""

    # Pop up loading animation for line bot
    loading_request = ShowLoadingAnimationRequest(chatId=line_user_id, loadingSeconds=10)
    line_bot_api.show_loading_animation(loading_request)
    straw_id = random.randint(1, 336)
    return inspiration_database[str(straw_id)]


def callback(event, context):
    signature = event['headers']['x-line-signature']
    body = event['body']

    try:
        line_bot_handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid signature')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }


@line_bot_handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    with ApiClient(line_bot_config) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        user_message = event.message.text

        if '如何使用' in user_message.replace(' ', ''):
            messages = [
                TextMessage(text='1.內心設想一個問題，\n要用「封閉式問題」陳述，\n例如：「我該不該換工作？」'),
                TextMessage(text='2.閉上眼睛，花10~15秒默想此問題。'),
                TextMessage(text='3.點選「獲得啟示」，\n或者在聊天室描述你的問題，\n解答之書就會告訴你答案。'),
                TextMessage(text='4.每問一個問題都重複此流程。'),
                TextMessage(text='5.運用吸引力法則，並仔細傾聽自己內心的聲音，可以得到更貼近你的結果。'),
            ]

        elif '關於本書' in user_message.replace(' ', ''):
            messages = [
                TextMessage(text='此應用參考至Carol Bolt的：\n'
                                 '《The Book of Answers》\n'
                                 '中文書名：《解答之書》'),
                TextMessage(text="它就如同一面鏡子，真實呈現你內心的想法。"
                                 "每一天，我們都要面對無數大大小小的問題，"
                                 "很多時候，我們明明有答案，卻自尋煩惱；"
                                 "有些時候，我們則是在衝動之下做了決定。"
                                 "當然，有些問題因為還差一點勇氣，"
                                 "也有些問題則要換個方向思考。"),
                TextMessage(text="這就是為何《解答之書》能回答你的大小問題：\n\n"
                                 "它能讓你真實面對自己的內心！"),
            ]

        elif '獲得啟示' in user_message.replace(' ', ''):
            straw = draw_straw(line_bot_api, user_id)
            time.sleep(1)
            messages = [
                TextMessage(text=straw['answer']),
                TextMessage(text=f'解析: {straw["explanation"]}'),
            ]

        else:
            straw = draw_straw(line_bot_api, user_id)
            time.sleep(3)
            messages = [
                TextMessage(text=straw['answer']),
                TextMessage(text=f'解析: {straw["explanation"]}'),
            ]

        # Reply message to user
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages)
        )

