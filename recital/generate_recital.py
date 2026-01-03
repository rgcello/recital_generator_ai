import sys
import json
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

import openai

from csv_loader import _load_single_csv
from ai.prompts import build_canonical_resolution_prompt
from ai.models import StudentPerformance  # your Pydantic model
from ai.llm_parser import parse_llm_recital_response
from docx_generator import generate_recital_docx
from sort_students import student_sort_key


def get_config_path():
    """Get the path to the user's config file."""
    home = Path.home()
    config_dir = home / ".recital_generator"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_api_key():
    """Load API key from config file."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("openai_api_key")
    return None


def save_api_key(api_key):
    """Save API key to config file."""
    config_path = get_config_path()
    config = {"openai_api_key": api_key}
    with open(config_path, "w") as f:
        json.dump(config, f)


def delete_api_key():
    """Delete the saved API key."""
    config_path = get_config_path()
    if config_path.exists():
        config_path.unlink()
        return True
    return False


def prompt_for_api_key(parent=None, show_password=True):
    """Show a dialog to get API key from user."""
    dialog = tk.Toplevel(parent) if parent else tk.Tk()
    dialog.title("OpenAI API Key Configuration")

    # Even larger window size
    window_width = 750
    window_height = 350

    dialog.resizable(False, False)

    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - window_width) // 2
    y = (dialog.winfo_screenheight() - window_height) // 2
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

    api_key_var = tk.StringVar()
    show_key = tk.BooleanVar(value=not show_password)
    result = {"api_key": None}

    frame = tk.Frame(dialog, padx=40, pady=30)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame, text="Please enter your OpenAI API Key:", font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 20))

    tk.Label(
        frame,
        text="This will be saved securely on your computer.",
        font=("Segoe UI", 11),
    ).pack(pady=(0, 25))

    # Entry field with show/hide toggle
    entry_frame = tk.Frame(frame)
    entry_frame.pack(pady=(0, 15))

    entry = tk.Entry(
        entry_frame,
        textvariable=api_key_var,
        width=70,
        show="*" if show_password else "",
        font=("Segoe UI", 12),
    )
    entry.pack(side="left", ipady=8, padx=(0, 10))

    def toggle_visibility():
        if show_key.get():
            entry.config(show="")
        else:
            entry.config(show="*")

    tk.Checkbutton(
        entry_frame,
        text="Show",
        variable=show_key,
        command=toggle_visibility,
        font=("Segoe UI", 10),
    ).pack(side="left")

    entry.focus()

    def on_save():
        key = api_key_var.get().strip()
        if key:
            result["api_key"] = key
            dialog.destroy()
        else:
            messagebox.showerror("Error", "API key cannot be empty", parent=dialog)

    def on_cancel():
        dialog.destroy()

    entry.bind("<Return>", lambda e: on_save())

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=15)

    tk.Button(
        button_frame,
        text="Save",
        command=on_save,
        bg="#6366f1",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        padx=30,
        pady=8,
        borderwidth=0,
    ).pack(side="left", padx=8)

    tk.Button(
        button_frame,
        text="Cancel",
        command=on_cancel,
        bg="#6b7280",
        fg="white",
        font=("Segoe UI", 11),
        padx=30,
        pady=8,
        borderwidth=0,
    ).pack(side="left", padx=8)

    if not parent:
        dialog.mainloop()
    else:
        dialog.wait_window()

    return result["api_key"]


def main():
    # Try to load API key from config file
    api_key = load_api_key()

    if not api_key:
        # Prompt user for API key
        api_key = prompt_for_api_key()
        if not api_key:
            messagebox.showerror(
                "Error", "OpenAI API key is required to run this application"
            )
            sys.exit(1)
        save_api_key(api_key)

    openai.api_key = api_key

    # Load Suzuki repertoire JSON
    repertoire_path = Path(__file__).parent / "repertoire" / "suzuki_repertoire.json"

    if not repertoire_path.exists():
        messagebox.showerror(
            "Error", f"suzuki_repertoire.json not found at {repertoire_path}"
        )
        sys.exit(1)

    with open(repertoire_path, "r", encoding="utf-8") as f:
        suzuki_repertoire = json.load(f)

    # Create GUI
    root = tk.Tk()
    root.title("Recital Program Generator")

    # Store window dimensions for later
    window_width = 800
    window_height = 900  # Increased from 650 to 750

    # Configure style with modern theme
    style = ttk.Style()
    style.theme_use("clam")

    # Modern color scheme - clean white background with purple/blue accents
    bg_color = "#ffffff"
    header_bg = "#6366f1"  # Modern indigo
    header_fg = "#ffffff"
    accent_color = "#6366f1"
    button_hover = "#4f46e5"
    label_color = "#374151"  # Dark gray for labels

    root.configure(bg=bg_color)

    style.configure(
        "Header.TLabel",
        background=header_bg,
        foreground=header_fg,
        font=("Segoe UI", 18, "bold"),
        padding=20,
    )

    style.configure(
        "TLabel", font=("Segoe UI", 10), foreground=label_color, background=bg_color
    )

    style.configure(
        "Bold.TLabel",
        font=("Segoe UI", 10, "bold"),
        foreground=label_color,
        background=bg_color,
    )

    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        fieldbackground="white",
        borderwidth=2,
        relief="flat",
        padding=5,
    )

    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        background=accent_color,
        foreground="white",
        borderwidth=0,
        relief="flat",
        focuscolor="none",
        padding=(15, 8),
    )

    style.map("TButton", background=[("active", button_hover)])

    style.configure(
        "Generate.TButton",
        font=("Segoe UI", 13, "bold"),
        padding=(25, 15),
        background=accent_color,
        relief="flat",
    )

    style.map("Generate.TButton", background=[("active", button_hover)])

    style.configure(
        "TLabelframe",
        background=bg_color,
        borderwidth=1,
        relief="solid",
        bordercolor="#e5e7eb",
    )

    style.configure(
        "TLabelframe.Label",
        font=("Segoe UI", 11, "bold"),
        foreground=accent_color,
        background=bg_color,
    )

    # Variables to store user inputs
    csv_file = tk.StringVar()
    output_folder = tk.StringVar()
    studio_name = tk.StringVar()
    recital_title = tk.StringVar()
    recital_date = tk.StringVar()
    accompanist = tk.StringVar()
    footer_text = tk.StringVar()

    def change_api_key():
        """Allow user to change their API key."""
        new_key = prompt_for_api_key(root)
        if new_key:
            save_api_key(new_key)
            openai.api_key = new_key
            messagebox.showinfo("Success", "API key updated successfully!")

    def view_api_key():
        """Show the current API key."""
        current_key = load_api_key()
        if current_key:
            # Show in a dialog with copy option
            view_dialog = tk.Toplevel(root)
            view_dialog.title("View API Key")
            view_dialog.geometry("700x250")
            view_dialog.resizable(False, False)

            # Center the dialog
            x = (root.winfo_screenwidth() - 700) // 2
            y = (root.winfo_screenheight() - 250) // 2
            view_dialog.geometry(f"700x250+{x}+{y}")

            frame = tk.Frame(view_dialog, padx=30, pady=25)
            frame.pack(fill="both", expand=True)

            tk.Label(
                frame, text="Your Current API Key:", font=("Segoe UI", 12, "bold")
            ).pack(pady=(0, 15))

            key_text = tk.Text(
                frame, height=3, width=75, font=("Segoe UI", 10), wrap="word"
            )
            key_text.pack(pady=(0, 15))
            key_text.insert("1.0", current_key)
            key_text.config(state="disabled")

            def copy_to_clipboard():
                root.clipboard_clear()
                root.clipboard_append(current_key)
                messagebox.showinfo(
                    "Copied", "API key copied to clipboard!", parent=view_dialog
                )

            btn_frame = tk.Frame(frame)
            btn_frame.pack()

            tk.Button(
                btn_frame,
                text="Copy to Clipboard",
                command=copy_to_clipboard,
                bg="#6366f1",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                padx=20,
                pady=8,
                borderwidth=0,
            ).pack(side="left", padx=5)

            tk.Button(
                btn_frame,
                text="Close",
                command=view_dialog.destroy,
                bg="#6b7280",
                fg="white",
                font=("Segoe UI", 10),
                padx=20,
                pady=8,
                borderwidth=0,
            ).pack(side="left", padx=5)
        else:
            messagebox.showinfo("No API Key", "No API key is currently saved.")

    def delete_api_key_confirm():
        """Delete the API key after confirmation."""
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete your saved API key?\n\nYou will need to enter it again the next time you run the application.",
            icon="warning",
        ):
            if delete_api_key():
                messagebox.showinfo(
                    "Deleted",
                    "API key has been deleted successfully.\n\nThe application will now close.",
                )
                root.quit()
            else:
                messagebox.showinfo("Not Found", "No API key was found to delete.")

    def select_csv():
        # Create a fixed-size toplevel window for the dialog
        dialog_root = tk.Toplevel(root)
        dialog_root.geometry("900x600")
        dialog_root.title("Select CSV File")
        dialog_root.withdraw()

        # Hide main window temporarily
        root.withdraw()

        filename = filedialog.askopenfilename(
            parent=dialog_root,
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~"),
        )

        dialog_root.destroy()
        root.deiconify()

        if filename:
            csv_file.set(filename)

    def select_output_folder():
        # Create a fixed-size toplevel window for the dialog
        dialog_root = tk.Toplevel(root)
        dialog_root.geometry("900x600")
        dialog_root.title("Select Output Folder")
        dialog_root.withdraw()

        # Hide main window temporarily
        root.withdraw()

        folder = filedialog.askdirectory(
            parent=dialog_root,
            title="Select Output Folder",
            initialdir=os.path.expanduser("~"),
            mustexist=True,
        )

        dialog_root.destroy()
        root.deiconify()

        if folder:
            output_folder.set(folder)

    def generate():
        # Validate inputs
        if not csv_file.get():
            messagebox.showerror("Error", "Please select a CSV file")
            return
        if not output_folder.get():
            messagebox.showerror("Error", "Please select an output folder")
            return
        if not all(
            [
                studio_name.get(),
                recital_title.get(),
                recital_date.get(),
                accompanist.get(),
                footer_text.get(),
            ]
        ):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            # Load CSV data
            csv_path = Path(csv_file.get())
            csv_data = _load_single_csv(csv_path)

            if not csv_data:
                messagebox.showerror("Error", "No valid data found in CSV file")
                return

            # Build prompt and call AI
            prompt = build_canonical_resolution_prompt(
                csv_entries=csv_data,
                suzuki_repertoire=suzuki_repertoire,
            )

            # Show progress
            progress_window = tk.Toplevel(root)
            progress_window.title("Processing")
            progress_window.geometry("400x150")
            progress_window.configure(bg=bg_color)
            progress_window.resizable(False, False)

            # Center the progress window
            progress_window.transient(root)
            progress_window.grab_set()

            progress_frame = tk.Frame(progress_window, bg=bg_color)
            progress_frame.pack(expand=True, fill="both", padx=20, pady=20)

            tk.Label(
                progress_frame,
                text="🎵 Processing...",
                font=("Arial", 14, "bold"),
                bg=bg_color,
                fg=header_bg,
            ).pack(pady=10)

            tk.Label(
                progress_frame,
                text="Resolving repertoire with AI...",
                font=("Arial", 10),
                bg=bg_color,
            ).pack(pady=5)

            progress_window.update()

            response = openai.responses.create(
                model="gpt-5.1",
                input=prompt,
                temperature=0.1,
            )

            raw_output = response.output_text
            performances = parse_llm_recital_response(raw_output)
            performances = sorted(performances, key=student_sort_key)

            # Generate output filename
            base_name = csv_path.stem
            output_dir = output_folder.get()

            # Check if file already exists and add timestamp if needed
            output_filename = f"{base_name}.docx"
            test_path = Path(output_dir) / output_filename
            if test_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{base_name}_{timestamp}.docx"

            # Generate DOCX
            full_output_path = generate_recital_docx(
                performances=performances,
                studio_name=studio_name.get(),
                recital_title=recital_title.get(),
                recital_date=recital_date.get(),
                accompanist=accompanist.get(),
                footer_text=footer_text.get(),
                output_dir=output_dir,
                filename=output_filename,
            )

            progress_window.destroy()
            messagebox.showinfo(
                "Success",
                f"✓ Program generated successfully!\n\nSaved to:\n{full_output_path}",
            )

            # Clear form
            csv_file.set("")
            studio_name.set("")
            recital_title.set("")
            recital_date.set("")
            accompanist.set("")
            footer_text.set("")

        except Exception as e:
            if "progress_window" in locals():
                progress_window.destroy()
            messagebox.showerror("Error", f"❌ An error occurred:\n\n{str(e)}")

    # ============================================================
    # GUI Layout
    # ============================================================

    # Menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Change API Key", command=change_api_key)
    settings_menu.add_command(label="View API Key", command=view_api_key)
    settings_menu.add_command(label="Delete API Key", command=delete_api_key_confirm)
    settings_menu.add_separator()
    settings_menu.add_command(label="Exit", command=root.quit)

    # Header
    header_frame = tk.Frame(root, bg=header_bg)
    header_frame.pack(fill="x")

    header_label = tk.Label(
        header_frame,
        text="🎼 Recital Program Generator",
        background=header_bg,
        foreground=header_fg,
        font=("Arial", 16, "bold"),
        pady=15,
    )
    header_label.pack()

    # Main content frame with padding
    main_frame = ttk.Frame(root, padding="25", style="TFrame")
    main_frame.columnconfigure(0, weight=1)
    main_frame.pack(fill="both", expand=True)

    style.configure("TFrame", background=bg_color)

    # File Selection Section
    file_section = ttk.LabelFrame(main_frame, text=" File Selection ", padding="15")
    file_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
    file_section.columnconfigure(1, weight=1)

    # CSV File Selection
    ttk.Label(file_section, text="CSV File:", style="Bold.TLabel").grid(
        row=0, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(file_section, textvariable=csv_file, width=50, state="readonly").grid(
        row=0, column=1, pady=8, sticky=(tk.W, tk.E), padx=(0, 10)
    )
    ttk.Button(file_section, text="Browse...", command=select_csv).grid(
        row=0, column=2, pady=8
    )

    # Output Folder Selection
    ttk.Label(file_section, text="Output Folder:", style="Bold.TLabel").grid(
        row=1, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(
        file_section, textvariable=output_folder, width=50, state="readonly"
    ).grid(row=1, column=1, pady=8, sticky=(tk.W, tk.E), padx=(0, 10))
    ttk.Button(file_section, text="Browse...", command=select_output_folder).grid(
        row=1, column=2, pady=8
    )

    # Program Details Section
    details_section = ttk.LabelFrame(main_frame, text=" Program Details ", padding="15")
    details_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
    details_section.columnconfigure(1, weight=1)

    # Header fields
    ttk.Label(details_section, text="Studio Name:").grid(
        row=0, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(details_section, textvariable=studio_name, width=50).grid(
        row=0, column=1, columnspan=2, pady=8, sticky=(tk.W, tk.E)
    )

    ttk.Label(details_section, text="Recital Title:").grid(
        row=1, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(details_section, textvariable=recital_title, width=50).grid(
        row=1, column=1, columnspan=2, pady=8, sticky=(tk.W, tk.E)
    )

    ttk.Label(details_section, text="Recital Date/Time:").grid(
        row=2, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(details_section, textvariable=recital_date, width=50).grid(
        row=2, column=1, columnspan=2, pady=8, sticky=(tk.W, tk.E)
    )

    ttk.Label(details_section, text="Accompanist:").grid(
        row=3, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(details_section, textvariable=accompanist, width=50).grid(
        row=3, column=1, columnspan=2, pady=8, sticky=(tk.W, tk.E)
    )

    ttk.Label(details_section, text="Footer Text:").grid(
        row=4, column=0, sticky=tk.W, pady=8, padx=(0, 10)
    )
    ttk.Entry(details_section, textvariable=footer_text, width=50).grid(
        row=4, column=1, columnspan=2, pady=8, sticky=(tk.W, tk.E)
    )

    # Generate button with custom style
    button_frame = tk.Frame(main_frame, bg=bg_color)

    button_frame.grid(row=2, column=0, pady=15)

    generate_btn = ttk.Button(
        button_frame,
        text="Generate Program",
        command=generate,
        style="Generate.TButton",
        width=25,
    )
    generate_btn.pack()

    # Calculate center position
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # Use after_idle to force geometry AFTER everything is fully rendered
    def force_geometry():
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.minsize(window_width, window_height)
        root.update()

    root.after_idle(force_geometry)

    root.mainloop()


if __name__ == "__main__":
    main()
