"""Reusable desktop widgets and form helpers for Aegis Health."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Iterable, Sequence

import customtkinter as ctk

from . import theme
from .store import StoreError


# --------------------------------------------------------------------------- fonts
def font(size: int = 12, bold: bool = False, mono: bool = False) -> tuple:
    family = theme.MONO_FAMILY if mono else theme.FONT_FAMILY
    return (family, size, "bold" if bold else "normal")


# --------------------------------------------------------------------------- ttk
def configure_table_style() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Aegis.Treeview",
        background=theme.CARD,
        fieldbackground=theme.CARD,
        foreground=theme.TEXT,
        borderwidth=0,
        relief="flat",
        rowheight=37,
        font=font(10),
    )
    style.configure(
        "Aegis.Treeview.Heading",
        background=theme.CARD_ALT,
        foreground=theme.MUTED,
        relief="flat",
        borderwidth=0,
        padding=(9, 9),
        font=font(9, bold=True),
    )
    style.map(
        "Aegis.Treeview",
        background=[("selected", theme.PRIMARY_SOFT)],
        foreground=[("selected", theme.TEXT)],
    )
    style.map(
        "Aegis.Treeview.Heading",
        background=[("active", theme.CARD_HOVER)],
        foreground=[("active", theme.TEXT)],
    )
    style.layout("Aegis.Treeview", [("Aegis.Treeview.treearea", {"sticky": "nswe"})])

    for orientation, name in (("Vertical", "Aegis.Vertical.TScrollbar"),
                              ("Horizontal", "Aegis.Horizontal.TScrollbar")):
        style.configure(
            name,
            gripcount=0,
            background=theme.BORDER_STRONG,
            darkcolor=theme.CARD,
            lightcolor=theme.CARD,
            troughcolor=theme.CARD,
            bordercolor=theme.CARD,
            arrowcolor=theme.MUTED,
            relief="flat",
            borderwidth=0,
        )
        style.map(name, background=[("active", theme.MUTED)])


# --------------------------------------------------------------------------- cards
class Card(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs: Any) -> None:
        kwargs.setdefault("fg_color", theme.CARD)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", theme.BORDER)
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)


class StatCard(Card):
    def __init__(
        self,
        master: Any,
        label: str,
        value: str,
        sub: str = "",
        value_color: str = theme.TEXT,
        sub_color: str = theme.MUTED,
    ) -> None:
        super().__init__(master, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=font(11, bold=True),
            text_color=theme.MUTED,
            anchor="w",
        )
        self.label.grid(row=0, column=0, sticky="ew", padx=14, pady=(11, 2))

        self.value = ctk.CTkLabel(
            self,
            text=value,
            font=font(24, bold=True),
            text_color=value_color,
            anchor="w",
        )
        self.value.grid(row=1, column=0, sticky="ew", padx=14)

        self.sub = ctk.CTkLabel(
            self,
            text=sub,
            font=font(10),
            text_color=sub_color,
            anchor="w",
        )
        self.sub.grid(row=2, column=0, sticky="ew", padx=14, pady=(1, 11))

    def update(self, value: str, sub: str | None = None,
               value_color: str | None = None, sub_color: str | None = None) -> None:
        self.value.configure(text=value)
        if sub is not None:
            self.sub.configure(text=sub)
        if value_color:
            self.value.configure(text_color=value_color)
        if sub_color:
            self.sub.configure(text_color=sub_color)


class SectionHeader(ctk.CTkFrame):
    def __init__(self, master: Any, title: str, subtitle: str = "") -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=title,
            font=font(14, bold=True),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")
        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=font(10),
                text_color=theme.MUTED,
                anchor="w",
            ).grid(row=1, column=0, sticky="ew", pady=(1, 0))
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.grid(row=0, column=1, rowspan=2, sticky="e")


class PageHeader(ctk.CTkFrame):
    def __init__(self, master: Any, title: str, subtitle: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=title,
            font=font(22, bold=True),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            self,
            text=subtitle,
            font=font(11),
            text_color=theme.MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.grid(row=0, column=1, rowspan=2, sticky="e")


# --------------------------------------------------------------------------- buttons
def primary_button(master: Any, text: str, command: Callable | None = None,
                   **kwargs: Any) -> ctk.CTkButton:
    kwargs.setdefault("fg_color", theme.PRIMARY)
    kwargs.setdefault("hover_color", theme.PRIMARY_HOVER)
    kwargs.setdefault("text_color", theme.INVERSE)
    kwargs.setdefault("font", font(11, bold=True))
    kwargs.setdefault("height", 32)
    kwargs.setdefault("corner_radius", 7)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def secondary_button(master: Any, text: str, command: Callable | None = None,
                     **kwargs: Any) -> ctk.CTkButton:
    kwargs.setdefault("fg_color", theme.CARD)
    kwargs.setdefault("hover_color", theme.CARD_HOVER)
    kwargs.setdefault("text_color", theme.TEXT_SECONDARY)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", theme.BORDER_STRONG)
    kwargs.setdefault("font", font(11, bold=True))
    kwargs.setdefault("height", 32)
    kwargs.setdefault("corner_radius", 7)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def tinted_button(master: Any, text: str, command: Callable | None = None,
                  color: str = theme.EMERALD, bg: str = theme.EMERALD_BG,
                  border: str = theme.EMERALD_BORDER, **kwargs: Any) -> ctk.CTkButton:
    kwargs.setdefault("fg_color", bg)
    kwargs.setdefault("hover_color", border)
    kwargs.setdefault("text_color", color)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", border)
    kwargs.setdefault("font", font(11, bold=True))
    kwargs.setdefault("height", 30)
    kwargs.setdefault("corner_radius", 6)
    return ctk.CTkButton(master, text=text, command=command, **kwargs)


def danger_button(master: Any, text: str, command: Callable | None = None,
                  **kwargs: Any) -> ctk.CTkButton:
    return tinted_button(
        master, text, command,
        color=theme.ROSE, bg=theme.ROSE_BG, border=theme.ROSE_BORDER, **kwargs,
    )


# --------------------------------------------------------------------------- filters
class PillTabs(ctk.CTkFrame):
    """A compact row of toggle buttons used for status/ward filters."""

    def __init__(self, master: Any, options: Sequence[str | tuple[str, str]],
                 command: Callable[[str], None] | None = None,
                 value: str | None = None, **kwargs: Any) -> None:
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self._command = command
        self._value = value
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._entries: list[tuple[str, str]] = []
        self.set_options(options, notify=False)

    def _normalise(self, options: Sequence[str | tuple[str, str]]) -> list[tuple[str, str]]:
        normalised: list[tuple[str, str]] = []
        for option in options:
            if isinstance(option, tuple):
                normalised.append((str(option[0]), str(option[1])))
            else:
                normalised.append((str(option), str(option)))
        return normalised

    def set_options(self, options: Sequence[str | tuple[str, str]], notify: bool = False) -> None:
        self._entries = self._normalise(options)
        valid = [value for value, _ in self._entries]
        if self._value not in valid:
            self._value = valid[0] if valid else None

        for child in self.winfo_children():
            child.destroy()
        self._buttons.clear()

        for value, label in self._entries:
            selected = value == self._value
            button = ctk.CTkButton(
                self,
                text=label,
                height=27,
                corner_radius=6,
                fg_color=theme.PRIMARY if selected else "transparent",
                hover_color=theme.PRIMARY_HOVER if selected else theme.PRIMARY_SOFT,
                text_color=theme.INVERSE if selected else theme.TEXT_SECONDARY,
                font=font(10, bold=selected),
                command=lambda v=value: self.set(v),
            )
            button.pack(side="left", padx=(0, 4))
            self._buttons[value] = button

        if notify and self._command and self._value is not None:
            self._command(self._value)

    def set(self, value: str, notify: bool = True) -> None:
        self._value = value
        for key, button in self._buttons.items():
            selected = key == value
            button.configure(
                fg_color=theme.PRIMARY if selected else "transparent",
                hover_color=theme.PRIMARY_HOVER if selected else theme.PRIMARY_SOFT,
                text_color=theme.INVERSE if selected else theme.TEXT_SECONDARY,
                font=font(10, bold=selected),
            )
        if notify and self._command:
            self._command(value)

    def get(self) -> str | None:
        return self._value

    def refresh_options(self, options: Sequence[str | tuple[str, str]]) -> None:
        self.set_options(options, notify=False)


# --------------------------------------------------------------------------- table
class DataTable(ctk.CTkFrame):
    """Styled ttk Treeview with headings, scrollbars and row tags."""

    def __init__(
        self,
        master: Any,
        columns: Sequence[dict],
        height: int = 10,
        on_double_click: Callable[[str], None] | None = None,
        on_select: Callable[[str], None] | None = None,
        empty_text: str = "No records match the current filters.",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("fg_color", theme.CARD)
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        self._on_double_click = on_double_click
        self._on_select = on_select
        self._records: dict[str, Any] = {}
        self._empty_text = empty_text
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        keys = [column["key"] for column in columns]
        self._column_keys = tuple(keys)
        self.tree = ttk.Treeview(
            self,
            columns=keys,
            show="headings",
            selectmode="browse",
            height=height,
            style="Aegis.Treeview",
        )
        scaling = ctk.ScalingTracker.get_window_scaling(self)
        for column in columns:
            self.tree.heading(column["key"], text=column["title"], anchor=column.get("anchor", "w"))
            self.tree.column(
                column["key"],
                width=max(40, round(column.get("width", 120) * scaling)),
                minwidth=max(40, round(column.get("minwidth", 60) * scaling)),
                anchor=column.get("anchor", "w"),
                stretch=column.get("stretch", True),
            )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure("row_even", background=theme.CARD)
        self.tree.tag_configure("row_odd", background="#FBFCFE")
        self.tree.tag_configure("rose", foreground=theme.ROSE)
        self.tree.tag_configure("amber", foreground=theme.AMBER)
        self.tree.tag_configure("emerald", foreground=theme.EMERALD)
        self.tree.tag_configure("blue", foreground=theme.BLUE)
        self.tree.tag_configure("muted", foreground=theme.MUTED)
        self.tree.tag_configure("text", foreground=theme.TEXT)
        self.tree.tag_configure("bold", font=font(10, bold=True))

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview,
                            style="Aegis.Vertical.TScrollbar")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview,
                            style="Aegis.Horizontal.TScrollbar")
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._hsb = hsb

        self.empty = ctk.CTkLabel(
            self,
            text=empty_text,
            font=font(11),
            text_color=theme.FAINT,
            fg_color="transparent",
        )

        self.tree.bind("<Double-1>", self._double_click)
        self.tree.bind("<<TreeviewSelect>>", self._selected)
        self.tree.bind("<Configure>", self._sync_hscroll, add="+")

    def _sync_hscroll(self, event: Any) -> None:
        """Only show the horizontal scrollbar when the columns cannot fit."""
        total = sum(int(self.tree.column(key, "width")) for key in self._column_keys)
        if total <= int(event.width) + 2:
            self._hsb.grid_remove()
        else:
            self._hsb.grid()

    def set_rows(self, rows: Iterable[dict]) -> None:
        selected = self.selected_id()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._records.clear()

        count = 0
        for index, row in enumerate(rows):
            iid = str(row["iid"])
            tags = ["row_even" if index % 2 == 0 else "row_odd", *row.get("tags", [])]
            self.tree.insert("", "end", iid=iid, values=row.get("values", []), tags=tuple(tags))
            self._records[iid] = row.get("record")
            count += 1

        if count == 0:
            self.empty.place(relx=0.5, rely=0.55, anchor="center")
        else:
            self.empty.place_forget()
            if selected and selected in self._records:
                self.tree.selection_set(selected)

    def selected_id(self) -> str | None:
        selection = self.tree.selection()
        return str(selection[0]) if selection else None

    def selected_record(self) -> Any:
        iid = self.selected_id()
        return self._records.get(iid) if iid else None

    def select_first(self) -> str | None:
        children = self.tree.get_children()
        if not children:
            return None
        self.tree.selection_set(children[0])
        return str(children[0])

    def _double_click(self, _event: Any) -> None:
        iid = self.selected_id()
        if iid and self._on_double_click:
            self._on_double_click(iid)

    def _selected(self, _event: Any) -> None:
        iid = self.selected_id()
        if iid and self._on_select:
            self._on_select(iid)


# --------------------------------------------------------------------------- forms
def _entry(parent: Any, **kwargs: Any) -> ctk.CTkEntry:
    kwargs.setdefault("height", 32)
    kwargs.setdefault("corner_radius", 6)
    kwargs.setdefault("fg_color", theme.CARD_ALT)
    kwargs.setdefault("border_color", theme.BORDER_STRONG)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("text_color", theme.TEXT)
    kwargs.setdefault("placeholder_text_color", theme.FAINT)
    kwargs.setdefault("font", font(11))
    return ctk.CTkEntry(parent, **kwargs)


def field(
    parent: Any,
    label: str,
    row: int,
    column: int = 0,
    colspan: int = 1,
    kind: str = "entry",
    values: Sequence[str] | None = None,
    default: Any = "",
    placeholder: str = "",
    height: int = 80,
    mono: bool = False,
) -> Any:
    """Create a labelled form control inside a grid parent and return the control."""
    wrapper = ctk.CTkFrame(parent, fg_color="transparent")
    wrapper.grid(row=row, column=column, columnspan=colspan, sticky="ew", padx=7, pady=5)
    ctk.CTkLabel(
        wrapper,
        text=label,
        font=font(10, bold=True),
        text_color=theme.TEXT_SECONDARY,
        anchor="w",
    ).pack(fill="x", pady=(0, 4))

    if kind == "option":
        options = [str(value) for value in (values or [])]
        widget = ctk.CTkOptionMenu(
            wrapper,
            values=options,
            height=32,
            corner_radius=6,
            fg_color=theme.CARD_ALT,
            button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG,
            text_color=theme.TEXT,
            dropdown_fg_color=theme.CARD,
            dropdown_hover_color=theme.CARD_HOVER,
            dropdown_text_color=theme.TEXT,
            font=font(11),
            dropdown_font=font(11),
        )
        if default not in (None, ""):
            widget.set(str(default))
        elif options:
            widget.set(options[0])
        widget.pack(fill="x")
        return widget

    if kind == "text":
        widget = ctk.CTkTextbox(
            wrapper,
            height=height,
            corner_radius=6,
            border_width=1,
            border_color=theme.BORDER_STRONG,
            fg_color=theme.CARD_ALT,
            text_color=theme.TEXT,
            font=font(11, mono=mono),
        )
        if default not in (None, ""):
            widget.insert("1.0", str(default))
        widget.pack(fill="x")
        return widget

    widget = _entry(
        wrapper,
        placeholder_text=placeholder,
        font=font(11, mono=mono),
    )
    if default not in (None, ""):
        widget.insert(0, str(default))
    widget.pack(fill="x")
    return widget


def value(widget: Any) -> str:
    """Read a value from an entry or textbox."""
    if isinstance(widget, ctk.CTkTextbox):
        return widget.get("1.0", "end").strip()
    try:
        return str(widget.get()).strip()
    except Exception:
        return ""


def section_label(parent: Any, text: str, row: int, colspan: int = 2) -> None:
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid(row=row, column=0, columnspan=colspan, sticky="ew", padx=7, pady=(12, 2))
    ctk.CTkLabel(
        frame,
        text=text.upper(),
        font=font(9, bold=True),
        text_color=theme.FAINT,
        anchor="w",
    ).pack(side="left")


def two_column_form(parent: Any, columns: int = 2) -> None:
    for index in range(columns):
        parent.grid_columnconfigure(index, weight=1, uniform="form")


def divider(parent: Any, row: int, colspan: int = 2) -> None:
    ctk.CTkFrame(parent, height=1, fg_color=theme.BORDER).grid(
        row=row, column=0, columnspan=colspan, sticky="ew", padx=7, pady=(8, 2)
    )


# --------------------------------------------------------------------------- dialogs
class BaseDialog(ctk.CTkToplevel):
    """Modal shell with a browser-style header, scrollable body and sticky footer."""

    def __init__(
        self,
        app: Any,
        title: str,
        subtitle: str = "",
        width: int = 760,
        height: int = 700,
    ) -> None:
        super().__init__(app)
        self.app = app
        self.store = app.store
        self._result: Any = None
        self.title(title)
        self.configure(fg_color=theme.BG)
        self.resizable(False, True)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", lambda _e: self.close())

        self.header = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        ctk.CTkLabel(
            self.header,
            text=title,
            font=font(15, bold=True),
            text_color=theme.TEXT,
            anchor="w",
        ).pack(side="left", padx=20, pady=(14, 0))
        if subtitle:
            ctk.CTkLabel(
                self.header,
                text=subtitle,
                font=font(10),
                text_color=theme.MUTED,
                anchor="w",
            ).place(x=20, y=40)
        ctk.CTkButton(
            self.header,
            text="\u2715",
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=theme.CARD_HOVER,
            text_color=theme.MUTED,
            font=font(14),
            command=self.close,
        ).pack(side="right", padx=14, pady=14)

        self.footer = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=62)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG,
            corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        self.body.pack(fill="both", expand=True, padx=14, pady=(14, 10))

        self._width = width
        self._height = height
        self.update_idletasks()
        self._center(width, height)
        self.after(40, self._activate)

    def _center(self, width: int, height: int) -> None:
        parent = self.app
        parent.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = min(max(10, x), max(10, screen_w - width - 10))
        y = min(max(10, y), max(10, screen_h - height - 40))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _activate(self) -> None:
        try:
            self.grab_set()
            self.focus_force()
        except tk.TclError:
            pass

    def add_footer(
        self,
        submit_text: str = "Save",
        submit_command: Callable | None = None,
        submit_color: str = theme.PRIMARY,
        cancel_text: str = "Cancel",
    ) -> ctk.CTkButton:
        if cancel_text:
            secondary_button(
                self.footer, cancel_text, self.close,
                height=34, width=100,
            ).pack(side="right", padx=(6, 16), pady=14)
        button = primary_button(
            self.footer,
            submit_text,
            submit_command or self.submit,
            fg_color=submit_color,
            hover_color=submit_color,
            height=34,
            width=160,
        )
        button.pack(side="right", pady=14)
        self.submit_button = button
        return button

    def run_action(self, action: Callable, *args: Any, **kwargs: Any) -> bool:
        try:
            action(*args, **kwargs)
            return True
        except StoreError as error:
            self.app.toast(str(error), error=True)
            return False
        except Exception as error:  # keep the desktop app alive on unexpected input
            self.app.toast(f"Could not complete action: {error}", error=True)
            return False

    def submit(self) -> None:  # pragma: no cover - overridden by form dialogs
        self.run_action(self.on_submit)

    def on_submit(self) -> None:  # pragma: no cover - overridden by form dialogs
        pass

    def close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


# --------------------------------------------------------------------------- base view
class BaseView(ctk.CTkFrame):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, fg_color=theme.BG)
        self.app = app
        self.store = app.store
        self.grid_columnconfigure(0, weight=1)

    def run_action(self, action: Callable, *args: Any, **kwargs: Any) -> Any:
        try:
            return action(*args, **kwargs)
        except StoreError as error:
            self.app.toast(str(error), error=True)
        except Exception as error:
            self.app.toast(f"Could not complete action: {error}", error=True)
        return None

    def refresh(self) -> None:
        pass
