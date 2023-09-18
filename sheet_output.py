import gspread, google.auth
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from time import time
from linebot.models import FlexSendMessage
from datetime import datetime

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

credentials, project = google.auth.default(scopes=scopes)
gclient = gspread.authorize(credentials)

def make_content(due, workout, total, completeness):
    content = {
        "type": "bubble",
        "size": "micro",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"{workout} {total} 次",
                    "color": "#ffffff",
                    "align": "start",
                    "size": "md",
                    "gravity": "center",
                },
                {
                    "type": "text",
                    "text": f"{int(completeness/total*100)}%",
                    "color": "#ffffff",
                    "align": "start",
                    "size": "xs",
                    "gravity": "center",
                    "margin": "lg",
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "filler"}],
                            "width": f"{int(completeness/total*100)}%",
                            "backgroundColor": "#AC1515",
                            "height": "6px",
                        }
                    ],
                    "backgroundColor": "#FFFFFF33",
                    "height": "6px",
                    "margin": "sm",
                },
            ],
            "backgroundColor": "#333333",
            "paddingTop": "19px",
            "paddingAll": "12px",
            "paddingBottom": "16px",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"Before {due}",
                            "color": "#8C8C8C",
                            "size": "sm",
                            "wrap": True,
                        }
                    ],
                    "flex": 1,
                }
            ],
            "spacing": "md",
            "paddingAll": "12px",
        },
        "styles": {"footer": {"separator": False}},
    }
    return content


def show_quest(sheet_filename):
    f = open("tmp/" + sheet_filename + ".txt", "r")
    spreadsheet = gclient.open_by_url(f.read())
    worksheet = spreadsheet.worksheet("Quest")
    df = pd.DataFrame(worksheet.get_all_records())
    row = df.iloc[-1]
    content = make_content(
        row["due"], row["workout"], int(row["total"]), int(row["completeness"])
    )
    message = FlexSendMessage(alt_text="Quest posted.", contents=content)
    return message


def show_progress(event, sheet_filename):
    f = open("tmp/" + sheet_filename + ".txt", "r")
    spreadsheet = gclient.open_by_url(f.read())
    worksheet = spreadsheet.worksheet("Quest")
    now = datetime.fromtimestamp(event.timestamp / 1000)
    dues = worksheet.range(f"B2:B{worksheet.row_count}")
    contents = []
    for due in dues:
        if not due.value:
            break
        d = list(map(int, due.value.split('-')))
        duedate = datetime(d[0], d[1], d[2])
        if duedate >= now:
            content = make_content(
                due.value,
                worksheet.cell(due.row, 3).value,
                int(worksheet.cell(due.row, 4).value),
                int(worksheet.cell(due.row, 5).value),
            )
            contents.append(content)
    message = FlexSendMessage(
        alt_text="Nothing to show.", contents={"type": "carousel", "contents": contents}
    )
    f.close()
    return message


def summary(sheet_filename):
    f = open("tmp/" + sheet_filename + ".txt", "r")
    spreadsheet = gclient.open_by_url(f.read())
    worksheet = spreadsheet.worksheet("Workout")
    df = pd.DataFrame(worksheet.get_all_records())
    df["date"] = pd.to_datetime(df["date"])
    m = datetime.fromtimestamp(time()).month
    month_workout = df[df["date"].dt.month == m]
    sns.set_theme()
    sns.histplot(data=month_workout, x="date", hue="name", cumulative=True)
    this_month_text = datetime.now().strftime("%B")
    plt.title(f"{this_month_text} Workout Summary")
    plt.ylabel('record count')
    plt.xticks([])
    plt.savefig(fname="tmp/sums/" + sheet_filename + "_summary.jpg")
    f.close()
