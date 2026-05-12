#!/usr/bin/env python3
"""Small desktop GUI for the address enrichment pipeline."""

from __future__ import annotations

import os
import threading
import traceback
from pathlib import Path
from tkinter import BooleanVar, IntVar, StringVar, Tk, filedialog, messagebox, ttk

from enrich_addresses import enrich_file, load_env_file


APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"


def save_api_key(api_key: str) -> None:
    lines: list[str] = []
    found = False
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    for line in lines:
        if line.strip().startswith("GOOGLE_PLACES_API_KEY="):
            updated.append(f"GOOGLE_PLACES_API_KEY={api_key.strip()}")
            found = True
        else:
            updated.append(line)
    if not found:
        updated.append(f"GOOGLE_PLACES_API_KEY={api_key.strip()}")
    ENV_PATH.write_text("\n".join(updated) + "\n", encoding="utf-8")
    os.environ["GOOGLE_PLACES_API_KEY"] = api_key.strip()


class AddressEnrichmentApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Address Enrichment")
        self.root.geometry("780x520")
        self.root.minsize(720, 480)

        load_env_file(ENV_PATH)

        self.input_path = StringVar()
        self.output_path = StringVar()
        self.api_key = StringVar(value=os.environ.get("GOOGLE_PLACES_API_KEY", ""))
        self.provider = StringVar(value="google" if self.api_key.get() else "heuristic")
        self.field_preset = StringVar(value="contact")
        self.search_strategy = StringVar(value="expanded")
        self.max_results = IntVar(value=5)
        self.limit_enabled = BooleanVar(value=True)
        self.limit = IntVar(value=25)
        self.status = StringVar(value="Choose an Excel or CSV file to begin.")

        self.build()

    def build(self) -> None:
        padding = {"padx": 12, "pady": 7}
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Address Enrichment", font=("", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", **padding
        )

        ttk.Label(main, text="Input file").grid(row=1, column=0, sticky="w", **padding)
        ttk.Entry(main, textvariable=self.input_path).grid(row=1, column=1, sticky="ew", **padding)
        ttk.Button(main, text="Browse", command=self.choose_input).grid(row=1, column=2, **padding)

        ttk.Label(main, text="Output file").grid(row=2, column=0, sticky="w", **padding)
        ttk.Entry(main, textvariable=self.output_path).grid(row=2, column=1, sticky="ew", **padding)
        ttk.Button(main, text="Save As", command=self.choose_output).grid(row=2, column=2, **padding)

        ttk.Label(main, text="Google API key").grid(row=3, column=0, sticky="w", **padding)
        ttk.Entry(main, textvariable=self.api_key, show="*").grid(row=3, column=1, sticky="ew", **padding)
        ttk.Button(main, text="Save Key", command=self.on_save_key).grid(row=3, column=2, **padding)

        ttk.Label(main, text="Provider").grid(row=4, column=0, sticky="w", **padding)
        provider_box = ttk.Combobox(
            main,
            textvariable=self.provider,
            values=["google", "heuristic", "auto"],
            state="readonly",
        )
        provider_box.grid(row=4, column=1, sticky="w", **padding)

        ttk.Label(main, text="Field preset").grid(row=5, column=0, sticky="w", **padding)
        ttk.Combobox(
            main,
            textvariable=self.field_preset,
            values=["contact", "basic", "ids"],
            state="readonly",
        ).grid(row=5, column=1, sticky="w", **padding)

        ttk.Label(main, text="Search strategy").grid(row=6, column=0, sticky="w", **padding)
        ttk.Combobox(
            main,
            textvariable=self.search_strategy,
            values=["expanded", "exact"],
            state="readonly",
        ).grid(row=6, column=1, sticky="w", **padding)

        ttk.Label(main, text="Max matches per address").grid(row=7, column=0, sticky="w", **padding)
        ttk.Spinbox(main, from_=1, to=20, textvariable=self.max_results, width=8).grid(
            row=7, column=1, sticky="w", **padding
        )

        limit_frame = ttk.Frame(main)
        limit_frame.grid(row=8, column=1, sticky="w", **padding)
        ttk.Checkbutton(limit_frame, text="Limit rows for testing", variable=self.limit_enabled).pack(side="left")
        ttk.Spinbox(limit_frame, from_=1, to=100000, textvariable=self.limit, width=10).pack(side="left", padx=10)

        self.run_button = ttk.Button(main, text="Run Enrichment", command=self.on_run)
        self.run_button.grid(row=9, column=1, sticky="w", **padding)

        ttk.Label(main, textvariable=self.status, wraplength=680).grid(
            row=10, column=0, columnspan=3, sticky="ew", **padding
        )

        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.grid(row=11, column=0, columnspan=3, sticky="ew", padx=12, pady=12)

        main.columnconfigure(1, weight=1)

    def choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose address file",
            filetypes=[("Excel or CSV", "*.xlsx *.csv"), ("Excel", "*.xlsx"), ("CSV", "*.csv")],
        )
        if not path:
            return
        self.input_path.set(path)
        input_path = Path(path)
        self.output_path.set(str(input_path.with_name(f"{input_path.stem}_enriched.xlsx")))

    def choose_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Choose output file",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")],
        )
        if path:
            self.output_path.set(path)

    def on_save_key(self) -> None:
        if not self.api_key.get().strip():
            messagebox.showwarning("Missing key", "Paste your Google Places API key first.")
            return
        save_api_key(self.api_key.get())
        self.status.set(f"Saved API key to {ENV_PATH.name}.")

    def on_run(self) -> None:
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showwarning("Missing files", "Choose both input and output files.")
            return
        if self.provider.get() == "google" and self.api_key.get().strip():
            save_api_key(self.api_key.get())

        self.run_button.configure(state="disabled")
        self.progress.start(10)
        self.status.set("Running enrichment. This can take a while for large files.")
        thread = threading.Thread(target=self.run_worker, daemon=True)
        thread.start()

    def run_worker(self) -> None:
        try:
            processed, output_rows = enrich_file(
                input_path=Path(self.input_path.get()),
                output_path=Path(self.output_path.get()),
                provider=self.provider.get(),
                limit=self.limit.get() if self.limit_enabled.get() else None,
                max_results=self.max_results.get(),
                search_strategy=self.search_strategy.get(),
                field_preset=self.field_preset.get(),
            )
            self.root.after(0, self.run_success, processed, output_rows)
        except Exception as error:
            details = traceback.format_exc()
            self.root.after(0, self.run_error, str(error), details)

    def run_success(self, processed: int, output_rows: int) -> None:
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.status.set(f"Done. Processed {processed} input rows and wrote {output_rows} output rows.")
        messagebox.showinfo("Done", f"Wrote enriched file:\n{self.output_path.get()}")

    def run_error(self, error: str, details: str) -> None:
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.status.set(f"Error: {error}")
        messagebox.showerror("Enrichment failed", f"{error}\n\nDetails:\n{details[-2000:]}")


def main() -> None:
    root = Tk()
    AddressEnrichmentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
