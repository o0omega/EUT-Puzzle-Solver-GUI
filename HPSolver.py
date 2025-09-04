Version = "1.5"
InfoText = """
Any app window must be in focus for keybinds
to function properly.

For Puzzle #2 you can input numbers right away.
For Puzzle #3 you can seperate the number and
the base (the other number in ()) with a space,
a stop or () 
For Puzzle #4 some questions are labeled as "evil"
By the creator of the puzzle, so you can input their
answers right away

Made by ozo
Discord: @m6ga
Edited by ltrc125 to fit the new Harry's puzzle
If ozo is unavailable or demotivated to update 
it to fix bugs, then tell ltrc
DM any bugs or suggestions, a forum post for the
app can be found on EUT discord (.gg/eut).
"""

Evil_Solutions = """
Asap question's answer is 1
33 + 77 is 100
the not not not not question is 1
the bottom blue hint is the number in the end + 1
the bottom red hint is the number in the end - 1
the 1 + 1 is 11
"""


import customtkinter as ctk
import keyboard, sys, os
from ctypes import windll
from PIL import Image
import pywinstyles as pws
import math
import sympy as sp


def formula_translation(n):
    if n.count('^') > 0:
        n = n.replace('^', '**')
    if n.count('pi') > 0:
        n = n.replace('pi', 'math.pi')
    if n.count('!') > 0:
        factorial_lib = {'1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5080, '8': 40640}
        for i in range(1, 9):
            if str(i) in n:
                n = n.replace(str(i) + '!', str(factorial_lib[str(i)]))
    if n.count(')(') > 0:
        n = n.replace(')(', ')*(')
    if n.count('math.round') > 0:
        n = n.replace('math.round', 'round')
    return n


def type2_equation_solver(equation_string):
    equations = equation_string.split(',')
    symbols = {}
    for eq in equations:
        eq = eq.strip()
        var, expr = eq.split('=')
        var = var.strip()
        expr = expr.strip()
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


def stage4_solving(form):
    form = formula_translation(form)
    special_formulas = {'Asap': 1, '1 + 1': 11, '77 + 33': 100}
    if form in special_formulas.keys():
        return special_formulas[form]
    elif form.count('Blue') > 0:
        res = int(form.split()[-1]) + 1
        return res
    elif form.count('Red') > 0:
        res = int(form.split()[-1]) - 1
        return res
    elif form.count('not') > 0:
        return 0
    if form.count('x') == 1 and form.count('a') > 0:
        return type2_equation_solver(form)
    elif form.count('x') > 0 and form.count('a') == 0:
        return type1_equation_solver(form)
    else:
        return eval(form) if eval(form) is not list else eval(form)[0]


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


icon_path = resource_path(r"images\M.ico")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app = ctk.CTk()
app.geometry("688x385")
app.title("HPSolver")
app.iconbitmap(resource_path(r"images\M.ico"))

labels = []
stage4_labels = []

replace2 = str.maketrans("!@#$%^&*()", "1234567890")


def copy_to_clipboard(event):
    label_text = event.widget.cget("text")
    app.clipboard_clear()
    app.clipboard_append(label_text)


def pin_window(window, button):
    try:
        current_topmost = window.attributes('-topmost')
        window.attributes('-topmost', not current_topmost)
        button.configure(text="Unpin" if not current_topmost else "Pin")
    except Exception as e:
        print(f"Error processing pin_window: {e}")


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
    return darken_color, initial_color


def titlebarify(widget, window, darkening=False):
    if darkening:
        darken_color, initial_color = darken(widget)

    def start_move(event):
        window._offset_x = event.x_root - window.winfo_rootx()
        window._offset_y = event.y_root - window.winfo_rooty()
        if darkening:
            widget.configure(fg_color=f"#{darken_color}")
        window.bind("<Motion>", drag_motion)

    def do_move(event):
        new_x = event.x_root - window._offset_x
        new_y = event.y_root - window._offset_y
        window.geometry(f"+{new_x}+{new_y}")

    def stop_move(event):
        if darkening:
            widget.configure(fg_color=f"#{initial_color}")
        window.unbind("<Motion>")

    def drag_motion(event):
        if darkening:
            widget.configure(fg_color=f"#{darken_color}")
        do_move(event)

    widget.bind("<ButtonPress-1>", start_move)
    widget.bind("<ButtonRelease-1>", stop_move)


def switch_to_english():
    user32 = windll.user32
    LANG_EN = 0x0409
    user32.ActivateKeyboardLayout(LANG_EN, 0)


settings_window = None


def open_settings():
    try:
        global settings_window, keybinds

        def hatch_bind(button, function):
            blacklist = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#', '$', '%', '^', '&', '*', '(',
                         ')', 'Esc', 'M', 'A', 'T', 'H', 'R', 'O', 'U', 'N', 'D', 'C', 'E', 'I', 'L', 'F']
            button.configure(text="Press a key", fg_color='#144870')

            def on_key_press(event):
                new_key = " ".join([w.capitalize() for w in event.name.split()])
                if not event.name.isascii():
                    print(
                        "Invalid keybind: Non-ASCII key detected, make sure you are using an English keyboard layout.")
                elif new_key not in blacklist:
                    button.configure(text=new_key, fg_color='#1f6aa5')
                    app.unbind_all(keybinds[function])
                    keybinds[function] = new_key if len(new_key) > 1 else "<" + new_key.lower() + ">"
                    app.bind_all(keybinds[function], function)
                    print("Keybind changed to:", keybinds[function], new_key)
                else:
                    button.configure(
                        text=keybinds[function].replace("<", "").replace(">", "") if "Return" not in keybinds[
                            function] else "Enter")
                    print("Invalid keybind:", new_key)
                    print('Some English letters are reserved due to Stage 4.')
                keyboard.unhook_all()

            switch_to_english()
            keyboard.on_press(on_key_press)

        if settings_window is not None and settings_window.winfo_exists():
            settings_window.lift()
            settings_window.focus_force()
            return

        settings_window = ctk.CTkToplevel(app)
        window = settings_window
        window.geometry("220x220")
        window.overrideredirect(True)
        window.wm_attributes("-transparentcolor", "#1a1a1a")
        window.after(10, lambda: window.focus_force())

        mainframe = ctk.CTkFrame(window,
                                 corner_radius=10)
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
                              text='Hide',
                              font=("", 10),
                              command=lambda: window.withdraw())
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar,
                            height=20,
                            width=15,
                            corner_radius=5,
                            fg_color='#002037',
                            text='Pin',
                            font=("", 10),
                            command=lambda: pin_window(window, pin))
        pin.pack(side='left', padx=2)

        grid = ctk.CTkFrame(mainframe,
                            corner_radius=5)
        grid.pack(pady=5, padx=5)

        Solve = ctk.CTkLabel(grid,
                             text="Solve:",
                             font=("", 15))
        Solve.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        Clear = ctk.CTkLabel(grid,
                             text="Clear:",
                             font=("", 15))
        Clear.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        Clickthrough = ctk.CTkLabel(grid,
                                    text="Clickthrough:",
                                    font=("", 15))
        Clickthrough.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        Stage4_Clickthrough = ctk.CTkLabel(grid,
                                           text="Stage 4 Clickthrough:",
                                           font=("", 15))
        Stage4_Clickthrough.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        grid.columnconfigure(1, weight=1)

        SolveBind = ctk.CTkButton(grid,
                                  width=90,
                                  height=30,
                                  border_width=1,
                                  corner_radius=2,
                                  text="Enter",
                                  font=("", 15, 'bold'),
                                  command=lambda: hatch_bind(SolveBind, hatch_puzzle))
        SolveBind.grid(row=0, column=1, pady=5, padx=5)

        ClearBind = ctk.CTkButton(grid,
                                  width=90,
                                  height=30,
                                  border_width=1,
                                  corner_radius=2,
                                  text="Y",
                                  font=("", 15, 'bold'),
                                  command=lambda: hatch_bind(ClearBind, clear_entries))
        ClearBind.grid(row=1, column=1, pady=5, padx=5)

        ClickthroughBind = ctk.CTkButton(grid,
                                         width=90,
                                         height=30,
                                         border_width=1,
                                         corner_radius=2,
                                         text="F1",
                                         font=("", 15, 'bold'),
                                         command=lambda: hatch_bind(ClickthroughBind, toggle_clickthrough))
        ClickthroughBind.grid(row=2, column=1, pady=5, padx=5)

        stage4_ClickthroughBind = ctk.CTkButton(grid,
                                                width=90,
                                                height=30,
                                                border_width=1,
                                                corner_radius=2,
                                                text="F2",
                                                font=("", 15, 'bold'),
                                                command=lambda: hatch_bind(stage4_ClickthroughBind,
                                                                           stage4_toggle_clickthrough))
        stage4_ClickthroughBind.grid(row=3, column=1, pady=5, padx=5)

        window.withdraw()

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

        window = ctk.CTkToplevel(app)
        info_window = window
        window.geometry("350x400")
        window.overrideredirect(True)
        window.wm_attributes("-transparentcolor", "#1a1a1a")
        window.after(10, lambda: window.focus_force())

        mainframe = ctk.CTkFrame(window,
                                 width=350,
                                 height=400,
                                 corner_radius=10)
        mainframe.pack(fill='both')

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
                              text='Hide',
                              font=("", 10),
                              command=window.withdraw)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar,
                            height=20,
                            width=15,
                            corner_radius=5,
                            fg_color='#002037',
                            text='Pin',
                            font=("", 10),
                            command=lambda: pin_window(window, pin))
        pin.pack(side='left', padx=2)

        versionlabel = ctk.CTkLabel(mainframe,
                                    anchor="center",
                                    width=280,
                                    text=f"Version {Version}",
                                    font=("", 20, 'bold'))
        versionlabel.pack()

        label = ctk.CTkLabel(mainframe,
                             text=InfoText,
                             font=("", 15),
                             justify="left",
                             width=280)
        label.pack(padx=5, pady=(0, 2))
        window.withdraw()

    except Exception as e:
        print(f"Error processing open_settings: {e}\n")


