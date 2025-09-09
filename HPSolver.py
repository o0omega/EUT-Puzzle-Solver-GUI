Version = "1.6"
InfoText = """\
Any app's window must be in focus 
for settings to function.

For Puzzle #2 you can input numbers right away.
For Puzzle #3 you can seperate the number and
the base (the other number in ()) with a space
or a t, so, for example, "100110 (2)" (in game)
will be "100110 2" or "100110t2" in your input.
For Puzzle #4 some questions are labeled as "evil"
by the creator of the puzzle, so you can input their
answers right away.

Made by ozo (Discord @m6ga)
Contributed by ltrc125 (@cat.0400)
DM any bugs or suggestions, a forum post for the
app can be found on EUT discord.\
"""
Evil_Solutions = """\
"Asap" question's answer is 1
"33 + 77" is 100
The not not not not question is 1
The bottom blue hint is the number in the end + 1
The bottom red hint is the number in the end - 1
The "1 + 1" is 11
Answers can be input right away, but solving is
also implemented

Puzzle #4 syntax shortcuts
c = math.ceil
f = math.floor
r = math.round
p = π (or just 3.14)
"""


import customtkinter as ctk
import tkinter as tk
import sys, os
from ctypes import windll
from PIL import Image
import pywinstyles as pws
import math
import sympy as sp
from re import sub
import json
import webbrowser


# required for proper images compiling
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# top window pinning utility
def pin_window(window, button):
    try:
        current_topmost = window.attributes('-topmost')
        window.attributes('-topmost', not current_topmost)
        button.configure(text="Unpin" if not current_topmost else "Pin")
    except Exception as e:
        print(f"Error processing pin_window: {e}")

# allows for darkening any colour, mainly applied to widgets upon hovering as feedback
def darken(widget, factor=0.8, bool=True):
    if bool:
        def on_enter(event):
            widget.configure(fg_color=f"#{darken_color}")

        def on_leave(event):
            widget.configure(fg_color=f"#{initial_color}")

    initial_color = widget.cget("fg_color").lstrip('#')
    rgb = tuple(int(initial_color[i:i + 2], 16) for i in (0, 2, 4))
    darken_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
    darken_color = '{:02x}{:02x}{:02x}'.format(*darken_rgb)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    return darken_color

# custom titlebar for subwindows
def titlebarify(widget, window, darkening=False):
    initial_color = widget.cget("fg_color")
    darken_color = darken(widget)

    def start_move(event):
        window._offset_x = event.x_root - window.winfo_rootx()
        window._offset_y = event.y_root - window.winfo_rooty()
        widget.configure(fg_color=f"#{darken_color}")

    def do_move(event):
        new_x = event.x_root - window._offset_x
        new_y = event.y_root - window._offset_y
        window.geometry(f"+{new_x}+{new_y}")

    def stop_move(event):
        widget.configure(fg_color=initial_color)

    widget.bind("<Button-1>", start_move)
    widget.bind("<B1-Motion>", do_move)
    widget.bind("<ButtonRelease-1>", stop_move)

# Save config to a JSON file
def save_settings():
    try:
        data = {
            "solve": settings[hatch_puzzle],
            "clear": settings[clear_entries],
            "playback": settings[order_playback],
            "cooldown": int(settings[order_cooldown]),
        }
        with open("settings.json", "w") as f:
            json.dump(data, f)
        print("Config saved.")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_settings():
    if not os.path.exists("settings.json"):
        return
    try:
        with open("settings.json", "r") as f:
            data = json.load(f)
        
        # Solve
        old_solve = settings[hatch_puzzle]
        new_solve = data.get("solve", old_solve)
        if new_solve != old_solve and new_solve != '??':
            app.unbind_all(old_solve)
            settings[hatch_puzzle] = new_solve
            app.bind_all(f"<{new_solve}>", hatch_puzzle)
        
        # Clear
        old_clear = settings[clear_entries]
        new_clear = data.get("clear", old_clear)
        if new_clear != old_clear and new_solve != '??':
            app.unbind_all(old_clear)
            settings[clear_entries] = new_clear
            app.bind_all(f"<{new_clear}>", clear_entries)
        
        # Order playback
        old_playback = settings[order_playback]
        new_playback = data.get("playback", old_playback)
        if new_playback != old_playback and new_solve != '??':
            app.unbind_all(old_playback)
            settings[order_playback] = new_playback
            app.bind_all(f"<{new_playback}>", order_playback)

        # Order cooldown
        old_cooldown = settings[order_cooldown]
        new_cooldown = data.get("cooldown", old_cooldown)
        if new_cooldown != old_cooldown:
            settings[order_cooldown] = int(new_cooldown)
    
    except Exception as e:
        print(f"Error loading settings: {e}")

