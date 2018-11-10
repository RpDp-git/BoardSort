from icalendar import Calendar
import os
import exifread
import datetime as dt
import codecs
import tkinter as tk
from tkinter import filedialog
import shutil
import traceback
root= tk.Tk()
data=[]

strt_date=dt.datetime(1970,12,3,12,12,12)
##Look for previous run:



#### UI
root.title("BoardSort")

title=tk.Label(root,text="BoardSort",font=("Times New Roman", 25),padx=150)
rcrdl=tk.Label(root,text="Start Sorting",font=("Times New Roman", 12))
rcrdl.grid(row=1)
title.grid(row=0)
var1=tk.IntVar()
tk.Label(root,text="").grid(row=2,pady=10)
tk.Checkbutton(root, text="Use custom start date: "+"DD-MM-YY",font=("Times New Roman", 10),
variable=var1).grid(column=0,row=3)
cdate=tk.StringVar()
cdatee = tk.Entry(root,textvariable=cdate).grid(row=4)
tk.Label(root,text="").grid(row=5,pady=10)

try :
    file=open("BoardSort.ini","r+")
    strt_date=dt.datetime.strptime(file.read(),"%Y-%m-%d %H:%M:%S")
    rcrdl.configure(text="Last run on "+str(strt_date.date()))
    file.close()
except:
    pass

# Functions

def open_calfile():
   root.fileName =  filedialog.askopenfile(initialdir="/~", title="select calendar file", filetypes=(("icalendar files", ".ics"), ("all files", "*.*")))
   tk.Label(text=str(root.fileName.name)).grid(row=6,column=0,padx=(40,0))
   global cpath
   cpath = root.fileName.name


#Fix problems with foreign characters
def encoding_fix(source):
    try:
        with codecs.open(source,'r',encoding='utf-16-le') as f :
            text=f.read()
    except:
        with codecs.open(source,'r',encoding='utf-8') as f :
            text=f.read()

    with codecs.open("cal_file.ics",'w',encoding='utf-8') as f :
        f.write(text)

    f.close()

def open_sourcedir():
   root.fileName =  filedialog.askdirectory(initialdir="/~")
   tk.Label(text=str(root.fileName)).grid(row=7,column=0,padx=(40,0))
   global sourcepath
   sourcepath = root.fileName


def collect_data(source):
    flag=0

    g=open(source,'rb')
    gcal = Calendar.from_ical(g.read())

    #Get schedule data from the file
    for e in gcal.walk():
        if e.name=="VEVENT":
                if e.get("dtstart").dt.weekday()==0 and flag==0 :
                    event=[]
                    label = str(e.get("summary"))
                    day=0
                    start=e.get("dtstart").dt.time()
                    end=e.get("dtend").dt.time()
                    event=[day,start,end,label]
                    data.append(event)
                    continue
                flag=1

                if e.get("dtstart").dt.weekday()==0 and flag==1 :
                    break
                event=[]
                label = str(e.get("summary"))
                day=e.get("dtstart").dt.weekday()
                start=e.get("dtstart").dt.time()
                end=e.get("dtend").dt.time()
                event=[day,start,end,label]
                data.append(event)
    return data

#make directories
def mkdir(data):
    for i in data:
        try:
            os.mkdir(i[3])
        except:
            continue

def about():
    popup=tk.Tk()
    popup.wm_title("About")
    B1=tk.Label(popup,text="Version 1.0",font=("Times New Roman", 12))
    B1.pack(pady=10,padx=10)
    B2=tk.Label(popup,text="Created by Ravi Pradip",font=("Times New Roman", 10))
    B2.pack(pady=5,padx=10)
    B3=tk.Button(popup,text="Close",command=popup.destroy)
    B3.pack(pady=10)
    popup.mainloop()




def predict(dtinfo):
    for cur_event in data :
        if dtinfo.weekday()==cur_event[0] and dtinfo.time()>=cur_event[1] and dtinfo.time()<=cur_event[2]:
            return cur_event[3]
    return 'None'


#parse through all files
def mains():
    try:
        T.configure(text="Status: Working")
        encoding_fix(cpath)
        data= collect_data("cal_file.ics")
        try:
            h=dt.datetime.strptime(cdate.get(),'%d-%m-%Y')
        except:
            h=dt.datetime(1970,12,3,12,12,12)


        else:
            pass

        mkdir(data)

        for filename in os.listdir(sourcepath):
            if filename.endswith(".jpg"):
                f=open(str(sourcepath)+'/'+str(filename),'rb')
                tag=exifread.process_file(f)
                try:
                    x=tag['EXIF DateTimeOriginal']
                except:
                    pass
                dtinfo=str(x)
                dtinfo=dt.datetime.strptime(dtinfo,'%Y:%m:%d %H:%M:%S')
                dir=predict(dtinfo)
                f.close()
            if(var1.get()):
                if dir!='None' and dtinfo>h:
                    shutil.copy(str(sourcepath)+'/'+str(filename), dir)

            else:

                if dir!='None' and dtinfo>strt_date:
                    shutil.copy(str(sourcepath)+'/'+str(filename), dir)


        T.configure(text="Sorting Complete !")



        file=open("BoardSort.ini","w+")
        file.write(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        file.close()

    except :
            
            T.configure(text="Error:Check file paths and date(if entered)")

cal_button = tk.Button(root, text="iCalendar File", command=open_calfile).grid(row=6,column=0,sticky='W',padx=(25,0))
source_button = tk.Button(root, text="Source Dir", command=open_sourcedir).grid(row=7,column=0,sticky='W',padx=(25,0),pady=5)
#dest_button = tk.Button(root, text="Destination Dir", command=open_destdir).grid(row=8,column=0,sticky='W',padx=(25,0),pady=3)
sort_button = tk.Button(root, text="SORT",bg='red',command=mains).grid(pady=10)
about_btton=tk.Button(root, text="About",command=about).grid(row=9,column=0,sticky='W',padx=(25,0),pady=5)
T=tk.Label(root,text="Status: Idle")
T.grid(row=10,pady=2)

root.mainloop()