def open_evil_solutions():
    try:
        global evil_solutions_windows
        if evil_solutions_windows is not None and evil_solutions_windows.winfo_exists():
            evil_solutions_windows.lift()
            evil_solutions_windows.focus_force()
            return

        window = ctk.CTkToplevel(app)
        evil_solutions_windows = window
        window.geometry("350x400")
        window.overrideredirect(True)
        window.wm_attributes("-transparentcolor", "#1a1a1a")
        window.after(10, lambda: window.focus_force())

        mainframe = ctk.CTkFrame(window,
                                 width=350,
                                 height=400,
                                 corner_radius=10)
        mainframe.pack(fill='both')

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
                              text='Hide',
                              font=("", 10),
                              command=window.withdraw)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar,
                            height=20,
                            width=15,
                            corner_radius=5,
                            fg_color='#002037',
                            text='Pin',
                            font=("", 10),
                            command=lambda: pin_window(window, pin))
        pin.pack(side='left', padx=2)

        versionlabel = ctk.CTkLabel(mainframe,
                                    anchor="center",
                                    width=280,
                                    text=f"Version {Version}",
                                    font=("", 20, 'bold'))
        versionlabel.pack()

        label = ctk.CTkLabel(mainframe,
                             text=Evil_Solutions,
                             font=("", 15),
                             justify="left",
                             width=280)
        label.pack(padx=5, pady=(0, 2))
        window.withdraw()

    except Exception as e:
        print(f"Error processing open_info: {e}\n")


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
            self.window.geometry("550x300")
            self.window.overrideredirect(True)
            self.window.wm_attributes("-transparentcolor", "#1a1a1a")
            self.window.after(10, lambda: self.window.focus_force())

            mainframe = ctk.CTkFrame(self.window,
                                     width=500,
                                     height=300,
                                     corner_radius=10)
            mainframe.pack_propagate(False)
            mainframe.pack(fill='both')

            freedom_dive = ctk.CTkImage(light_image=Image.open(resource_path("images/freedomdive.png")),
                                        size=(550, 300))
            freedom_image = ctk.CTkLabel(mainframe,
                                         text="",
                                         image=freedom_dive)
            freedom_image.place(x=0, y=0)

            titlebar = ctk.CTkFrame(mainframe,
                                    height=25,
                                    fg_color='#1f6aa5',
                                    corner_radius=5,
                                    background_corner_colors=('#97aabf', '#0d1121', '#465b2f', '#64975f'))
            titlebar.pack_propagate(False)
            titlebar.pack(fill='x', pady=5, padx=5)
            titlebarify(titlebar, self.window, True)

            clear = ctk.CTkButton(titlebar,
                                  height=20,
                                  width=30,
                                  corner_radius=5,
                                  fg_color='#002037',
                                  text='Clear',
                                  font=("", 10),
                                  command=self.clear_console)
            clear.pack(side='left', padx=2)

            pin = ctk.CTkButton(titlebar,
                                height=20,
                                width=15,
                                corner_radius=5,
                                fg_color='#002037',
                                text='Pin',
                                font=("", 10),
                                command=lambda: pin_window(self.window, pin))
            pin.pack(side='left')

            close = ctk.CTkButton(titlebar,
                                  height=20,
                                  width=15,
                                  corner_radius=5,
                                  fg_color='#002037',
                                  text='Hide',
                                  font=("", 10),
                                  command=self.window.withdraw)
            close.pack(side='right', padx=2)

            self.console_text = ctk.CTkTextbox(mainframe,
                                               wrap="word",
                                               corner_radius=0,
                                               height=250,
                                               width=530,
                                               state='normal',
                                               font=("Calibri", 12, "bold"))
            pws.set_opacity(self.console_text, 0.9)
            self.console_text.pack(pady=(0, 10), padx=10, expand=True)
            self.console_text.configure(state='disabled')

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
                self.console_text.configure(state='normal')
                self.console_text.insert("end", text)
                self.console_text.see("end")
                self.console_text.configure(state='disabled')
                self.console_text.update()

            with open("output.log", "a") as f:
                f.write(f"{text}")
        except Exception as e:
            with open("console_error.log", "a") as f:
                f.write(f"Error in write_console: {e}\n")

    def clear_console(self):
        try:
            if self.console_text is not None:
                self.console_text.configure(state='normal')
                self.console_text.delete("1.0", "end")
                self.console_text.configure(state='disabled')
        except Exception as e:
            self.write_console(f"Error processing clear_console: {e}\n")

    def toggle(self):
        if self.window is not None and self.window.winfo_exists():
            if self.window.state() == 'withdrawn':
                self.window.deiconify()
                self.window.lift()
                self.window.focus_force()
            else:
                self.window.withdraw()


