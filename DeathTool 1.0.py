# -*- coding: utf-8 -*-
"""
Basic counter able to track multiple games, and be controled with hotkey 
while the program is minimized.  This program constantly update a text file 
with the current death count such that said text file may be picked up by a 
streaming software like OBS for use as a livestream widget displaying the 
amount of death in a playthrough.

------------
LICENCE
------------
  
MIT License

Copyright (c) 2021 Gonzalez87
Github : Gonzalez87ttv
gonzalez87.ttv@gmail.com
https://www.twitch.tv/gonzalez87

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from tkinter import Tk, Button, Entry, OptionMenu, Frame, _setit, Toplevel, Label
from tkinter import IntVar, StringVar
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, askokcancel, showinfo
from os.path import isfile, dirname
from functools import partial
import keyboard as kb
from time import sleep

### THIS is a fix for a bug in the keyboard.read_hotkey() fct.  I use this instead of the original
###For the original, check Keyboard.read_hotkey
###Original keyboard package by Copyright (c) 2016 Lucas Boppre Niehues under the same MIT license
def homemade_read_hotkey(suppress=True):
    """
    Similar to `read_key()`, but blocks until the user presses and releases a
    hotkey (or single key), then returns a string representing the hotkey
    pressed.

    Example:

        read_hotkey()
        # "ctrl+shift+p"
    """
    kb._pressed_events = {} # <----THIS is the added line.  [event.name] is somehow persistant through multiple itteration of read_hotkey().  Got to erase it.
    queue = kb._queue.Queue()
    
    fn = lambda e: queue.put(e) or e.event_type == kb.KEY_DOWN
    hooked = kb.hook(fn, suppress=suppress)
    while True:
        event = queue.get()
        if event.event_type == kb.KEY_UP:
            kb.unhook(hooked)
            with kb._pressed_events_lock:
                names = [e.name for e in kb._pressed_events.values()] + [event.name]
            kb.release(names)
            return kb.get_hotkey_name(names)
        

class DeathTool():
    """
    Tool that keeps track of your deaths in all of your games.  
    
    Ctrl+Shift+= will increase the count while Ctrl+Shift+- will decrease, 
    even when the interface is minimized.  The selected game's death is 
    constantly written to a text file that can be picked up by OBS for a 
    custom widget.

    """
    def __del__(self) :
        """
        Executes when the class is garbaged (in theory) to save progress, 
        but is also manually called after the window is closed.  
        
        A.K.A Autosave #gonzalez is a genius
        """
        self.games[self.currgame] = self.Death.get()
        kb.remove_hotkey(self.dhk)
        kb.remove_hotkey(self.ahk)
        with open(self.source, 'w') as f:
            for name in self.gamelist :
                line = '%s\t%s' %(name, self.games[name])
                for i in self.infos[name]:
                    line = line + '\t' + i    
                line = line + '\n'
                f.write(line)
                
            for name in self.final_gamelist :
                line = '%s\t%s' %(name, self.games[name])
                for i in self.infos[name]:
                    line = line + '\t' + i
                line = line + '\n'
                f.write(line)


    def __init__(self, root):
        """
        Creates all the widgets
        """
        def death_update(*arg):
            """
            Executes when the death count changes
            
            Format the death count for display and update entry
            """
            #update the display variable
            val = str(self.Death.get())
            if len(val)==1:
                val = '00'+val
            elif len(val)==2:
                val = '0'+val
            elif len(val) >3:
                self.DeathE.config(width=len(val))
            self.DeathVar.set(val)

            #update the display file text            
            with open(self.dest,'w') as f :
                f.write(self.DeathVar.get())
        
        #this default bind makes "tab" key swap to next widget.  
        #We want to use a tab keybind in entry so need to deactivate this crap.
        self.root = root
        self.root.unbind_all("<<NextWindow>>") 
        
        self.F1 = Frame(self.root)
        self.F2 = Frame(self.root)
        self.F3 = Frame(self.root)
        
        self.F1.grid(column=0, row=0)
        self.F2.grid(column=1, row=0)
        self.F3.grid(column=2, row=0)
        
        if isfile('./DeathTool.ini') is False:
            with open('./DeathTool.ini','w') as f :
                f.write('Source = ./DeathTool_DB.dt\nDestination = ./DeathTool_visual.txt\n')
                f.write('Add keybind = ctrl+shift+-\nDecrease keybind = ctrl+shift+=')
#                f.write('\nTMI token = None\nClient ID = None\nBot name (account name) = None\nCommand prefix = None\nChannel name = None')
            self.source = './DeathTool_DB.dt'
            self.dest = './DeathTool_visual.txt'
            self.hotkeys = ('ctrl+shift+=', 'ctrl+shift+-')
            self.dhk = kb.add_hotkey('ctrl+shift+-', self.decrease)
            self.ahk = kb.add_hotkey('ctrl+shift+=', self.add)

#            self.token = None  #Maybe keep those for an Invoker-like code, calling both deathtool and other programs?
#            self.client = None
#            self.nickname = None
#            self.prefix = None
#            self.channel = None
        else :
            with open('./DeathTool.ini','r') as f :
                line = f.readline().strip()
                self.source = line[9:]
                line = f.readline().strip()
                self.dest = line[14:]
                line = f.readline().strip()
                low_hotkey = line[14:]
                self.dhk = kb.add_hotkey(line[14:], self.decrease)
                line = f.readline().strip()
                up_hotkey = line[19:]
                self.ahk = kb.add_hotkey(line[19:], self.add)
                self.hotkeys = (up_hotkey, low_hotkey)
                
        #Get info from source
        if isfile(self.source) is False :
            with open(self.source,'w') as f :
                f.write('Unknown game\t0\n')
        self.games = {}
        self.final_gamelist = []
        self.total_gamelist = []
        self.gamelist = []
        self.infos = {}
        with open(self.source,'r') as f :
            line = f.readline()
            while line != '' :
                line = line.strip().split('\t')
                self.games[line[0]] = int(line[1])
                infos=[]
                for info in line[2:]:
                    infos.append(info)
                self.infos[line[0]] = infos
                if 'FINAL' in infos :
                    self.final_gamelist.append(line[0])
                else :
                    self.gamelist.append(line[0])
                self.total_gamelist.append(line[0])
                line = f.readline()
        self.currgame = self.gamelist[0]
        
        #set the counter and game from the source info
        self.Death = IntVar(value=self.games[self.currgame])
        self.Death.trace('w',death_update)
        self.DeathVar = StringVar(value='000')
        self.NameOMVar = StringVar(value=self.currgame)
        self.NameEVar = StringVar(value='')
        
        #Set the dest file
        if isfile(self.dest) is False :
            with open(self.dest,'w') as f :
                f.write('000')
        
        death_update()
        
        #%%Frame1 Buttons
        def add_game(*arg):
            """
            Adds a game with 000 death with the name taken from the entry.
            """
            name = self.NameEVar.get()
            if name == '' :
                showerror(title='Oups!', message='You forgot to enter a game name to add in the entry!')
            elif name in self.total_gamelist :
                if name in self.final_gamelist :
                    showerror(title='Oups!', message='You already have that game name in the completed games!')
                else:
                    showerror(title='Oups!', message='You already have that game name in the database!')
            else :
                with open(self.dest,'a') as f:
                    f.write('%s\t0\n' %(name))
                self.total_gamelist.append(name)
                self.gamelist.append(name)
                self.games[name] = 0
                self.infos[name] = []
                
                self.NameOM['menu'].add_command(label=name,command=_setit(self.NameOMVar, name))
                self.NameOMVar.set(name)
                    
                    
        def menu_change(*arg):
            """
            Executes when the OM selection changes.
            
            Changes the game and update all
            """
            #update DB file
            self.games[self.currgame] = self.Death.get()
            with open(self.source, 'w') as f:
                for name in self.gamelist :
                    line = '%s\t%s' %(name, self.games[name])
                    for i in self.infos[name]:
                        line = line + '\t' + i    
                    line = line + '\n'
                    f.write(line)
                    
                for name in self.final_gamelist :
                    line = '%s\t%s' %(name, self.games[name])
                    for i in self.infos[name]:
                        line = line + '\t' + i
                    line = line + '\n'
                    f.write(line)
            
            #change game
            self.currgame = self.NameOMVar.get()
            self.Death.set(self.games[self.currgame])
            

        def name_edit(*arg):
            """
            Executes when the name entry's text changes.
            
            Updates the OM to only show games that starts with what was typed
            """            

            text = self.NameEVar.get().lower()
            choices = []
            if text != '' :
                for i in self.gamelist :
                    if i.lower().startswith(text) is True :
                        choices.append(i)
                if len(choices) < 1 :
                    choices = self.gamelist
                    
            else :
                choices = self.gamelist
                
            self.NameOM['menu'].delete(0, 'end')
            for choice in choices :
                self.NameOM['menu'].add_command(label=choice, command=_setit(self.NameOMVar, choice))
            
        
        def name_entry_enter(*arg):
            """
            Executes when enter is pressed with the name entry in focus.
            
            Resets the choices of the OM and select the first match for what
            was typed in the entry.
            """
            text = self.NameEVar.get()
            #if in the games, select it
            if text.lower() in [i.lower() for i in self.gamelist] :
                self.NameEVar.set('')
                self.NameOMVar.set(text)
            
            elif text.lower() in [i.lower() for i in self.final_gamelist] :
                idx = [i.lower() for i in self.final_gamelist].index(text.lower())
                game = self.final_gamelist[idx]
                showinfo(title='Result', message='This game is in the finalised list,\n'+
                         "you can't edit it anymore.\n\nYou're final death count was %s" %(self.games[game]))
                
            #if not in the games, offer to create
            else :
                answer = askokcancel('Create?', '%s is not an existing' %(text)+
                                     ' game, would you like to create it?')
                if answer is True :
                    self.NameEVar.set(text)
                    add_game()
            
        def name_entry_tab(*arg):
            """
            Executes when tab is pressed with the name entry in focus.
            
            Autocompletes with the first match in the game list.
            """
            text = self.NameEVar.get().lower()
            if text != '' :
                select = None
                for game in self.gamelist :
                    if game.lower().startswith(text) is True :
                        select = game
                        break
                if select is not None :
                    self.NameEVar.set(select)


        def name_entry_unfocus(*arg):
            """
            Executes when you stop writing in the entry.
            
            Resets the choices of the OM
            """
            self.NameEVar.set('')
            
        
        self.NameEVar.trace('w',name_edit)
        self.NameOMVar.trace('w',menu_change)
        
        self.AddGameB = Button(self.F1, width=18, text='Add a game', font=('Verdana', 12), command=add_game)
        self.NameE = Entry(self.F1, width=18, textvar=self.NameEVar, font=('Verdana',12))
        self.NameE.bind("<FocusOut>", name_entry_unfocus)
        self.NameE.bind('<Return>', name_entry_enter)
        self.NameE.bind('<Tab>', name_entry_tab)
        self.NameOM = OptionMenu(self.F1, self.NameOMVar, *self.gamelist)
        self.NameOM.config(width=15, font=('Verdana', 12))
        
        self.AddGameB.grid(column=0, row=0)
        self.NameE.grid(column=0, row=1)
        self.NameOM.grid(column=0, row=2)  
        
        #%%Frame2 Buttons
        def death_edit(*arg):
            """
            Executes when enter is pressed with focus on the death count entry.
            
            Updates the actual Death count to the value entered in the entry.
            """
            self.Death.set(int(self.DeathVar.get()))
                
        self.AddB = Button(self.F2, text='/\\', font=('Verdana', 12), command=self.add)
        self.DeathE = Entry(self.F2, justify='center', width=3, 
                            textvar=self.DeathVar, font=('Verdana',12))
        self.DeathE.bind('<Return>', death_edit)
        self.DecB = Button(self.F2, text='\/', font=('Verdana', 12), command=self.decrease)
        
        self.AddB.grid(column=0, row=0)
        self.DeathE.grid(column=0, row=1)
        self.DecB.grid(column=0, row=2)        
        
        
        #%%Frame3 Buttons
        
        def config(*arg):
            """
            Menu to change the source or destination file, or the keybind for 
            increasing/decreasing the count.
            """
            def source(*arg):
                """
                Changes the source .dt file (i.e. the file where all the games,
                death count, and infos are stored.)
                """
                source = askopenfilename(initialdir=dirname(self.source),
                                        title='Select new source file',
                                        filetypes=(("DeathTool files","*.dt"),("DeathTool files","*.dt")))
                if source != '' :
                    self.source = source
                    self.games = {}
                    self.final_gamelist = []
                    self.total_gamelist = []
                    self.gamelist = []
                    self.infos = {}
                    
                    with open(self.source,'r') as f :
                        line = f.readline()
                        while line != '' :
                            line = line.strip().split('\t')
                            self.games[line[0]] = int(line[1])
                            infos=[]
                            for info in line[2:]:
                                infos.append(info)
                            self.infos[line[0]] = infos
                            if 'FINAL' in infos :
                                self.final_gamelist.append(line[0])
                            else :
                                self.gamelist.append(line[0])
                            self.total_gamelist.append(line[0])
                            line = f.readline()
                            
                    self.currgame = self.gamelist[0]
                    
                    #set the counter and game from the source info
                    self.Death.set(self.games[self.currgame])
                    self.NameOMVar.set(self.currgame)
                    self.NameEVar.set('')
                    answer = askokcancel('Default?','Would you like to make this '+
                                         'file the default source file?')
                    if answer is True :
                        with open('./DeathTool.ini','r') as f :
                            text = f.readlines()
                            
                        for idx, line in enumerate(text) :
                            if line.startswith('Source') :
                                text[idx] = 'Source = %s\n' %(self.source)
                                break
                        with open('./DeathTool.ini','w') as f :
                            for lines in text :
                                f.write(lines)
                ConfigW.destroy()
                        
                
            def dest(*arg):
                """
                Changes the destination text file (i.e. the file where the 
                count is written and can be captured by OBS)
                """
                dest = askopenfilename(initialdir=dirname(self.dest),
                                            title='Select destination txt file',
                                            filetypes=(("Text files","*.txt"), ("Text files","*.txt")))
                if dest != '':                        
                    self.dest = dest
                    with open(self.dest,'w') as f :
                        f.write(self.DeathVar.get())
                    
                    answer = askokcancel('Default?','Would you like to make this '+
                                         'file the default destination file?') 
                    if answer is True :
                        with open('./DeathTool.ini','r') as f :
                            text = f.readlines()
                        for idx, line in enumerate(text) :
                            if line.startswith('Destination') :
                                text[idx] = 'Destination = %s\n' %(self.dest)
                                break

                        with open('./DeathTool.ini','w') as f :
                            for lines in text :
                                f.write(lines)
                ConfigW.destroy()

                
            def hotkey_change(*arg):
                """
                Menu to change the keybind to increase/decrease the count while 
                in game
                """
                def save_hk(*arg):
                    """
                    Checks if the selected keybind is valid/ appropriatly typed
                    for the keyboard module.  If so, save the new binding
                    """
                    
                    try :
                        kb.parse_hotkey(AddHkVar.get())
                        kb.parse_hotkey(DecreaseHkVar.get())
                        stop = False
                    except Exception as err:
                        message="If you don't know how to the key is called in this software,\ntry the Record button!"
                        showerror(title='Uh Oh!', message=err.args[0]+'\n'+message)
                        stop = True
                    
                    if stop is False :
                        kb.remove_hotkey(self.dhk)
                        kb.remove_hotkey(self.ahk)
                        
                        self.hotkeys = (AddHkVar.get(), DecreaseHkVar.get())
                        self.dhk = kb.add_hotkey(DecreaseHkVar.get(), self.decrease)
                        self.ahk = kb.add_hotkey(AddHkVar.get(), self.add)
                        ConfigW.destroy()
                    
                
                def record(up,*arg):
                    """
                    Records keypresses until a key is released and write it to 
                    the Entry.
                    
                    DOES NOT SAVE the keybind until save is pressed
                    
                    If up is True, affect the increase keybind, otherwise 
                    affect the decrease keybind
                    """
                    HotkeySaveB.config(state='disabled')
                    if up is True :
                        RecordAddB.config(relief='sunken', fg='red')
                    else :
                        RecordDecB.config(relief='sunken', fg='red')
                    
                    sleep(0.3) #prevent the pressing of key as it starts to be counted (like enter on a command line)
                    new = homemade_read_hotkey()
                    
                    if up is True :
                        AddHkVar.set(new)
                        RecordAddB.config(relief='raised', fg='black')
                    else :
                        DecreaseHkVar.set(new)
                        RecordDecB.config(relief='raised', fg='black')    
                    HotkeySaveB.config(state='normal')
                
                SourceB.destroy()
                DestB.destroy()
                HotkeyB.destroy()
                ConfigBackB.destroy()
                
                AddHkVar = StringVar(value=self.hotkeys[0])
                DecreaseHkVar = StringVar(value=self.hotkeys[1])
                
                XtraF = Frame(ConfigW)
                DecreaseE = Entry(ConfigW, width=25, textvar=DecreaseHkVar, font=('Verdana',12))
                AddE = Entry(ConfigW, width=25, textvar=AddHkVar, font=('Verdana',12))
                DecreaseL = Label(ConfigW, text='Decrease')
                AddL = Label(ConfigW, text='Increase')
                HotkeySaveB = Button(XtraF, text='Save', font=('Verdana', 12), command=save_hk)
                HotkeyCancelB = Button(XtraF, text='Cancel', font=('Verdana', 12), command=ConfigW.destroy)
                RecordDecB = Button(ConfigW, text='Record', command=partial(record, False))
                RecordAddB = Button(ConfigW, text='Record', command=partial(record, True))
                
                DecreaseE.grid(column=0, row=1)
                AddE.grid(column=0, row=0)
                DecreaseL.grid(column=2, row=1)
                AddL.grid(column=2, row=0)
                XtraF.grid(column=0, columnspan=3, row=2)
                HotkeySaveB.grid(column=0, row=0)
                HotkeyCancelB.grid(column=1, row=0)
                RecordDecB.grid(column=1, row=1)
                RecordAddB.grid(column=1, row=0)
                
            
            ConfigW = Toplevel(self.root)
            ConfigW.title('DeathTool configs')
            ConfigW.transient(self.root)
            ConfigW.grab_set()
            
            SourceB = Button(ConfigW, width=15, text='Source file', font=('Verdana', 12), command=source)
            DestB = Button(ConfigW, width=15, text='Visual file', font=('Verdana', 12), command=dest)
            HotkeyB = Button(ConfigW, width=15, text='Keybinds', font=('Verdana', 12), command=hotkey_change)
            ConfigBackB = Button(ConfigW, width=15, text='Back', font=('Verdana', 12), command=ConfigW.destroy)
            
            SourceB.grid(column=0, row=0)
            DestB.grid(column=0, row=1)
            HotkeyB.grid(column=0, row=2)
            ConfigBackB.grid(column=0, row=3)
            

        def finalise_game(*arg):
            """
            Sends the game to the completed list.  Completed games are not 
            available/modifiable in the drop down menu, but are accessible in 
            the "edit games" menu to consult final score.
            """
            self.final_gamelist.append(self.currgame)
            self.gamelist.remove(self.currgame)
            self.infos[self.currgame].append('FINAL')
                
            self.NameOM['menu'].delete(0, 'end')
            for game in self.gamelist :
                self.NameOM['menu'].add_command(label=game, command=_setit(self.NameOMVar, game))
                self.NameOMVar.set(self.gamelist[0])
        
        
        def edit_games():
            """
            Offers options to manage/see the infos of a game or to modify games 
            themselves (delete/reset/add)
            """
            
            def info():
                """
                Look/delete/add tags to the game and see the deathcount (even completed games)
                """
                def add_info():
                    to_add = AddInfoVar.get()
                    game = GameVar.get()
                    
                    with open(self.source, 'r') as f :
                        data = f.readlines()
                    with open(self.source, 'w') as f :
                        for line in data :
                            if line.startswith(game) is False :
                                f.write(line)
                            else :
                                line = line.strip()
                                line = line + '\t%s\n' %to_add
                                f.write(line)
                    
                    self.infos[game].append(to_add)
                    
                    leny = len(self.infos[game])//10
                    if len(self.infos[game])%10 != 0 :
                        leny +=1
                    if leny != TotPageVar.get() :
                        page = True
                    else : page = False
                    game_change(page)
                
                def del_butt(idx):
                    """
                    Removes a specific information from the list
                    """
                    info = self.infos[GameVar.get()]
                    
                    bonus = 10*(PageVar.get()-1)
                    x = info.pop(bonus+idx)

                    leny = len(info)//10
                    if len(info)%10 != 0 :
                        leny +=1
                    if leny != TotPageVar.get() :
                        page = True
                    else : page = False

                    game_change(page)
                    
                    with open(self.source, 'r') as f :
                        data = f.readlines()
                    with open(self.source, 'w') as f :
                        for line in data :
                            if line.startswith(GameVar.get()) is False :
                                f.write(line)
                            else :
                                line = line.strip().split('\t')
                                line.remove(x)
                                f.write(line[0])
                                line.pop(0)
                                for i in line :
                                    f.write('\t')
                                    f.write(i)
                                f.write('\n')

                def change_page(UD):
                    """
                    If more than 10 infos, swap between sets of 10
                    """
                    #update page
                    page = PageVar.get()-1
                    tot = TotPageVar.get()-1
                    if UD == 'up':
                        if page == tot :
                            page = 0
                        else :
                            page += 1
                    else :
                        if page == 0 :
                            page = tot
                        else :
                            page -= 1
                    PageVar.set(page+1)
                    
                    game_change(False)
                    
                
                def game_change(page, *arg):
                    """
                    Is called when the game selection changes in the info menu
                    """
                    info = self.infos[GameVar.get()]
                    CountVar.set(self.games[GameVar.get()])
                    if len(info) > 10 :
                        if page is True :
                            leny = len(info)//10
                            if len(info)%10 != 0 :
                                leny +=1
                            TotPageVar.set(leny)
                            TotPage.config(text='/%s' %(leny))
                            PageVar.set(1)
                          
                        PageF.grid(column=1, columnspan=2, row=11)
                    else : PageF.grid_remove()

                        
                    bonus = (PageVar.get()-1)*10
                    index = []
                    for i in range(10):
                        try :
                            Labels[i].config(text='-->' + info[i+bonus])
                            index.append(bonus+i)
                            DelB[i].grid(column=2, sticky='e', row=i)
                        except IndexError:
                            Labels[i].config(text = '')
                            DelB[i].grid_remove()

                InfosB.destroy()
                ManageB.destroy()
                BackB.destroy()
                
                GameVar = StringVar(value=self.total_gamelist[0])
                GameOM = OptionMenu(ConfigW, GameVar, *self.total_gamelist)
                GameOM.config(font=('Arial Black', 12), width=20)
                DeathL = Label(ConfigW, text='Death count :', 
                               height=1, font=('Arial Black', 12))
                CountVar = StringVar(value=self.games[GameVar.get()])
                CountL = Label(ConfigW, font=('Arial Black', 20), textvar=CountVar)
                DoneB = Button(ConfigW, text = 'Done', width=15, 
                               font=('Verdana', 12), command=ConfigW.destroy)
                AddInfoVar = StringVar(value='')
                AddInfoE = Entry(ConfigW, textvar=AddInfoVar)
                AddInfoB = Button(ConfigW, text='Add', command=add_info)
                XtraF = Frame(ConfigW)
                
                Labels = []
                DelB = []   
                
                for i in range(10) :
                    Labels.append(Label(XtraF, text='', width=30, anchor='w'))
                    DelB.append(Button(XtraF, text='-',font=('Arial Black',12), 
                                       command=partial(del_butt,i)))
                    
                    Labels[i].grid(column=1, sticky='w', row=i)
                    
                PageF = Frame(XtraF)
                PageVar = IntVar(value=1)
                TotPageVar = IntVar(value=1)
                LastB = Button(PageF, text='<', command=partial(change_page, 'down'))
                CurrPage = Label(PageF, textvar=PageVar) 
                TotPage = Label(PageF, text='/%s' %TotPageVar.get())
                NextB = Button(PageF, text='>', command=partial(change_page, 'up'))
                
                #will not appear until PageF is gridded in game_change
                LastB.grid(column=0, row=0)
                CurrPage.grid(column=1, row=0)
                TotPage.grid(column=2, row=0)
                NextB.grid(column=3, row=0)
                
                GameVar.trace('w', partial(game_change, True))
                
                GameOM.grid(column=0, row=0, )
                DeathL.grid(column=0, row=1, sticky='s')
                CountL.grid(column=0, row=2, sticky='n')
                DoneB.grid(column=0, row=3)
                
                XtraF.grid(column=1, row=0, rowspan=3, columnspan=2)
                
                AddInfoE.grid(column=1, row=3, sticky='e')
                AddInfoB.grid(column=2, row=3, sticky='w')
                
            
            def manage():
                """
                Allows to change the count, delete, or reset the games (finalized included)
                """
                def entry_change(idx, *arg) :
                    """
                    Triggers when enter is pressed in an entry for the counts
                    """
                    self.games[game_var[idx].get()] = count_var[idx].get()
                    if self.currgame == game_var[idx].get() :
                        self.Death.set(count_var[idx].get())
                    
                                    
                def reset(idx, *arg):
                    """
                    Resets a game count to 0 and un-finalize it if it was finalized
                    """
                    self.games[game_var[idx].get()] = 0
                    if 'FINAL' in self.infos[game_var[idx].get()] :
                        self.infos[game_var[idx].get()].remove('FINAL')
                        count_entry[idx].config(state='normal')
                        count_var[idx].set(0)
                        
                        self.gamelist.append(game_var[idx].get())
                        self.final_gamelist.remove(game_var[idx].get())
                        self.NameEVar.set('')
                        if self.currgame == game_var[idx].get() :
                            self.Death.set(0)
                    
                def del_idx(idx, *arg) :
                    """
                    Removes a game from the data
                    """
                    game = game_var[idx].get()
                    if 'FINAL' in self.infos[game] :
                        self.final_gamelist.remove(game)
                    else :
                        self.gamelist.remove(game)
                        
                    self.games.pop(game)
                    self.total_gamelist.remove(game)
                    self.infos.pop(game)
                    if self.currgame == game :
                        self.currgame
                        self.NameOMVar.set(self.gamelist[0])
                    self.NameEVar.set('')
                        
                    with open(self.source, 'r') as f :
                        text = f.readlines()
                        
                    with open(self.source, 'w') as f :
                        for lines in text :
                            if lines.startswith(game) is True :
                                pass
                            else :
                                f.write(lines)
                    
                    game_change_page('lawl','page')
                    
                
                def game_change_page(UD, *arg) :
                    """
                    updates games shown, page, etc
                    """
                    page = PageVar.get()-1
                    tot = TotPageVar.get()-1
                    if UD == 'up':
                        if page == tot :
                            page = 0
                        else :
                            page += 1
                    elif UD == 'down' :
                        if page == 0 :
                            page = tot
                        else :
                            page -= 1
                    else :
                        pass
                    PageVar.set(page+1)
                    

                    if len(self.total_gamelist) > 10 :
                        if 'page' in arg :
                            leny = len(self.total_gamelist)//10
                            if len(self.total_gamelist)%10 != 0 :
                                leny +=1
                            TotPageVar.set(leny)
                            TotPage.config(text='/%s' %(leny))
                            PageVar.set(1)
                          
                        PageF.grid(column=1, row=0)
                    else : PageF.grid_remove()

                    bonus = (PageVar.get()-1)*10
                    index = []
                    for i in range(10):
                        try :
                            game_var[i].set(self.total_gamelist[i+bonus])
                            count_var[i].set(self.games[game_var[i].get()])
                            index.append(bonus+i)
                            del_button[i].grid(column=3, row=i)
                            reset_button[i].grid(column=2, row=i)
                            count_entry[i].grid(column=1, row=i)
                            if 'FINAL' in self.infos[game_var[i].get()]:
                                count_entry[i].config(state='disabled')
                        except IndexError:
                            game_var[i].set('')
                            del_button[i].grid_remove()
                            count_entry[i].grid_remove()
                            count_entry[i].config(state='normal')
                            reset_button[i].grid_remove()
                            del_button[i].grid_remove()

                InfosB.destroy()
                ManageB.destroy()
                BackB.destroy()
                
                game_var = []
                game_label = []
                count_var = []
                count_entry = []
                reset_button = []
                del_button = []
                for i in range(10):
                    game_var.append(StringVar(value=''))
                    game_label.append(Label(ConfigW, textvar=game_var[i], height=2, width=25, anchor='w'))
                    count_var.append(IntVar(value=0))
                    count_entry.append(Entry(ConfigW, width=4, textvar=count_var[i]))
                    count_entry[i].bind('<Return>', partial(entry_change, i))
                    reset_button.append(Button(ConfigW, text='Reset', command=partial(reset, i)))
                    del_button.append(Button(ConfigW, text='-', font=('Arial Black',12),command=partial(del_idx, i)))
                    
                    game_label[i].grid(column=0, row=i)                
                
                BotF = Frame(ConfigW)
                DoneB = Button(BotF, text='Done',command=ConfigW.destroy)
                DoneB.grid(column=0, row=0)
                
                #all invis until PageF is grided
                PageF = Frame(BotF)
                BackB2 = Button(PageF, text='<', command=partial(game_change_page,'down'))
                PageVar = IntVar(value=1)
                TotPageVar = IntVar(value=1)
                CurrPage = Label(PageF, textvar=PageVar)
                TotPage = Label(PageF, text='/%s' %TotPageVar.get())
                NextB = Button(PageF, text='>', command=partial(game_change_page,'up'))
                BackB2.grid(column=0, row=0)
                CurrPage.grid(column=1, row=0)
                TotPage.grid(column=2, row=0)
                NextB.grid(column=3, row=0)
                
                game_change_page('lol', 'page') #trigger 1st update without page change
                
                BotF.grid(column=0, row=11, columnspan=4)
                
                           
            ConfigW = Toplevel(self.root)
            ConfigW.title('DeathTool game management')
            ConfigW.transient(self.root)
            ConfigW.grab_set()
            
            
            InfosB = Button(ConfigW, text='Infos', width=15, font=('Verdana', 12), command=info)
            BackB = Button(ConfigW, text='Back', width=15, font=('Verdana', 12), command=ConfigW.destroy)
            ManageB = Button(ConfigW, text = 'Manage games', width=15, font=('Verdana', 12), command=manage)
            
            InfosB.grid(column=0,row=0)
            ManageB.grid(column=0, row=1)
            BackB.grid(column=0, row=2)
            
            
        

        
        
        
        ConfigB = Button(self.F3, text='Configuration', font=('Verdana', 12), width=15, command=config)
        FinaliseB = Button(self.F3, text='Finalise', font=('Verdana', 12), width=15, command=finalise_game)
        EditB = Button(self.F3, text='Edit games', font=('Verdana', 12), width=15, command=edit_games)
        
        ConfigB.grid(column=0, row=0)
        FinaliseB.grid(column=0, row=1)
        EditB.grid(column=0, row=2)
        
    def add(self,*arg):
        """
        Adds 1 death to the currently selected count.
        """
        sleep(0.1)
        if kb.is_pressed(self.hotkeys[0]) is False :
            self.Death.set(self.Death.get()+1)
    
    def decrease(self, *arg):
        """
        Removes 1 death to the currently selected count.
        """
        val = self.Death.get()
        if val == 0:
            pass
        else :
            sleep(0.1)
            if kb.is_pressed(self.hotkeys[1]) is False :
                self.Death.set(self.Death.get()-1)
    


def main():
    

    root = Tk()
    root.title("DeathTool") #Change the window title    
    X = DeathTool(root)
    root.mainloop()
    X.__del__()

if __name__=="__main__":
    main()