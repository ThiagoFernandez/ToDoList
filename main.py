import json, hashlib, pwinput, os, smtplib
from email.message import EmailMessage
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError


# File
try:
    with open("./task_list.json", "r") as f:
        taskList = json.load(f)
        print("The task list was found")
except FileNotFoundError:
    print("The task list was not found")
    taskList = {
        "users":{}
    }
except json.JSONDecodeError:
    print("The task list was found empty. Starting a new one...")
    taskList = {}
try:
    with open("./notificationSettings.json", "r") as f:
        notificationList = json.load(f)
        print("The notification list was found")
except FileNotFoundError:
    print("The notification list was not found")
    notificationList = {
        "users":{}
    }
except json.JSONDecodeError:
    print("The notification list was found empty. Starting a new one...")
    notificationList = {}
# fix for a new file
def saveFile(fileObject):
    with open("./task_list.json", "w") as f:
        json.dump(fileObject, f, indent=4)

def saveNotificationFile(fileObject):
    with open("./notificationSettings.json", "w") as f:
        json.dump(fileObject, f, indent=4)

# cryptography section
KEY_PATH = "./secret.key"

def loadOrCreateKey():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        return key

key = loadOrCreateKey()
cipher = Fernet(key)

def encrypt_text(text: str) -> str:
    return cipher.encrypt(text.encode("utf-8")).decode("utf-8")

def decrypt_text(token: str) -> str:
    return cipher.decrypt(token.encode("utf-8")).decode("utf-8")

# user functions menu

def userLogin():
    if not taskList["users"]:
        print("Cannot login because there are not a single user yet")
        return userRegister()


    usersList = list(taskList["users"].keys())
    while True:
        for i, users in enumerate(usersList):
            print(f"{i+1}. {users}")
        try:
            option = int(input("Select your user: ")) -1 
            if option <0 or option >=len(usersList):
                print(f"The option must be between 1-{len(usersList)} | Try again")
            else:
                while True:
                    checkPassword = pwinput.pwinput(prompt="Write your password: ", mask="*")
                    hashedCheckedPassword = hashlib.sha256(checkPassword.encode("utf-8")).hexdigest()
                    if hashedCheckedPassword == taskList["users"][usersList[option]]["password"]:
                        return usersList[option]
                    else:
                        print("Wrong password | Try again")
        except ValueError:
            print("The option must be a number | Try again")

def userRegister():
    while True:
        newUser = input("Write your username: ")
        if newUser in taskList["users"]:
            print(f"The username {newUser} is already in use | Try again")
        else:
            break
    while True:
        newPassword = pwinput.pwinput(prompt="Create a password: ", mask="*")
        checkNewPassword = pwinput.pwinput(prompt="Write it again to confirm: ", mask="*")
        if newPassword == checkNewPassword:
            hashpassword = hashlib.sha256(newPassword.encode("utf-8")).hexdigest()
            while True:
                email = input("Write your email: ")
                try:
                    valid = validate_email(email)
                    print("Valid email:", valid.email)
                    break
                except EmailNotValidError as e:
                    print("Invalid email: ", str(e))

            taskList["users"][newUser] = {
                "password": hashpassword,
                "tasks": {
                    "daily": {},
                    "weekly": {},
                    "monthly": {},
                    "yearly": {}
                    }
                }
            notificationList["users"][newUser] = {
                "enabled": "",
                "email": email,
                "time": "09:00",
                "daily": "",
                "weekly": "",
                "monthly": "",
                "yearly": "",
                "next_run": {
                    "daily": "2026-01-08",
                    "weekly": "2026-01-13",
                    "monthly": "2026-02-01",
                    "yearly": "2027-01-01"
                    }
                }
            saveFile(taskList)
            saveNotificationFile(notificationList)
            return newUser

def userSelectorMenu():
    while True:
        print(f"{'Welcome to the user selector menu':-^60}\n1. Login\n2. Register\n3. Exit")
        try:
            option = int(input("Choose an option: "))
            if option>3 or option <1:
                print("The option must be between 1-3 | Try again")
            elif option == 3:
                print("Closing program...")
                return None
            match option:
                case 1:
                    return userLogin()
                case 2:
                    return userRegister()
        except ValueError:
            print("The option must be a number | Try again")
    

