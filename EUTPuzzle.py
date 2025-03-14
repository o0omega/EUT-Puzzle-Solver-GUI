import customtkinter as ctk
import sys

app = ctk.CTk()
app.geometry("740x450")
app.title("EUT Harry's Puzzle Solver")
app.iconbitmap("M.ico")

tabview = ctk.CTkTabview(app)
tabview.pack(pady=14, padx=20, expand=True, fill="both")

tabs = [
    "Puzzle #1",
    "Puzzle #2",
    "Puzzle #3",
    "Puzzle #4"
]
custom_limits = {
    "Puzzle #1": 3,
    "Puzzle #2": 3,
    "Puzzle #3": 4,
    "Puzzle #4": 11
}
entries_dict = {}
labels_dict = {}

info_window = None
def open_info():
    try:
        global info_window

        if info_window is not None and info_window.winfo_exists():
            info_window.lift()
            info_window.focus_force()
            return

        info_window = ctk.CTkToplevel(app)
        info_window.geometry("350x300")
        info_window.title("Information")

        info_window.after(10, lambda: info_window.focus_force())
        info_window.after(200, lambda: info_window.iconbitmap("DM.ico"))

        label = ctk.CTkLabel(info_window, 
            text=(
"""
Key Binds:
"Tab" = Go to next entry window
"Shift+Tab" = Go to previous entry window
"R" = Reset (Clear entries on current puzzle)
"Enter" = Enter (Find order)
"[" = Previous (Go to previous puzzle)
"]" = Next (Go to next puzzle)
            
Puzzle #4 entries take all 3 RGB values of one color
separated by either "t" or "-" (both can be used)
Puzzle #2 can be used for Puzzle #1 as well

Made by ozomega
Discord: @m6ga
"""
            ), 
            font=("", 15),
            justify="left",
            anchor="w",
            width=280
        )
        label.pack(pady=20)
    except Exception as e:
        sys.__stdout__.write(f"Error processing open_info: {e}\n")

console_window = None
console_text = None
def open_console():
    try:
        global console_window, console_text

        if console_window is not None and console_window.winfo_exists():
            console_window.lift()
            console_window.focus_force()
            return

        console_window = ctk.CTkToplevel(app)
        console_window.geometry("500x300")
        console_window.title("Console Output")
        console_window.iconbitmap("RM.ico")

        console_window.after(10, lambda: console_window.focus_force())
        console_window.after(200, lambda: console_window.iconbitmap("RM.ico"))

        button_frame = ctk.CTkFrame(console_window)
        button_frame.pack(anchor="nw", padx=10, pady=5)
        button_frame.configure(fg_color='transparent')

        close_button = ctk.CTkButton(button_frame, text="Close", command=console_window.destroy, width=60, height=20, font=("", 15))
        close_button.pack(side="left", padx=5)

        pin_button = ctk.CTkButton(button_frame, text="Pin", command=lambda: pin_window(console_window, pin_button), width=40, height=20, font=("", 15))
        pin_button.pack(side="left")

        console_text = ctk.CTkTextbox(console_window, wrap="word", height=250)
        console_text.pack(pady=(0,10), padx=10, fill="both", expand=True)

        app.after(100, setup_redirection)

    except Exception as e:
        sys.__stdout__.write(f"Error processing open_console: {e}\n")

def setup_redirection():
    sys.stdout.write = write_console
    sys.stderr.write = write_console

def write_console(text):
    try:
        if console_text is not None:
            console_text.insert("end", text)
            console_text.see("end")
    except Exception as e:
        sys.__stdout__.write(f"Error in write_console: {e}\n")
        sys.__stdout__.write(text)

def clear_console():
    try:
        if console_text is not None:
            console_text.delete("1.0", "end")
    except Exception as e:
        print(f"Error processing clear_console: {e}")

def pin_window(window, button):
    try:
        current_topmost = window.attributes('-topmost')
        window.attributes('-topmost', not current_topmost)
        button.configure(text="Unpin" if not current_topmost else "Pin")
    except Exception as e:
        print(f"Error processing pin_window: {e}")