def change_transparency(value):
    try:
        order_window.attributes("-alpha", float(value))
    except Exception as e:
        print(f"Error processing change_transparency: {e}")


def stage4_change_transparency(value):
    try:
        stage4_window.attributes("-alpha", float(value))
    except Exception as e:
        print(f"Error processing change_transparency: {e}")


clickthrough = False
clickthroughlabel = None


def toggle_clickthrough(event=None):
    global clickthrough, clickthroughlabel
    try:
        if order_window is None or not order_window.winfo_exists() or order_window.state() == 'withdrawn':
            print("Order window is not open. Open the Order window to enable clickthrough.")
            return

        order_window.lift()
        order_window.focus_force()
        order_window.update_idletasks()

        hwnd = windll.user32.GetForegroundWindow()
        style = windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20

        if not clickthrough:
            new_style = style | 0x00000020  # WS_EX_TRANSPARENT
            windll.user32.SetWindowLongW(hwnd, -20, new_style)
            if clickthroughlabel:
                clickthroughlabel.configure(text="Clickthrough enabled", text_color='#c4ffa8')
        else:
            new_style = style & ~0x00000020  # Remove WS_EX_TRANSPARENT
            windll.user32.SetWindowLongW(hwnd, -20, new_style)
            if clickthroughlabel:
                clickthroughlabel.configure(text="Clickthrough disabled", text_color='#ffa8a8')
            force_focus_window(hwnd)

        windll.user32.UpdateWindow(hwnd)
        clickthrough = not clickthrough

    except Exception as e:
        print(f"Error processing toggle_clickthrough: {e}")