# Task manipulation functions
def addWhere(user, where):
    while True:
        taskName = input(f"Write the name of your new {where} task: ").strip().title()

        if not taskName:
            print("Task name can't be empty | Try again")
            continue

        if taskName in taskList["users"][user]["tasks"][where]:
            print(f"That name is already in the {where} task list | Try again")
            continue

        taskList["users"][user]["tasks"][where][taskName] = {
            "description": "",
            "status": "",
            "quadrant": ""
        }

        description = input("Add a description: ").strip()
        taskList["users"][user]["tasks"][where][taskName]["description"] = encrypt_text(description)

        statusList = ["Done", "In progress", "Canceled", "PostPoned", "Need review"]
        while True:
            for i, st in enumerate(statusList, start=1):
                print(f"{i}. {st}")
            try:
                option = int(input("Choose the task status: ")) - 1
                if option < 0 or option >= len(statusList):
                    print(f"The option must be between 1-{len(statusList)} | Try again")
                else:
                    taskList["users"][user]["tasks"][where][taskName]["status"] = statusList[option]
                    break
            except ValueError:
                print("The option must be a number | Try again")

        quadrantList = ["Do First", "Schedule", "Delegate", "Delete"]
        while True:
            for i, q in enumerate(quadrantList, start=1):
                print(f"{i}. {q}")
            try:
                option = int(input("Choose the Eisenhower Matrix Quadrant: ")) - 1
                if option < 0 or option >= len(quadrantList):
                    print(f"The option must be between 1-{len(quadrantList)} | Try again")
                else:
                    taskList["users"][user]["tasks"][where][taskName]["quadrant"] = quadrantList[option]
                    break
            except ValueError:
                print("The option must be a number | Try again")

        break 

    return None


def addTaskMenu(user):
    while True:
        print(f"{'Welcome to the adding a task menu':-^60}\n1. Add in daily\n2. Add in weekly\n3. Add in monthly\n4. Add in yearly\n5. Exit")
        try:
            option = int(input("Choose an option between 1-6: "))
            if option<1 or option>5:
                print("The option must be a number between 1-6 | Try again")
            elif option == 5:
                print("Back to the main menu")
                break
            else:
                match option:
                    case 1:
                        addWhere(user, "daily")
                    case 2:
                        addWhere(user, "weekly")
                    case 3:
                        addWhere(user, "monthly")
                    case 4:
                        addWhere(user, "yearly")
        except ValueError:
            print("The option must be a number | Try again")
    return None

def removeWhere(user, where):
    nameTaskList = list(taskList["users"][user]["tasks"][where].keys())
    if not nameTaskList:
        print(f"You do not have {where} tasks | Back to the menu")
        return None
    while True:
        cont=0
        for i in nameTaskList:
            print(f"{cont+1}. {i}")
            cont+=1
        try:
            option = int(input("Choose a task to remove: "))-1
            if option < 0 or option>=len(nameTaskList):
                print(f"The option must be between 1-{len(nameTaskList)} | Try again")
            else:
                del taskList["users"][user]["tasks"][where][nameTaskList[option]]
                print(f"The task {nameTaskList[option]} has been removed")
                break
        except ValueError:
            print("The option must be a number | Try again")
    return None

def removeTaskMenu(user):
    while True:
        print(f"{'Welcome to the removing a task menu':-^60}\n1. Remove in daily\n2. Remove in weekly\n3. Remove in monthly\n4. Remove in yearly\n5. Exit")
        try:
            option = int(input("Choose an option between 1-5: "))
            if option<1 or option>5:
                print("The option must be a number between 1-5 | Try again")
            elif option == 5:
                print("Back to the main menu")
                break
            else:
                match option:
                    case 1:
                        removeWhere(user, "daily")
                    case 2:
                        removeWhere(user, "weekly")
                    case 3:
                        removeWhere(user, "monthly")
                    case 4:
                        removeWhere(user, "yearly")
        except ValueError:
            print("The option must be a number | Try again")
    return None

def changeWhere(user, where):
    nameTaskList = list(taskList["users"][user]["tasks"][where].keys())
    if not nameTaskList:
        print(f"You do not have {where} tasks | Back to the menu")
        return None
    while True:
        cont = 0
        for i in nameTaskList:
            print(f"{cont+1}. {i}")
            cont+=1
        try:
            option = int(input("Choose a task to change its status: ")) - 1
            if option < 0 or option >= len(nameTaskList):
                print(f"The option must be between 1-{len(nameTaskList)} | Try again")
            else:
                statusList = ["Done", "In progress", "Canceled", "PostPoned", "Need review"]
                for i, status in enumerate (statusList):
                    print(f"{i+1}. {status}")
                try:
                    statusOption = int(input("Choose the new status for your task: ")) -1
                    if statusOption < 0 or statusOption >= len(statusList):
                        print(f"The option must be between 1-{len(statusList)} | Try again")
                    else:
                        taskList["users"][user]["tasks"][where][nameTaskList[option]]["status"]=statusList[statusOption]
                        break
                except ValueError:
                    print("The option must be a number | Try again")
                    
        except ValueError:
            print("The option must be a number | Try again")

