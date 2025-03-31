############################################# IMPORTING ################################################
from pymongo import MongoClient
import base64
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2, os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import io
from dotenv import load_dotenv  # Import dotenv
from cryptography.fernet import Fernet 

# Load environment variables
load_dotenv()
import os

# Connect to MongoDB using the URI from .env file
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MongoDB URI not found in .env file")

client = MongoClient(MONGO_URI)
db = client["face_detection_db"]  # Database name
collection = db["face_images"]  # Collection name


# Encryption Key Setup
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("Encryption key not found in .env file")

cipher = Fernet(ENCRYPTION_KEY.encode())  # Convert key to Fernet object

############################################# FUNCTIONS ################################################

def assure_path_exists(path):
    """Ensures that a given directory path exists, creates it if not."""
    if not os.path.exists(path):
        os.makedirs(path)

##################################################################################

def tick():
    """Updates the clock label every 200ms with the current time."""
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200, tick)

###################################################################################

def contact():
    """Displays the contact information in a message box."""
    mess.showinfo(title="Contact Us", message="Please contact us at: 'gaurav552sharma@gmail.com'")

###################################################################################

def check_haarcascadefile():
    """Checks if the Haarcascade file exists; if not, prompts the user and closes the application."""
    if not os.path.isfile("haarcascade_frontalface_default.xml"):
        mess.showerror(title="File Missing", message="Haarcascade file is missing! Please contact support.")
        window.destroy()


###################################################################################

def save_pass():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel\psd.txt")
    if exists1:
        tf = open("TrainingImageLabel\psd.txt", "r")
        key = tf.read()
    else:
        master.destroy()
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess._show(title='No Password Entered', message='Password not set!! Please try again')
        else:
            tf = open("TrainingImageLabel\psd.txt", "w")
            tf.write(new_pas)
            mess._show(title='Password Registered', message='New password was registered successfully!!')
            return
    op = (old.get())
    newp= (new.get())
    nnewp = (nnew.get())
    if (op == key):
        if(newp == nnewp):
            txf = open("TrainingImageLabel\psd.txt", "w")
            txf.write(newp)
        else:
            mess._show(title='Error', message='Confirm new password again!!!')
            return
    else:
        mess._show(title='Wrong Password', message='Please enter correct old password.')
        return
    mess._show(title='Password Changed', message='Password changed successfully!!')
    master.destroy()

###################################################################################

def change_pass():
    global master
    master = tk.Tk()
    master.geometry("400x160")
    master.resizable(False,False)
    master.title("Change Password")
    master.configure(background="white")
    lbl4 = tk.Label(master,text='    Enter Old Password',bg='white',font=('comic', 12, ' bold '))
    lbl4.place(x=10,y=10)
    global old
    old=tk.Entry(master,width=25 ,fg="black",relief='solid',font=('comic', 12, ' bold '),show='*')
    old.place(x=180,y=10)
    lbl5 = tk.Label(master, text='   Enter New Password', bg='white', font=('comic', 12, ' bold '))
    lbl5.place(x=10, y=45)
    global new
    new = tk.Entry(master, width=25, fg="black",relief='solid', font=('comic', 12, ' bold '),show='*')
    new.place(x=180, y=45)
    lbl6 = tk.Label(master, text='Confirm New Password', bg='white', font=('comic', 12, ' bold '))
    lbl6.place(x=10, y=80)
    global nnew
    nnew = tk.Entry(master, width=25, fg="black", relief='solid',font=('comic', 12, ' bold '),show='*')
    nnew.place(x=180, y=80)
    cancel=tk.Button(master,text="Cancel", command=master.destroy ,fg="black"  ,bg="red" ,height=1,width=25 , activebackground = "white" ,font=('comic', 10, ' bold '))
    cancel.place(x=200, y=120)
    save1 = tk.Button(master, text="Save", command=save_pass, fg="black", bg="#00fcca", height = 1,width=25, activebackground="white", font=('comic', 10, ' bold '))
    save1.place(x=10, y=120)
    master.mainloop()

#####################################################################################

