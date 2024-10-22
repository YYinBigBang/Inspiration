# -*- coding: utf-8 -*-

import json
import random
import time

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

    json_file_path = '/var/task/the_book_of_answers.json'
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


# Load the necessary data
inspiration_database = read_the_book_of_answers()
line_bot_config = Configuration(access_token='LINE_CHANNEL_ACCESS_TOKEN')
line_bot_handler = WebhookHandler('LINE_CHANNEL_SECRET')


def draw_straw(line_bot_api, line_user_id):
    """Draw a straw from the inspiration database."""
    # Pop up loading animation for line bot
    loading_request = ShowLoadingAnimationRequest(chatId=line_user_id, loadingSeconds=10)
    line_bot_api.show_loading_animation(loading_request)
    straw_id = random.randint(1, 336)
    return inspiration_database[straw_id]


def callback(event, context):
    signature = event['headers']['X-Line-Signature']
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
            messages = [TextMessage(text='')]

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

