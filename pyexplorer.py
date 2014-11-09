#!/usr/bin/env python
"""Pyexplorer : A Terminal application to browse local directories
and ftp directories with FTP downloading and uploading Support."""

import curses
import os
import time
import threading
import ftputil #A high-level ftplib interface.
import ftplib #For use with exception handling.
from string import center
from sys import argv
import keybinds #Self developed module for managing key bindings.
import cmd_args #Self developed module for managing command line arguments.

def set_defaults():
    """Sets default values to command line argument variables"""

    global parent_navigation, show_hidden, origin, buff, use, fhost, fuser, fpass

    parent_navigation = True

    show_hidden = False

    origin = '.'

    buff = 'page'

    use = 'local'

    fhost = 'localhost'

    fuser = 'anonymous'

    fpass = ''

set_defaults() #Setting up default values to command line argument variables.

#Setting up command-line arguments
arguments = cmd_args.getargs(argv) #Getting command-line arguments dictionary. This module function also manages with errors.

if len(arguments) > 0:

    globals().update(arguments) #Variables declaration in global scope eg:- parent_navigation, show_hidden etc.

#--------------------------------------

class FTPHost(ftputil.FTPHost):

    def get_session_copy(self):
        """First copy the instance and then reterive ftplib's FTP object from that copied session and changes current directory to current directory of original(previous instance). And finally returns that curdir changed, copied FTPHost's ftplib's FTP instance.
        """
        FTPHost_copy_session = self._copy()._session

        FTPHost_copy_session.cwd(self.getcwd())

        return FTPHost_copy_session #Returns another(instance copy) ftplib's FTP object from ftputil's FTPHost object

if use=='ftp':

    try:
        ftp = FTPHost(fhost, fuser, fpass) #Creates an instance of ftputil's FTPHost.

    except ftputil.error.FTPOSError: #If ftp address could not be found.

        print "\n 'ftp://"+str(fhost)+"'", "could not be resolved."
        print "\n Please check your 'internet connection' and make sure the host is up and running."

        print "\n Exiting...\n"

        exit()

    except ftputil.error.PermanentError: #If username or password if invalid.

        print "\n Username or Password Invalid.\n"

        print "\n Exiting...\n"
        exit()

    except: #If their is an unknown error.

        print "\n Unknown Error"

        print "\n Exiting...\n"
        exit()

    ftp_os = ftp

elif use=='local': #If 'local' instance is demanded then store 'os' into ftp_os due to which local system is manipulated such as os.path.isfile checks for file in local system while ftputil.FTPHost.isfile checks for file in remote system(ftp)

    ftp_os = os

#--------------------------------------

#Initializes curses screen.
screen = curses.initscr()

screen.keypad(1) #Enable use of curses.KEY_UP, curses.KEY_DOWN etc. if it is enabled i.e. screen.keypad() is passed a value 1 instead of 0.

