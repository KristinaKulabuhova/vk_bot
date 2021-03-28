
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import time, datetime, timedelta, date
from enum import Enum
import requests
import get_pictures
import threading
from time import sleep

import logger

list_of_users = []
token = ''
id_headman = 0

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
session = requests.Session()

log_engine_main_thread = logger.Logger("main_thread_run_log.txt")
log_engine_notification_thread = logger.Logger("notification_thread_run_log.txt")


class Weekdays(Enum):
    MON = 0
    TUE = 1
    WEN = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class lesson:

    def __init__(self, time, room, name, link):
        self.time  = time
        self.room  = room
        self.name  = name
        self.link  = link

timetables = {'вторник' : 'https://raw.githubusercontent.com/KristinaKulabuhova/VK_bot_photos/master/pictures/Tuesday.jpg',
              'среда'   : 'https://raw.githubusercontent.com/KristinaKulabuhova/VK_bot_photos/master/pictures/Wednesday.jpg',
              'четверг' : 'https://raw.githubusercontent.com/KristinaKulabuhova/VK_bot_photos/master/pictures/Thursday.jpg',
              'пятница' : 'https://raw.githubusercontent.com/KristinaKulabuhova/VK_bot_photos/master/pictures/Friday.jpg',
              'суббота' : 'https://raw.githubusercontent.com/KristinaKulabuhova/VK_bot_photos/master/pictures/Saturday.jpg'}

lessons=\
            {
             Weekdays.MON : [],
             Weekdays.TUE : 
                    [lesson(time=time(9, 00, 00),  room='УЛК_1 №2.36',     name='Практика на С++',                      link= None),
                     lesson(time=time(12, 20, 00), room='413 ГК',          name='Гармонический анализ',                 link= None),
                     lesson(time=time(13, 55, 00), room='НК',              name='Иностранный язык',                     link= None),
                     lesson(time=time(17, 5, 00),  room='(без аудитории)', name='Физическая культура',                  link= None)],
             Weekdays.WEN: 
                    [lesson(time=time(9, 00, 00),  room='422 ГК',          name='Диффуренциальные уравнения',           link= None),
                     lesson(time=time(10, 45, 00), room='(без аудитории)', name='Физическая культура',                  link= None),
                     lesson(time=time(12, 20, 00), room='УЛК_2 №424',      name='ТиПМС',                                link= None),
                     lesson(time=time(17, 5, 00),  room='УЛК_2 №418-419',  name='Базы данных',                          link= None)],
             Weekdays.THU: 
                    [lesson(time=time(9, 00, 00),  room='202 НК',          name='Гармонический анализ. Лекция',         link= ""),
                     lesson(time=time(13, 55, 00), room='113 ГК',          name='Дискретные структуры. Лекция',         link= "")],
             Weekdays.FRI: 
                    [lesson(time=time(9, 00, 00),  room='УЛК_1 №2.36',     name='Практика на С++',                      link= None),
                     lesson(time=time(12, 20, 00), room='512 ГК',          name='Теория вероятностей',                  link= None),
                     lesson(time=time(13, 55, 00), room='НК',              name='Иностранный язык',                     link= None),
                     lesson(time=time(17, 5, 00),  room='518 ГК',          name='Дискретные структуры',                 link= None)],
             Weekdays.SAT: 
                    [lesson(time=time(9, 00, 00),  room='(без аудитории)', name='Дифференциальные уравнения. Лекция',   link= ""),
                     lesson(time=time(10, 45, 00), room='(без аудитории)', name='Теория вероятностей. Лекция',          link= ""),
                     lesson(time=time(12, 20, 00), room='(без аудитории)', name='ТиПМС. Лекция',                        link= ""),
                     lesson(time=time(13, 55, 00), room='(без аудитории)', name='Базы данных. Лекция',                  link= ""),
                     lesson(time=time(16, 30, 00), room='(без аудитории)', name='Введение в анализ данных. Лекция',     link= None)],
             Weekdays.SUN: []}


def get_time_difference(t1, t2):
    current_day = date.today()
    return datetime.combine(current_day, t1) -  datetime.combine(current_day, t2)

def the_nearest_lesson():
    time = datetime.now().time()
    day = Weekdays(datetime.now().weekday())

    min_delta = timedelta.max
    lesson_idx = -1

    for i in range(len(lessons[day])):
        if lessons[day][i].time > time:
            cur_delta = get_time_difference(lessons[day][i].time, time)
            if cur_delta < min_delta:
                min_delta = cur_delta
                lesson_idx = i

    return (lesson_idx, day)
  

