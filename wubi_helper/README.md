# 五笔查询小工具

这是一个按 `需求说明.md` 实现的桌面小工具，特点：

- 小窗口、默认置顶，方便随手切回来查字词编码；
- 默认查询 98 版五笔，内置 98 单字码表，所以不依赖系统安装 98 词库；
- 也可以切换到 86 版，读取系统里的 `ibus-table` 五笔 86 词库；
- 查到编码后，会把主编码拆成最多 4 张字根图片展示，优先读取 `wubi_pics/` 里的自定义图片；
- 可以通过命令行参数切换显示推荐码、最短码、最长码，适合学习阶段看全码；
- 如果词库里没有这个词，会按 `打字规则.md` 里的词组规则自动推导编码。

## 需求里还可以补充的点

当前文档已经足够做一个可用版本，但如果后面要继续迭代，建议再明确这几项：

1. 使用哪套词库/哪一版五笔
   - 当前实现默认使用内置 98 单字码表；如需 86 版，可通过 `--wubi-version 86` 使用 `wubi-jidian86.db` 等系统词库。
2. 一个字/词存在多个编码时怎么展示
   - 当前实现主显示推荐码，同时在“其他编码”里列出剩余可用编码。
3. 词库里查不到时怎么处理
   - 当前实现会按 `打字规则.md` 的词组规则，用单字全码自动推导。
4. 交付形式
   - 当前实现是 Python 脚本，不是打包后的独立可执行文件。

## 运行方式

```bash
python3 wubi_helper.py
```

默认会按“最长码”显示，方便练习全码。

默认查询 98 版五笔。例如：

```bash
python3 wubi_helper.py --text 显 --code-mode longest
```

会返回 98 版全码 `jof`。如果需要查 86 版，可以指定：

```bash
python3 wubi_helper.py --text 显 --code-mode longest --wubi-version 86
```

如果想切换显示方式，可以在启动时指定：

```bash
python3 wubi_helper.py --code-mode preferred
python3 wubi_helper.py --code-mode shortest
python3 wubi_helper.py --code-mode longest
python3 wubi_helper.py --wubi-version 86
```

如果只想在终端里查一次：

```bash
python3 wubi_helper.py --text 中
python3 wubi_helper.py --text 五笔编码
python3 wubi_helper.py --text 中 --code-mode longest
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

- 程序会按编码字母去 `wubi_pics/` 目录找对应图片，比如 `K.png`、`T.png`
- 98 版优先读取 `wubi_pics/98wubi/`，86 版优先读取 `wubi_pics/86wubi/`
- 当前优先匹配大写文件名，支持 `png/jpg/jpeg/webp`
- 如果某个键位没找到对应图片，会退回到程序内置的字根卡片样式

## 码表来源

- 98 单字码表：`assets/wubi98-single.tsv`
- 来源：[`yanhuacuo/98wubi-tables`](https://github.com/yanhuacuo/98wubi-tables) 的 `98五笔单字表-【单义】.txt`
- 上游许可：public domain / unencumbered software

## 依赖说明

- Python 3
- Tkinter
- Pillow
- 查询 98 版单字不需要系统词库；查询 86 版需要本机已安装的 `ibus-table` 五笔词库数据库

86 版数据库通常位于：

- `/usr/share/ibus-table/tables/wubi-jidian86.db`
- `~/.local/share/ibus-table/tables/wubi-jidian86-user.db`
