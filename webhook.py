import os
import json
import quick_replies
import sheet_edit
import sheet_output
from google.cloud import storage
from my_secrets import line_channel_secret, line_channel_access_token
from datetime import datetime, timedelta
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, FlexSendMessage, ImageSendMessage, TextMessage, RichMenu
from linebot.models.events import (
    FollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    MessageEvent,
    PostbackEvent,
)

# create webhook handler
handler = WebhookHandler(line_channel_secret)
# create LINE Bot Api
api = LineBotApi(line_channel_access_token)
# create rich menu
menu = RichMenu.new_from_json_dict(
    json.load(open("static/rich_menu.json", "r")))
menu_id = api.create_rich_menu(rich_menu=menu)
# set rich menu background
image = open("static/menu.png", "rb")
api.set_rich_menu_image(menu_id, "image/png", image)
# make default rich menu
api.set_default_rich_menu(menu_id)


# return group_id if message type is group else user_id
def get_sheet_filename(event):
    if event.source.type == "group":
        return event.source.group_id
    else:
        return event.source.user_id

# load tmp folder from google cloud storage


def load_folder_from_gcs(bucket_name, folder_path):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    # Retrieve all objects within the folder path
    blobs = bucket.list_blobs(prefix=folder_path)
    for blob in blobs:
        # Process each blob or perform desired operations
        # For example, you can download the blob to a local file
        try:
            blob.download_to_filename(f"{blob.name}")
        except:
            pass

# save tmp folder to google cloud storage


def save_folder_to_gcs(bucket_name, folder_path, destination_prefix=""):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            gcs_blob_name = os.path.join(
                destination_prefix, os.path.relpath(local_file_path, folder_path))
            blob = bucket.blob(gcs_blob_name)
            blob.upload_from_filename(local_file_path)


start_message = FlexSendMessage(
    alt_text='start',
    contents={
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "Press to start",
                        "text": ":start"
                    },
                    "color": "#FFFFFF"
                }],
            "backgroundColor": "#AC1515",
            "paddingAll": "5px"
        }
    },
)

# handle user follow event
@handler.add(FollowEvent)
def reply_follow(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get user id from event source by line bot api
    user_id = event.source.user_id
    # create user_id.txt temp file
    open("tmp/" + user_id + '.txt', "w").close()
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")

# handle bot join event
@handler.add(JoinEvent)
def reply_self_join(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get group id from event source by line bot api
    group_id = event.source.group_id
    # create group_id.txt temp file
    open("tmp/" + group_id + '.txt', "a").close()
    api.reply_message(event.reply_token, start_message)
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")


# handle bot left event
@handler.add(LeaveEvent)
def reply_self_left(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get group id from event source by line bot api
    group_id = event.source.group_id
    # remove group_id.txt temp file
    os.remove("tmp/" + group_id + ".txt")
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")


# handle user join event
@handler.add(MemberJoinedEvent)
def reply_user_join(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get user id from event source by line bot api
    # user_id = event.source.user_id
    # get group id from event source by line bot api
    group_id = event.source.group_id
    # create user_id.txt temp file
    # open(user_id + '.txt', "w").close()
    # create group_id.txt temp file
    open("tmp/" + group_id + '.txt', "a").close()
    api.reply_message(event.reply_token, start_message)
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")


# handle user left event
@handler.add(MemberLeftEvent)
def reply_user_left(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get user id from event source by line bot api
    # user_id = event.source.user_id
    # get group id from event source by line bot api
    group_id = event.source.group_id
    # remove user_id.txt temp file
    # os.remove(user_id + ".txt")
    # remove group_id.txt temp file
    os.remove("tmp/" + group_id + ".txt")
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")


# when user send text
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    if event.message.text[:6] == ":start":
        # create user_id.txt temp file
        open("tmp/" + event.source.user_id + '.txt', "a").close()
        # create rich menu
        menu = RichMenu.new_from_json_dict(
            json.load(open("static/rich_menu.json", "r")))
        menu_id = api.create_rich_menu(rich_menu=menu)
        # set rich menu background
        image = open("static/menu.png", "rb")
        api.set_rich_menu_image(menu_id, "image/png", image)
        api._post(
            f'/v2/bot/group/{event.source.group_id}/richmenu/{menu_id}',
            timeout=None
        )

    elif event.message.text[:5] == ":link":
        sheet_edit.link(event.message.text[5:].strip(
            ' '), get_sheet_filename(event))
        api.reply_message(event.reply_token, TextSendMessage('已連結。'))
    elif event.message.text[:5] == ":post":
        if sheet_edit.post(event, get_sheet_filename(event)):
            api.reply_message(
                event.reply_token,
                sheet_output.show_quest(get_sheet_filename(event)),
            )
    elif event.message.text[:5] == ":prog":
        api.reply_message(
            event.reply_token,
            sheet_output.show_progress(event, get_sheet_filename(event)),
        )
    elif event.message.text[:4] == ":rec":
        profile = api.get_profile(event.source.user_id)
        if sheet_edit.record(event, profile, get_sheet_filename(event)):
            api.reply_message(event.reply_token, TextSendMessage('已記錄。'))
    elif event.message.text[:4] == ":sum":
        sheet_filename = get_sheet_filename(event)
        sheet_output.summary(sheet_filename)
        path = "https://urik-gym-bot-uaapd4w7vq-de.a.run.app/images/" + \
            sheet_filename + "_summary.jpg"
        api.reply_message(
            event.reply_token,
            ImageSendMessage(
                path,
                path,
            ),
        )
    else:
        pass
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")


# post back event will happen after button press
@handler.add(PostbackEvent)
def handle_post_message(event):
    load_folder_from_gcs("urik_gym_bot_bucket", "tmp/")
    # get user id by line bot api
    user_id = event.source.user_id

    match event.postback.data:
        # button 1 : record workout
        case "record_workout":
            api.reply_message(
                event.reply_token, quick_replies.record_workout_reply_message
            )

        # button 2 : record food
        case "record_food":
            api.reply_message(
                event.reply_token, quick_replies.record_food_reply_message
            )

        # button 3 : quest
        case "quest":
            api.reply_message(event.reply_token,
                              quick_replies.quest_reply_message)

        case "chose_due":
            api.reply_message(event.reply_token,
                              quick_replies.chose_due_reply_message)

        case "due_date":
            with open("tmp/" + user_id + "_questdue.txt", "w") as f:
                f.write(event.postback.params["date"])
            api.reply_message(
                event.reply_token,
                quick_replies.post_reply_message,
            )

        case "week_due":
            dt = datetime.fromtimestamp(event.timestamp / 1000)
            with open("tmp/" + user_id + "_questdue.txt", "w") as f:
                f.write((dt + timedelta(weeks=1)).strftime('%Y-%m-%d'))
            api.reply_message(
                event.reply_token,
                quick_replies.post_reply_message,
            )

        # button 5 : link sheet
        case "save_sheet_link":
            api.reply_message(
                event.reply_token,
                quick_replies.link_reply_message,
            )

        # button 6 : help
        case "help":
            with open("static/help.txt", "r") as f:
                api.reply_message(event.reply_token,
                                  TextSendMessage(text=f.read()))
    save_folder_to_gcs("urik_gym_bot_bucket", "tmp", "tmp/")