def psw():
    """Checks password before training images."""
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel/psd.txt")
    
    if exists1:
        with open("TrainingImageLabel/psd.txt", "r") as tf:
            key = tf.read()
    else:
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas is None:
            mess.showwarning(title='No Password Entered', message='Password not set! Please try again.')
        else:
            with open("TrainingImageLabel/psd.txt", "w") as tf:
                tf.write(new_pas)
            mess.showinfo(title='Password Registered', message='New password was registered successfully!')
            return

    password = tsd.askstring('Password', 'Enter Password', show='*')
    if password == key:
        TrainImages()  # Train images and save them in MongoDB instead of local storage
    elif password is None:
        pass
    else:
        mess.showerror(title='Wrong Password', message='You have entered the wrong password')


######################################################################################

def clear():
    txt.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)


def get_registered_users_count():
    if not os.path.isfile("StudentDetails/StudentDetails.csv"):
        return 0  # No users registered yet

    with open("StudentDetails/StudentDetails.csv", 'r') as csvFile:
        reader = csv.reader(csvFile)
        next(reader, None)  # Skip the header

        registered_users = set()  # Use a set to store unique IDs
        for row in reader:
            if len(row) > 2 and row[2].strip().isdigit():  # Ensure ID is valid
                registered_users.add(row[2].strip())

    return len(registered_users)


#######################################################################################
def TakeImages():
    check_haarcascadefile()
    assure_path_exists("StudentDetails/")  # Ensure CSV folder exists
    
    serial = get_registered_users_count() + 1  # Correctly count total users
    Id = txt.get()
    name = txt2.get()

    if name.isalpha() or ' ' in name:
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0

        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum += 1

                # Convert image to binary format
                _, img_encoded = cv2.imencode('.jpg', gray[y:y + h, x:x + w])
                img_bytes = img_encoded.tobytes()

                # Encrypt Image Data
                encrypted_img = cipher.encrypt(img_bytes)

                # Store Encrypted Image in MongoDB
                collection.insert_one({
                    "filename": f"{name}.{serial}.{Id}.{sampleNum}.jpg",
                    "user_id": Id,
                    "name": name,
                    "image_data": encrypted_img
                })

                # Display frame
                cv2.imshow('Taking Images', img)

            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 100:
                break

        cam.release()
        cv2.destroyAllWindows()

        res = f"Images Taken for ID: {Id}"
        with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([serial, '', Id, '', name])

        message1.configure(text=res)
    else:
        res = "Enter Correct Name"
        message.configure(text=res)


########################################################################################
def TrainImages():
    check_haarcascadefile()
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    
    faces, ID = getImagesAndLabels_from_MongoDB()  # Retrieve images from MongoDB
    
    try:
        recognizer.train(faces, np.array(ID))
    except:
        mess.showerror(title='No Registrations', message='Please Register someone first!')
        return

    # Save trained model locally
    recognizer.save("TrainingImageLabel/Trainner.yml")

    res = "Profile Saved Successfully"
    message1.configure(text=res)
    total_users = get_registered_users_count()  # Get correct total users
    message.configure(text=f'Total Registrations till now: {total_users}')


############################################################################################3
def getImagesAndLabels_from_MongoDB():
    faceSamples = []
    ids = []
    
    for record in collection.find():
        encrypted_img = record["image_data"]
        user_id = int(record["user_id"])  # Convert to int for recognizer
        
        # Decrypt Image Data
        decrypted_img_bytes = cipher.decrypt(encrypted_img)

        # Convert bytes back to image
        image = Image.open(io.BytesIO(decrypted_img_bytes))
        gray_image = np.array(image, 'uint8')  # Convert to NumPy array

        faceSamples.append(gray_image)
        ids.append(user_id)

    return faceSamples, ids


