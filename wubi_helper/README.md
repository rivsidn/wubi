# 虎码/五笔查询小工具

这是一个桌面编码查询工具，默认用于查询虎码，也保留五笔 86、五笔 98 和新世纪五笔。特点：

- 小窗口、默认置顶，方便随手切回来查字词编码；
- 默认查询系统里的 `ibus-table` 虎码词库；
- 同一个字词存在多个编码时，默认主显示最长码/全码，方便学习拆码；
- 查询到编码后，会把主编码拆成最多 4 张键位图片展示；
- 五笔 86 读取系统 `ibus-table` 词库，五笔 98 和新世纪五笔使用内置码表；
- 五笔方案保留按词组规则推导编码；虎码方案只查数据库精确结果，未收录词显示未命中。

## 运行方式

```bash
python3 wubi_helper.py
```

默认方案是虎码，默认按“最长码”显示。例如虎码里 `中` 的主显示编码为 `dgs`，其他编码里会列出 `d`。

如果只想在终端里查一次：

```bash
python3 wubi_helper.py --text 中
python3 wubi_helper.py --text 虎码
python3 wubi_helper.py --text 中 --code-mode preferred
```

切换输入方案：

```bash
python3 wubi_helper.py --scheme tiger
python3 wubi_helper.py --scheme wubi86
python3 wubi_helper.py --scheme wubi98
python3 wubi_helper.py --scheme xinshiji
```

CLI 查询示例：

```bash
python3 wubi_helper.py --scheme wubi86 --text 中 --code-mode longest
python3 wubi_helper.py --scheme wubi98 --text 显 --code-mode longest
python3 wubi_helper.py --scheme xinshiji --text 显 --code-mode longest
```

旧参数 `--wubi-version` 仍可用，会自动映射到对应五笔方案：

```bash
python3 wubi_helper.py --wubi-version 86 --text 中
python3 wubi_helper.py --wubi-version 98 --text 显
python3 wubi_helper.py --wubi-version xinshiji --text 显
```

可用编码显示方式：

```bash
python3 wubi_helper.py --code-mode preferred
python3 wubi_helper.py --code-mode shortest
python3 wubi_helper.py --code-mode longest
```

## 数据库和码表

虎码直接依赖系统中已安装的 ibus-table 数据库，源码目录不需要 `tiger.db`。

虎码默认查找：

- `~/.local/share/ibus-table/tables/tiger-user.db`
- `/usr/share/ibus-table/tables/tiger.db`

五笔 86 默认查找：

- `~/.local/share/ibus-table/tables/wubi-jidian86-user.db`
- `/usr/share/ibus-table/tables/wubi-jidian86.db`
- `/usr/share/ibus-table/tables/wubi-haifeng86.db`

五笔 98 和新世纪五笔内置码表：

- 98 单字码表：`assets/wubi98-single.tsv`
- 新世纪五笔码表：`assets/wubi06.tsv`

如需临时指定数据库，可传 `--db`，可重复传多次：

```bash
python3 wubi_helper.py --scheme tiger --db /usr/share/ibus-table/tables/tiger.db --text 中
```

## 安装和卸载

安装到当前用户系统目录：

```bash
make install
```

安装后会创建：

- 命令行入口：`~/.local/bin/wubi-helper`
- 桌面应用入口：`~/.local/share/applications/wubi-helper.desktop`
- 应用资源目录：`~/.local/share/wubi-helper/`
- 多尺寸应用图标：`~/.local/share/icons/hicolor/*/apps/wubi-helper.png`

卸载：

```bash
make uninstall
```

## 快捷键

- `Enter`：查询
- `Ctrl+L`：清空
- `Ctrl+F`：把光标重新放回输入框
- `Esc`：退出程序
- `Ctrl+T`：切换窗口置顶

## 图片资源

- 虎码图片位于 `tiger_pics/`，由 `zigf.webp` 中的虎码字根图裁剪生成；运行时只依赖 `tiger_pics/`。
- 五笔 86 优先读取 `wubi_pics/86wubi/`。
- 五笔 98 优先读取 `wubi_pics/98wubi/`。
- 新世纪五笔优先读取 `wubi_pics/xinshiji_wubi/`。
- 程序会按编码字母找对应图片，比如 `D.png`、`G.png`、`S.png`。
- 如果某个键位没有对应图片，五笔会退回到程序内置字根卡片；虎码会显示“暂无字根”。

## 码表来源

- 98 单字码表：`assets/wubi98-single.tsv`
- 来源：[`yanhuacuo/98wubi-tables`](https://github.com/yanhuacuo/98wubi-tables) 的 `98五笔单字表-【单义】.txt`
- 上游许可：public domain / unencumbered software
- 新世纪五笔码表：`assets/wubi06.tsv`
- 来源：[`g178253/rime-wubi06`](https://github.com/g178253/rime-wubi06) 的 `wubi06.dict.yaml`
- 上游许可：Apache License 2.0，许可文本见 `assets/wubi06-LICENSE.txt`

## 依赖说明

- Python 3
- Tkinter
- Pillow
- 查询虎码需要本机已安装的 `ibus-table` 虎码词库数据库
- 查询五笔 86 需要本机已安装的 `ibus-table` 五笔 86 词库数据库
- 查询五笔 98、新世纪五笔不需要系统词库
