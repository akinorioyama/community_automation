# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import appointment_slot_web_object as web_object

class ProcessFailed(RuntimeError):
    """Exception raise when a DDE errpr occures."""
    def __init__(self, msg =""):
        RuntimeError.__init__(self, msg)

def close_screen(webobj):
    try:
        webobj.tryClose()
    except Exception as e:
        print("error closing screen")
        return False
    return True

def prepare_screen(year,month, day):
    try:
        webobj = web_object.webmanagerobj()
        if webobj.createBrowser() == None:
            raise Exception
        webobj.get_agenda_list(year=year,month=month, day=day)
        webobj.login()
        webobj.readBrowserData()
    except Exception as e:
        print("error preparing screen")
        return None
    return webobj

def main():
    isExit = False
    webobj = None
    prevDatetime = datetime.now()
    reopen_timer_in_second = 60
    isToInitiateScreen = True
    while isExit == False:

        # fields for appointment slots
        year = 2021
        month = 8
        day = 5
        title="title"
        starttime_in_hhmm="16:00"
        endtime_in_hhmm="17:00"
        slot_details = "test1\ntest2"
        if webobj == None:
            while webobj == None:
                webobj = prepare_screen(year=year,month=month,day=day)
        else:
            if ( prevDatetime + timedelta(seconds=reopen_timer_in_second) ) <= datetime.now():
            # close by timer to avoid timeout

                closed_or_not = close_screen(webobj=webobj)
                webobj = None

                while webobj == None:
                    webobj = prepare_screen(year=year,month=month,day=day)
                prevDatetime = datetime.now()
                isToInitiateScreen = True

        # prepare screen
        if isToInitiateScreen == True:
            isToInitiateScreen = False
            # pass the fields to create appointment slots
            result_one = webobj.create_slots(title=title,
                                             starttime_in_hhmm=starttime_in_hhmm,endtime_in_hhmm=endtime_in_hhmm,
                                             slot_detail_text=slot_details)
            if result_one is None:
                print(f"Slot not created for title:{title}, date: {year}/{month}/{day} , time:{starttime_in_hhmm}-{endtime_in_hhmm}")
                isToInitiateScreen = True
                webobj = None
                continue
            else:
                print(f"slot created for title:{title}, date: {year}/{month}/{day} , time:{starttime_in_hhmm}-{endtime_in_hhmm}")

if __name__ == '__main__':
    main()