class manage(object):

    def __init__(self, parent_navigation, show_hidden, origin, move_buffer): #previous_directories a bool value which means wheather to include .. in the contents of current directories or not.

        self.update_dims() #getting screen dimensions.

        self.parent_navigation = parent_navigation

        self.show_hidden = show_hidden

        self.origin = origin #Defining 'self.origin' variable is useless here. But defined as per standard.

        self.move_buffer = move_buffer

        ftp_os.chdir(self.origin) #Changing the initial path. We are not doing this with self.Chdir() method since we do not want to change self.dir_navigation(their is a possibility for changing this if done with self.Chdir() method.) and also don't want to set Signals since everything is intial.

        curses.start_color()

        #Color Pairs Specially For Files.
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

        #Color Pairs Specially For Directories
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

        #Color Pair For credits.
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)

        #Color Pairs For Status.
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_WHITE)

        self.BOLD = [curses.A_NORMAL, curses.A_BOLD]

        screen.bkgd(" ", curses.color_pair(1)) #Foreground and Background color pair set from first pair.

        curses.noecho() #No echo of typed character.

        curses.curs_set(0) #0 For Cursor Invisible

        self.y = 1
        self.x = 0
        self.q = 0

        self.status = 'idle' #Setting the current status to 'idle' since their is none data which is outgoing/nothing which is being received.

        self.color_pair = 1

        self.selected = 0

        self.global_selected = 0

        self.jumpchar = '.' #Initial jump character.

        self.dir_navigations = 0 #Stats the number of forward movements or backward movements in terms of numbers. It can be considered as 1 dimensional "vector" quantity. As we move forward(i.e. enters into the directories) then +1 is added, if backward then -1 is added to the variable's value at that time. 0 represents no movement(i.e. currently in the starting directory), -1(can be up-to -infinity) represents currently in the parent directory relative to the starting directory and similarly +1(can be up-to +infinity) represents currently in the child's directory relative to starting directory

        self.switch_extra_paths() #Creates a extra_paths variable(self.extra_paths) that will be used to define dir_items i.e. immediately following line below.

        self.dir_items = self.extra_paths+ftp_os.listdir('.') #For initialization, it is needed, even Chdir method needs that dir_items should already exist.

        self.dirs = [] #Contains only directories from self.dir_items.

        self.files = [] #Contains only files from self.dir_items.

        self.items_onscreen = self.dir_items #Items that will be shown on the screen.

        self.screen_range = [] #Range in which items(dirs, files) can occupy whole screen.

        self.update_data() #See method's own comments.

        self.sorter() #Sorts dir_items. See comments in sorter method.

        self.ftp_transfers = {} #Have key role in ftp transfer tracking system. Contains key:value pairs where key are tickets of transfer task given to ftp_download tasks. And where a single key have four values in which first value is 'thread object', second value is the filename(server filename), third value is the pathname(local download file full path) and the fourth value states the status of task i.e. DP(Download Progress), UP(Upload Progress), DC(Download Complete), UC(Upload Complete), DE(Download Error) and UE(Upload Error).

        self.ftp_d_tickets = [] #ftp download tickets
        self.ftp_u_tickets = [] #ftp upload tickets

        self.slice_start = 0 #Starts slicing the dir_items from value 0 by default i.e. start printing from first item/element(file/directory.).

        self.SIG = 0 #define SIG:- Stands for "Signal" and means to recent key action. -1 represents KEY_UP, +1 represents KEY_DOWN, +2 represents ENTER, +3 represents HOME, +4 represents END and 0 represents initial State(i.e. no key pressed since the program was started).

        self.credits = "Developed By - Devesh"

        self.pre_printer()

    def get_ticket(self, transfer_type='download'): #Gives tickets to downloads/uploads.

        if transfer_type == 'download':
            tickets_type = self.ftp_d_tickets

        elif transfer_type == 'upload':
            tickets_type = self.ftp_u_tickets

        try:

            return tickets_type[-1]+1 #New ticket = last ticket + 1. Returns New ticket.

        except IndexError:

            return 0 #Returns initial ticket.

    def _transfer_tracker_update(self): #Updates screen

        while True:

            upload_counts = self._get_transfers('upload', 'DP')[0]
            download_counts = self._get_transfers('download', 'DP')[0]

            if upload_counts > 0:
                self.pre_printer()

            elif download_counts > 0:
                self.pre_printer()

            else:
                self.pre_printer()
                break

            time.sleep(0.5)

    def is_ftp_transfer_active(self, transfer_type='both'): #Returns ftp_transferer's activity. transfer_type can be 'upload', 'download' and 'both'.

        if transfer_type == 'upload':

            if self._get_transfers('upload', 'DP')[0] > 0:

                return True

        elif transfer_type == 'download':

            if self._get_transfers('download', 'DP')[0] > 0:

                return True

        elif transfer_type == 'both':

            if self._get_transfers('download', 'DP')[0] + self._get_transfers('upload', 'DP')[0] > 0:

                return True

        else:

            exit("function is_ftp_transfer_active(), unknown transfer_type %s" %transfer_type)

        return False

    def _get_transfers(self, transfer_type='both', count_factor='DC'): #Returns a 3 element tuple where first element is the counts of count_facter matches in ftp_tickets's ticket's 4th element.

        d_tickets = [] #Stores tickets if count_factor in present in each 3rd index of self.tickets(where tickets are from ftp_u_tickets)
        u_tickets = [] #Stores tickets if count_factor in present in each 3rd index of self.tickets(where tickets are from ftp_d_tickets).

        if transfer_type in ['download', 'both']:

            for i in self.ftp_d_tickets:

                try:

                    if self.ftp_transfers[i][3] == count_factor:

                        d_tickets.append(i)

                except:
                    pass

        if transfer_type in ['upload', 'both']:

            for i in self.ftp_u_tickets:

                try:

                    if self.ftp_transfers[i][3] == count_factor:

                        u_tickets.append(i)

                except:
                    pass

        if transfer_type == 'download':

            return (len(d_tickets), d_tickets, None)

        elif transfer_type == 'upload':

            return (len(u_tickets), None, u_tickets)

        elif transfer_type == 'both':

            return (len(d_tickets)+len(u_tickets), d_tickets, u_tickets)

    def ftp_download(self): # Resume supported ftp downloading. It manages screen to show ftp downloading, resuming, pausing, stoping and queing i.e. it itself manages how to act(on the screen) on an ftp transfer(only download case).

        download_file = self.items_onscreen[self.selected]

        ticket = self.get_ticket() #Getting upload/download tickets.

        self.ftp_d_tickets.append(ticket) #Append to ftp download tickets. i.e. ftp_d_tickets

        download_thread = threading.Thread(target=self._ftp_download, args=(download_file, ticket)) #Actual downloading by self._ftp_download method.

        download_thread.setDaemon(True) #Daemonizing the thread so that 'downloading' will stop after program exit.

        self.ftp_transfers[ticket] = [download_thread, download_file, os.getcwd()+'/'+download_file] #Last 4th element i.e. download status will be appended in the thread running.

        download_thread.start()

        transfer_update = threading.Thread(target=self._transfer_tracker_update)

        transfer_update.setDaemon(True)

        transfer_update.start()

    def _ftp_download(self, download_file, ticket): #[Real]Resume supported ftp downloading method.

        self.ftp_transfers[ticket].append("DP") #Appends Download Status - "DP"(Download Progress) into the global self.ftp_transfers[ticket] list initially.

        if use == 'ftp':

            ftplib_obj = ftp_os.get_session_copy()
            ftplib_obj.cwd(str(ftp_os.getcwd()))

        if os.path.isfile(download_file): #If file which is to be downloaded exists on disk, then it may need to be resumed.

            with open(download_file, 'rb') as f:

                size_downloaded = len(f.read())

            mode = 'ab'

        else: #If file which is to be downloaded does not exist on disk.

            size_downloaded = 0 #0 bytes are downloaded already in this case.

            mode = 'wb'

        ftplib_obj.sendcmd("REST %s" %(str(size_downloaded))) #Send data about from where(bytes offsets) to start downloading. TODO: Here If else conditions should be used to match last time of creation/modification of file which was partially downloaded with the same time of file now. If they matches then it means that file is not modified and downloading it, makes sense.

        try: #Getting Size to be downloaded.

            self.download_file_size = ftp.stat(download_file)[6] #Getting size using ftputil's FTPHost object.

        except ftplib.error_perm: #If server could not give 'size' details.

            self.download_file_size = -1 #To recognize that size is Unknown, -1 is used.

        local_file = open(download_file, mode)

        try:
            ftplib_obj.retrbinary("RETR %s" %(download_file), local_file.write)

        except: #Downloading not permitted by server.

            download_status = 'DE' #DE means "error" downloading file.

            self.ftp_transfers[ticket][3] = download_status

            return #Stops execution of function here since Error occured, if program is left to be continued then it will change its status to "DC" which is not true.

        download_status = 'DC' #DC means downloader has completed the download.

        self.ftp_transfers[ticket][3] = download_status

    def update_data(self): #Updates screen dimensions, global_selected and screen_range.

        self.update_dims()

        self.global_selected = self.dir_items.index(self.items_onscreen[0]) + self.selected

        start = self.global_selected-self.selected
        end = start + self.dims[0]-3

        self.screen_range = [start, end]

    def update_dims(self):

        self.dims = screen.getmaxyx()

    def refresh(self):

        if curses.is_term_resized(self.dims[0], self.dims[1]):

            self.pre_printer()

    def show_status(self): #It's use is nothing but a fashion.

        self.pre_printer()

    def sorter(self): #Breaks dir_items into two lists containing directories and files(dirs and files). Sort them individually in alphabetical order with lower cased file/dir name first and then combines them.

        self.dir_items = sorted(self.dir_items, key=ftp_os.path.isdir, reverse=True) #Output order - Directories first then Files.

        dirs = []
        files = []

        for item in self.dir_items: #Seperates Directories and Files
            if ftp_os.path.isdir(item):
                dirs.append(item)
            else:
                files.append(item)

        dirs = sorted(dirs, key=str.lower) #Sorts seperated directories(alphabetical order, lower case first)

        files = sorted(files, key=str.lower) #Sorts seperated directories(alphabetical order, lower case first)

        if not self.show_hidden: #Deny showing hidden files/directories acc. to a variable self.show_hidden which can be modified by the user i.e. Allow showing hidden files/directories.

            rm_hidden = [] #For dirs. Stands for 'removed hiddens'

            if len(dirs) >= 2: #In case if the directory do not have any sub directories, correnposing this if-else condition is used.

                if dirs[1] == '..': #Due to parent_navigation, '..' is already removed. That's why wee need these conditions i.e. dirs[2:] and dirs[1:]
                    mutable_dirs = dirs[2:] #mutable_dirs is same as 'dirs' but preserved reserved directory/directories i.e. '.' and '..'

                elif not dirs[1] == '..':
                    mutable_dirs = dirs[1:]

            else:

                mutable_dirs = dirs[1:]

            for i in mutable_dirs: #Removing hidden directories.

                if not i[0] == '.':
                    rm_hidden.append(i)

            dirs = self.extra_paths+rm_hidden

            rm_hidden = [] #For files. Stands for 'removed hiddens'

            for i in files: #Removing hidden files.
                if not i[0] == '.':
                    rm_hidden.append(i)

            files = rm_hidden

        self.dir_items = dirs+files #Now finally dir_items have everything sorted.

    def switch_extra_paths(self):

        if not self.parent_navigation:

            if self.dir_navigations > 0:
                self.extra_paths = ['.', '..']

            else:
                self.extra_paths = ['.']
        else:
            self.extra_paths = ['.', '..']

    def Enter_press(self):

        item = self.items_onscreen[self.selected]

        if ftp_os.path.isfile(item) and use=='ftp':

            self.ftp_download() #Downloads Selected File(If connection is FTP).

        elif ftp_os.path.isdir(item):

            self.Chdir() #Changes current directory to selected directory

    def Chdir(self, switch_dir='.'): #A directory changing method which selects directory from selected region i.e. from self.selected, self.items_onscreen etc.

        self.status = 'working' #Set status.
        self.show_status() #Show status.
        screen.refresh() #Updates screen to actually show status on screen.

        if switch_dir == '.': #When variable is not set by user

            switch_dir = self.items_onscreen[self.selected]

        if not (self.dir_navigations==0 and (not self.parent_navigation)) or switch_dir!='..': #Specially for goto_HOME method to block navigation to previous(..) directory on False parent_navigation

            ftp_os.chdir(switch_dir) #Changing the current working directory.

            if switch_dir == '..':
                self.dir_navigations -= 1

            elif switch_dir == '.':
                pass

            else:
                self.dir_navigations += 1

            self.switch_extra_paths() #Updates the self.extra_paths variable.

            self.dir_items = self.extra_paths+ftp_os.listdir('.')

            self.sorter() #Sorting current directory items in alphabetical order.

            self.selected = 0 #Reset self.selected on dir change.

            self.SIG = 2 #Enter pressed Signal. SIG = 2

            self.status = 'idle'
            #self.show_status() <- No need of it here since pre_printer() do the work.

            self.pre_printer()

        self.dirs = [] #Resetting...
        self.files = [] #Resetting...

        self.status = 'idle'
        self.show_status()

    def goto_Home(self):

        self.selected = 0

        self.SIG = 3

        self.pre_printer()

    def goto_END(self):

        self.SIG = 4

        self.pre_printer()

    def Move_Up(self):

        self.update_dims()

        if self.selected > 0 or not self.items_onscreen[0] == self.dir_items[0]:

            self.SIG = -1 #KEY_UP signal stored.

            self.selected -= 1

            self.pre_printer()

    def Move_Down(self):

        self.update_dims()

        if self.selected < len(self.items_onscreen)-1 or not self.items_onscreen[-1:] == self.dir_items[-1:]:

            self.SIG = 1 #KEY_DOWN signal stored.

            self.selected += 1

            self.pre_printer()

    def Buffer_Up(self):

        self.update_dims()

        self.SIG = 7

        self.pre_printer()

    def Buffer_Down(self):

        self.update_dims()

        self.SIG = 8

        self.pre_printer()

    def Jump(self, jumpchar): #Jump to filename/dirname starting with the given character.

        jumpchar = ord(chr(jumpchar).lower())

        self.update_dims()

        self.first_chars = [ord(x[0].lower()) for x in self.dir_items] #A list containing first characters of elements of dir_items.

        if self.SIG == 5: #If last signal was a jumpchar signal then...

            if self.jumpchar == jumpchar: #...If the given character jumpchar is same as last one then...

                try: #...try to get next dir_item's element's first character. (Try-except here for managing Index-error exception)

                    if self.first_chars[self.jumpindex+1] == self.jumpchar:

                        self.jumpindex += 1

                        self.pre_printer()

                        return True

                    else: pass #We have passed it instead of returning something(breaking everything here) since selection is now at the end of possible element and we want to return to the first filename/dirname of pressed character on keyboard.

                except IndexError:
                    pass #Same here as "else: pass" says.

            else: pass #Same here.

        else: pass #Same here

        try: #try-except here because there is possibility that no key available at that index.

            self.jumpindex = self.first_chars.index(jumpchar) #Index of the required element in dir_items.

        except ValueError:

            return False #Returning because we do not want signal to be stored since the signal wasn't executed.

        self.jumpchar = jumpchar

        self.SIG = 5 #5 key when any jumpchar key is pressed eg: a, b, g, z, 5, 9, 1...

        self.pre_printer()

    def goto_BACK(self):

        self.Chdir(switch_dir='..')

        self.SIG = 6 #Signal 6 -> Backspace key

        self.pre_printer()

    def pre_printer(self):

        self.update_dims()

        if self.SIG == -1: #UP Arrow Key

            if self.selected == -1: #Selected out of screen range in upper side. It simply means user requests for upper elements.

                self.selected += 1

                self.slice_start -= 1


        elif self.SIG == 1: #DOWN Arrow Key

            if self.selected == self.dims[0]-2: #Selected out of screen range in downward side. It simply means user requests for more elements from downwards.

                self.selected -= 1

                self.slice_start += 1


        elif self.SIG == 2: #ENTER Key

            self.slice_start = 0


        elif self.SIG == 3: #HOME Key

            self.slice_start = 0


        elif self.SIG == 4: #END Key

            if len(self.dir_items) > self.dims[0] - 2:

                self.selected = self.dims[0] - 3

                self.slice_start = len(self.dir_items)-(self.dims[0]-2)

            else:

                self.selected = len(self.dir_items)-1


        elif self.SIG == 5: #Jumpchar keys.

            self.update_data() #Updating screen range

            if self.screen_range[0] <= self.jumpindex <= self.screen_range[1]: #If the item we are looking for is on the screen then simply change self.selected value to select that.

                self.selected = self.jumpindex - self.screen_range[0]

            else: #If the item we are looking for is not on the screen then...

                if self.jumpindex > self.screen_range[0] + self.selected: #If index of required element is greater than the index we are on(selected item index.) then show selection at the end.

                    self.slice_start = self.jumpindex - (self.dims[0] - 3)

                    self.selected = self.dims[0] - 3

                else: #If index of required element is lesser than the index we are on(selected element index) then show selection at the top.

                    self.slice_start = self.jumpindex

                    self.selected = 0

        elif self.SIG == 7: #Buffering Up

            self.update_data() #Updates self.global_selected

            if self.move_buffer == 'page':

                move_buffer = len(self.items_onscreen) - 1 #Not changing the value in self.move_buffer since if it is changed then it will be maintained till the end of the program life and in between its life, if directory is changed then that value shows if defect(move with buffer which was previously obtained from previous directory) eg:- If a dir contains 10 elements(then self.move_buffer will be set to 10) but if we have switched to its child/parent directory and if it have 50 elements(on screen) then Paging down will result in jumping to 10th element(buffer 10) again and again instead of jumping 50 elements

            else:

                move_buffer = self.move_buffer

            if self.selected - move_buffer >= 0:

                self.selected -= move_buffer

            elif self.selected - move_buffer < 0:


                slice_start = self.global_selected - move_buffer

                self.selected = 0

                if slice_start >= 0:

                    self.slice_start = slice_start

                else:

                    self.slice_start = 0

        elif self.SIG == 8: #Buffering Down

            self.update_data()

            if self.move_buffer == 'page': #Page Down.

                move_buffer = len(self.items_onscreen) - 1 #Not changing the value in self.move_buffer since if it is changed then it will be maintained till the end of the program life and in between its life, if directory is changed then that value shows if defect(move with buffer which was previously obtained from previous directory) eg:- If a dir contains 10 elements(then self.move_buffer will be set to 10) but if we have switched to its child/parent directory and if it have 50 elements(on screen) then Paging down will result in jumping to 10th element(buffer 10) again and again instead of jumping 50 elements

            else:

                move_buffer = self.move_buffer #Obtaining user defined value of move_buffer.

            if (self.global_selected + move_buffer) > len(self.dir_items) - 1: #If needed(upcoming) item/element is out of max range of dir_items then...

                self.slice_start = len(self.dir_items) - len(self.items_onscreen) #Start slicing in such a way that it is the last page(i.e no other slicing provides last element of dir_items at the very last of current y-dimension) and

                self.selected = len(self.items_onscreen) - 1 #and selects the last element. OVER!

            elif move_buffer <= (len(self.items_onscreen)-1) - self.selected:

                self.selected += move_buffer

            elif move_buffer > (len(self.items_onscreen)-1) -self.selected:

                self.slice_start = self.screen_range[0] + move_buffer - ((len(self.items_onscreen)-1) - self.selected)

                self.selected = len(self.items_onscreen)-1 #Selects last element on the screen.

        #Finally passing arguments to printer.
        self.printer(self.slice_start, (self.dims[0]-2)+self.slice_start)

        #Preserves self.slice_start value to be used in refreshing.

    def printer(self, slice_start=0, slice_end=1000): #1000 is assumption that none screen will have capacity to print more than 1000 characters.

        self.update_dims() #If terminal size have been resized.

        self.items_onscreen = self.dir_items[slice_start : slice_end] #self.dir_items is preserved to have an option for recovery.

        screen.erase()

        #----------------------------------------------------------------------------------

        cwd = ftp_os.getcwd() #Current working directory

        if use == 'ftp': #If on ftp connection, prefix "ftp://host" before working directory.
            cwd = "ftp://"+fhost+cwd
            ftp_space = 10
        else:
            ftp_space = 0

        #Current working directory. Visible at the top of window.
        screen.addstr(0, ftp_space, center(cwd, self.dims[1]-ftp_space), curses.color_pair(3) | self.BOLD[1])

        #----------------------------------------------------------------------------------

        if use=='ftp': #Shows statuses of various activities at the top as described below.

            screen.addstr(0, 1, " |", curses.color_pair(9)) #Status seperator.
            screen.addstr(0, 4, "|", curses.color_pair(9)) #Status seperator.
            screen.addstr(0, 6, "|", curses.color_pair(9)) #Status seperator.
            screen.addstr(0, 8, "|", curses.color_pair(9)) #Status seperator.

            if self.status=='working':

                #Show red 'B' at top-left of screen to show 'Busy' status.
                screen.addstr(0, 0, " ", curses.color_pair(6))
                screen.addstr(0, 3, "B", curses.color_pair(7) | self.BOLD[1])

            elif self.status == 'idle':

                #Show green 'F' at the top-left of screen to show 'Free' status.
                screen.addstr(0, 3, "F", curses.color_pair(9))

            download_active = self.is_ftp_transfer_active('download') #Checks wheather downloader is downloading any file i.e. downloader's activity.
            upload_active = self.is_ftp_transfer_active('upload') #Checks wheather uploader is uploading any file i.e. uploader's activity.

            if download_active: #If Downloader is active then...

                screen.addstr(0, 0, " ", curses.color_pair(6)) #...Turns the vertical bar to 'red' colored.
                screen.addstr(0, 5, "D", curses.color_pair(7) | self.BOLD[1]) #...Turns the letter "D" to 'red' colored.

            else: #If Downloader isn't downloading anything at all then...

                screen.addstr(0, 5, "D", curses.color_pair(9)) #...Turn the letter 'D' to 'green' colored.

            if upload_active: #If uploader is active then...

                screen.addstr(0, 0, " ", curses.color_pair(6)) #...Turns the vertical bar to 'red' colored.
                screen.addstr(0, 7, "U", curses.color_pair(7) | self.BOLD[1]) #...Turns the letter 'U' to 'red' colored.

            else: #If upload isn't uploading any file at all then...

                screen.addstr(0, 7, "U", curses.color_pair(9)) #...Turns the letter 'U' to 'green' colored.

            if (((self.status=='idle') & (not download_active)) & (not upload_active)): #If uploader/downloaders are 'not active' and status is 'idle'(i.e. 'Free' status) then...

                screen.addstr(0, 0, " ", curses.color_pair(8)) #...Finally turns the vertical bar into 'green' colored stating no activity.

        #-----------------------------------------------------------------------------------------

        #Printing Files/Dirs and backgrounds.
        for y, dir_item in enumerate(self.items_onscreen):

            if (dir_item in self.dirs) or (ftp_os.path.isdir(dir_item)): #Setting configurations to color up directories when printed. Exception: Appending to self.dirs.

                if dir_item not in self.dirs: #Just appends directories to another self variable(Purpose: cache to avoid calling ftp_os.path.isfile/isdir again and again.)
                    self.dirs.append(dir_item)

                dir_item = "+ "+dir_item

                if y == self.selected: #When the current directory is selected.
                    self.bold = 1
                    self.color_pair = 4

                else:
                    self.bold = 1
                    self.color_pair = 3

            elif (dir_item in self.files) or (not ftp_os.path.isdir(dir_item)): #Setting configurations to color up files when printed. Exception: Appending to self.files.

                if dir_item not in self.files: #Just appends files to another self variable(Purpose: cache to avoid calling ftp_os.path.isfile/isdir again and again.)
                    self.files.append(dir_item)

                dir_item = "  "+dir_item #Indentation because of symmetry with "+" before directory(ies) names.

                if y == self.selected: #When the current file is selected.
                    self.color_pair = 2
                    self.bold = 1

                else:
                    self.color_pair = 1
                    self.bold = 0
        #-----------------------------------------------------------------------------------------
        
            #Printing elements(Directories and Files.) and backgrounds.
            screen.addstr(y+1, self.x, " "+dir_item+(self.dims[1]-len(dir_item)-1)*" ", curses.color_pair(self.color_pair) | self.BOLD[self.bold])

        #Credits to Developer.
        screen.addstr(self.dims[0]-1, self.dims[1]-len(" "+self.credits+" ")-1, " "+self.credits+" ", curses.color_pair(5) | self.BOLD[1])

    def end(self): #To exit curses environment(opposite of initstr() method of curses). Restores previous terminal configuration.

        curses.endwin()
        os.system("clear")

keybinds.load_keybinds() #Loaded key:values as variable=value in global scope. For details :- See "keybinds.py" source code.

browser = manage(parent_navigation, show_hidden, origin, buff)
q = 0

try:
    while q!=keybinds.quit: #ASCII code 81 = 'Q'

        q = screen.getch()

        if q == 10:

            browser.Enter_press()

        elif q == keybinds.MoveDown:

            browser.Move_Down()

        elif q == keybinds.MoveUp:

            browser.Move_Up()

        elif q == keybinds.goto_First:

            browser.goto_Home()

        elif q == keybinds.goto_Last:

            browser.goto_END()

        elif q == keybinds.BufferUp:

            browser.Buffer_Up()

        elif q == keybinds.BufferDown:

            browser.Buffer_Down()

        elif q in [ord(x) for x in keybinds.Jumper_alphabets]:

            browser.Jump(q)

        elif q == keybinds.goto_Back:

            browser.goto_BACK()

        screen.timeout(100)

        browser.refresh()

    browser.end()

except KeyboardInterrupt: #To prevent unrestored terminal/tty etc. configuration on unexpected exits i.e. Unhandled exceptions.

    browser.end()
