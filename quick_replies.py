from linebot.models import (
    QuickReply,
    QuickReplyButton,
    TextSendMessage,
    MessageAction,
    URIAction,
    CameraAction,
    CameraRollAction,
    DatetimePickerAction,
    PostbackAction,
)

# :recw quick reply
recw_text_qr_button = QuickReplyButton(
    action=URIAction(
        label=':recw',
        uri="https://line.me/R/oaMessage/@318hswmt/?%3Arecw%20",
    )
)
recw_buttons = QuickReply(items=[recw_text_qr_button])
record_workout_reply_message = TextSendMessage(
    text='''請按[:recw]即可輸入前綴。
運動可記項目 : [workout], [sets], [reps], [weight], [duration], [distance], [calories]
範例 :
:recw 跑步,30min,4.2km
:recw 硬舉,3,8,80kg''',
    quick_reply=recw_buttons,
)

# :recf quick reply
recf_text_qr_button = QuickReplyButton(
    action=URIAction(
        label=':recf',
        uri="https://line.me/R/oaMessage/@318hswmt/?%3Arecf%20",
    )
)
recf_camera_qr_button = QuickReplyButton(
    action=CameraAction(
        label='camera',
    )
)
recf_photo_qr_button = QuickReplyButton(
    action=CameraRollAction(
        label='picture',
    )
)
recf_buttons = QuickReply(
    items=[recf_text_qr_button, recf_camera_qr_button, recf_photo_qr_button]
)
record_food_reply_message = TextSendMessage(
    text='''其實你只有一個選項。
功能不全，只能以文字記錄。
請按[:recf]即可輸入前綴。
飲食可記項目 : [meal], [food]
範例 :
:recf 午餐,便當
:recf 牛肉燉飯''',
    quick_reply=recf_buttons,
)

# quest quick reply
quest_post_new_qr_button = QuickReplyButton(
    action=PostbackAction(
        label="發佈新任務",
        data="chose_due",
    )
)
view_progress_qr_button = QuickReplyButton(
    action=MessageAction(
        label="任務進度",
        text=":prog",
    )
)
quest_buttons = QuickReply(items=[quest_post_new_qr_button, view_progress_qr_button])
quest_reply_message = TextSendMessage(
    text='請選擇。',
    quick_reply=quest_buttons,
)

# post new quest : chose due date quick reply
due_date_qr_button = QuickReplyButton(
    action=DatetimePickerAction(
        label='到期日',
        mode="date",
        data="due_date",
    )
)
week_qr_button = QuickReplyButton(
    action=PostbackAction(
        label="一週",
        data="week_due",
    )
)
chose_due_quest_buttons = QuickReply(items=[due_date_qr_button, week_qr_button])
chose_due_reply_message = TextSendMessage(
    text='選擇此任務的到期日。',
    quick_reply=chose_due_quest_buttons,
)

# :post quick reply
post_qr_button = QuickReplyButton(
    action=URIAction(
        label=":post",
        uri="https://line.me/R/oaMessage/@318hswmt/?%3Apost%20",
    )
)
post_button = QuickReply(items=[post_qr_button])
post_reply_message = TextSendMessage(
    text='''請依規格輸入[運動],[次數]
範例 :
:post 跳繩,400''',
    quick_reply=post_button,
)

# :link quick reply
link_qr_button = QuickReplyButton(
    action=URIAction(
        label=":link",
        uri="https://line.me/R/oaMessage/@318hswmt/?%3Alink%20",
    )
)
link_button = QuickReply(items=[link_qr_button])
link_reply_message = TextSendMessage(
    text='''1. 在你的 Google 雲端硬碟創建新的試算表。
2. 左上角點選 [檔案] -> [共用] -> [與他人共用]。
3. 在 [一般存取權] 中選擇 [知到連結的任何人] ，且將 [檢視者] 換成 [編輯者]。
4. 點選 [複製連結] 與 [完成] 按鈕。
5. 在 [:link] 之後貼上你的連結。

範例 :
:link https://docs.google.com/spreadsheets/d/xxxxxxxxxxxxxxxx''',
quick_reply=link_button,
)