def changeTaskStatusMenu(user):
    while True:
        print(f"{'Welcome to the changing task status menu':-^60}\n1. Change in daily\n2. Change in weekly\n3. Change in monthly\n4. Change in yearly\n5. Exit")
        try:
            option = int(input("Choose an option between 1-5: "))
            if option <1 or option >5:
                print("The option must be between 1-5 | Try again")
            elif option == 5:
                print("Back to the main menu")
                break
            else:
                match option:
                    case 1:
                        changeWhere(user, "daily")
                    case 2:
                        changeWhere(user, "weekly")
                    case 3:
                        changeWhere(user, "monthly")
                    case 4:
                        changeWhere(user, "yearly")
        except ValueError:
            print("The option must be a number | Try again")
    return None

# Task display functions

def displayWhat(user, what):
    if what == "all":
        taskListSectionsList = list(taskList["users"][user]["tasks"].keys())
        for i, sections in enumerate(taskListSectionsList):
            nameTaskList = list(taskList["users"][user]["tasks"][sections].keys())
            for j, names in enumerate (nameTaskList):
                print(f"{i+1}-{sections} ----- {j+1}.{names}\nDescription: {decrypt_text(taskList["users"][user]["tasks"][sections][names]["description"])}\nStatus: {taskList["users"][user]["tasks"][sections][names]["status"]}\n")
            print(f"{'':-^60}\n")
    else:
        nameTaskList = list(taskList["users"][user]["tasks"][what].keys())
        for i, names in enumerate(nameTaskList):
            print(f"{what} ----- {i+1}. {names}\nDescription: {decrypt_text(taskList["users"][user]["tasks"][what][names]["description"])}\nStatus: {taskList["users"][user]["tasks"][what][names]["status"]}\n")
    return None

def displayTaskListMenu(user):
    while True:
        print(f"{'Welcome to the displaying task menu':-^60}\n1. Display all your tasks\n2. Display only daily tasks\n3. Display only weekly tasks\n4. Display only monthly tasks\n5. Display only yearly tasks\n6. Exit")
        try:
            option = int(input("Choose an option between 1-6: "))
            if option <1 or option >6:
                print("The option must be between 1-6 | Try again")
            elif option == 6:
                print("Back to the main menu")
                break
            else:
                match option:
                    case 1:
                        displayWhat(user, "all")
                    case 2:
                        displayWhat(user, "daily")
                    case 3:
                        displayWhat(user, "weekly")
                    case 4:
                        displayWhat(user, "monthly")
                    case 5:
                        displayWhat(user, "yearly")
        except ValueError:
            print("The option must be a number | Try again")
    return None

# matrix functions

def collect_by_quadrant(user):
    quadrants = {
        "Do First": [],
        "Schedule": [],
        "Delegate": [],
        "Delete": []
    }

    for section, tasks_in_section in taskList["users"][user]["tasks"].items():
        for name, task in tasks_in_section.items():
            q = task.get("quadrant", "Delete")
            if q not in quadrants:
                q = "Delete"
            quadrants[q].append((section, name, task))

    return quadrants

def displayEisenhowerMatrix(user):
    quads = collect_by_quadrant(user)

    q1 = quads["Do First"]
    q2 = quads["Schedule"]
    q3 = quads["Delegate"]
    q4 = quads["Delete"]

    col_width = 60  

    def fmt(item):
        # item = (section, name, task)
        section, name, task = item
        status = task.get("status", "")
        return f"[{section}] {name} ({status})"

    def print_two_columns(left_title, left_list, right_title, right_list):
        print(f"{left_title:^{col_width}} | {right_title:^{col_width}}")
        print(f"{'-'*col_width} | {'-'*col_width}")
        rows = max(len(left_list), len(right_list))
        for i in range(rows):
            left = fmt(left_list[i]) if i < len(left_list) else ""
            right = fmt(right_list[i]) if i < len(right_list) else ""
            print(f"{left:<{col_width}} | {right:<{col_width}}")
        print()

    print_two_columns("DO FIRST (Urgent+Important)", q1, "SCHEDULE (Important+Not Urgent)", q2)
    print_two_columns("DELEGATE (Urgent+Not Important)", q3, "DELETE (Neither)", q4)
          