stage4_clickthrough = False
stage4_clickthroughlabel = None


def stage4_toggle_clickthrough(event=None):
    global stage4_clickthrough, stage4_clickthroughlabel
    try:
        if stage4_window is None or not stage4_window.winfo_exists() or stage4_window.state() == 'withdrawn':
            print("Stage 4 window is not open. Open the Stage 4 window to enable clickthrough.")
            return

        stage4_window.lift()
        stage4_window.focus_force()
        stage4_window.update_idletasks()

        hwnd = windll.user32.GetForegroundWindow()
        style = windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20

        if not stage4_clickthrough:
            new_style = style | 0x00000020  # WS_EX_TRANSPARENT
            windll.user32.SetWindowLongW(hwnd, -20, new_style)
            if stage4_clickthroughlabel:
                stage4_clickthroughlabel.configure(text="Clickthrough enabled", text_color='#c4ffa8')
        else:
            new_style = style & ~0x00000020  # Remove WS_EX_TRANSPARENT
            windll.user32.SetWindowLongW(hwnd, -20, new_style)
            if stage4_clickthroughlabel:
                stage4_clickthroughlabel.configure(text="Clickthrough disabled", text_color='#ffa8a8')
            force_focus_window(hwnd)

        windll.user32.UpdateWindow(hwnd)
        stage4_clickthrough = not stage4_clickthrough

    except Exception as e:
        print(f"Error processing toggle_clickthrough: {e}")