def create_subwindow(geometry=""):
    window = ctk.CTkToplevel(app)
    window.attributes("-toolwindow", True)
    window.attributes('-topmost', True)
    window.overrideredirect(True)
    window.wm_attributes("-transparentcolor", "#1a1a1a")
    window.after(10, lambda: window.focus_force())
    if geometry:
        window.geometry(geometry)

    mainframe = ctk.CTkFrame(window, corner_radius=10)
    mainframe.pack()

    titlebar = ctk.CTkFrame(mainframe,
                            height=25,
                            fg_color='#1f6aa5',
                            corner_radius=5)
    titlebar.pack_propagate(False)
    titlebar.pack(fill='x', pady=(5, 0), padx=5)
    titlebarify(titlebar, window, True)

    close = ctk.CTkButton(titlebar,
                          height=20,
                          width=15,
                          corner_radius=5,
                          fg_color='#002037',
                          text='Close',
                          font=("", 10),
                          command=window.withdraw)
    close.pack(side='right', padx=2)

    return window, mainframe, titlebar

settings_window = None
def open_settings():
    try:
        global settings_window, settings

        def hatch_bind(button, function):
            blacklist = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#', '$', '%', '^', '&', '*', '(',
                        ')', '-', '+', '.', ',', '/', 'm', 'a', 't', 'h', 'r', 'o', 'u', 'n', 'd', 'c', 'e', 'i', 'l', 'f', 's', 'p', "Tab", "Escape"]
            button.configure(text="Press a Key", fg_color='#144870')

            def on_key_press(event):
                if not event.keysym.isascii():
                    print("Invalid keybind: Non-ASCII key detected.")
                    return

                key = event.keysym
                # Normalizing
                key = key.upper() if key.lower() in [f'f{i}' for i in range(1, 13)] else key
                if key in blacklist:
                    print(f"Invalid keybind: {key}.\nFollowing keys are reserved:\n{blacklist}.")
                    return

                button.configure(text=key, fg_color='#1f6aa5')
                
                old_key = settings.get(function)
                if old_key:
                    try:
                        app.unbind_all(f"<{old_key}>")
                        app.unbind_all(f"<Key-{old_key}>")  # Try alternative form
                        app.unbind_all(old_key)  # Try raw keysym
                    except Exception as e:
                        print(f"Error unbinding old key {old_key}: {e}")
                
                # Update settings and bind new key
                settings[function] = key
                app.bind_all(f"<{key}>", function)
                print(f"{function.__name__} keybind changed to:", key)

                settings_window.unbind("<Any-KeyPress>")

            settings_window.bind("<Any-KeyPress>", on_key_press)
            settings_window.focus_force()

        def update_cooldown(event):
            try:
                new_value = event.widget.get().strip()
                if new_value.isdigit() and int(new_value) > 0:
                    settings[order_cooldown] = int(new_value)
                    print(f"Cooldown updated to: {settings[order_cooldown]}ms")
                    save_settings()
                else:
                    print("Invalid cooldown: Must be a positive integer.")
                    event.widget.delete(0, "end")
                    event.widget.insert(0, str(settings[order_cooldown]))
            except Exception as e:
                print(f"Error updating cooldown: {e}")
                event.widget.delete(0, "end")
                event.widget.insert(0, str(settings[order_cooldown]))

        if settings_window is not None and settings_window.winfo_exists():
            settings_window.lift()
            settings_window.focus_force()
            return

        window, mainframe, titlebar = create_subwindow(geometry=f"+{screen_w - 225}+{screen_h//10}")

        grid = ctk.CTkFrame(mainframe, corner_radius=5)
        grid.pack(pady=5, padx=5)
        grid.columnconfigure(1, weight=1)
        SettingsLabel = ctk.CTkLabel(grid,
                                     text="Settings",
                                     font=("", 20, "bold"))
        SettingsLabel.grid(row=0, columnspan=2)
        Solve = ctk.CTkLabel(grid,
                             text="Solve:",
                             font=("", 15))
        Solve.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        SolveBind = ctk.CTkButton(grid,
                                  width=90,
                                  height=30,
                                  border_width=1,
                                  corner_radius=2,
                                  text=settings[hatch_puzzle],
                                  font=("", 15, 'bold'), command=lambda: hatch_bind(SolveBind, hatch_puzzle))
        SolveBind.grid(row=1, column=1, pady=5, padx=5)

        Clear = ctk.CTkLabel(grid,
                             text="Clear:",
                             font=("", 15))
        Clear.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        ClearBind = ctk.CTkButton(grid,
                                  width=90,
                                  height=30,
                                  border_width=1,
                                  corner_radius=2,
                                  text=settings[clear_entries],
                                  font=("", 15, 'bold'),
                                  command=lambda: hatch_bind(ClearBind, clear_entries))
        ClearBind.grid(row=2, column=1, pady=5, padx=5)

        Playback = ctk.CTkLabel(grid,
                                text="Order Playback:",
                                font=("", 15))
        Playback.grid(row=3, column=0, pady=5, padx=5, sticky="w")
        PlaybackBind = ctk.CTkButton(grid,
                                     width=90,
                                     height=30,
                                     border_width=1,
                                     corner_radius=2,
                                     text=settings[order_playback],
                                     font=("", 15, 'bold'),
                                     command=lambda: hatch_bind(PlaybackBind, order_playback))
        PlaybackBind.grid(row=3, column=1, pady=5, padx=5)

        Cooldown = ctk.CTkLabel(grid,
                                text="Cooldown (ms):",
                                font=("", 15))
        Cooldown.grid(row=4, column=0, pady=5, padx=5, sticky="w")
        CooldownValue = ctk.CTkEntry(grid,
                                     justify="center",
                                     width=90,
                                     height=30,
                                     border_width=1,
                                     corner_radius=2,
                                     font=("", 15, 'bold'))
        CooldownValue.insert(0, str(settings[order_cooldown]))
        CooldownValue.grid(row=4, column=1, pady=5, padx=5)
        CooldownValue.bind("<FocusOut>", update_cooldown)

        TabLabel = ctk.CTkLabel(grid,
                                text="Focus Next Entry = Tab\nPrevious Entry = Shift+Tab",
                                font=("", 15))
        TabLabel.grid(row=5, column=0, columnspan=2, pady=5)

        window.withdraw()
        settings_window = window

    except Exception as e:
        print(f"Error processing open_settings: {e}\n")

