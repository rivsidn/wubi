APP_ID := wubi-helper
APP_NAME := 五笔查询助手
PYTHON ?= python3
PREFIX ?= $(HOME)/.local
BINDIR := $(PREFIX)/bin
DATADIR := $(PREFIX)/share
APPDIR := $(DATADIR)/$(APP_ID)
DESKTOPDIR := $(DATADIR)/applications
ICONDIR := $(DATADIR)/icons/hicolor
ICON_SIZES := 16 24 32 48 64 128 256 512

.PHONY: all help run test install uninstall install-app install-icons install-desktop check-deps clean

all: help

help:
	@printf '%s\n' '可用命令:'
	@printf '%s\n' '  make run        直接运行图形界面'
	@printf '%s\n' '  make test       运行单元测试'
	@printf '%s\n' '  make install    安装到当前用户系统目录'
	@printf '%s\n' '  make uninstall  从当前用户系统目录卸载'
	@printf '%s\n' '  make clean      清理 Python 缓存'

run:
	$(PYTHON) wubi_helper.py

test:
	$(PYTHON) -m unittest -v

check-deps:
	@command -v $(PYTHON) >/dev/null
	@$(PYTHON) -c 'import tkinter; from PIL import Image, ImageTk'

install: install-app install-icons install-desktop
	@printf '已安装：%s\n' '$(BINDIR)/$(APP_ID)'
	@printf '桌面入口：%s\n' '$(DESKTOPDIR)/$(APP_ID).desktop'

install-app: check-deps
	install -d '$(APPDIR)' '$(BINDIR)'
	rm -rf '$(APPDIR)/assets' '$(APPDIR)/wubi_pics'
	rm -f '$(APPDIR)/README.md' '$(APPDIR)/需求说明.md'
	install -m 755 wubi_helper.py '$(APPDIR)/wubi_helper.py'
	cp -R assets '$(APPDIR)/assets'
	cp -R wubi_pics '$(APPDIR)/wubi_pics'
	printf '%s\n' '#!/bin/sh' \
		'exec $(PYTHON) "$(APPDIR)/wubi_helper.py" "$$@"' > '$(BINDIR)/$(APP_ID)'
	chmod 755 '$(BINDIR)/$(APP_ID)'

install-icons:
	@for size in $(ICON_SIZES); do \
		install -d '$(ICONDIR)'/$${size}x$${size}/apps; \
		install -m 644 assets/icons/wubi-helper-icon-$${size}.png '$(ICONDIR)'/$${size}x$${size}/apps/$(APP_ID).png; \
	done
	install -d '$(ICONDIR)'/scalable/apps
	install -m 644 assets/wubi-helper-icon-concept.svg '$(ICONDIR)'/scalable/apps/$(APP_ID).svg
	@command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -t -f '$(ICONDIR)' >/dev/null 2>&1 || true

install-desktop: install-app
	install -d '$(DESKTOPDIR)'
	printf '%s\n' \
		'[Desktop Entry]' \
		'Type=Application' \
		'Name=$(APP_NAME)' \
		'Name[zh_CN]=$(APP_NAME)' \
		'Comment=查询五笔字词编码并显示字根' \
		'Exec=$(BINDIR)/$(APP_ID)' \
		'Icon=$(APP_ID)' \
		'Terminal=false' \
		'StartupNotify=true' \
		'Categories=Utility;' \
		'Keywords=五笔;Wubi;编码;字根;' > '$(DESKTOPDIR)/$(APP_ID).desktop'
	chmod 644 '$(DESKTOPDIR)/$(APP_ID).desktop'
	@command -v update-desktop-database >/dev/null && update-desktop-database '$(DESKTOPDIR)' >/dev/null 2>&1 || true

uninstall:
	rm -f '$(BINDIR)/$(APP_ID)'
	rm -f '$(DESKTOPDIR)/$(APP_ID).desktop'
	rm -rf '$(APPDIR)'
	@for size in $(ICON_SIZES); do \
		rm -f '$(ICONDIR)'/$${size}x$${size}/apps/$(APP_ID).png; \
	done
	rm -f '$(ICONDIR)'/scalable/apps/$(APP_ID).svg
	@command -v update-desktop-database >/dev/null && update-desktop-database '$(DESKTOPDIR)' >/dev/null 2>&1 || true
	@command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -t -f '$(ICONDIR)' >/dev/null 2>&1 || true
	@printf '%s\n' '已卸载。'

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
