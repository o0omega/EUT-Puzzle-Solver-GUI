import customtkinter as ctk
import sys
from ctypes import windll
# from keyboard import add_hotkey maybe will add later

app = ctk.CTk()
app.geometry("498x450")
app.title("HPSolver")
app.iconbitmap(r'C:\Users\ozo\Documents\vs code stuff\eut lol\GUI Puzzle\M.ico')

tabview = ctk.CTkTabview(app)
tabview.pack(pady=14, padx=20, expand=True, fill="both")

tabs = [
    "Puzzle #1/#2",
    "Puzzle #3",
    "Puzzle #4"
]
custom_limits = {
    "Puzzle #1/#2": 3,
    "Puzzle #3": 4,
    "Puzzle #4": 11
}
entries_dict = {}
labels_dict = {}

def darken(widget, factor=0.8): # basically custom hover function for frames
    initial_color = widget.cget("fg_color").lstrip('#')
    rgb = tuple(int(initial_color[i:i+2], 16) for i in (0, 2, 4))
    darken_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
    darken_color = '{:02x}{:02x}{:02x}'.format(*darken_rgb)
    def on_enter(event):
        widget.configure(fg_color=f"#{darken_color}")
    def on_leave(event):
        widget.configure(fg_color=f"#{initial_color}")

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def titlebarify(widget, window, darkening=False):
    if darkening:
        darken(widget)

    def start_move(event):
        window._offset_x = event.x
        window._offset_y = event.y

    def do_move(event):
        new_x = event.x_root - window._offset_x
        new_y = event.y_root - window._offset_y
        window.geometry(f"+{new_x}+{new_y}")

    widget.bind("<ButtonPress-1>", start_move)
    widget.bind("<B1-Motion>", do_move)

info_window = None
def open_info():
    try:
        global info_window
        if info_window is not None and info_window.winfo_exists():
            info_window.lift()
            info_window.focus_force()
            return

        info_window = ctk.CTkToplevel(app)
        info_window.geometry("350x400")
        info_window.overrideredirect(True)
        info_window.wm_attributes("-transparentcolor", "#242424")
        info_window.after(10, lambda: info_window.focus_force())

        mainframe = ctk.CTkFrame(info_window, width=350, height=400, corner_radius=10)
        mainframe.pack(fill='both')

        titlebar = ctk.CTkFrame(mainframe, height=25, fg_color='#1f6aa5', corner_radius=5)
        titlebar.pack_propagate(False)
        titlebar.pack(fill='x', pady=(5, 0), padx=5)
        titlebarify(titlebar, info_window, True)

        close = ctk.CTkButton(titlebar,
                              height=20,
                              width=15,
                              corner_radius=5,
                              fg_color='#002037',
                              text='Close',
                              font=("", 10),
                              command=info_window.destroy)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar, height=20, width=15, corner_radius=5, fg_color='#002037', text='Pin', font=("", 10), command=lambda: pin_window(info_window, pin))
        pin.pack(side='left', padx=2)

        labelinfo = ctk.CTkLabel(mainframe, 
            text='Version 1.3', 
            font=("", 20, 'bold'),
            anchor="center",
            width=280,
        )
        labelinfo.pack()

        label = ctk.CTkLabel(mainframe, 
            text=(
"""
Key Binds:
"Tab" = Go to next entry window
"Shift+Tab" = Go to previous entry window
"R" = Reset (Clear entries on current puzzle)
"Enter" = Enter (Find order)
"[" = Previous (Go to previous puzzle)
"]" = Next (Go to next puzzle)
"F1" = Click through the order window toggle
(Make sure to be focused on the correct window
for keybinds to work properly)
            
Puzzle #4 entries take all 3 RGB values of one color
separated by either "t" or "-" (both can be used)
Puzzle #1/#2 works universally for ingame ones

Made by ozomega
Discord: @m6ga
"""
            ), 
            font=("", 15),
            justify="left",
            width=280
        )
        label.pack(padx=5, pady=(0,2))
    except Exception as e:
        sys.__stdout__.write(f"Error processing open_info: {e}\n")


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
        console_window.overrideredirect(True)
        console_window.wm_attributes("-transparentcolor", "#242424")
        console_window.after(10, lambda: console_window.focus_force())

        mainframe = ctk.CTkFrame(console_window, width=500, height=300, corner_radius=10)
        mainframe.pack_propagate(False)
        mainframe.pack(fill='both')

        titlebar = ctk.CTkFrame(mainframe, height=25, fg_color='#1f6aa5', corner_radius=5)
        titlebar.pack_propagate(False)
        titlebar.pack(fill='x', pady=5, padx=5)
        titlebarify(titlebar, console_window, True)

        close = ctk.CTkButton(titlebar, height=20, width=15, corner_radius=5, fg_color='#002037', text='Close', font=("", 10), command=console_window.destroy)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar, height=20, width=15, corner_radius=5, fg_color='#002037', text='Pin', font=("", 10), command=lambda: pin_window(console_window, pin))
        pin.pack(side='left', padx=2)

        console_text = ctk.CTkTextbox(mainframe, wrap="word", height=250)
        console_text.pack(pady=(0,10), padx=10, fill="both", expand=True)

        app.after(100, setup_redirection)

    except Exception as e:
        sys.__stdout__.write(f"Error processing open_console: {e}\n")