info_window = None
def open_info():
    try:
        global info_window
        if info_window is not None and info_window.winfo_exists():
            info_window.lift()
            info_window.focus_force()
            return

        window, mainframe, titlebar = create_subwindow("+0+0")

        versionlabel = ctk.CTkLabel(mainframe,
                                    anchor="center",
                                    width=280,
                                    text=f"Version {Version}",
                                    font=("", 20, 'bold'))
        versionlabel.pack()

        label = ctk.CTkLabel(mainframe,
                             text=InfoText,
                             font=("", 15),
                             justify="left")
        label.pack(padx=5)
        DiscordLabel = ctk.CTkLabel(mainframe,
                             text="Everything Upgrade Tree Discord",
                             font=("", 18, "bold"),
                             anchor="center",
                             text_color="#48a7ff",
                             cursor="hand2")
        DiscordLabel.pack(padx=5, pady=(0, 2))
        DiscordLabel.bind("<Enter>", lambda e: DiscordLabel.configure(font=("", 18, "underline")))
        DiscordLabel.bind("<Leave>", lambda e: DiscordLabel.configure(font=("", 18, "bold")))
        DiscordLabel.bind("<Button-1>", lambda e: (webbrowser.open("https://discord.gg/eut"), app.iconify()))

        window.withdraw()
        info_window = window

    except Exception as e:
        print(f"Error processing open_info: {e}\n")

evil_solutions_windows = None
def open_evil_solutions():
    try:
        global evil_solutions_windows
        if evil_solutions_windows is not None and evil_solutions_windows.winfo_exists():
            evil_solutions_windows.lift()
            evil_solutions_windows.focus_force()
            return

        window, mainframe, titlebar = create_subwindow(f"+0+{screen_h//3}")

        evillabel = ctk.CTkLabel(mainframe,
                                 width=100,
                                 text="Evil Solutions",
                                 text_color="#ff0000",
                                 font=("", 20))
        evillabel.pack()

        label = ctk.CTkLabel(mainframe,
                             text=Evil_Solutions,
                             font=("", 15),
                             justify="left",
                             width=280)
        label.pack(padx=5)

        window.withdraw()
        evil_solutions_windows = window

    except Exception as e:
        print(f"Error processing open_evil_solutions: {e}\n")

