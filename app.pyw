import re
import time
import sqlite3
import threading
from tkinter import *
from pygame import mixer
from datetime import datetime

alarm_dict = {}
tones_duration = {
    "1": 7,
    "2": 9,
    "3": 2
}

pattern = re.compile("\d{2}:\d{2}$")

######################################################
#                   DATABASE                         #
######################################################
connection = sqlite3.connect("ALARM_DB.db")
cursor = connection.cursor()

query = """
        CREATE TABLE IF NOT EXISTS alarms
        (
            hour varchar(5) PRIMARY KEY NOT NULL,
            tone integer,
            duration integer
        );
        """

cursor.execute(query)
charging = True
######################################################

# Check user input in entry widget
def check_input():
    
    match = re.match(pattern, entry.get())

    if match:
        hs, min_ = match.string.split(":")

        hs = int(hs)
        min_ = int(min_)

        if 0 <= hs <= 23 and 0 <= min_ <= 59:
            return True
        
    return False


def remove_button(entry_txt):
    alarm_dict[entry_txt][0].destroy()
    del alarm_dict[entry_txt]

    query = """
            DELETE FROM alarms WHERE hour = ?
            """
    cursor.execute(query, (entry_txt, ))
    connection.commit()


def add_alarm():
    ok = check_input()

    if ok:
        hs = entry.get()
        tone = choice.get()

        if hs not in alarm_dict:
            btn = Button(root, text = hs, command = lambda: remove_button(hs))
            btn.grid()

            # Save button instance to delete alarm
            alarm_dict[hs] = (btn, tone, tones_duration[tone])

            if not charging:
                query = """
                        INSERT INTO alarms(hour, tone, duration) VALUES (?, ?, ?)
                        """

                cursor.execute(query, (hs, tone, tones_duration[tone]))
                connection.commit()

def add_database_alarms():
    global charging
    data = cursor.execute("SELECT * FROM alarms")

    # There is data in the database
    for row in data.fetchall():
        hs = row[0]
        choice.set(row[1])
        entry.delete(0, END)
        entry.insert(0, hs)
        add_alarm()
        print(row)

    # All data was uploaded
    charging = False

    # After loading the data, we put the current time in the widget
    now = get_time_and_format()
    entry.delete(0, END)
    entry.insert(0, now)
    
# Thread for check time and play alarm sound
def check_time():
    while True:
        now = get_time_and_format()
        
        if now in alarm_dict:
            tone = alarm_dict[now][1]
            duration = alarm_dict[now][2]

            play_sound(tone)
            time.sleep(duration + 3)
        else:
            time.sleep(1)


def get_time_and_format():
    # Get current time
    now = datetime.now()
    hs, min_ = now.hour, now.minute

    # Prefix 0 is added to match the pattern if the hs/min is less than 10
    #if hs < 10: hs = "0" + str(hs)
    #if min_ < 10: min_ = "0" + str(min_)

    # Giving the time format hh:mm
    now = "{:02}:{:02}".format(hs, min_)

    return now

def fast_add(event):
    add_alarm()

def play_sound(tone):
    file = "sounds/" + tone + ".mp3"
    mixer.init()
    s = mixer.Sound(file)
    s.play()


#def finishProgram(e):
    #connection.close()
    
#############
# Start APP #
#############
now = get_time_and_format()

# GUI
root = Tk()
root["bg"] = "lightblue"

now = StringVar(value = now)
choice = StringVar()
choice.set("1")

# Entry
entry = Entry(root, width = 10, textvariable = now)
entry.grid(row = 0, column = 0, sticky = NS, padx = 3, pady = 3)
entry.bind("<Return>", fast_add)

# Button
button = Button(root, text = "+", command = add_alarm)
button.grid(row = 0, column = 1, sticky = NS, padx = 3, pady = 3)

label = Label(root, text = "Choose an alarm tone", bg = "lightblue")
label.grid(row = 0, column = 2, sticky = NS, columnspan = 2)

rb1 = Radiobutton(root, text = "#1", variable = choice, value = 1, bg = "lightblue")
rb2 = Radiobutton(root, text = "#2", variable = choice, value = 2, bg = "lightblue")
rb3 = Radiobutton(root, text = "#3", variable = choice, value = 3, bg = "lightblue")
rb1.grid(row = 1, column = 2)
rb2.grid(row = 1, column = 3)
rb3.grid(row = 2, column = 2)

# Load buttons from DB
add_database_alarms()

#root.bind("<Destroy>", finishProgram)

hilo = threading.Thread(target = check_time, daemon = True)
hilo.start()

root.mainloop()