def change_transparency(value):
    try:
        order_window.attributes("-alpha", float(value))
    except Exception as e:
        print(f"Error processing change_transparency: {e}")

clickthrough = False
clickthroughlabel = None
def toggle_clickthrough(event=None):
    try:
        global clickthrough, clickthroughlabel 
        hwnd = windll.user32.GetForegroundWindow()
        style = windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20

        if clickthrough:
            windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000020)  # WS_EX_TRANSPARENT
            if clickthroughlabel:
                clickthroughlabel.configure(text="Clickthrough enabled", text_color='#c4ffa8')
        else:
            windll.user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)  # WS_EX_TRANSPARENT removed
            if clickthroughlabel:
                clickthroughlabel.configure(text="Clickthrough disabled", text_color='#ffa8a8')

        clickthrough = not clickthrough
    except Exception as e:
        print(f"Error processing toggle_clickthrough: {e}")

order_window = None
def open_order():
    try:
        global order_window, clickthroughlabel, labels_dict

        if order_window is not None and order_window.winfo_exists():
            order_window.lift()
            order_window.focus_force()
            return

        order_window = ctk.CTkToplevel(app)
        order_window.geometry("262x340")
        order_window.overrideredirect(True)
        order_window.wm_attributes("-transparentcolor", "#242424")
        order_window.after(10, lambda: order_window.focus_force())

        mainframe = ctk.CTkFrame(order_window, width=262, height=340, corner_radius=10)
        mainframe.pack_propagate(False)
        mainframe.pack(fill='both')

        titlebar = ctk.CTkFrame(mainframe, height=25, fg_color='#1f6aa5', corner_radius=5)
        titlebar.pack_propagate(False)
        titlebar.pack(fill='x', pady=5, padx=5)
        titlebarify(titlebar, order_window, True)

        close = ctk.CTkButton(titlebar, height=20, width=15, corner_radius=5, fg_color='#002037', text='Close', font=("", 10), command=order_window.destroy)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar, height=20, width=15, corner_radius=5, fg_color='#002037', text='Pin', font=("", 10), command=lambda: pin_window(order_window, pin))
        pin.pack(side='left', padx=2)

        frame = ctk.CTkFrame(mainframe)
        frame.pack()

        grid = ctk.CTkFrame(frame)
        grid.pack()

        labels_dict["order"] = []
        for i in range(5):
            row_labels = []
            for j in range(5):
                label = ctk.CTkLabel(grid, width=50, height=50, justify="center", text="", fg_color="#025c9d", font=("", 16, "bold"))
                label.grid(row=i, column=j, padx=1, pady=1)
                row_labels.append(label)
            labels_dict["order"].append(row_labels)

        transparency_slider = ctk.CTkSlider(mainframe, from_=0.1, to=1, number_of_steps=10, state="normal", width=200, height=5, command=change_transparency)
        transparency_slider.set(1)
        transparency_slider.pack(pady=(10, 5))

        clickthroughlabel = ctk.CTkLabel(mainframe, text="Clickthrough disabled", text_color='#ffa8a8')
        clickthroughlabel.pack()

    except Exception as e:
        sys.__stdout__.write(f"Error processing open_order: {e}\n")

