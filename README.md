# PyExplorer

PyExplorer is a command-line file explorer written in Python, allowing users to navigate and interact with both local directories and FTP servers. Below is a comprehensive guide on installing, running, and customizing PyExplorer.

## Dependencies

### Main Dependency

- Python 3.8 or above

### External Python Libraries

Install these libraries using `pip` on Linux-based platforms:

1. termcolor
    ```bash
    pip install termcolor
    ```

2. ftputil
    ```bash
    pip install ftputil
    ```

## Installation

Currently, PyExplorer does not support installation to any system, but it can be run directly.

1. Make the script executable:
    ```bash
    chmod +x pyexplorer.py
    ```

2. Run PyExplorer:
    ```bash
    ./pyexplorer.py
    ```

## Supported Keys

- **Enter:** Switch directories (local) or switch directories and download files (FTP).
- **Backspace:** Switch to the parent directory.
- **Up/Down Arrow:** Move one element (directory/file) upward/downward.
- **Page Up/Down:** Move a specified number of elements (configurable using the `buff` command line argument).
- **Home/End:** Jump to the beginning or end of the list.
- **Uppercased Q:** Quit the application.
- **Lowercased ASCII Characters:** Jump to elements starting with the pressed character.

## Command-line Arguments

Arguments are passed as "key=value" pairs. Here are the supported command-line arguments:

- **origin:** Start exploration from a path other than the current path.
    ```bash
    ./pyexplorer.py origin=<path to start exploration>
    ```

- **parent_navigation:** Permit/forbid navigation to parent directories (default is `True`).
    ```bash
    ./pyexplorer.py parent_navigation=<True/False>
    ```

- **show_hidden:** Enable/disable showing hidden files/directories (default is `False`).
    ```bash
    ./pyexplorer.py show_hidden=<True/False>
    ```

- **buff:** Configure Page Up/Down movements (default is 1).
    ```bash
    ./pyexplorer.py buff=<any number>
    ```

- **use:** Explore directories locally or via FTP (default is `local`).
    ```bash
    ./pyexplorer.py use=<ftp/local>
    ```

- **fhost:** Set the FTP host to connect to (default is `localhost`).
    ```bash
    ./pyexplorer.py use=ftp fhost=<host address>
    ```

- **fuser:** Pass FTP username to connect to the FTP server.
    ```bash
    ./pyexplorer.py use=ftp fhost=<host address> fuser=<username>
    ```

- **fpass:** Pass FTP password to connect to the FTP server.
    ```bash
    ./pyexplorer.py use=ftp fhost=<host address> fuser=<username> fpass=<password>
    ```

## Contribution

Feel free to contribute to our [GitHub repository](https://github.com/0xdsaini/pyexplorer).

Explore and navigate effortlessly with PyExplorer!
