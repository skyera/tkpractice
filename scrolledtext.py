import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import *

TXT = """
This window is a scrolled text widget.  It displays one or more lines of text
and allows you to edit the text.  Here is a summary of the things you
can do to a text widget:

1. Scrolling. Use the scrollbar to adjust the view in the text window.

2. Scanning. Press the left mouse button in the text window and drag 
up or down. This will drag the text at high speed to allow you to scan 
its contents.

3. Insert text. Press the left mouse button to set the insertion cursor, then
type text.  What you type will be added to the widget.

4. Select. Press mouse button 1 and drag to select a range of characters.
Once you've released the button, you can adjust the selection by pressing
button 1 with the shift key down.  This will reset the end of the
selection nearest the mouse cursor and you can drag that end of the
selection by dragging the mouse before releasing the mouse button.
You can double-click to select whole words or triple-click to select
whole lines.

5. Delete and replace. To delete text, select the characters you'd like
to delete and type Backspace or Delete.  Alternatively, you can type new
text, in which case it will replace the selected text.

6. Copy the selection. To copy the selection into this window, select
what you want to copy (either here or in another application), then
click button 2 to copy the selection to the point of the mouse cursor.

7. Edit.  Text widgets support the standard Motif editing characters
plus many Emacs editing characters.  Backspace and Control-h erase the
character to the left of the insertion cursor.  Delete and Control-d
erase the character to the right of the insertion cursor.  Meta-backspace
deletes the word to the left of the insertion cursor, and Meta-d deletes
the word to the right of the insertion cursor.  Control-k deletes from
the insertion cursor to the end of the line, or it deletes the newline
character if that is the only thing left on the line.  Control-o opens
a new line by inserting a newline character to the right of the insertion
cursor.  Control-t transposes the two characters on either side of the
insertion cursor.  Control-z undoes the last editing action performed,
and, Control-Shift-z (or Control-y) redoes undone edits.

8. Resize the window.  This widget has been configured with the "setGrid"
option on, so that if you resize the window it will always resize to an
even number of characters high and wide.  Also, if you make the window
narrow you can see that long lines automatically wrap around onto
additional lines so that all the information is always visible."""

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y)
        text = ScrolledText(height=30, wrap=tk.WORD, undo=True,
                setgrid=True, pady=2, padx=3)
        text.pack(in_=frame, fill=tk.BOTH, expand=tk.Y)
        text.insert(tk.END, TXT)


if __name__ == '__main__':
    app = App()
    app.mainloop()