class ConsoleWindow:
    def __init__(self, master):
        self.master = master
        self.window = None
        self.console_text = None
        self.master.after(200, self.setup)

    def setup(self):
        self.setup_ui()
        self.setup_redirection()
        self.write_console("Console initialized.\n")

    def setup_ui(self):
        try:
            if self.window is not None and self.window.winfo_exists():
                self.window.lift()
                self.window.focus_force()
                return
            
            self.window = ctk.CTkToplevel(self.master)
            self.window.attributes("-toolwindow", True)
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)
            self.window.geometry(f"+{screen_w-550}+{screen_h-670}")
            mainframe = ctk.CTkFrame(self.window,
                                    corner_radius=10,
                                    fg_color="#1a1a1a",
                                    width=550,
                                    height=300)
            mainframe.pack_propagate(False)
            mainframe.pack(fill='both')


            freedom_dive = ctk.CTkImage(light_image=Image.open(resource_path("images/freedomdive.png")),
                                        size=(550, 300))
            freedom_image = ctk.CTkLabel(mainframe,
                                         text="",
                                         image=freedom_dive)
            freedom_image.place(relx=0, rely=0, relwidth=1, relheight=1)

            titlebar = ctk.CTkFrame(mainframe,
                                    height=25,
                                    fg_color='#1f6aa5',
                                    corner_radius=5,
                                    background_corner_colors=('#97aabf', '#0d1121', '#465b2f', '#64975f'))
            titlebar.pack_propagate(False)
            titlebar.pack(fill='x', pady=5, padx=5)
            titlebarify(titlebar, self.window, True)
            titlebar.grid_columnconfigure(1, weight=1)

            clear = ctk.CTkButton(titlebar,
                                  height=20,
                                  width=30,
                                  corner_radius=5,
                                  fg_color='#002037',
                                  text='Clear',
                                  font=("", 10),
                                  command=self.clear_console)
            clear.grid(column=0, row=0, padx=2, pady=2, sticky='w')

            copy_button = ctk.CTkButton(titlebar,
                                        height=20,
                                        width=30,
                                        corner_radius=5,
                                        fg_color='#002037',
                                        text='Copy',
                                        font=("", 10),
                                        command=self.copy_console)
            copy_button.grid(column=1, row=0)

            close = ctk.CTkButton(titlebar,
                                  height=20,
                                  width=15,
                                  corner_radius=5,
                                  fg_color='#002037',
                                  text='Close',
                                  font=("", 10),
                                  command=self.window.withdraw)
            close.grid(column=2, row=0, padx=2, sticky='e')

            text_frame = ctk.CTkFrame(mainframe,
                                      fg_color="#1a1a1a")
            pws.set_opacity(text_frame, value=0.9)
            text_frame.pack(pady=(0, 5), padx=5, fill='both', expand=True)
            #tk.text required for errors colormapping
            self.console_text = tk.Text(text_frame,
                                        wrap="word",
                                        height=15,
                                        width=60,
                                        bg="#000000",
                                        fg="#ffffff",
                                        insertbackground="#ffffff",
                                        font=("Calibri", 10, ""),
                                        bd=0,
                                        relief="flat")
            self.console_text.pack(fill='both', expand=True)
            # error text
            self.console_text.tag_configure("error", foreground="#ff5959")
            self.console_text.config(state='disabled')

            self.window.withdraw()

        except Exception as e:
            with open("console_error.log", "a") as f:
                f.write(f"Error setting up console UI: {e}\n")

    class NullOutput:
        def write(self, text):
            pass

        def flush(self):
            pass

    def setup_redirection(self):
        try:
            if sys.stdout is None:
                sys.stdout = self.NullOutput()
            if sys.stderr is None:
                sys.stderr = self.NullOutput()

            sys.stdout.write = self.write_console
            sys.stderr.write = self.write_console
        except Exception as e:
            with open("console_error.log", "a") as f:
                f.write(f"Error setting up redirection: {e}\n")

    def write_console(self, text):
        try:
            if self.console_text is not None:
                self.console_text.config(state='normal')
                # Apply red color to error messages
                tag = "error" if "Error" in text else None
                self.console_text.insert("end", text, tag)
                self.console_text.see("end")
                self.console_text.config(state='disabled')
                self.console_text.update()

            with open("output.log", "a") as f:
                f.write(f"{text}")
        except Exception as e:
            with open("console_error.log", "a") as f:
                f.write(f"Error in write_console: {e}\n")

    def clear_console(self):
        try:
            if self.console_text is not None:
                self.console_text.config(state='normal')
                self.console_text.delete("1.0", "end")
                self.console_text.config(state='disabled')
        except Exception as e:
            self.write_console(f"Error processing clear_console: {e}\n")

    def copy_console(self):
        try:
            if self.console_text is not None:
                text = self.console_text.get("1.0", "end-1c")
                app.clipboard_clear()
                app.clipboard_append(text)
        except Exception as e:
            self.write_console(f"Error processing copy_console: {e}\n")

    def toggle(self):
        if self.window is not None and self.window.winfo_exists():
            if self.window.state() == 'withdrawn':
                self.window.deiconify()
                self.window.lift()
            else:
                self.window.withdraw()

# change transparency of a window
def change_transparency(value, window):
    try:
        window.attributes("-alpha", float(value))
    except Exception as e:
        print(f"Error processing change_transparency: {e}")


clickthroughlabel = None
playback_live = False

def order_playback(event=None, cooldown=None):
    global clickthroughlabel, playback_live, hwnd
    after_id = None

    try:
        if order_window is None or not order_window.winfo_exists() or order_window.state() == 'withdrawn':
            print("Order window is not open. Open the Order window to enable playback.")
            return

        if order is None or not order:
            print("No order available. Solve a puzzle first.")
            return

        if not playback_live:
            playback_live = True
            order_window.lift()
            order_window.focus_force()
            order_window.update_idletasks()

            if cooldown is None:
                cooldown = settings[order_cooldown]

            # Enable clickthrough
            hwnd = windll.user32.GetForegroundWindow() # declare only once here!!!!!
            style = windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20
            windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000020)  # WS_EX_TRANSPARENT
            clickthroughlabel.configure(text="Clickthrough Enabled", text_color="#50ff6d")

            label_order = []
            for i in range(5):
                for j in range(5):
                    text = labels[i][j].cget("text")
                    if text and text.isdigit() and int(text) in order.values():
                        label_order.append((int(text), labels[i][j]))
            label_order.sort(key=lambda x: x[0])

            def highlight_sequence(idx):
                global playback_live
                nonlocal after_id, label_order, cooldown
                if not playback_live:
                    return
                if idx >= len(label_order):
                    style = windll.user32.GetWindowLongW(hwnd, -20)
                    windll.user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)  # Remove WS_EX_TRANSPARENT
                    clickthroughlabel.configure(text="Clickthrough Disabled", text_color='#ffa8a8')
                    windll.user32.UpdateWindow(hwnd)
                    playback_live = False
                    after_id = None
                    print("Playback completed.")
                    return

                order_num, label = label_order[idx]
                original_color = label.cget("fg_color")
                label.configure(fg_color="#cc00ff")

                def unhighlight_and_next():
                    nonlocal after_id
                    label.configure(fg_color=original_color)
                    highlight_sequence(idx + 1)

                after_id = app.after(cooldown, unhighlight_and_next)

            highlight_sequence(0)
            print(f"Playback started for {len(label_order)} labels with cooldown of {cooldown}ms")
        else:
            playback_live = False
            if after_id is not None:
                app.after_cancel(after_id)
                after_id = None

            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(fg_color="#025c9d")

            style = windll.user32.GetWindowLongW(hwnd, -20)
            windll.user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)  # Remove WS_EX_TRANSPARENT
            clickthroughlabel.configure(text="Clickthrough Disabled", text_color='#ffa8a8')
            windll.user32.UpdateWindow(hwnd)
            print("Playback stopped.")

    except Exception as e:
        print(f"Error processing order_playback: {e}")