###########################################################################################
def TrackImages():
    check_haarcascadefile()
    assure_path_exists("Attendance/")

    global tv
    if 'tv' not in globals():
        tv = ttk.Treeview()  # Placeholder, replace with actual Treeview initialization

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    exists3 = os.path.isfile("TrainingImageLabel/Trainner.yml")
    if exists3:
        recognizer.read("TrainingImageLabel/Trainner.yml")
    else:
        mess.showerror(title='Data Missing', message='Please click on Save Profile to reset data!!')
        return

    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)

    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']

    # ✅ Fetch all registered user details from MongoDB
    users = {}
    for record in collection.find():
        users[int(record["user_id"])] = record["name"]  # Store {ID: Name} mapping

    if not users:
        mess.showerror(title='Details Missing', message='No registered users found in the database!')
        cam.release()
        cv2.destroyAllWindows()
        return

    recorded_ids = set()  # ✅ Track IDs to prevent multiple entries
    attendance = []  # ✅ List to store attendance

    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    attendance_file = f"Attendance/Attendance_{date}.csv"

    while True:
        ret, im = cam.read()
        if not ret:
            mess.showerror("Camera Error", "Failed to capture image from camera.")
            break
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])

            if conf < 50 and serial in users:
                ts = time.time()
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

                ID = str(serial)  # Convert ID to string
                name = users[serial]  # Fetch name from MongoDB

                # ✅ Register attendance **only if ID is not already recorded**
                if ID not in recorded_ids:
                    recorded_ids.add(ID)
                    attendance.append([ID, '', name, '', str(date), '', str(timeStamp)])

                    # ✅ Display in Treeview
                    if 'tv' in globals():
                        tv.insert('', 0, text=ID, values=(name, date, timeStamp))

            else:
                ID = 'Unknown'
                name = 'Unknown'

            cv2.putText(im, name, (x, y + h), font, 1, (255, 255, 255), 2)

        cv2.imshow('Taking Attendance', im)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    # ✅ Save unique attendance entries to CSV
    file_exists = os.path.isfile(attendance_file)

    with open(attendance_file, 'r+', newline='') as csvFile1:
        reader = csv.reader(csvFile1)
        existing_entries = set(tuple(row) for row in reader)  # Read existing entries
        
    with open(attendance_file, 'a+', newline='') as csvFile1:
        writer = csv.writer(csvFile1)
        if not file_exists:
            writer.writerow(col_names)
        for entry in attendance:
            if tuple(entry) not in existing_entries:  # Avoid duplicate entries
                writer.writerow(entry)


######################################## USED STUFFS ############################################
    
global key
key = ''

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day,month,year=date.split("-")

mont={'01':'January',
      '02':'February',
      '03':'March',
      '04':'April',
      '05':'May',
      '06':'June',
      '07':'July',
      '08':'August',
      '09':'September',
      '10':'October',
      '11':'November',
      '12':'December'
      }

######################################## GUI FRONT-END ###########################################

window = tk.Tk()
window.geometry("1280x720")
window.resizable(True,False)
window.title("Attendance System")
window.configure(background='#2d420a')

frame1 = tk.Frame(window, bg="#c79cff")
frame1.place(relx=0.11, rely=0.17, relwidth=0.39, relheight=0.80)

frame2 = tk.Frame(window, bg="#c79cff")
frame2.place(relx=0.51, rely=0.17, relwidth=0.38, relheight=0.80)

message3 = tk.Label(window, text="Face Recognition Based Attendance Monitoring System" ,fg="white",bg="#2d420a" ,width=55 ,height=1,font=('comic', 29, ' bold '))
message3.place(x=10, y=10)

frame3 = tk.Frame(window, bg="#c4c6ce")
frame3.place(relx=0.52, rely=0.09, relwidth=0.09, relheight=0.07)

frame4 = tk.Frame(window, bg="#c4c6ce")
frame4.place(relx=0.36, rely=0.09, relwidth=0.16, relheight=0.07)

datef = tk.Label(frame4, text = day+"-"+mont[month]+"-"+year+"  |  ", fg="#ff61e5",bg="#2d420a" ,width=55 ,height=1,font=('comic', 22, ' bold '))
datef.pack(fill='both',expand=1)

clock = tk.Label(frame3,fg="#ff61e5",bg="#2d420a" ,width=55 ,height=1,font=('comic', 22, ' bold '))
clock.pack(fill='both',expand=1)
tick()

head2 = tk.Label(frame2, text="                       For New Registrations                       ", fg="black",bg="#00fcca" ,font=('comic', 17, ' bold ') )
head2.grid(row=0,column=0)

head1 = tk.Label(frame1, text="                       For Already Registered                       ", fg="black",bg="#00fcca" ,font=('comic', 17, ' bold ') )
head1.place(x=0,y=0)

lbl = tk.Label(frame2, text="Enter ID",width=20  ,height=1  ,fg="black"  ,bg="#c79cff" ,font=('comic', 17, ' bold ') )
lbl.place(x=80, y=55)

txt = tk.Entry(frame2,width=32 ,fg="black",font=('comic', 15, ' bold '))
txt.place(x=30, y=88)

