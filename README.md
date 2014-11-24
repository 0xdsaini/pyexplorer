#Pyexplorer


##Dependencies

###Main dependency

    1. python2.7

###External Python libraries
(Hint : Below libs can be installed with the help of **pip** on Linux based
platforms.)

    1. termcolor
    2. ftputil

###Installation
Currently, it **does not support** installation to any system but you can
run it directly.

    Step 1 - chmod +x pyexplorer.py
    Step 2 - ./pyexplorer.py

##Supported keys
Once, you have started the application. These keys are supported ```Up Arrow```, ```Down Arrow```,
```Page Up```, ```Page Down```, ```Home```, ```End```, ```Enter```, ```Q```(Uppercased Q) and all the
lowercased ASCII characters(a, b, c, d, ., ~, 1, 5, 0, etc.).

####Enter
If on local connection, used to switch directories. If on FTP connection,
used to switch directories and download files.

####Backspace
It is used to switch to its parent directory.

####Up/Down Arrow
These two keys are used to move 1 element(directory/file) upward/downward
respectively.

####Page Up/Down
These two keys can be used to move ```x``` no. of elements upwards/downwards
(Here ```x``` is the **no. of elements on the screen**.). It can be optionally
changed by passing a value with ```buff```(Stands for buffer) command line
argument before starting the application. See **buff** in 
**Command-line arguments** section for more info.

####Uppercased Q
This is used to quit the application anytime.

####lowercased ASCII characters.
lowercased ASCII characters are used to jump to elements(directories/files)
starting whose name starts with that character which has been pressed.

##Command-line arguments
Passing command-line arguments are bit different. Arguments can be passed as
"key=value" pairs. Have a look here.

####origin
This argument allows to start exploration from another path other than the
current path.

    ./pyexplorer.py origin=<path to initially start exploration.>

Example(s):-

    1 - ./pyexplorer.py origin=/usr/bin
    2 - ./pyexplorer.py "origin=/home/moore/Desktop/Source Codes"

####parent_navigation
This permit/forbid navigation to parent directories according to the
boolean value passed to it. Allowed values are ```True, true, 1``` for
True and ```False/false/0``` for False. By default it is set to ```True```
i.e. it does not forbid navigation to parent directories

    ./pyexplorer.py parent_navigation=<boolean>

Example(s):-

    1 - ./pyexplorer.py parent_navigation=False

####show_hidden
As it sounds loudly, it enable/disable showing of hidden files/directories.
Allowed values are ```True, true, 1``` for True and ```False/false/0```
for False. By default it is set to ```False```.

    ./pyexplorer.py show_hidden=<boolean>

Example(s):-

    1 - ./pyexplorer.py show_hidden=True

####buff
It stands for **buff*er. It can be used to optionally configure Page Up/Down
movements. For example if its value is set to 5, Page Up/Down will result in
moving 5 elements(directories/files) Up/Down.

    ./pyexplorer.py buff=<any number>

Example(s):-

    1 - ./pyexplorer.py buff=5

####use
Its values can be ```local``` or ```ftp```. By default it is set to ```local```.
If set to ```local```, explores directories locally. If set to ```ftp```, explores
directories of a ftp server(can be passed using ```fhost``` argument) and supports
**resumable downloading**. Currently **no uploading** support is implemented. 

    ./pyexplorer.py use=<ftp/local>

Example(s):-

    1 - ./pyexplorer.py use=ftp

####fhost
The value passed with it is the **ftp host** to connect to. This is by default set
to ```localhost```. Allowed values are up and working ftp server addresses. It
must not start with a ```ftp://``` prefix.
  To use it, you have to explicitly tell pyexplorer to use ftp by passing ```use=ftp```
argument before starting it.

    ./pyexplorer.py use=ftp fhost=<host address>

Example(s):-

    1 - ./pyexplorer.py use=ftp fhost=ftp.debian.org

####fuser
This is to pass **ftp username** to the ftp server with which you want to connect
to ftp server. See **fhost**, **fpass** for **host address** and
**passwords** respectively.

    ./pyexplorer.py use=ftp fhost=<host address> fuser=<username>

Example(s):-

    1 - ./pyexplorer.py use=ftp fhost=localhost fhost=devesh

####fpass
This is to pass **ftp password** to ftp server. See **fhost**, **fuser** for
**host address** and **password** respectively. This is what I personally
don't like, but I promise to change it soon.

    ./pyexplorer.py use=ftp fpass=<password>

Example(s):-

    1 - ./pyexplorer.py use=ftp fhost=localhost fhost=devesh fpass=trustmeIwonttellyou

You can also offer your own contribution(s) to our [Github](https://github.com/devesh525s/pyexplorer) repository.