labels = []
order_window = None
def open_order():
    try:
        global order_window, clickthroughlabel, labels

        if order_window is not None and order_window.winfo_exists():
            order_window.lift()
            order_window.focus_force()
            return

        window, mainframe, titlebar = create_subwindow(f"+{screen_w//3+130}+{screen_h//40}")

        frame = ctk.CTkFrame(mainframe, fg_color='transparent')
        frame.pack(padx=5, pady=5)

        grid = ctk.CTkFrame(frame)
        grid.pack()
        for i in range(5):
            row_labels = []
            for j in range(5):
                label = ctk.CTkLabel(grid,
                                     width=72,
                                     height=72,
                                     justify="center",
                                     text="",
                                     fg_color="#025c9d",
                                     font=("", 16, "bold"))
                label.grid(row=i, column=j, padx=1, pady=1, sticky='nsew')
                row_labels.append(label)
            labels.append(row_labels)

        transparency_slider = ctk.CTkSlider(mainframe,
                                            width=200,
                                            height=5,
                                            from_=0.1,
                                            to=1,
                                            number_of_steps=10,
                                            command=lambda value: change_transparency(value, window))
        window.attributes("-alpha", 0.73)
        transparency_slider.set(0.7)
        transparency_slider.pack(pady=(10, 5))

        clickthroughlabel = ctk.CTkLabel(mainframe, text="Clickthrough disabled", text_color='#ffa8a8')
        clickthroughlabel.pack(pady=(0, 10))

        resize_button = ctk.CTkButton(mainframe,
                                      width=20,
                                      height=20,
                                      text=">",
                                      font=("", 12, "bold"),
                                      fg_color="#006ec9",
                                      hover_color="#0080ff",
                                      text_color="#ffffff",
                                      corner_radius=2,
                                      cursor="size_nw_se")
        resize_button.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)

        # Resize event bindings
        def start_resize(event):
            window.resizeStartX = event.x_root
            window.resizeStartY = event.y_root
            window.startWidth = window.winfo_width()
            window.startHeight = window.winfo_height()

        def stop_resize(event):
            delta_x = event.x_root - window.resizeStartX
            new_w = max(200, window.startWidth + delta_x)
            new_h = max(350, new_w + 90)
            window.geometry(f"{int(new_w)}x{int(new_h)}")
            mainframe.configure(width=int(new_w), height=int(new_h))
            cell_size = (new_w - 20) // 5
            for row in labels:
                for label in row:
                    label.configure(width=cell_size,
                                    height=cell_size,
                                    font=("", max(12, cell_size // 4), "bold"))

        resize_button.bind("<Button-1>", start_resize)
        resize_button.bind("<ButtonRelease-1>", stop_resize)

        window.withdraw()
        order_window = window

    except Exception as e:
        print(f"Error processing open_order: {e}\n")

puzzle4_labels = []
puzzle4_window = None
def open_puzzle4():
    try:
        global puzzle4_window, puzzle4_labels

        if puzzle4_window is not None and puzzle4_window.winfo_exists():
            puzzle4_window.lift()
            puzzle4_window.focus_force()
            return

        window, mainframe, titlebar = create_subwindow(f"+{screen_w//3}+{screen_h//2.1}")

        frame = ctk.CTkFrame(mainframe, fg_color='transparent')
        frame.pack()

        grid = ctk.CTkFrame(frame)
        grid.pack(padx=5, pady=5)

        for i in range(5):
            puzzle4_row_labels = []
            for j in range(5):
                label = ctk.CTkLabel(grid,
                                     width=100,
                                     height=30,
                                     justify="center",
                                     text="",
                                     fg_color="#025c9d",
                                     font=("", 16, "bold"),
                                     cursor="hand2")
                label.grid(row=i, column=j, padx=1, pady=1)
                label.bind("<Button-1>", copy_to_clipboard)
                darken(label, factor=0.8, bool=True)
                label._label.place(relwidth=1, relheight=1, relx=0, rely=0, anchor="nw")
                
                puzzle4_row_labels.append(label)
            puzzle4_labels.append(puzzle4_row_labels)

        window.withdraw()
        puzzle4_window = window

    except Exception as e:
        print(f"Error processing open_puzzle4: {e}\n")

def toggle_window(window):
    if window is not None and window.winfo_exists():
        if window.state() == 'withdrawn':
            window.deiconify()
            window.lift()
            window.focus_force()
        else:
            window.withdraw()

# window labels copying for puzzle 4
def copy_to_clipboard(event):
    label_text = event.widget.master.cget("text")
    app.clipboard_clear()
    app.clipboard_append(label_text)

# reset entry borders to default color
def reset_entry_borders():
    for i in range(5):
        for j in range(5):
            entries[i][j].configure(border_color="#acacac")

# calculate cell number for error reporting
def get_cell_number(i, j):
    return i * 5 + j + 1

def hatch_puzzle(event=None):
    try:
        reset_entry_borders()
        values = []
        checkstop = False
        puzzle = 124
        error_detected = False

        for i in range(5):
            for j in range(5):
                data = str(entries[i][j].get()).strip()
                values.append(data)
                if not checkstop:
                    if " " in data or "t" in data:
                        puzzle = 3
                        checkstop = True
                    elif '+' in data or len(data) > 3:
                        puzzle = 4
                        checkstop = True

        print(f"Entries: {values}")

        if puzzle == 4:
            print(f"Detected Puzzle #4 Answers")
            puzzle4(values)
        elif puzzle == 3:
            print(f"Detected Puzzle #3 Order")
            puzzle3(values)
        else:
            print(f"Detected Puzzle #1/#2/#4 Order")
            puzzle1_2(values)

        if error_detected:
            print("Please check highlighted cells for invalid inputs.")

    except Exception as e:
        print(f"Error processing hatch_puzzle: {e}\n")
        for i in range(5):
            for j in range(5):
                entries[i][j].configure(border_color="#ff0000")
        print("All cells highlighted due to general error.")

order = None
def puzzle1_2(values):
    try:
        global order
        replace = str.maketrans("!@#$%^&*()", "1234567890")
        error_detected = False
        for i in range(5):
            for j in range(5):
                num = values[i * 5 + j]
                if num == '':
                    continue
                try:
                    int(num.translate(replace))
                except ValueError as e:
                    print(f"Error in cell {get_cell_number(i, j)}: Invalid number format '{num}'")
                    entries[i][j].configure(border_color="#ff0000")
                    error_detected = True

        values = [int(num.translate(replace)) if num != '' else '' for num in values]
        print(f"Converted: {values}")

        if error_detected:
            return

        non_zero_values = [value for value in values if value != '']
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Order: {ordered_values}\n")

        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #1/#2: {e}")
        for i in range(5):
            for j in range(5):
                if values[i * 5 + j] != '':
                    entries[i][j].configure(border_color="#ff0000")
                    print(f"Error in cell {get_cell_number(i, j)}: Unable to process '{values[i * 5 + j]}'")

def puzzle3(values):
    try:
        global order
        replace = str.maketrans("t", " ")
        error_detected = False
        base10s = []
        for i in range(5):
            for j in range(5):
                num = values[i * 5 + j]
                if num == '':
                    base10s.append(0)
                    continue
                try:
                    num = num.translate(replace).split()
                    if len(num) != 2:
                        raise ValueError("Invalid format: Expected number and base")
                    number, base = num
                    base10s.append(int(str(number), int(base)))
                except ValueError as e:
                    print(f"Error in cell {get_cell_number(i, j)}: Invalid base conversion '{num}' - {str(e)}")
                    entries[i][j].configure(border_color="#ff0000")
                    error_detected = True
                    base10s.append(0)

        print(f"Base 10: {base10s}")

        if error_detected:
            return

        non_zero_values = [value for value in base10s if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in base10s]
        print(f"Order: {ordered_values}\n")

        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #3: {e}")
        for i in range(5):
            for j in range(5):
                if values[i * 5 + j] != '':
                    entries[i][j].configure(border_color="#ff0000")
                    print(f"Error in cell {get_cell_number(i, j)}: Unable to process '{values[i * 5 + j]}'")

# puzzle 4
def luau_round(n, ndigits=0):
    scale = 10 ** ndigits
    n_scaled = n * scale
    result = math.floor(n_scaled + 0.5) if n_scaled >= 0 else math.ceil(n_scaled - 0.5)
    return result / scale if ndigits > 0 else int(result / scale)

# replacing default python round to mimic luau's math.round()
math.round = luau_round

def formula_translation(n):
    replacements = {
        '^': '**',
        'p': '3.14',
        'r(': 'math.round(',
        'f(': 'math.floor(',
        'c(': 'math.ceil(',
        ')(': ')*(',
    }
    for old, new in replacements.items():
        n = n.replace(old, new)
    if '!' in n:
        n = sub(r'(\d+)!', lambda m: f"math.factorial({m.group(1)})", n)
    return n

def type2_equation_solver(equation_string):
    equations = equation_string.split(',')
    symbols = {}
    for eq in equations:
        eq = eq.strip()
        var, expr = eq.split('=')
        var, expr = var.strip(), expr.strip()
        if var not in symbols:
            symbols[var] = sp.symbols(var)
        parsed_expr = sp.sympify(expr, locals=symbols)
        symbols[var] = parsed_expr
    return round({var: expr.evalf() for var, expr in symbols.items()}['x'])

def type1_equation_solver(equation):
    left, right = equation.split('=')
    x = sp.symbols('x')
    left_expr = sp.sympify(left.strip())
    right_expr = sp.sympify(right.strip())
    eq = sp.Eq(left_expr, right_expr)
    solution = sp.solve(eq, x)
    return solution[0]

def puzzle4_solving(form):
    form = formula_translation(form)
    special_formulas = {'Asap': 1, '1+1': 11, '77+33': 100}
    if form in special_formulas.keys():
        return special_formulas[form]
    elif 'Blue' in form:
        res = int(form.split()[-1]) + 1
        return res
    elif 'Red' in form:
        res = int(form.split()[-1]) - 1
        return res
    elif 'not' in form:
        return 0
    if form.count('x') == 1 and 'a' in form:
        return type2_equation_solver(form)
    elif 'x' in form and not 'a' in form:
        return type1_equation_solver(form)
    else:
        return eval(form) if not isinstance(eval(form), list) else eval(form)[0]

def puzzle4(values):
    try:
        global order
        solutions = []
        error_detected = False
        for i in range(5):
            for j in range(5):
                value = values[i * 5 + j]
                if value == '':
                    solutions.append('')
                    continue
                try:
                    solutions.append(puzzle4_solving(value))
                except Exception as e:
                    print(f"Error in cell {get_cell_number(i, j)}: Unable to solve '{value}' - {str(e)}")
                    entries[i][j].configure(border_color="#ff0000")
                    error_detected = True
                    solutions.append('')

        print(f"Answers: {solutions}")

        if error_detected:
            return

        non_empty_solutions = [sol for sol in solutions if sol != '']
        order = {num: i + 1 for i, num in enumerate(sorted(non_empty_solutions))}
        ordered_values = [order.get(sol, 0) if sol != '' else '' for sol in solutions]
        print(f"Order: {ordered_values}\n")
        
        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1
        
        if puzzle4_window is not None and puzzle4_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    puzzle4_labels[i][j].configure(text=str(solutions[label_index]) if solutions[label_index] != '' else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #4: {e}")
        for i in range(5):
            for j in range(5):
                if values[i * 5 + j] != '':
                    entries[i][j].configure(border_color="#ff0000")
                    print(f"Error in cell {get_cell_number(i, j)}: Unable to process '{values[i * 5 + j]}'")

def limit_input(entry_text, max_length):
    try:
        valid_chars = set("qwertyuiopasdfghjklzxcvbnm0123456789!@#$%^&*()-+=,./ ")
        return (len(entry_text) <= int(max_length) and all(char in valid_chars for char in entry_text))
    except Exception as e:
        print(f"Error processing limit_input: {e}")

def clear_entries(event=None):
    try:
        global order, labels, puzzle4_labels
        for i in range(5):
            for j in range(5):
                entries[i][j].delete(0, "end")
                entries[i][j].configure(border_color="#acacac")
                labels[i][j].configure(text="")
                puzzle4_labels[i][j].configure(text="")
        order = None
        print("Inputs Cleared")
    except Exception as e:
        print(f"Error processing clear_entries: {e}")


# adjusting border color for focused entry window
def focus_in(event):
    event.widget.master.configure(border_color="#00D300")

def focus_out(event):
    event.widget.master.configure(border_color="#acacac")


# right bracket auto addition
def bracket_helper(event):
    try:
        entry = event.widget
        pos = entry.index("insert")
        entry.insert(pos, "()")
        entry.icursor(pos + 1)
        return "break"

    except Exception as e:
        print(f"Error processing handle_parenthesis: {e}")


expanded = False
def resize_window(button):
    try:
        global expanded
        current_y = app.winfo_y()
        if not expanded:
            app.geometry(f"{screen_w}x{app_height}+-8+{current_y}")
            button.configure(text="> <")
            expanded = True
        else:
            app.geometry(f"545x{app_height}+{screen_w//2-8-545//2}+{current_y}")
            button.configure(text="< >")
            expanded = False
    except Exception as e:
        print(f"Error processing resize_window: {e}")

# force dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
# app initialization
app = ctk.CTk()
app.resizable(True, False)
app.minsize(545, 0)
app.title("HPSolver")
app.iconbitmap(resource_path(r"images\M.ico"))
icon_path = resource_path(r"images\M.ico")

screen_w = app.winfo_screenwidth()
screen_h = app.winfo_screenheight()

app.grid_columnconfigure(0, weight=1)

frame = ctk.CTkFrame(app, bg_color='#1a1a1a', fg_color="transparent")
frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
frame.grid_columnconfigure(0, weight=1)

grid0 = ctk.CTkFrame(frame, fg_color="transparent")
grid0.grid(row=0, column=0, sticky="ew")
grid0.grid_columnconfigure(4, weight=1)

grid1 = ctk.CTkFrame(frame, fg_color='transparent')
grid1.grid(row=1, column=0, sticky="ew", pady=5)
for j in range(5):
    grid1.columnconfigure(j, weight=1)

grid2 = ctk.CTkFrame(frame, fg_color='transparent')
grid2.grid(row=2, column=0, sticky="ew", pady=5)
grid2.grid_columnconfigure(1, weight=1)

inputlabel = ctk.CTkLabel(grid0,
                          width=100,
                          text="Input",
                          font=("", 18, "bold"))
inputlabel.grid(row=0, column=0, columnspan=6)

pin_button = ctk.CTkButton(grid0,
                           width=40,
                           height=20,
                           text="Pin",
                           font=("", 15, "bold"),
                           command=lambda: pin_window(app, pin_button))
pin_button.grid(row=0, column=0, sticky='w')

settings_icon = ctk.CTkImage(light_image=Image.open(resource_path("images/settings.png")), size=(15, 15))
settings_button = ctk.CTkButton(grid0,
                                width=20,
                                height=20, text="",
                                image=settings_icon,
                                command=lambda: toggle_window(settings_window))
settings_button.grid(row=0, column=1, sticky='w', padx=5)

info_button = ctk.CTkButton(grid0,
                            width=20,
                            height=20,
                            text="?",
                            font=("", 13, "bold"),
                            command=lambda: toggle_window(info_window))
info_button.grid(row=0, column=2, sticky='w')

evil_info_button = ctk.CTkButton(grid0,
                                 width=20,
                                 height=20,
                                 text="?",
                                 font=("", 13, "bold"),
                                 text_color='#ff0000',
                                 command=lambda: toggle_window(evil_solutions_windows))
evil_info_button.grid(row=0, column=3, sticky='w', padx=(5, 0))

resize_button = ctk.CTkButton(grid0,
                              width=40, 
                              height=20,
                              text='< >',
                              font=("", 16, "bold"),
                              command=lambda: resize_window(resize_button))
resize_button.grid(row=0, column=4, padx=5, sticky='e')

console = ConsoleWindow(app)
console_button = ctk.CTkButton(grid0,
                               width=80,
                               height=20,
                               text="Console",
                               font=("", 15, "bold"),
                               command=console.toggle)
console_button.grid(row=0, column=5, sticky='e')

max_characters = 100
entries = []
for i in range(5):
    row_entries = []
    validate_cmd = app.register(lambda text: limit_input(text, max_characters))
    for j in range(5):
        entry = ctk.CTkEntry(grid1,
                             justify="center",
                             height=35, width=0,
                             border_width=1,
                             border_color="#acacac",
                             corner_radius=0,
                             validate="key",
                             validatecommand=(validate_cmd, "%P"),
                             font=("", 16))
        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)
        entry.bind("<KeyPress-(>", bracket_helper)
        entry.grid(row=i + 1, column=j, sticky='ew', padx=1, pady=1)
        row_entries.append(entry)
    entries.append(row_entries)

order_button = ctk.CTkButton(grid2,
                             width=130,
                             text="Order",
                             font=("", 20),
                             command=lambda: toggle_window(order_window))
order_button.grid(row=0, column=0, sticky='w')

puzzle4_button = ctk.CTkButton(grid2,
                               width=130,
                               text='P4 Answers',
                               font=("", 20),
                               command=lambda: toggle_window(puzzle4_window))
puzzle4_button.grid(row=0, column=1, padx=(5, 0), sticky='w')

clear_button = ctk.CTkButton(grid2,
                             width=130,
                             text="Clear",
                             font=("", 20),
                             command=clear_entries)
clear_button.grid(row=0, column=3, padx=(0, 5), sticky='e')

solve_button = ctk.CTkButton(grid2,
                             width=130,
                             text="Solve", 
                             font=("", 20),
                             command=hatch_puzzle)
solve_button.grid(row=0, column=4, sticky='e')

app.geometry(f"+{screen_w//2-app.winfo_width()-118}+{screen_h-app.winfo_height()-155}")

# defaults
order_cooldown = object()
settings = {
    hatch_puzzle: "Return",
    clear_entries: "y",
    order_playback: "F1",
    order_cooldown: 2000
}

for function, key in settings.items():
    if isinstance(key, str):
        app.bind_all(f"<{key}>", function)

load_settings()

# Preloading subwindows
open_settings()
open_info()
open_order()
open_puzzle4()
open_evil_solutions()

def on_close():
    save_settings()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_close)

# Keeping track of subwindows to minimize along side main window
visible_subwindows = []
subwindows = [settings_window,
              info_window,
              evil_solutions_windows,
              order_window,
              puzzle4_window,
              console.window]

def on_minimize(event):
    if event.widget == app:
        visible_subwindows.clear()
        for win in subwindows:
            if win and win.winfo_exists() and win.state() != 'withdrawn':
                visible_subwindows.append(win)
                win.withdraw()

def on_restore(event):
    if event.widget == app:
        for win in visible_subwindows:
            if win and win.winfo_exists():
                win.deiconify()

app.bind('<Unmap>', on_minimize)
app.bind('<Map>', on_restore)

app.update()
app_height = app.winfo_height()

app.mainloop()