def force_focus_window(hwnd):  # ctk focus_force doesn't work after disabling clickthrough for whatever reason
    try:
        if windll.user32.IsIconic(hwnd):
            windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0003)  # HWND_TOPMOST
        windll.user32.SetForegroundWindow(hwnd)
        windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0003)  # HWND_NOTOPMOST
    except Exception as e:
        print(f"Error processing force_focus_window: {e}")


order_window = None
stage4_window = None


def open_order():
    try:
        global order_window, clickthroughlabel, labels

        if order_window is not None and order_window.winfo_exists():
            order_window.lift()
            order_window.focus_force()
            return

        window = ctk.CTkToplevel(app)
        order_window = window
        window.geometry("262x340")
        window.overrideredirect(True)
        window.wm_attributes("-transparentcolor", "#1a1a1a")
        window.after(10, lambda: window.focus_force())

        mainframe = ctk.CTkFrame(window,
                                 width=262,
                                 height=340,
                                 corner_radius=10)
        mainframe.pack_propagate(False)
        mainframe.pack(fill='both')

        titlebar = ctk.CTkFrame(mainframe,
                                height=25,
                                fg_color='#1f6aa5',
                                corner_radius=5)
        titlebar.pack_propagate(False)
        titlebar.pack(fill='x', pady=5, padx=5)
        titlebarify(titlebar, window, True)

        close = ctk.CTkButton(titlebar,
                              height=20,
                              width=15,
                              corner_radius=5,
                              fg_color='#002037',
                              text='Hide',
                              font=("", 10),
                              command=window.withdraw)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar,
                            height=20,
                            width=15,
                            corner_radius=5,
                            fg_color='#002037',
                            text='Pin',
                            font=("", 10),
                            command=lambda: pin_window(window, pin))
        pin.pack(side='left', padx=2)

        stage4 = ctk.CTkButton(titlebar,
                               height=20,
                               width=15,
                               corner_radius=5,
                               fg_color='#002037',
                               text='Stage4',
                               font=("", 10),
                               command=lambda: toggle_window(stage4_window))
        stage4.place(x=103, y=2)

        frame = ctk.CTkFrame(mainframe)
        frame.pack()

        grid = ctk.CTkFrame(frame)
        grid.pack()

        for i in range(5):
            row_labels = []
            for j in range(5):
                label = ctk.CTkLabel(grid,
                                     width=50,
                                     height=50,
                                     justify="center",
                                     text="",
                                     fg_color="#025c9d",
                                     font=("", 16, "bold"))
                label.grid(row=i, column=j, padx=1, pady=1)
                row_labels.append(label)
            labels.append(row_labels)

        transparency_slider = ctk.CTkSlider(mainframe,
                                            width=200,
                                            height=5,
                                            from_=0.1,
                                            to=1,
                                            number_of_steps=10,
                                            command=change_transparency)
        transparency_slider.set(1)
        transparency_slider.pack(pady=(10, 5))

        clickthroughlabel = ctk.CTkLabel(mainframe,
                                         text="Clickthrough disabled",
                                         text_color='#ffa8a8')
        clickthroughlabel.pack()
        window.withdraw()

    except Exception as e:
        print(f"Error processing open_order: {e}\n")


