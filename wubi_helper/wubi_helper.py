#!/usr/bin/env python3
"""五笔编码查询图形工具.

默认读取 ibus-table 的 `wubi-jidian86` 词库：
- 精确命中词库时，显示推荐编码和其他可用编码；
- 词库未命中时，按 `打字规则.md` 中的词组规则推导编码；
- 结果以字根卡片形式展示主编码对应的按键信息。
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk


@dataclass(frozen=True)
class KeyMeta:
    position: str
    zone: int
    root_lines: tuple[str, ...]


@dataclass(frozen=True)
class QueryResult:
    text: str
    main_code: str
    all_codes: tuple[str, ...]
    mode: str
    code_mode: str
    note: str

    @property
    def other_codes(self) -> tuple[str, ...]:
        return tuple(code for code in self.all_codes if code != self.main_code)


KEY_METAS: dict[str, KeyMeta] = {
    "a": KeyMeta("15", 1, ("工 戈 艹 匚", "七")),
    "s": KeyMeta("14", 1, ("木 丁 西",)),
    "d": KeyMeta("13", 1, ("大 犬 三", "羊 古 石 厂")),
    "f": KeyMeta("12", 1, ("土 士 二 干", "十 寸 雨")),
    "g": KeyMeta("11", 1, ("王 五 一", "青 戋")),
    "h": KeyMeta("21", 2, ("目 止 卜", "虎 皮")),
    "j": KeyMeta("22", 2, ("日 曰 早", "虫 刂")),
    "k": KeyMeta("23", 2, ("口", "川")),
    "l": KeyMeta("24", 2, ("田 甲 囗", "车 力 四")),
    "m": KeyMeta("25", 2, ("山 由 贝", "冂 几")),
    "t": KeyMeta("31", 3, ("禾 竹 丿", "彳 攵 夂")),
    "r": KeyMeta("32", 3, ("白 手 扌", "斤")),
    "e": KeyMeta("33", 3, ("月 彡 乃 用", "豕 衣")),
    "w": KeyMeta("34", 3, ("人 亻 八", "癶")),
    "q": KeyMeta("35", 3, ("金 钅 勹", "儿 夕 鱼")),
    "y": KeyMeta("41", 4, ("言 讠 文", "方 广")),
    "u": KeyMeta("42", 4, ("立 辛 六", "门 疒")),
    "i": KeyMeta("43", 4, ("水 氵 小",)),
    "o": KeyMeta("44", 4, ("火 米 灬", "业")),
    "p": KeyMeta("45", 4, ("之 宀 辶", "礻 衤")),
    "n": KeyMeta("51", 5, ("已 巳 尸", "心 羽 折")),
    "b": KeyMeta("52", 5, ("子 孑 耳", "也 乃 凵")),
    "v": KeyMeta("53", 5, ("女 刀 九", "臼")),
    "c": KeyMeta("54", 5, ("又 巴 马", "厶")),
    "x": KeyMeta("55", 5, ("幺 纟 弓", "匕")),
    "z": KeyMeta("Z", 0, ("万能", "学习键")),
}

ZONE_COLORS = {
    0: "#d8e9c6",
    1: "#f3c9b8",
    2: "#cfe58e",
    3: "#cbe7f8",
    4: "#f2cce7",
    5: "#f6edab",
}

PRIMARY_DB_CANDIDATES = (
    Path.home() / ".local/share/ibus-table/tables/wubi-jidian86-user.db",
    Path("/usr/share/ibus-table/tables/wubi-jidian86.db"),
    Path("/usr/share/ibus-table/tables/wubi-haifeng86.db"),
)

KEY_IMAGE_DIR = Path(__file__).resolve().parent / "wubi_pics"
CODE_MODE_LABELS = {
    "preferred": "推荐码",
    "shortest": "最短码",
    "longest": "最长码",
}


def dedupe_keep_order(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


class WubiRepository:
    def __init__(self, db_paths: Iterable[Path] | None = None) -> None:
        candidates = tuple(db_paths or PRIMARY_DB_CANDIDATES)
        self.db_paths = tuple(path for path in candidates if path.exists())
        self._connections = [sqlite3.connect(path) for path in self.db_paths]
        if not self._connections:
            raise FileNotFoundError("未找到可用的五笔词库数据库。")
        self._example_cache: dict[str, str] = {}

    @property
    def source_summary(self) -> str:
        return " / ".join(path.name for path in self.db_paths)

    def close(self) -> None:
        for connection in self._connections:
            connection.close()

    def _query_exact_codes(self, text: str) -> tuple[str, ...]:
        rows: list[tuple[str, int, int, int]] = []
        for priority, connection in enumerate(self._connections):
            cursor = connection.execute(
                """
                SELECT tabkeys, COALESCE(freq, 0), COALESCE(user_freq, 0)
                FROM phrases
                WHERE phrase = ?
                """,
                (text,),
            )
            for tabkeys, freq, user_freq in cursor.fetchall():
                rows.append((tabkeys, len(tabkeys), priority, -(user_freq + freq)))

        rows.sort(key=lambda item: (item[1], item[2], item[3], item[0]))
        return dedupe_keep_order(row[0] for row in rows)

    def _query_full_char_code(self, char: str) -> str | None:
        for connection in self._connections:
            try:
                row = connection.execute(
                    "SELECT goucima FROM goucima WHERE zi = ?",
                    (char,),
                ).fetchone()
            except sqlite3.OperationalError:
                row = None
            if row and row[0]:
                return str(row[0]).lower()

        codes = self._query_exact_codes(char)
        if not codes:
            return None
        return max(codes, key=len)

    def _derive_phrase_code(self, text: str) -> str | None:
        full_codes = [self._query_full_char_code(char) for char in text]
        if any(code is None for code in full_codes):
            return None

        codes = [code for code in full_codes if code]
        count = len(codes)
        if count == 1:
            return codes[0]
        if count == 2:
            return f"{codes[0][:2]}{codes[1][:2]}"
        if count == 3:
            return f"{codes[0][0]}{codes[1][0]}{codes[2][:2]}"
        return f"{codes[0][0]}{codes[1][0]}{codes[2][0]}{codes[-1][0]}"

    def lookup_example_char(self, key: str) -> str:
        if key in self._example_cache:
            return self._example_cache[key]

        if key == "z":
            self._example_cache[key] = ""
            return ""

        for connection in self._connections:
            cursor = connection.execute(
                """
                SELECT phrase
                FROM phrases
                WHERE tabkeys = ?
                ORDER BY COALESCE(freq, 0) DESC, COALESCE(user_freq, 0) DESC
                LIMIT 1
                """,
                (key,),
            )
            row = cursor.fetchone()
            if row and row[0]:
                self._example_cache[key] = str(row[0])
                return self._example_cache[key]

        self._example_cache[key] = ""
        return ""

    def _select_main_code(self, codes: tuple[str, ...], code_mode: str) -> str:
        if code_mode == "longest":
            max_length = max(len(code) for code in codes)
            return next(code for code in codes if len(code) == max_length)
        if code_mode == "shortest":
            min_length = min(len(code) for code in codes)
            return next(code for code in codes if len(code) == min_length)
        return codes[0]

    def query(self, text: str, code_mode: str = "preferred") -> QueryResult | None:
        normalized = text.strip()
        if not normalized:
            return None

        exact_codes = self._query_exact_codes(normalized)
        if exact_codes:
            main_code = self._select_main_code(exact_codes, code_mode)
            mode_label = CODE_MODE_LABELS.get(code_mode, CODE_MODE_LABELS["preferred"])
            return QueryResult(
                text=normalized,
                main_code=main_code,
                all_codes=exact_codes,
                mode="exact",
                code_mode=code_mode,
                note=f"词库精确命中，当前按“{mode_label}”显示主编码；其余编码列为可用备选。",
            )

        derived_code = self._derive_phrase_code(normalized)
        if derived_code:
            return QueryResult(
                text=normalized,
                main_code=derived_code,
                all_codes=(derived_code,),
                mode="derived",
                code_mode=code_mode,
                note="词库未命中，结果按五笔词组规则由单字全码推导。",
            )

        return None


class KeyCard(ttk.Frame):
    def __init__(self, master: tk.Misc, repository: WubiRepository) -> None:
        super().__init__(master, style="CardHost.TFrame")
        self.repository = repository
        self.image_ref: ImageTk.PhotoImage | None = None
        self.canvas = tk.Canvas(
            self,
            width=126,
            height=126,
            bg="#faf7f2",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

    def render(self, key: str) -> None:
        image_path = self._resolve_image_path(key)
        if image_path is not None:
            self._draw_image(image_path)
            return

        meta = KEY_METAS.get(key)
        if meta is None:
            self._draw_missing(key)
            return

        self.canvas.delete("all")
        self._draw_rounded_rect(4, 4, 122, 122, 18, fill=ZONE_COLORS[meta.zone], outline="#2f2f2f")

        y = 24
        for line in meta.root_lines:
            self.canvas.create_text(
                16,
                y,
                text=line,
                anchor="w",
                fill="#27321d",
                font=("Noto Sans CJK SC", 18, "bold"),
            )
            y += 24

        example = self.repository.lookup_example_char(key)
        bottom = f"{meta.position}{key.upper()}{example}"
        self.canvas.create_text(
            63,
            102,
            text=bottom,
            anchor="center",
            fill="#387245",
            font=("Noto Sans CJK SC", 16, "bold"),
        )

    def clear(self) -> None:
        self.canvas.delete("all")
        self.image_ref = None

    def _draw_missing(self, key: str) -> None:
        self.canvas.delete("all")
        self.image_ref = None
        self._draw_rounded_rect(4, 4, 122, 122, 18, fill="#eadfd6", outline="#2f2f2f")
        self.canvas.create_text(
            63,
            56,
            text=key.upper(),
            fill="#6b4b3b",
            font=("Noto Sans CJK SC", 26, "bold"),
        )
        self.canvas.create_text(
            63,
            86,
            text="暂无字根",
            fill="#6b4b3b",
            font=("Noto Sans CJK SC", 14),
        )

    def _draw_image(self, image_path: Path) -> None:
        self.canvas.delete("all")
        with Image.open(image_path) as source:
            image = source.copy()

        image.thumbnail((118, 118))
        self.image_ref = ImageTk.PhotoImage(image)
        self.canvas.create_image(63, 63, image=self.image_ref, anchor="center")

    def _resolve_image_path(self, key: str) -> Path | None:
        for suffix in (".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".webp", ".WEBP"):
            path = KEY_IMAGE_DIR / f"{key.upper()}{suffix}"
            if path.exists():
                return path
        return None

    def _draw_rounded_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int,
        *,
        fill: str,
        outline: str,
    ) -> None:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=2)


class WubiApp:
    def __init__(self, repository: WubiRepository, topmost: bool = True, code_mode: str = "longest") -> None:
        self.repository = repository
        self.code_mode = code_mode
        self.root = tk.Tk()
        self.root.title("五笔字词查询")
        self.root.configure(bg="#faf7f2")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", topmost)

        width = 600
        height = 376
        screen_width = self.root.winfo_screenwidth()
        x = max(screen_width - width - 36, 24)
        self.root.geometry(f"{width}x{height}+{x}+48")

        self.topmost_var = tk.BooleanVar(value=topmost)
        self.query_var = tk.StringVar()
        self.code_var = tk.StringVar(value="编码：-")
        self.alt_var = tk.StringVar(value="其他编码：-")
        self.hit_var = tk.StringVar(value="命中结果：-")

        self._build_style()
        self._build_ui()
        self._bind_events()

    def _build_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#faf7f2")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("CardHost.TFrame", background="#faf7f2")
        style.configure("Heading.TLabel", background="#faf7f2", foreground="#1f1f1f", font=("Noto Sans CJK SC", 14, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#2a2a2a", font=("Noto Sans CJK SC", 11))
        style.configure("Mono.TLabel", background="#ffffff", foreground="#0e5530", font=("DejaVu Sans Mono", 13, "bold"))
        style.configure("Status.TLabel", background="#faf7f2", foreground="#666666", font=("Noto Sans CJK SC", 10))
        style.configure(
            "Query.TButton",
            font=("Noto Sans CJK SC", 11, "bold"),
            padding=(16, 8),
        )

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=16)
        container.pack(fill="both", expand=True)

        query_panel = ttk.Frame(container, style="Panel.TFrame", padding=14)
        query_panel.pack(fill="x", pady=(0, 10))

        entry = ttk.Entry(query_panel, textvariable=self.query_var, font=("Noto Sans CJK SC", 16))
        entry.pack(side="left", fill="x", expand=True)
        entry.focus_set()
        self.entry = entry

        ttk.Button(query_panel, text="查询", style="Query.TButton", command=self.search).pack(side="left", padx=(10, 0))
        ttk.Button(query_panel, text="清空", command=self.clear).pack(side="left", padx=(8, 0))

        result_panel = ttk.Frame(container, style="Panel.TFrame", padding=14)
        result_panel.pack(fill="x")

        ttk.Label(result_panel, textvariable=self.code_var, style="Mono.TLabel").pack(anchor="w")
        ttk.Label(result_panel, textvariable=self.alt_var, style="Body.TLabel").pack(anchor="w", pady=(0, 4))

        card_panel = ttk.Frame(container, style="App.TFrame")
        card_panel.pack(fill="x", pady=(14, 8))

        self.cards = [KeyCard(card_panel, self.repository) for _ in range(4)]
        for card in self.cards:
            card.pack(side="left", padx=(0, 10))

        ttk.Label(container, textvariable=self.hit_var, style="Status.TLabel").pack(anchor="w", pady=(2, 0))

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda _event: self.search())
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<Control-l>", lambda _event: self.clear())
        self.root.bind("<Control-f>", lambda _event: self.entry.focus_set())
        self.root.bind("<Control-t>", lambda _event: self._toggle_topmost())

    def _toggle_topmost(self) -> None:
        self.topmost_var.set(not self.topmost_var.get())
        self.root.attributes("-topmost", self.topmost_var.get())

    def clear(self) -> None:
        self.query_var.set("")
        self.code_var.set("编码：-")
        self.alt_var.set("其他编码：-")
        self.hit_var.set("命中结果：-")
        self.entry.focus_set()
        for card in self.cards:
            card.clear()

    def search(self) -> None:
        text = self.query_var.get().strip()
        if not text:
            self.clear()
            return

        result = self.repository.query(text, code_mode=self.code_mode)
        for card in self.cards:
            card.clear()

        if result is None or result.mode != "exact":
            self.code_var.set("编码：-")
            self.alt_var.set("其他编码：-")
            self.hit_var.set("命中结果：未命中")
            return

        self.code_var.set(f"编码：{result.main_code}")
        if result.other_codes:
            self.alt_var.set(f"其他编码：{' / '.join(result.other_codes)}")
        else:
            self.alt_var.set("其他编码：-")
        self.hit_var.set("命中结果：精确命中")
        for card, key in zip(self.cards, result.main_code[:4]):
            card.render(key)

    def run(self) -> None:
        self.root.mainloop()


def build_cli_result_text(result: QueryResult | None) -> str:
    if result is None:
        return "未找到可用编码。"
    lines = [
        f"字词：{result.text}",
        f"主显示编码：{result.main_code}",
        f"所有编码：{' / '.join(result.all_codes)}",
        f"结果类型：{'精确匹配' if result.mode == 'exact' else '规则推导'}",
        f"显示方式：{CODE_MODE_LABELS.get(result.code_mode, CODE_MODE_LABELS['preferred'])}",
        f"说明：{result.note}",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="五笔编码查询工具")
    parser.add_argument("--text", help="直接查询并在终端输出结果，不打开图形界面")
    parser.add_argument("--db", action="append", help="手动指定词库数据库路径，可传多次")
    parser.add_argument("--no-topmost", action="store_true", help="启动时取消窗口置顶")
    parser.add_argument(
        "--code-mode",
        choices=tuple(CODE_MODE_LABELS),
        default="longest",
        help="编码显示方式：preferred=推荐码，shortest=最短码，longest=最长码",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_paths = tuple(Path(path) for path in args.db) if args.db else None

    try:
        repository = WubiRepository(db_paths)
    except FileNotFoundError as exc:
        if args.text:
            print(str(exc))
            return
        messagebox.showerror("五笔字词查询", str(exc))
        return

    try:
        if args.text:
            print(build_cli_result_text(repository.query(args.text, code_mode=args.code_mode)))
            return

        app = WubiApp(repository, topmost=not args.no_topmost, code_mode=args.code_mode)
        app.run()
    finally:
        repository.close()


if __name__ == "__main__":
    main()
