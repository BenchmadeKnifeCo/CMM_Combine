"""Script for combining inspection records together which are all located in the same folder, which a user selects
These are character files from Zeiss Calypso which are exported to a file system chosen by a user during a run"""
"""Written by Ryan Johnson 2019"""

import pandas as pd
import re
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
import os, time
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create the Program Window
root = Tk()
root.title('Benchmade CMM Manager')
root.geometry('350x175')
root.resizable(width=False, height=False)

# List of Variables used
home = os.path.expanduser('~')
downloads = os.path.join(home, 'Downloads')
check1 = IntVar()
mysep = StringVar()



# Send Error Email when Exceptions
def error_email(error, mymessage):
    you = 'rjohnson@benchmade.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'CMM File Combine Error'
    msg['From'] = 'Benchmade CMM File Combine Program Error'
    msg['To'] = you

    #EMail Body

    text = mymessage
    html = """\
    <html>
      <head></head>
      <body>
        <p>This is the error message being thrown. </p>
        <br>
        {code}
        <br>
        {message}
      </body>
    </html>
    """.format(code=error, message=mymessage)

    body1 = MIMEText(text, 'plain')
    body2 = MIMEText(html, 'html')

    msg.attach(body1)
    msg.attach(body2)

    try:

        server = smtplib.SMTP('exch01.benchmade.local','25')
        server.ehlo()
        server.starttls()
        server.set_debuglevel(False)
        server.sendmail(you, you, msg.as_string())
        server.quit()

    except ConnectionError:
        messagebox.showinfo("Program Terminated", "Error in connecting to email server. Can not send email.")
        sys.exit('Program Terminated')


# Choose the directory prompt
def choose_dir():
    global directory
    directory = filedialog.askdirectory()
    DirText.config(text=directory)
    return directory

# Creates a new dict to stuff all the data from the txt file
def newrow(dataframe):
    global mydict
    mydict = {}
    part=re.sub('\D','',df.partnb[0])
    mydict.update({'planid': df.planid[0], 'part_num': part})

    if check1.get() == 1:

        for index, row in dataframe.iterrows():
            if (row[2].find('.X') == -1) and (row[2].find('.Y') == -1):
                mydict.update({row[2].split(mysep.get(),1)[0]: row[5]})
            else:
                continue

    else:

        for index, row in dataframe.iterrows():
            if row[2].find('.X') == -1 and row[2].find('.Y') == -1:
                mydict.update({row[2]:row[5]})
            else:
                continue

    return mydict


# Reorders the data by part number and saves files to csv in users downloads folder
def reorder(dataframe):

    try:
        cols = list(dataframe)
        cols.insert(0, cols.pop(cols.index('part_num')))
        cols.insert(0, cols.pop(cols.index('planid')))
        new_df = dataframe.loc[:, cols]
        try:
            new_df['part_num'] = new_df.part_num.astype(dtype='int32')
            new_df.sort_values('part_num', inplace=True)
        except ValueError as e:
            messagebox.showinfo('Error', "File Complete, Couldn't Sort, id numbers not integers")
            error_email(e, "Couldn't Sort, id numbers not integers")
            pass
        fileext = downloads + '\\' + 'export_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
        new_df.to_csv(fileext)
        os.startfile(fileext)

    except ValueError as e:
        messagebox.showinfo("Program Terminated", "No text files found containing information, or files in wrong format.")
        error_email(e, "No text files found, or file in wrong format")
        sys.exit('Program Terminated')


# Loop to read all files in selected directory with extension ending in *chr.txt
def readfile():
    global df
    new_df = pd.DataFrame()
    try:
       for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith("chr.txt"):
                df = pd.read_csv(directory + '\\' + filename, sep='\t')
                df.drop(df.tail(1).index, inplace=True)
                newrow(df)
                new_df = new_df.append(mydict, ignore_index=True)

            else:
                continue

       reorder(new_df)

    except NameError:
        messagebox.showinfo("Error", "Please select a directory")
        choose_dir()

    except (RuntimeError, TypeError, UnicodeDecodeError) as e:
        messagebox.showinfo("Program Terminated", "An Error has Occurred, to many files selected.")
        error_email(e, "To many files selected")
        sys.exit('Program Terminated')



#Set size of the input box to 1
def limitsizeday(*args):
    value = mysep.get()
    if len(value) > 1: mysep.set(value[:1])


mysep.trace('w', limitsizeday)

# Close the program window
def close_window():
    root.destroy()

# Fill the program window with needed widgets
DirText = ttk.Label(root, text='')
DirButton = ttk.Button(root, text='Select Directory', command=choose_dir)
RunButton = ttk.Button(root, text='Compile', command=readfile)
ExitButton = ttk.Button(root, text='Exit', command=close_window)
CRText = ttk.Label(root, text='Written by: Ryan Johnson', anchor=S)
CheckLabel = ttk.Label(root, text="Check if attributes prefixed with Numbers")
MyCheckBox = ttk.Checkbutton(root, text='Check if Attributes have prefixes, enter separator.', variable=check1)
MyInputBox = ttk.Entry(root, text='Enter the separator used',width=3, textvariable=mysep)
MyInputLabel = ttk.Label(root, text='Enter Separator Value Used.')
root.iconbitmap(r'C:\Users\ryanj\PycharmProjects\CMManager\favicon.ico')
DirButton.grid(pady=3, column=1, row=0, columnspan=3)
DirText.grid(pady=1, column=1, row=1, columnspan=4)
MyCheckBox.grid(pady=1, column=1, row=2, columnspan=2)
MyInputBox.grid(padx= 5, pady=1, column=0, row=2)
RunButton.grid(pady=1, row=3, column=1, columnspan=3)
ExitButton.grid(column=1, row=4, columnspan=3)
CRText.grid(pady=4, column=1, row=6, rowspan=2, columnspan=3)
root.mainloop()