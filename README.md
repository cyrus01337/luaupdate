# luaupdate
Luau installer and updater - ensure the latest version of Luau is always at your fingertips

## Requirements
Git
Python 3.6+

## Setup
Ensure the requirements above are installed, then run the commands below according to your OS:
```
git clone https://github.com/cyrus01337/luaupdate.git
cd luaupdate
```

Install the *project's* requirements (`python3` for Mac/Linux which translates to  `py -3` for Windows):
```sh
python3 -m pip install -r requirements.txt
```

Then run it as you would any Python script:
```sh
python3 luaupdate.py
```

Future plans include an install script that does this for you and even sets it up as a CLI tool (which was the original intent).
