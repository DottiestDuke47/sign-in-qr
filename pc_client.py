#Import the required Libraries
from tkinter import *
#Create an instance of Tkinter frame
win= Tk()
#Set the Geometry
win.geometry("750x250")
#Full Screen Window
win.attributes('-fullscreen', True)
win.configure(bg='white')
def quit_win():
   win.destroy()

#Cretae 2 fames and se grid to layout side by side. Fill the entire window
frame1=Frame(win, bg='blue')
frame1.grid(row=0, column=0, sticky='nsew')
frame2=Frame(win, bg='red')
frame2.grid(row=0, column=1, sticky='nsew')
#Set the Grid Weight
win.grid_rowconfigure(0, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)



#Bind esc to quit
win.bind('<Escape>', lambda e: win.destroy())

#Create a Quit Button  
#button=Button(win,text="Quit", font=('Comic Sans', 13, 'bold'), command= quit_win)
#button.pack(pady=20)
win.mainloop()