lbl2 = tk.Label(frame2, text="Enter Name",width=20  ,fg="black"  ,bg="#c79cff" ,font=('comic', 17, ' bold '))
lbl2.place(x=80, y=140)

txt2 = tk.Entry(frame2,width=32 ,fg="black",font=('comic', 15, ' bold ')  )
txt2.place(x=30, y=173)

message1 = tk.Label(frame2, text="1)Take Images  >>>  2)Save Profile" ,bg="#c79cff" ,fg="black"  ,width=39 ,height=1, activebackground = "#3ffc00" ,font=('comic', 15, ' bold '))
message1.place(x=7, y=230)

message = tk.Label(frame2, text="" ,bg="#c79cff" ,fg="black"  ,width=39,height=1, activebackground = "#3ffc00" ,font=('comic', 16, ' bold '))
message.place(x=7, y=450)

lbl3 = tk.Label(frame1, text="Attendance",width=20  ,fg="black"  ,bg="#c79cff"  ,height=1 ,font=('comic', 17, ' bold '))
lbl3.place(x=100, y=115)

res=0
exists = os.path.isfile("StudentDetails\StudentDetails.csv")
if exists:
    with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
        reader1 = csv.reader(csvFile1)
        for l in reader1:
            res = res + 1
    res = (res // 2) - 1
    csvFile1.close()
else:
    res = 0

total_users = get_registered_users_count()  # Get correct total users
message.configure(text=f'Total Registrations till now: {total_users}')


##################### MENUBAR #################################

menubar = tk.Menu(window,relief='ridge')
filemenu = tk.Menu(menubar,tearoff=0)
filemenu.add_command(label='Change Password', command = change_pass)
filemenu.add_command(label='Contact Us', command = contact)
filemenu.add_command(label='Exit',command = window.destroy)
menubar.add_cascade(label='Help',font=('comic', 29, ' bold '),menu=filemenu)

################## TREEVIEW ATTENDANCE TABLE ####################

tv= ttk.Treeview(frame1,height =13,columns = ('name','date','time'))
tv.column('#0',width=82)
tv.column('name',width=130)
tv.column('date',width=133)
tv.column('time',width=133)
tv.grid(row=2,column=0,padx=(0,0),pady=(150,0),columnspan=4)
tv.heading('#0',text ='ID')
tv.heading('name',text ='NAME')
tv.heading('date',text ='DATE')
tv.heading('time',text ='TIME')

###################### SCROLLBAR ################################

scroll=ttk.Scrollbar(frame1,orient='vertical',command=tv.yview)
scroll.grid(row=2,column=4,padx=(0,100),pady=(150,0),sticky='ns')
tv.configure(yscrollcommand=scroll.set)

###################### BUTTONS ##################################

clearButton = tk.Button(frame2, text="Clear", command=clear  ,fg="black"  ,bg="#ff7221"  ,width=11 ,activebackground = "white" ,font=('comic', 11, ' bold '))
clearButton.place(x=335, y=86)
clearButton2 = tk.Button(frame2, text="Clear", command=clear2  ,fg="black"  ,bg="#ff7221"  ,width=11 , activebackground = "white" ,font=('comic', 11, ' bold '))
clearButton2.place(x=335, y=172)    
takeImg = tk.Button(frame2, text="Take Images", command=TakeImages  ,fg="white"  ,bg="#6d00fc"  ,width=34  ,height=1, activebackground = "white" ,font=('comic', 15, ' bold '))
takeImg.place(x=30, y=300)
trainImg = tk.Button(frame2, text="Save Profile", command=psw ,fg="white"  ,bg="#6d00fc"  ,width=34  ,height=1, activebackground = "white" ,font=('comic', 15, ' bold '))
trainImg.place(x=30, y=380)
trackImg = tk.Button(frame1, text="Take Attendance", command=TrackImages  ,fg="black"  ,bg="#3ffc00"  ,width=35  ,height=1, activebackground = "white" ,font=('comic', 15, ' bold '))
trackImg.place(x=30,y=50)
quitWindow = tk.Button(frame1, text="Quit", command=window.destroy  ,fg="black"  ,bg="#eb4600"  ,width=35 ,height=1, activebackground = "white" ,font=('comic', 15, ' bold '))
quitWindow.place(x=30, y=450)

##################### END ######################################

window.configure(menu=menubar)
window.mainloop()

####################################################################################################

