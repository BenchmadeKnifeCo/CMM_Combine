"""Script for combining inspection records together which are all located in the same folder, which a user selects"""
"""Written by Ryan Johnson """

import pandas as pd
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
import os, time
import sys

"""Create the Program Window"""
root = Tk()
root.title('Benchmade CMM Manager')
root.geometry('350x150')
root.resizable(width=False, height=False)

"""List of Variables used"""
home = os.path.expanduser('~')
downloads = os.path.join(home, 'Downloads')
global check1
check1 = IntVar()

"""Choose the directory prompt"""
def choose_dir():
    global directory
    directory = filedialog.askdirectory()
    DirText.config(text=directory)
    return directory

"""Creates a new dict to stuff all the data from the txt file"""
def newrow(dataframe):
    global mydict
    mydict = {}
    mydict.update({'planid': df.planid[0], 'part_num': df.partnb[0]})

    if check1.get() == 1:
        for index, row in dataframe.iterrows():
            if (row[2].find('.X') == -1) and (row[2].find('.Y') == -1):
                mydict.update({row[2].split("_",1)[0]: row[5]})
            else:
                continue
    else:
        for index, row in dataframe.iterrows():
            if row[2].find('.X') == -1 and row[2].find('.Y') == -1:
                mydict.update({row[2]:row[5]})
            else:
                continue

    return mydict


"""Reorders the data by part number and saves files to csv in users downloads folder"""
def reorder(dataframe):

    try:
        cols = list(dataframe)
        cols.insert(0, cols.pop(cols.index('part_num')))
        cols.insert(0, cols.pop(cols.index('planid')))
        new_df = dataframe.loc[:, cols]
        try:
            new_df['part_num'] = new_df.part_num.astype(dtype='int32')
            new_df.sort_values('part_num', inplace=True)
        except ValueError:
            messagebox.showinfo('Error', "File Complete, Couldn't Sort, id numbers not integers")
            pass
        fileext = downloads + '\\' + 'export_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
        new_df.to_csv(fileext)
        os.startfile(fileext)

    except ValueError:
        messagebox.showinfo("Error", "No text files found containing information, or files in wrong format.")
        sys.exit('Program Terminated')


"""Loop to read all files in user selected directory with extension ending in *chr.txt"""
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

    except NameError:
        messagebox.showinfo("Error", "Please select a directory")
        choose_dir()
        readfile()
        sys.exit()

    except (RuntimeError, TypeError, UnicodeDecodeError):
        messagebox.showinfo("Error", "An Error has Occurred, to many files selected.")
        sys.exit('Program Terminated')

    reorder(new_df)

"""Close the program window"""
def close_window():
    root.destroy()

"""Fill the program window with needed widgets"""
DirText = ttk.Label(root, text='')
DirButton = ttk.Button(root, text='Select Directory', command=choose_dir)
RunButton = ttk.Button(root, text='Compile', command=readfile)
ExitButton = ttk.Button(root, text='Exit', command=close_window)
CRText = ttk.Label(root, text='Written by: Ryan Johnson', anchor=S)
CheckLabel = ttk.Label(root, text="Check if attributes prefixed with Numbers")
MyCheckBox = ttk.Checkbutton(root, text='Check if Attributes are Prefixed with Numbers', variable=check1)
root.iconbitmap(r'C:\Users\ryanj\PycharmProjects\CMManager\favicon.ico')
DirButton.pack(pady=3)
DirText.pack(pady=1)
MyCheckBox.pack(pady=1)
RunButton.pack(pady=1)
ExitButton.pack()
CRText.pack(side=BOTTOM)
root.mainloop()