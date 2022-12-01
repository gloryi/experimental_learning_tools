import random
from threading import Thread, Lock
import random
import time
import sys, select

vim_commands = []

vim_commands.append(""":e filename	Open filename for edition""")
vim_commands.append(""":w	Save file""")
vim_commands.append(""":q	Exit Vim""")
vim_commands.append(""":q!	Quit without saving""")
vim_commands.append(""":x	Write file (if changes has been made) and exit""")
vim_commands.append(""":sav filename	Saves file as filename""")
vim_commands.append(""".	Repeats the last change made in normal mode""")
vim_commands.append("""k or Up Arrow	move the cursor position up one line""")
vim_commands.append("""j or Down Arrow	move the cursor down one line""")
vim_commands.append("""e	move the cursor to the end of the word""")
vim_commands.append("""b	move the cursor to the begining of the word""")
vim_commands.append("""0	move the cursor to the begining of the line""")
vim_commands.append("""G	move the cursor to the end of the file""")
vim_commands.append("""gg	move the cursor to the begining of the file""")
vim_commands.append("""L	move the cursor to the bottom of the screen""")
vim_commands.append(""":59	move cursor to line number 59. Replace 59 by the desired line number.""")
vim_commands.append("""%	Move cursor to matching parenthesis""")
vim_commands.append("""[[	Jump to function start""")
vim_commands.append("""[{	Jump to block start""")
vim_commands.append("""y	Copy the selected text to clipboard""")
vim_commands.append("""p	Paste clipboard contents""")
vim_commands.append("""dd	Cut current line""")
vim_commands.append("""yy	Copy current line""")
vim_commands.append("""y$	Copy to end of line""")
vim_commands.append("""D	Cut to end of line""")
vim_commands.append("""/word	Search word from top to bottom""")
vim_commands.append("""?word	Search word from bottom to top""")
vim_commands.append("""*	Search the word under cursor""")
vim_commands.append("""/\cstring	Search STRING or string, case insensitive""")
vim_commands.append("""/jo[ha]n	Search john or joan""")
vim_commands.append("""/\< the	Search the, theatre or then""")
vim_commands.append("""/the\>	Search the or breathe""")
vim_commands.append("""/fred\|joe	Search fred or joe""")
vim_commands.append("""/\<\d\d\d\d\>	Search exactly 4 digits""")
vim_commands.append("""/^\n\{3}	Find 3 empty lines""")
vim_commands.append(""":bufdo /searchstr/	Search in all open files""")
vim_commands.append("""bufdo %s/something/somethingelse/g	Search something in all the open buffers and replace it with somethingelse""")
vim_commands.append("""%s/old/new/g	Replace all occurences of old by new in file""")
vim_commands.append(""":%s/onward/forward/gi	Replace onward by forward, case unsensitive""")
vim_commands.append(""":%s/old/new/gc	Replace all occurences with confirmation""")
vim_commands.append(""":%s/^/hello/g	Replace the begining of each line by hello""")
vim_commands.append(""":%s/$/Harry/g	Replace the end of each line by Harry""")
vim_commands.append(""":%s/onward/forward/gi	Replace onward by forward, case unsensitive""")
vim_commands.append(""":%s/ *$//g	Delete all white spaces""")
vim_commands.append(""":g/string/d	Delete all lines containing string""")
vim_commands.append(""":s/Bill/Steve/	Replace the first occurence of Bill by Steve in current line""")
vim_commands.append(""":s/Bill/Steve/g	Replace Bill by Steve in current line""")
vim_commands.append(""":%s/Bill/Steve/g	Replace Bill by Steve in all the file""")
vim_commands.append(""":%s/^M//g	Delete DOS carriage returns (^M)""")
vim_commands.append(""":%s/\r/\r/g	Transform DOS carriage returns in returns""")
vim_commands.append(""":%s#<[^>]\+>##g	Delete HTML tags but keeps text""")
vim_commands.append(""":%s/^\(.*\)\n\1$/\1/	Delete lines which appears twice""")
vim_commands.append("""Ctrl+a	Increment number under the cursor""")
vim_commands.append("""Ctrl+x	Decrement number under cursor""")
vim_commands.append("""ggVGg?	Change text to Rot13""")
vim_commands.append("""Vu	Lowercase line""")
vim_commands.append("""VU	Uppercase line""")
vim_commands.append("""g~~	Invert case""")
vim_commands.append("""vEU	Switch word to uppercase""")
vim_commands.append("""vE~	Modify word case""")
vim_commands.append("""ggguG	Set all text to lowercase""")
vim_commands.append("""gggUG	Set all text to uppercase""")
vim_commands.append(""":set ignorecase	Ignore case in searches""")
vim_commands.append(""":set smartcase	Ignore case in searches excepted if an uppercase letter is used""")
vim_commands.append(""":%s/\<./\l&/g	Sets first letter of each word to lowercase""")
vim_commands.append(""":%s/.*/\l&	Sets first letter of each line to lowercase""")
vim_commands.append(""":1,10 w outfile	Saves lines 1 to 10 in outfile""")
vim_commands.append(""":1,10 w >> outfile	Appends lines 1 to 10 to outfile""")
vim_commands.append(""":r infile	Insert the content of infile""")
vim_commands.append(""":23r infile	Insert the content of infile under line 23""")
vim_commands.append(""":e .	Open integrated file explorer""")
vim_commands.append(""":Sex	Split window and open integrated file explorer""")
vim_commands.append(""":Sex!	Same as :Sex but split window vertically""")
vim_commands.append(""":browse e	Graphical file explorer""")
vim_commands.append(""":ls	List buffers""")
vim_commands.append(""":cd ..	Move to parent directory""")
vim_commands.append(""":args	List files""")
vim_commands.append(""":args *.php	Open file list""")
vim_commands.append(""":grep expression *.php	Returns a list of .php files contening expression""")
vim_commands.append("""gf	Open file name under cursor""")
vim_commands.append(""":!pwd	Execute the pwd unix command, then returns to Vi""")
vim_commands.append("""!!pwd	Execute the pwd unix command and insert output in file""")
vim_commands.append(""":sh	Temporary returns to Unix""")
vim_commands.append("""$exit	Retourns to Vi""")
vim_commands.append(""":%!fmt	Align all lines""")
vim_commands.append("""!}fmt	Align all lines at the current position""")
vim_commands.append("""5!!fmt	Align the next 5 lines""")
vim_commands.append(""":tabnew	Creates a new tab""")
vim_commands.append("""gt	Show next tab""")
vim_commands.append(""":tabfirst	Show first tab""")
vim_commands.append(""":tablast	Show last tab""")
vim_commands.append(""":tabm n(position)	Rearrange tabs""")
vim_commands.append(""":tabdo %s/foo/bar/g	Execute a command in all tabs""")
vim_commands.append(""":tab ball	Puts all open files in tabs""")
vim_commands.append(""":new abc.txt	Edit abc.txt in new window""")
vim_commands.append(""":e filename	Edit filename in current window""")
vim_commands.append(""":split filename	Split the window and open filename""")
vim_commands.append("""ctrl-w up arrow	Puts cursor in top window""")
vim_commands.append("""ctrl-w ctrl-w	Puts cursor in next window""")
vim_commands.append("""ctrl-w_	Maximize current window vertically""")
vim_commands.append("""ctrl-w|	Maximize current window horizontally""")
vim_commands.append("""ctrl-w=	Gives the same size to all windows""")
vim_commands.append("""10 ctrl-w+	Add 10 lines to current window""")
vim_commands.append(""":vsplit file	Split window vertically""")
vim_commands.append(""":sview file	Same as :split in readonly mode""")
vim_commands.append(""":hide	Close current window""")
vim_commands.append(""":b 2	Open #2 in this window""")
vim_commands.append("""Ctrl+n Ctrl+p (To be used in insert mode)	Complete word""")
vim_commands.append("""Ctrl+x Ctrl+l	Complete line""")
vim_commands.append(""":set dictionary=dict	Define dict as a dictionnary""")
vim_commands.append("""Ctrl+x Ctrl+k	Complete with dictionnary""")
vim_commands.append("""m {a-z}	Marks current position as {a-z}""")
vim_commands.append(""":ab mail mail@provider.org	Define mail as abbreviation of mail@provider.org""")
vim_commands.append(""":set autoindent	Turn on auto-indent""")
vim_commands.append(""":set smartindent	Turn on intelligent auto-indent""")
vim_commands.append(""":set shiftwidth=4	Defines 4 spaces as indent size""")
vim_commands.append("""ctrl-t, ctrl-d	Indent/un-indent in insert mode""")
vim_commands.append(""">>	Indent""")
vim_commands.append("""<<	Un-indent""")
vim_commands.append("""=%	Indent the code between parenthesis""")
vim_commands.append("""1GVG=	Indent the whole file""")

for i in range(len(vim_commands)):
    vim_commands[i] = [vim_commands[i],0]


time_in_seconds = 60
synchroniser = Lock()
positive_count = 0
missed_count = 0

def print_stats():
    global time_in_seconds
    print(f"CORRECT    : {positive_count}")
    print(f"MISSED     : {missed_count}")
    percent = int(positive_count / (positive_count + missed_count) * 100)
    print(f"PERFOMANCE : {percent}%")

    if positive_count + missed_count > 10:
        if percent > 80:
            time_in_seconds -= 5
            if time_in_seconds <= 20:
                time_in_seconds = 20
        elif percent < 60:
            time_in_seconds += 5

def random_tasks_feeder():
    while True:
        synchroniser.acquire()
        random_command = random.choice(vim_commands)
        print(random_command[0])
        print(time_in_seconds," ss")

t = Thread(target = random_tasks_feeder, args=())
t.start()
while True:
    i, o, e = select.select( [sys.stdin], [], [], int(time_in_seconds))
    if (i):
        sys.stdin.readline().strip()
        positive_count += 1
    else:
        missed_count += 1
    print_stats()
    if synchroniser.locked():
        synchroniser.release()