def displayEisenhowerMatrixMenu(user):
    while True:
        print(f"{'Welcome to the Eisenhower Matrix menu':-^60}\n1. Display matrix\n2. Exit")
        try:
            option = int(input("Choose an option: "))
            if option == 1:
                displayEisenhowerMatrix(user)
            elif option == 2:
                print("Back to the main menu")
                break
            else:
                print("The option must be between 1-2 | Try again")
        except ValueError:
            print("The option must be a number | Try again")

# notifications functions

def sendEmail(subject, body, to_email):
    msg = EmailMessage()
    msg["From"] = "todolistwithpy@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("todolistwithpy@gmail.com", "fqyd atpz bqdn fflg")
        smtp.send_message(msg)

def tuneNotifications(user, mode):
    if "enabled" not in notificationList["users"][user]:
        notificationList["users"][user]["enabled"] = ""

    notifications = notificationList["users"][user]["email"]
    if mode == "True":
        if notificationList["users"][user]["email"] == "":
            while True:
                email = input("Write your email:  ")
                notificationList["users"][user]["email"] = email
                break
        notificationList["users"][user]["enabled"] = mode
        try:
            sendEmail(
                "Notifications activated",
                "Now you will be receiving your tasks that are not done yet",
                notificationList["users"][user]["email"]
            )
            return None
        except Exception as e:
            print("Could not send a email:", e)
    else:
        notificationList["users"][user]["enabled"] = mode
        try:
            sendEmail(
                "Notifications deactivated",
                "Now you will not be receiving your tasks",
                notificationList["users"][user]["email"]
            )
            
            return None
        except Exception as e:
            print("Could not send WhatsApp message:", e)


def notificationSettings(user, what, state):
    if what == "all":
        if state == "True":
            notificationList["users"][user]["daily"] = state
            notificationList["users"][user]["weekly"] = state
            notificationList["users"][user]["monthly"] = state
            notificationList["users"][user]["yearly"] = state
        else:
            notificationList["users"][user]["daily"] = state
            notificationList["users"][user]["weekly"] = state
            notificationList["users"][user]["monthly"] = state
            notificationList["users"][user]["yearly"] = state
    else:
        notificationList["users"][user][what] = state
    return None

def manageNotificationSettings(user):
    while True:
        print(f"{'Welcome to the notificacion queue manager':-^60}\n1. All your tasks\n2. Daily tasks\n3. Weekly tasks\n4. Monthly tasks\n5. Yearly tasks\n6. Exit")
        try:
            option = int(input("Choose an option: "))
            if option <1 or option >6:
                print("The option must be between 1-6 | Try again")
            elif option == 6:
                print("Back to the menu")
                break
            else:
                while True:
                    print(f"1. Off\n2. On")
                    try:
                        mode = int(input("Choose to turn them off or on: "))
                        if mode<1 or mode>2:
                            print("The option must be between 1-2| Try again")
                        else:
                            if mode == 1:
                                mode = "False"
                                break
                            else:
                                mode = "True"
                                break
                    except ValueError:
                        print("The option must be a number | Try again ")
                match option:
                    case 1:
                        notificationSettings(user, "all", mode)
                        saveNotificationFile(notificationList)
                    case 2:
                        notificationSettings(user, "daily", mode)
                        saveNotificationFile(notificationList)
                    case 3:
                        notificationSettings(user, "weekly", mode)
                        saveNotificationFile(notificationList)
                    case 4:
                        notificationSettings(user, "monthly", mode)
                        saveNotificationFile(notificationList)
                    case 5:
                        notificationSettings(user, "yearly", mode)
                        saveNotificationFile(notificationList)
        except ValueError:
            print("The option must be a number | Try again")
    return None

def getPendingTaskNames(user, section):
    # section: "daily" | "weekly" | "monthly" | "yearly"
    tasks = taskList["users"][user]["tasks"][section]
    return [name for name, t in tasks.items() if t.get("status") != "Done"]