def the_nearest_lesson_string():
    log_engine_main_thread.log("the_nearest_lesson_string")

    lesson_idx, day = the_nearest_lesson()
    
    if lesson_idx == -1:
        return 'На сегодня пары закончились)'

    closest_lesson = lessons[day][lesson_idx]
    return closest_lesson.name + ' в ' + closest_lesson.time.strftime("%H:%M") + '. Аудитория ' + closest_lesson.room


def create_menu():
    log_engine_main_thread.log("create_menu")

    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(label='Расписание',     color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(label='Ближайшая пара', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_openlink_button(label='Полезные материалы', link="")

    return keyboard.get_keyboard()


def create_lecture():
    log_engine_main_thread.log("create_lecture")

    keyboard = VkKeyboard(one_time=False)

    lesson_idx, day = the_nearest_lesson()
    closest_lesson = lessons[day][lesson_idx]
    keyboard.add_openlink_button(label= closest_lesson.name, link= closest_lesson.link)
    keyboard.add_line()
    keyboard.add_button(label='Меню', color=VkKeyboardColor.POSITIVE)

    return keyboard.get_keyboard()


def create_keyboard(response):
    log_engine_main_thread.log("create_keyboard")

    keyboard = VkKeyboard(one_time=True)

    if response == 'расписание':

        keyboard.add_button(label='Вторник', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='Среда',   color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='Четверг', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='Пятница', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='Суббота', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='Меню', color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def send_message(id, message=None, attachment=None, keyboard=None):
    log_engine_main_thread.log("send_message")
    vk_session.method('messages.send', {'user_id': id, 'message': message, 'random_id': 0, 'attachment': attachment, 'keyboard': keyboard})

# global variable
keyboard_menu = create_menu()

def main():
    try: 
        log_engine_main_thread.log("main:")
        log_engine_main_thread.log("Longpoll listen")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                log_engine_main_thread.log("Got message")
                id = event.user_id
                response = event.text.lower()

                if list_of_users.count(id) == 0:
                    list_of_users.append(id)

                if event.from_user and id == id_headman and not event.from_me:
                    if 'all' in response:
                        log_engine_main_thread.log("Got announcement from headman")
                        for user in list_of_users:
                            if not user == id_headman:
                                send_message(user, message=event.text, keyboard=keyboard_menu)
                            else:
                                send_message(user, message='Сообщение отправлено', keyboard=keyboard_menu)

                elif event.from_user and not event.from_me:

                    if response ==   'расписание':
                        log_engine_main_thread.log("Sending timetable")
                        keyboard = create_keyboard(response)
                        send_message(id, message='Выберите день', keyboard=keyboard)

                    elif response == 'ближайшая пара':
                        log_engine_main_thread.log("Sending nearest lesson")
                        lesson_idx, day = the_nearest_lesson()
                        if lessons[day][lesson_idx].link == None or lesson_idx == -1:
                            keyboard=keyboard_menu
                        else:
                            keyboard = create_lecture()
                        send_message(id, message=the_nearest_lesson_string(), keyboard=keyboard)

                    elif response in timetables.keys():
                        log_engine_main_thread.log("Sending timetable for a day")
                        attachment = get_pictures.get(vk_session, session, timetables[response])
                        send_message(id, message=response.capitalize(), attachment=attachment, keyboard=keyboard_menu)
                    else:
                        log_engine_main_thread.log("Sending usage")
                        send_message(id, message='Возможные действия', keyboard=keyboard_menu)
    except Exception as e:
        log_engine_main_thread.log(str(e))

def notification_thread_worker():
    log_engine_notification_thread.log("Notification thread worker:")
    last_lesson = -1

    while True:
        lesson_idx, day = the_nearest_lesson()
        
        if lesson_idx != -1 and last_lesson != lesson_idx:
            delta = get_time_difference(lessons[day][lesson_idx].time, datetime.now().time())
            ten_minute_delta = timedelta(minutes=10)

            if delta <= ten_minute_delta:

                keyboard = None
                if lessons[day][lesson_idx].link != None:
                    keyboard = create_lecture()

                for user in list_of_users:
                    log_engine_notification_thread.log("sending notifications")
                    send_message(user, message='Через десять минут начнется ' + lessons[day][lesson_idx].name + ' в аудитории ' + lessons[day][lesson_idx].room, keyboard=keyboard)
                    last_lesson = lesson_idx
        else:
            sleep(15)


class MainThreadClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        log_engine_main_thread.log("Main thread start")
        while True:
            main()

class NotificationThreadClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        log_engine_notification_thread.log("Notification thread start")
        notification_thread_worker()


main_thread = MainThreadClass()
notification_thread = NotificationThreadClass()

main_thread.start()
notification_thread.start()
