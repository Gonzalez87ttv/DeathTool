# DeathTool
DeathTool was created to offer livestreamers a better tool than chatbot commands for tracking death counts in live playthrough.  As opposed to traditionnaly used methods of updating a chatbot command or manually changing the count on your overlay, DeathTool doesn'T have a 5 seconds cooldown and can be forgotten in the background while you control it with hotkeys without ever leaving the game. The program can be set up in less than a minute and offers some management options for you to effiently keep track of all your playthroughs at once.  

Of course, the program was conceived with death count in mind, but you can also use it to keep track of crashes in...Oblivionly stable games (see what i did there hehe....)... or the amount of time you have done something on stream.

Here is offered both the source python 3 file, but also an executable that can be used by anyone without the proper python installation.

FOR EXECUTABLE :
----------------------------------------------
1. Download the .exe (https://github.com/Gonzalez87ttv/DeathTool/blob/main/DeathTool%201.0.exe)
2. Run
3. Enjoy

FOR PYTHON FILE :
----------------------------------------------
The program was created in python 3.7.3.  Although it will most likely work in future versions, I can not garanty it without testing it, which i probably won't...
1. Download the one-file code (https://github.com/Gonzalez87ttv/DeathTool/blob/main/DeathTool%201.0.py)
2. Make sure you have all necessary package installed
3. Execute the code in a python shell
4. Enjoy

Needed packages :
----------------------------------------------
1. keyboard 0.13.5 (can be installed via Pip, created by Lucas Boppre Niehues https://github.com/boppreh/keyboard
2. tkinter (python3.7 included)
3. functools (python3.7 included)
4. time (python3.7 included)

GETTING STARTED
----------------------------------------------
Upon starting, press "Add a game" to initialize your first data.  The death count is displayed in the middle of the window and can be controlled with the default hotkey Ctrl+Shift+- to decrease and Ctrl+Shift+= to increase.  The games' data is stored in a file called DeathTool_DB.dt created upon starting the program.  The active deathcount is sent to a file named DeathTool_visual.txt which is also created upon starting the program.  Capture this last file as a text source in your OBS or other streaming software to display on your overlay.

FEATURES
----------------------------------------------
On the main window, the entry allows you to search through your games quickly by limitting the choices in the popup menu to those corresponding to what you typed.  pressing Tab in the entry will autocomplete with the first game that matches.  Pressing Enter will select the game and make it active.  Pressing enter with a non-existent game in your data will offer you to add it, just like the "Add a game" button.

The deathcount displayed in the middle of the screen can be manually typed in, but will only update/save if Enter is pressed after changing it.  It can also be controlled by the arrows.

The "Configuration" button allows you to select a source file (data file containing your game and count, DeathTool_DB.dt by default) and a visual file for capturing in OBS.  Your selection is remembered via the .ini file that will be created with the software, so you can safely store this clutter of file away where you never have to worry about them again!

Pressing the "Finalise" button will freeze your deathcount for the active game and consider the playthrough as over.  It will not show up in the main window's option menu anymore, but the count is still stored and will be available in the managing options.

The "Edit games" button gives you the choices of looking at the games themselves or at the informations stored for a specific game.  The informations are Tag-like string you can associate like the difficulty you were playing, the date you started the playthrough, the type of character etc.  The games options allow you to reset a playthrough (removing the finalise tag at the same time), delete a game entirely, or manually change the count for multiple games at once.


FUTUR FEATURES
----------------------------------------------
Sometimes you are so absorbed that you forget to update the count.  It happens to the best of us.  Although I can not say if and when that will happen, I plan on trying to integrate this tool in another code making your own chatbot.  This way, your moderator would have the power to control the deathcount directly on the overlay the same way you do if you forget!

Got comment/suggestion?  Feel free to visit me during one of my livestreams.  I would love to discuss the tool with users and see what I can upgrade on it!