def parse_time_hhmm(timeStr: str):
    if not isinstance(timeStr, str):
        return None
    timeStr = timeStr.strip()
    if timeStr == "":
        return None
    try:
        dt = datetime.strptime(timeStr, "%H:%M")
        return dt.hour, dt.minute
    except ValueError:
        return None


def parse_next_run(next_run_str: str):
    if not next_run_str:
        return None

    s = next_run_str.strip()

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    return None

def bumpNextRun(user, section, timeStr):
    now = datetime.now()
    hm = parse_time_hhmm(timeStr)
    if hm:
        hh, mm = hm
    else:
        hh, mm = 9, 0

    if section == "daily":
        nxt = (now + timedelta(days=1)).replace(hour=hh, minute=mm, second=0, microsecond=0)

    elif section == "weekly":
        nxt = (now + timedelta(days=7)).replace(hour=hh, minute=mm, second=0, microsecond=0)

    elif section == "monthly":
        y, m = now.year, now.month
        if m == 12:
            y += 1; m = 1
        else:
            m += 1
        nxt = now.replace(year=y, month=m, day=1, hour=hh, minute=mm, second=0, microsecond=0)

    elif section == "yearly":
        nxt = now.replace(year=now.year+1, month=1, day=1, hour=hh, minute=mm, second=0, microsecond=0)

    notificationList["users"][user]["next_run"][section] = nxt.strftime("%Y-%m-%d %H:%M")

    saveNotificationFile(notificationList)

def notificationFlag(user, section, timeStr):
    now = datetime.now()

    nextRunStr = notificationList["users"][user]["next_run"][section]
    nextRunDt = parse_next_run(nextRunStr)
    if not nextRunDt:
        return 0

    # si el nextRun viene sin hora (00:00), metemos la hora del usuario
    if nextRunDt.hour == 0 and nextRunDt.minute == 0:
        hm = parse_time_hhmm(timeStr)
        if not hm:
            return 0
        hh, mm = hm
        nextRunDt = nextRunDt.replace(hour=hh, minute=mm)

    if now < nextRunDt:
        return 0

    bumpNextRun(user, section, timeStr)  # actualiza next_run y guarda JSON
    return 1


def sendTasks(user, timeStr):

    if notificationList["users"][user]["enabled"] == "False":
        return None
    
    def block(title, items):
        if not items:
            return f"{title}: sin pendientes"
        lines = "\n".join([f"- {name}" for name in items])
        return f"{title} pendientes ({len(items)}):\n{lines}"
    
    msg_parts = []

    if notificationList["users"][user]["daily"] =="True":
        flag = notificationFlag(user, "daily", timeStr)
        if flag == 1:
            dailyTasks  = getPendingTaskNames(user, "daily")
            msg_parts.append(block("DAILY", dailyTasks))

    if notificationList["users"][user]["weekly"] =="True":
        flag = notificationFlag(user, "weekly", timeStr)
        if flag == 1:
            weeklyTasks = getPendingTaskNames(user, "weekly")
            msg_parts.append(block("WEEKLY", weeklyTasks))

    if notificationList["users"][user]["monthly"] =="True":
        flag = notificationFlag(user, "monthly", timeStr)
        if flag == 1:
            monthlyTasks= getPendingTaskNames(user, "monthly")
            msg_parts.append(block("MONTHLY", monthlyTasks))

    if notificationList["users"][user]["yearly"] =="True":
        flag = notificationFlag(user, "yearly", timeStr)
        if flag == 1:
            yearlyTasks = getPendingTaskNames(user, "yearly")
            msg_parts.append(block("YEARLY", yearlyTasks))

    if msg_parts != []:
        final_msg = "\n\n".join(msg_parts)

        email = notificationList["users"][user]["email"]
        if not email:
            print("No email configured.")
            return None

        else:
            sendEmail("TASKS REPORT", final_msg, email)
            return None
        
            
    else:
        return None

def sendNotifications(user):
    while True:
        print(f"{'Welcome to the notification menu':-^60}\n1. Activate notifications\n2. Deactivate notifications\n3. Manage notifications\n4. Exit")  
        try:
            option = int(input("Choose an option: "))
            if option < 1 or option > 4:
                print("The option must be between 1-3 | Try again")
            elif option == 4:
                print("Back to the menu")
                break
            else:
                match option:
                    case 1:
                        tuneNotifications(user, "True")
                        saveNotificationFile(notificationList)
                    case 2:
                        tuneNotifications(user, "False")
                        saveNotificationFile(notificationList)
                    case 3:
                        manageNotificationSettings(user)
        except ValueError:
            print("The option must be a number | Try again")
    return None

