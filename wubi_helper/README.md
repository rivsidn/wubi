# 五笔查询小工具

这是一个按 `需求说明.md` 实现的桌面小工具，特点：

- 小窗口、默认置顶，方便随手切回来查字词编码；
- 优先查询系统里的 `ibus-table` 五笔 86 词库；
- 查到编码后，会把主编码拆成最多 4 张字根图片展示，优先读取 `wubi_pics/` 里的自定义图片；
- 可以通过命令行参数切换显示推荐码、最短码、最长码，适合学习阶段看全码；
- 如果词库里没有这个词，会按 `打字规则.md` 里的词组规则自动推导编码。

## 需求里还可以补充的点

当前文档已经足够做一个可用版本，但如果后面要继续迭代，建议再明确这几项：

1. 使用哪套词库/哪一版五笔
   - 当前实现默认使用 `wubi-jidian86.db`，找不到时再尝试其他已安装的 86 版词库。
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

如果想切换显示方式，可以在启动时指定：

```bash
python3 wubi_helper.py --code-mode preferred
python3 wubi_helper.py --code-mode shortest
python3 wubi_helper.py --code-mode longest
```

如果只想在终端里查一次：

```bash
python3 wubi_helper.py --text 中
python3 wubi_helper.py --text 五笔编码
python3 wubi_helper.py --text 中 --code-mode longest
```

## 快捷键

- `Enter`：查询
- `Ctrl+L`：清空
- `Ctrl+F`：把光标重新放回输入框
- `Esc`：退出程序
- `Ctrl+T`：切换窗口置顶

## 图片资源

- 程序会按编码字母去 `wubi_pics/` 目录找对应图片，比如 `K.png`、`T.png`
- 当前优先匹配大写文件名，支持 `png/jpg/jpeg/webp`
- 如果某个键位没找到对应图片，会退回到程序内置的字根卡片样式

## 依赖说明

- Python 3
- Tkinter
- 本机已安装的 `ibus-table` 五笔词库数据库

当前环境里使用到的数据库通常位于：

- `/usr/share/ibus-table/tables/wubi-jidian86.db`
- `~/.local/share/ibus-table/tables/wubi-jidian86-user.db`
