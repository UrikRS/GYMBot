import gspread, google.auth
from datetime import datetime

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

credentials, project = google.auth.default(scopes=scopes)
gclient = gspread.authorize(credentials)

workout_header = [
    "uid",
    "date",
    "name",
    "workout",
    "sets",
    "reps",
    "weight",
    "duration",
    "distance",
    "calories",
]
food_header = ["uid", "date", "name", "meal", "food"]
quest_header = ["date", "due", "workout", "total", "completeness"]


def link(url, sheet_filename):
    # write link url in user_id.txt or group_id.txt
    with open("tmp/" + sheet_filename + ".txt", "w") as f:
        f.write(url)
    # open sheet url by google spreadsheet client
    spreadsheet = gclient.open_by_url(url)
    # place initial data in spreadsheet
    gym_sheet_initcial(spreadsheet)


def gym_sheet_initcial(spreadsheet):
    try:
        # change spreadsheet title if not set
        if (
            "Untitled spreadsheet" in spreadsheet.title
            or "未命名的試算表" in spreadsheet.title
        ):
            spreadsheet.update_title("Workout & Food")
        else:
            pass
        # change name of worksheet 1 for workout records
        ws1 = spreadsheet.get_worksheet(0)
        if ws1.title != "Workout":
            ws1.update_title("Workout")
            ws1.insert_row(values=workout_header, index=1)
        else:
            pass
        # change name of worksheet 2 for food records
        ws2 = spreadsheet.get_worksheet(1)
        if ws2.title != "Food":
            ws2.update_title("Food")
            ws2.insert_row(values=food_header, index=1)
        else:
            pass
        # change name of worksheet 3 for quests
        ws3 = spreadsheet.get_worksheet(2)
        if ws3.title != "Quest":
            ws3.update_title("Quest")
            ws3.insert_row(values=quest_header, index=1)
        else:
            pass
    except:
        # if not enough worksheet numbers then create new worksheet
        spreadsheet.add_worksheet("new sheet", rows=20, cols=20)
        gym_sheet_initcial(spreadsheet)

def get_sep(event):
    if ',' in event.message.text:
        return ','
    elif '，' in event.message.text:
        return '，'
    elif '/' in event.message.text:
        return '/'
    else:
        return ' '


def record(event, profile, sheet_filename):
    f = open("tmp/" + sheet_filename + ".txt", "r")
    spreadsheet = gclient.open_by_url(f.read())
    row, sr = [], []
    row.append(event.source.user_id)
    dt = datetime.fromtimestamp(event.timestamp / 1000)
    row.append(dt.strftime('%Y-%m-%d'))
    row.append(profile.display_name)
    contents = event.message.text[5:].strip(' ').split(sep=get_sep(event))
    match event.message.text[4]:
        case "w":
            dic = {
                "workout": "",
                "sets": "",
                "reps": "",
                "weight": "",
                "duration": "",
                "distance": "",
                "calories": "",
            }
            for content in contents:
                if content[0] in "1234567890":
                    match content[-1]:
                        case "g" | "b":
                            dic["weight"] = content
                        case "h" | "r" | "n":
                            dic["duration"] = content
                        case "m" | "i":
                            dic["distance"] = content
                        case "l":
                            dic["calories"] = content
                        case _:
                            sr.append(content)
                else:
                    dic["workout"] = content
            if sr:
                dic["sets"] = sr[0]
                dic["reps"] = sr[1]
            for key in [
                "workout",
                "sets",
                "reps",
                "weight",
                "duration",
                "distance",
                "calories",
            ]:
                row.append(str(dic[key]).strip(' '))
            worksheet = spreadsheet.worksheet("Workout")
            worksheet.add_rows(1)
            worksheet.append_row(row)
            questsheet = spreadsheet.worksheet("Quest")
            for c in questsheet.findall(row[3], in_column=3):
                d = (
                    row[1].split('-')
                    + questsheet.cell(c.row, 1).value.split('-')
                    + questsheet.cell(c.row, 2).value.split('-')
                )
                now = datetime(int(d[0]), int(d[1]), int(d[2]))
                start = datetime(int(d[3]), int(d[4]), int(d[5]))
                due = datetime(int(d[6]), int(d[7]), int(d[8]))
                if start <= now and now <= due:
                    if sr:
                        questsheet.update_cell(
                            c.row,
                            5,
                            str(
                                min(
                                    int(questsheet.cell(c.row, 5).value)
                                    + int(sr[0]) * int(sr[1]),
                                    100,
                                )
                            ),
                        )
                    else:
                        questsheet.update_cell(
                            c.row,
                            5,
                            str(min(int(questsheet.cell(c.row, 5).value) + 1, 100)),
                        )
            return True
        case "f":
            for content in contents:
                row.append(content.strip(' '))
            worksheet = spreadsheet.worksheet("Food")
            worksheet.add_rows(1)
            if len(row) < 5:
                time = int(dt.strftime('%H')) + 8
                if time >= 5 and time < 11:
                    row.insert(3, '早餐')
                elif time >= 11 and time < 14:
                    row.insert(3, '午餐')
                elif time >= 14 and time < 17:
                    row.insert(3, '下午')
                elif time >= 17 and time < 21:
                    row.insert(3, '晚餐')
                else:
                    row.insert(3, '宵夜')
            worksheet.append_row(row)
            return True


def post(event, sheet_filename):
    f = open("tmp/" + sheet_filename + ".txt", "r")
    spreadsheet = gclient.open_by_url(f.read())
    row = []
    dt = datetime.fromtimestamp(event.timestamp / 1000)
    row.append(dt.strftime('%Y-%m-%d'))
    with open("tmp/" + event.source.user_id + "_questdue.txt", "r") as f2:
        row.append(f2.read().strip(' '))
    wt = event.message.text[5:].strip(' ').split(sep=get_sep(event))
    row = row + [wt[0].strip(' ')] + [wt[1].strip(' ')]
    row.append(0)
    worksheet = spreadsheet.worksheet("Quest")
    worksheet.add_rows(1)
    worksheet.append_row(row)
    f.close()
    return True