def pin_window(window, button):
    try:
        current_topmost = window.attributes('-topmost')
        window.attributes('-topmost', not current_topmost)
        button.configure(text="Unpin" if not current_topmost else "Pin")
    except Exception as e:
        print(f"Error processing pin_window: {e}")

def parse_entries_puzzle1_2():
    try:
        tab = tabview.get()
        values = [entry.get() if entry.get() else '0' for row in entries_dict[tab] for entry in row]
        print(f"Puzzle #1/#2 Entries:", values)
        
        replace = str.maketrans("!@#$%^&*()", "1234567890")
        values = [int(num.translate(replace)) for num in values]
        print(f"Puzzle #2 Converted:", values)

        non_zero_values = [value for value in values if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Puzzle #1/#2 Order:", ordered_values)

        if "order" in labels_dict:
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels_dict["order"][i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #1/#2: {e}")


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

        if "order" in labels_dict:
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels_dict["order"][i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
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

        if "order" in labels_dict:
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels_dict["order"][i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
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
        if tab == "Puzzle #1/#2":
            parse_entries_puzzle1_2()
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

# keybinds
app.bind_all('<F1>', toggle_clickthrough)
app.bind('<Return>', output_order)
app.bind('[', prev_puzzle)
app.bind(']', next_puzzle)
app.bind('r', reset_entries)

for tabname in tabs:
    tab = tabview.add(tabname)

    frame = ctk.CTkFrame(tab)
    frame.pack(padx=10, pady=10)

    grid1 = ctk.CTkFrame(frame)
    grid2 = ctk.CTkFrame(frame)
    grid1.pack(side="top",anchor='center')
    grid2.pack(side="bottom", pady=10,anchor='center')

    grid2.configure(fg_color='transparent')

    entries = []
    n = 45 if tabname != "Puzzle #4" else 85
    for i in range(5):
        row_entries = []
        max_length = custom_limits[tabname]
        validate_cmd = app.register(lambda text, length, tab=tabname: limit_input(text, length, tab))
        for j in range(5):
            entry = ctk.CTkEntry(
                grid1,
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
        
    entries_dict[tabname] = entries

    inputlabel = ctk.CTkLabel(grid1, width=100, text="Input", font=("", 20))
    inputlabel.grid(row=0, column=0, columnspan=5, pady=10)

    if tabname == "Puzzle #1/#2":
        enterbutton = ctk.CTkButton(grid2, width=100, text="Enter", command=parse_entries_puzzle1_2, font=("", 20))
    elif tabname == "Puzzle #3":
        enterbutton = ctk.CTkButton(grid2, width=100, text="Enter", command=parse_entries_puzzle3, font=("", 20))
    else:
        enterbutton = ctk.CTkButton(grid2, width=100, text="Enter", command=parse_entries_puzzle4, font=("", 20))
    enterbutton.grid(row=0, column=1, padx=5)

    resetbutton = ctk.CTkButton(grid2, width=100, text='Reset', command=reset_entries, font=("", 20))
    resetbutton.grid(row=0, column=0, padx=5)

app.after(10, lambda: set_initial_focus())

info_button = ctk.CTkButton(app, text="?", command=open_info, width=20, height=20, font=("", 15))
info_button.place(x=5, y=5)

pin_button = ctk.CTkButton(app, text="Pin", command=lambda: pin_window(app, pin_button), width=40, height=20, font=("", 15))
pin_button.place(x=30, y=5)

console_button = ctk.CTkButton(app, text="Console", command=open_console, width=80, height=20, font=("", 15), bg_color='#2b2b2b')
console_button.place(x=30, y=403)

order = ctk.CTkButton(app, text="Order", width=20, height=20, font=("",15), bg_color='#2b2b2b', command=open_order)
order.place(x=416, y=403)

app.mainloop()

# for .exe compiling use following 2 commands, make sure to replace M.ico path in the line "app.iconbitmap(r'C:\Users\ozo\Documents\vs code stuff\eut lol\GUI Puzzle\M.ico')" to yours, it must be full path as it wont work otherwise.
# pip install pyinstaller
# pyinstaller --onefile --icon=M.ico --add-data="M.ico;." --clean --noconsole HPSolver.py