def parse_entries_puzzle1():
    try:
        tab = tabview.get()
        values = [int(entry.get()) if entry.get().isdigit() else 0 for row in entries_dict[tab] for entry in row]
        print(f"Puzzle #1 Entries:", values)
        
        non_zero_values = [value for value in values if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Puzzle #1 Order:", ordered_values)

        label_index = 0
        for i in range(5):
            for j in range(5):
                labels_dict[tab][i][j].configure(text=str(ordered_values[label_index]))
                label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #1: {e}")

def parse_entries_puzzle2():
    try:
        tab = tabview.get()
        values = [entry.get() if entry.get() else '0' for row in entries_dict[tab] for entry in row]
        print(f"Puzzle #2 Entries:", values)

        replace = str.maketrans("!@#$%^&*()", "1234567890")
        values = [int(num.translate(replace)) for num in values]
        print(f"Puzzle #2 Converted:", values)

        non_zero_values = [value for value in values if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Puzzle #2 Order:", ordered_values)

        label_index = 0
        for i in range(5):
            for j in range(5):
                labels_dict[tab][i][j].configure(text=str(ordered_values[label_index]))
                label_index += 1
            
    except Exception as e:
        print(f"Error processing Puzzle #2: {e}")

def parse_entries_puzzle3():
    try:
        tab = tabview.get()
        values = [int(entry.get()) if entry.get().isdigit() else 0 for row in entries_dict[tab] for entry in row]
        print(f"Puzzle #3 Entries:", values)

        binary_ones_count = [bin(i)[2:].count('1') for i in values]
        print(f"Puzzle #3 Binary 1s Counts:", binary_ones_count)

        non_zero_values = [(i, count) for i, count in enumerate(binary_ones_count) if count != 0]
        non_zero_values.sort(key=lambda x: x[1])
        order = {pair[0]: i + 1 for i, pair in enumerate(non_zero_values)}
        ordered_values = [order.get(i, 0) for i in range(25)]
        print(f"Puzzle #3 Order:", ordered_values)

        label_index = 0
        for i in range(5):
            for j in range(5):
                labels_dict[tab][i][j].configure(text=str(ordered_values[label_index]))
                label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #3: {e}")

def parse_entries_puzzle4():
    try:
        def rgb_to_hsv(r, g, b):
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            cmax, cmin = max(r, g, b), min(r, g, b)
            d = cmax - cmin
            if d == 0:
                h = 0
            elif cmax == r:
                h = (60 * ((g - b) / d) + 360) % 360
            elif cmax == g:
                h = (60 * ((b - r) / d) + 120) % 360
            elif cmax == b:
                h = (60 * ((r - g) / d) + 240) % 360
            s = 0 if cmax == 0 else d * 100 / cmax
            v = cmax * 100
            return h + s + v
        
        tab = tabview.get()
        values = [entry.get() if entry.get() else '0' for row in entries_dict[tab] for entry in row]
        print(f"Puzzle #4 Entries:", values)

        rgb_values = []
        for value in values:
            value = value.replace('t', '-')
            rgb_triplet = list(map(int, value.split('-')))
            if len(rgb_triplet) == 3:
                rgb_values.append(rgb_triplet)
            else:
                rgb_values.append([0, 0, 0])
        
        print(f"Parsed RGB Values:", rgb_values)

        hsv_values = [rgb_to_hsv(r, g, b) for r, g, b in rgb_values]
        print(f"Puzzle #4 HSV Values:", hsv_values)

        non_zero_values = [value for value in hsv_values if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in hsv_values]
        print(f"Puzzle #4 Order:", ordered_values)

        label_index = 0
        for i in range(5):
            for j in range(5):
                labels_dict[tab][i][j].configure(text=str(ordered_values[label_index]))
                label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #4: {e}")


def limit_input(entry_text, max_length, tabname):
    try:
        valid_chars = set("0123456789-t!@#$%^&*()")
        return (len(entry_text) <= int(max_length) and 
                all(char in valid_chars for char in entry_text))
    except Exception as e:
        print(f"Error processing limit_input: {e}")

def set_initial_focus(event=None):
    try:
        tab = tabview.get()
        if tab in entries_dict and entries_dict[tab]:
            entries_dict[tab][0][0].focus_set()
    except Exception as e:
        print(f"Error processing set_initial_focus: {e}")

def reset_entries(event=None):
    try:
        tab = tabview.get()
        for row in entries_dict[tab]:
            for entry in row:
                entry.delete(0, "end")
    except Exception as e:
        print(f"Error processing reset_entries: {e}")

def output_order(event=None):
    try:
        tab = tabview.get()
        if tab == "Puzzle #1":
            parse_entries_puzzle1()
        elif tab == "Puzzle #2":
            parse_entries_puzzle2()
        elif tab == "Puzzle #3":
            parse_entries_puzzle3()
        elif tab == "Puzzle #4":
            parse_entries_puzzle4()
    except Exception as e:
        print(f"Error processing output_order: {e}")

def next_puzzle(event=None):
    try:
        tab = tabview.get()
        tab_index = tabs.index(tab)
        next_tab_index = (tab_index + 1) % len(tabs)
        tabview.set(tabs[next_tab_index])
        set_initial_focus()
    except Exception as e:
        print(f"Error processing next_puzzle: {e}")

def prev_puzzle(event=None):
    try:
        tab = tabview.get()
        tab_index = tabs.index(tab)
        prev_tab_index = (tab_index - 1) % len(tabs)
        tabview.set(tabs[prev_tab_index])
        set_initial_focus()
    except Exception as e:
        print(f"Error processing prev_puzzle: {e}")

app.bind('<Return>', output_order)
app.bind('[', prev_puzzle)
app.bind(']', next_puzzle)
app.bind('r', reset_entries)

for tabname in tabs:
    tab = tabview.add(tabname)

    frame1 = ctk.CTkFrame(tab)
    frame1.pack(side="left", padx=10, pady=10)

    frame1grid1 = ctk.CTkFrame(frame1)
    frame1grid2 = ctk.CTkFrame(frame1)
    frame1grid1.pack(side="top")
    frame1grid2.pack(side="bottom", pady=10)

    frame1grid2.configure(fg_color='transparent')

    frame2 = ctk.CTkFrame(tab)
    frame2.pack(side="right", padx=10, pady=10)

    frame2grid1 = ctk.CTkFrame(frame2)
    frame2grid2 = ctk.CTkFrame(frame2)
    frame2grid1.pack(side="top")
    frame2grid2.pack(side="bottom", pady=10)
    frame2grid2.configure(fg_color='transparent')

    entries = []
    n = 45 if tabname != "Puzzle #4" else 85
    for i in range(5):
        row_entries = []
        max_length = custom_limits[tabname]
        validate_cmd = app.register(lambda text, length, tab=tabname: limit_input(text, length, tab))
        for j in range(5):
            entry = ctk.CTkEntry(
                frame1grid1,
                width=n,
                height=45,
                justify="center",
                validate="key",
                validatecommand=(validate_cmd, "%P", max_length),
                border_width=1,
                corner_radius=2
            )
            entry.grid(row=i+1, column=j)
            row_entries.append(entry)
        entries.append(row_entries)

    labels = []
    for i in range(5):
        row_labels = []
        for j in range(5):
            label = ctk.CTkLabel(frame2grid1, width=45, height=45, justify="center", text="0", fg_color="#025c9d", font=("", 16, "bold"))
            label.grid(row=i+1, column=j)
            row_labels.append(label)
        labels.append(row_labels)

    entries_dict[tabname] = entries
    labels_dict[tabname] = labels

    inputlabel = ctk.CTkLabel(frame1grid1, width=100, text="Input", font=("", 20))
    inputlabel.grid(row=0, column=0, columnspan=5, pady=10)

    outputlabel = ctk.CTkLabel(frame2grid1, width=100, text="Order", font=("", 20))
    outputlabel.grid(row=0, column=0, columnspan=5, pady=10)

    if tabname == "Puzzle #1":
        enterbutton = ctk.CTkButton(frame1grid2, width=100, text="Enter", command=parse_entries_puzzle1, font=("", 20))
    elif tabname == "Puzzle #2":
        enterbutton = ctk.CTkButton(frame1grid2, width=100, text="Enter", command=parse_entries_puzzle2, font=("", 20))
    elif tabname == "Puzzle #3":
        enterbutton = ctk.CTkButton(frame1grid2, width=100, text="Enter", command=parse_entries_puzzle3, font=("", 20))
    else:
        enterbutton = ctk.CTkButton(frame1grid2, width=100, text="Enter", command=parse_entries_puzzle4, font=("", 20))
    enterbutton.grid(row=0, column=1, padx=5)

    resetbutton = ctk.CTkButton(frame1grid2, width=100, text='Reset', command=reset_entries, font=("", 20))
    resetbutton.grid(row=0, column=0, padx=5)

    previousbutton = ctk.CTkButton(frame2grid2, width=100, text="Previous", command=prev_puzzle, font=("", 20))
    previousbutton.grid(row=0, column=0, padx=5)

    nextbutton = ctk.CTkButton(frame2grid2, width=100, text="Next", command=next_puzzle, font=("", 20))
    nextbutton.grid(row=0, column=1, padx=5)

app.after(10, lambda: set_initial_focus())

info_button = ctk.CTkButton(app, text="?", command=open_info, width=20, height=20, font=("", 15))
info_button.place(x=5, y=5)

pin_button = ctk.CTkButton(app, text="Pin", command=lambda: pin_window(app, pin_button), width=40, height=20, font=("", 15))
pin_button.place(x=113, y=5)

console_button = ctk.CTkButton(app, text="Console", command=open_console, width=80, height=20, font=("", 15))
console_button.place(x=30, y=5)

app.mainloop()

# python -m nuitka --enable-plugin=tk-inter --standalone --onefile --windows-console-mode=disable --include-data-files="M.ico=M.ico" --include-data-files="DM.ico=DM.ico" --include-data-files="RM.ico=RM.ico" --windows-icon-from-ico=M.ico EUTPuzzle.py
# Nuitka library required to use compiling line above, put ico files in the same repository as the script (the files are present on github).4