evil_solutions_windows = None


def open_stage4():
    try:
        global stage4_window, stage4_clickthroughlabel, stage4_labels, on_click

        if stage4_window is not None and stage4_window.winfo_exists():
            stage4_window.lift()
            stage4_window.focus_force()
            return

        window = ctk.CTkToplevel(app)
        stage4_window = window
        window.geometry("387x340")
        window.overrideredirect(True)
        window.wm_attributes("-transparentcolor", "#1a1a1a")
        window.after(10, lambda: window.focus_force())

        mainframe = ctk.CTkFrame(window,
                                 width=387,
                                 height=340,
                                 corner_radius=10)
        mainframe.pack_propagate(False)
        mainframe.pack(fill='both')

        titlebar = ctk.CTkFrame(mainframe,
                                height=25,
                                fg_color='#1f6aa5',
                                corner_radius=5)
        titlebar.pack_propagate(False)
        titlebar.pack(fill='x', pady=5, padx=5)
        titlebarify(titlebar, window, True)

        close = ctk.CTkButton(titlebar,
                              height=20,
                              width=15,
                              corner_radius=5,
                              fg_color='#002037',
                              text='Hide',
                              font=("", 10),
                              command=window.withdraw)
        close.pack(side='right', padx=2)

        pin = ctk.CTkButton(titlebar,
                            height=20,
                            width=15,
                            corner_radius=5,
                            fg_color='#002037',
                            text='Pin',
                            font=("", 10),
                            command=lambda: pin_window(window, pin))
        pin.pack(side='left', padx=2)

        evil_solution = ctk.CTkButton(titlebar,
                               height=20,
                               width=15,
                               corner_radius=5,
                               fg_color='#002037',
                               text='Evil Solutions',
                               font=("", 10),
                               command=lambda: toggle_window(evil_solutions_windows))
        evil_solution.place(x=150, y=2)

        frame = ctk.CTkFrame(mainframe)
        frame.pack()

        grid = ctk.CTkFrame(frame)
        grid.pack()

        for i in range(5):
            stage4_row_labels = []
            for j in range(5):
                label = ctk.CTkLabel(grid,
                                     width=75,
                                     height=50,
                                     justify="center",
                                     text="",
                                     fg_color="#025c9d",
                                     font=("", 16, "bold"))
                label.grid(row=i, column=j, padx=1, pady=1)
                label['state'] = 'readonly'
                label.bind("<Button-1>", copy_to_clipboard)
                stage4_row_labels.append(label)
            stage4_labels.append(stage4_row_labels)

        stage4_transparency_slider = ctk.CTkSlider(mainframe,
                                                   width=200,
                                                   height=5,
                                                   from_=0.1,
                                                   to=1,
                                                   number_of_steps=10,
                                                   command=change_transparency)
        stage4_transparency_slider.set(1)
        stage4_transparency_slider.pack(pady=(10, 5))

        stage4_clickthroughlabel = ctk.CTkLabel(mainframe,
                                                text="Clickthrough disabled",
                                                text_color='#ffa8a8')
        stage4_clickthroughlabel.pack()
        window.withdraw()

    except Exception as e:
        print(f"Error processing open_order: {e}\n")


