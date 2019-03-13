import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os, time


root = Tk()
root.title('Benchmade CMM Manager')
root.geometry('400x350+50+50')

home = os.path.expanduser('~')
downloads = os.path.join(home, 'Downloads')


def choose_dir():
    global directory
    directory = filedialog.askdirectory()
    DirText.config(text=directory)
    return directory

def newrow(dataframe):
    global mydict
    mydict = {}
    mydict.update({'planid': df.planid[0], 'part_num': df.partnb[0]})
    for index, row in dataframe.iterrows():
        mydict.update({row[2]: row[5]})
    return mydict

def reorder(dataframe):
    cols = list(dataframe)
    cols.insert(0, cols.pop(cols.index('part_num')))
    cols.insert(0, cols.pop(cols.index('planid')))
    new_df = dataframe.loc[:, cols]
    new_df['part_num'] = new_df.part_num.astype(dtype='int32')
    new_df.sort_values('part_num', inplace=True)
    fileext = downloads + '\\' + 'export_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
    new_df.to_csv(fileext)
    os.startfile(fileext)


def createfile():
    global df
    global new_df
    new_df = pd.DataFrame()
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


def close_window():
    root.destroy()



DirText = ttk.Label(root, text='')
DirButton = ttk.Button(root, text = 'Select Directory', command = choose_dir)
RunButton = ttk.Button(root, text = 'Compile', command = createfile)
ExitButton = ttk.Button(root, text = 'Exit', command = close_window)
DirButton.pack()
DirText.pack()
RunButton.pack()
ExitButton.pack()
root.mainloop()