# User settings section

def displayUserSettings(user):
    notificationSettingsList = list(notificationList["users"][user].keys())
    for i, setting in enumerate(notificationSettingsList):
        if setting == "next_run":
            next_runList = list(notificationList["users"][user]["next_run"].keys())
            for j, section in enumerate(next_runList):
                print(f"{i+1}.{j+1}. {section}:{notificationList["users"][user]["next_run"][section]}")
        else:
            print(f"{i+1}. {setting}:{notificationList["users"][user][setting]}")

    return None

def changeWhatSetting(user, what):
    if what == "password":
        newPassword = pwinput.pwinput(prompt="Write your new password: ", mask="*")
        newHashedPassword = hashlib.sha256(newPassword.encode("utf-8")).hexdigest()
        taskList["users"][user][what]=newHashedPassword
        saveFile(taskList)
    else:
        if what == "time":
            while True:
                newWhat = input(f"Write your new {what}: ")
                if parse_time_hhmm(newWhat) == None:
                    print(f"The {what} format must be hh:mm | Try again")
                else:
                    break
        else:
            print(f"Remember that if your {what} does not have @gmail.com or alike, the system cannot send you notifications")
            while True:
                newWhat = input(f"Write your new {what}: ")
                try:
                    valid = validate_email(newWhat)
                    print("Valid email:", valid.email)
                    break
                except EmailNotValidError as e:
                    print("Invalid email:", str(e))
        
        notificationList["users"][user][what] = newWhat
        print(f"Your {what} has been changed")
    
    return None

def deleteUser(user):
    while True:
        print(f"Once deleted the user, it cannot be restored\nWrite -1 if you want to go back")
        decision = input("Write your password to delete your user: ") 
        if decision == "-1":
            print("Back to the menu")
            break
        else:
            decisionHashed = hashlib.sha256(decision.encode("utf-8")).hexdigest()
            if decisionHashed == taskList["users"][user]["password"]:
                del taskList["users"][user]
                del notificationList["users"][user]
                saveFile(taskList)
                saveNotificationFile(notificationList)
                newActiveUser = userSelectorMenu()
                if newActiveUser == None:
                    return -1
    return None

def userSettingsMenu(user):
    while True:
        print(f"{'Welcome to the user settings menu':-^60}\n1. See your settings\n2. Change your mail\n3. Change your notification time\n4. Change your password\n5. Delete user\n6. Exit")
        try:
            option = int(input("Choose an option: "))
            if option <1 or option>6:
                print("The option must be between 1-5 | Try again")
            elif option == 6:
                print("Back to the menu")
                break
            else:
                match option:
                    case 1:
                        displayUserSettings(user) 
                    case 2:
                        changeWhatSetting(user, "email")
                    case 3:
                        changeWhatSetting(user,  "time")
                    case 4:
                        changeWhatSetting(user,  "password")
                    case 5:
                        result = deleteUser(user)
                        if result == -1:
                            return -1
        except ValueError:
            print("The option must be a number | Try again")
    return None


# m.p
def mainMenu(user):
    while True:
        sendTasks(user, reportTasksTime)
        print(f"{'Welcome to the main menu':-^60}\n1. Add a task\n2. Remove a task\n3. Change task's status\n4. Display your task list\n5. Display your Eisenhower Matrix\n6. Activate/deactivate notifications\n7. User settings\n8. Exit")
        try:
            option = int(input("Choose an option: "))
            if option<1 or option>8:
                print("The option must be a number between 1-8 | Try again")
            elif option ==8:
                print("See you next time")
                break
            else:
                match option:
                    case 1:
                        addTaskMenu(user)
                        saveFile(taskList)
                    case 2:
                        removeTaskMenu(user)
                        saveFile(taskList)
                    case 3:
                        changeTaskStatusMenu(user)
                        saveFile(taskList)
                    case 4:
                        displayTaskListMenu(user)
                        saveFile(taskList)
                    case 5:
                        displayEisenhowerMatrixMenu(user)
                        saveFile(taskList)
                    case 6:
                        sendNotifications(user)
                    case 7:
                        result = userSettingsMenu(user)
                        if result == -1:
                            return None
        except ValueError:
            print("The option must be a number | Try again")

activeUser = userSelectorMenu()
if activeUser != None:
    reportTasksTime = notificationList["users"][activeUser]["time"]
    mainMenu(activeUser)