def toggle_window(window):
    if window is not None and window.winfo_exists():
        if window.state() == 'withdrawn':
            window.deiconify()
            window.lift()
            window.focus_force()
        else:
            window.withdraw()


def hatch_puzzle(event=None):
    try:
        values = []
        checkstop = False
        puzzle = 12
        for row in entries:
            for entry in row:
                data = str(entry.get()) if entry.get() else '0'
                values.append(data)
                if not checkstop:
                    if len(data) > 4 and data.count('+') + data.count('-') > 0:
                        puzzle = 4
                        checkstop = True
                    elif len(data) > 3 and data.count(' ') + data.count('(') + data.count(',') == 1:
                        puzzle = 3
                        checkstop = True

        print(f"Entries: {values}")

        if puzzle == 4:
            print(f"Detected Puzzle #4")
            puzzle4(values)
        elif puzzle == 3:
            print(f"Detected Puzzle #3")
            puzzle3(values)
        else:
            print(f"Detected Puzzle #1/#2")
            puzzle1_2(values)
    except Exception as e:
        print(f"Error processing hatch_puzzle: {e}\n")


def puzzle1_2(values):
    try:
        replace = str.maketrans("!@#$%^&*()", "1234567890")
        values = [int(num.translate(replace)) for num in values]
        print(f"Converted: {values}")

        non_zero_values = [value for value in values if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Order: {ordered_values}\n")

        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(
                        text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #1/#2: {e}")


def puzzle3(values):
    try:
        replace = str.maketrans(" (),", "tttt")
        values = [num.translate(replace).split('t') for num in values]
        base10s = [int(str(i[0]), int(i[1])) for i in values]
        print(f"Transferred to base 10: {base10s}")

        non_zero_values = [value for value in base10s if value != 0]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in base10s]
        print(f"Order: {ordered_values}\n")

        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(
                        text=str(ordered_values[label_index]) if ordered_values[label_index] != 0 else '')
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #3: {e}")


def puzzle4(values):
    try:
        non_zero_values = [stage4_solving(value) for value in values]
        order = {num: i + 1 for i, num in enumerate(sorted(non_zero_values))}
        ordered_values = [order.get(num, 0) for num in values]
        print(f"Order: {ordered_values}")

        if order_window is not None and order_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    labels[i][j].configure(text=str(ordered_values[label_index]))
                    label_index += 1

        if stage4_window is not None and stage4_window.winfo_exists():
            label_index = 0
            for i in range(5):
                for j in range(5):
                    stage4_labels[i][j].configure(text=str(non_zero_values[label_index]))
                    label_index += 1

    except Exception as e:
        print(f"Error processing Puzzle #4: {e}")


def limit_input(entry_text, max_length):
    try:
        valid_chars = set("0123456789-t!@#$%^&*()qweryuiopasdfghjklzxcvbnm+ ")
        return (len(entry_text) <= int(max_length) and all(char in valid_chars for char in entry_text))
    except Exception as e:
        print(f"Error processing limit_input: {e}")


def clear_entries(event=None):
    try:
        for row in entries:
            for entry in row:
                entry.delete(0, "end")
    except Exception as e:
        print(f"Error processing clear_entries: {e}")


frame = ctk.CTkFrame(app, bg_color='#1a1a1a')
frame.pack(pady=(32, 10))

grid1 = ctk.CTkFrame(frame, bg_color='#1a1a1a')
grid2 = ctk.CTkFrame(frame, fg_color='transparent')
grid1.pack(side="top")
grid2.pack(side="bottom", pady=5)

entries = []
for i in range(5):
    row_entries = []
    validate_cmd = app.register(lambda text: limit_input(text, 32))
    for j in range(5):
        entry = ctk.CTkEntry(
            grid1,
            justify="center",
            width=135,
            height=45,
            border_width=1,
            corner_radius=2,
            validate="key",
            validatecommand=(validate_cmd, "%P"))
        entry.grid(row=i + 1, column=j)
        row_entries.append(entry)
    entries.append(row_entries)

inputlabel = ctk.CTkLabel(grid1,
                          width=100,
                          text="Input",
                          font=("", 20))
inputlabel.grid(row=0, column=0, columnspan=5, pady=5)

solve_button = ctk.CTkButton(grid2,
                             width=100,
                             text="Solve",
                             font=("", 20),
                             command=hatch_puzzle)
solve_button.grid(row=0, column=1, padx=5)

clear_button = ctk.CTkButton(grid2,
                             width=100,
                             text="Clear",
                             font=("", 20),
                             command=clear_entries)
clear_button.grid(row=0, column=0, padx=5)

order_button = ctk.CTkButton(grid2,
                             width=100,
                             text="Order",
                             font=("", 20),
                             command=lambda: toggle_window(order_window))
order_button.grid(row=2, column=0, columnspan=2, pady=5)

info_button = ctk.CTkButton(app,
                            width=20,
                            height=20,
                            text="?",
                            font=("", 15),
                            command=lambda: toggle_window(info_window))
info_button.place(x=5, y=5)

settings_icon = ctk.CTkImage(light_image=Image.open(resource_path("images/settings.png")),
                             size=(15, 15))
settings_button = ctk.CTkButton(app,
                                width=20,
                                height=20,
                                text="",
                                image=settings_icon,
                                command=lambda: toggle_window(settings_window))
settings_button.place(x=32, y=5)

pin_button = ctk.CTkButton(app,
                           width=40,
                           height=20,
                           text="Pin",
                           font=("", 15),
                           command=lambda: pin_window(app, pin_button))
pin_button.place(x=67, y=5)

console = ConsoleWindow(app)
console_button = ctk.CTkButton(app,
                               width=80,
                               height=20,
                               text="Console",
                               font=("", 15),
                               command=console.toggle)
console_button.place(x=600, y=5)

keybinds = {
    toggle_clickthrough: "<F1>",
    hatch_puzzle: "<Return>",
    clear_entries: "y",
    stage4_toggle_clickthrough: "<F2>"
}

for function, key in keybinds.items():
    app.bind_all(key, function)

# Preloading top level windows
open_settings()
open_info()
open_order()
open_stage4()
open_evil_solutions()

print("HPSolver Started")
app.mainloop()

# for .exe compiling use 2 following commands, make sure all file paths are correct.
# pip install pyinstaller
# pyinstaller --onefile --noconsole --icon="images/M.ico" --add-data="images/*;images" --add-data="images/M.ico;." --add-data="images/settings.png;." --add-data="images/freedomdive.png;." --clean HPSolver.py
