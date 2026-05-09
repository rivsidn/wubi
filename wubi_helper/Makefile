APP_ID := wubi-helper
APP_WM_CLASS := Wubi-helper
APP_NAME := Tiger Wubi Helper
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
	@printf '%s\n' 'Available targets:'
	@printf '%s\n' '  make run        Run the GUI directly'
	@printf '%s\n' '  make test       Run unit tests'
	@printf '%s\n' '  make install    Install for the current user'
	@printf '%s\n' '  make uninstall  Uninstall from the current user'
	@printf '%s\n' '  make clean      Remove Python cache files'

run:
	$(PYTHON) wubi_helper.py

test:
	$(PYTHON) -m unittest -v

check-deps:
	@command -v $(PYTHON) >/dev/null
	@$(PYTHON) -c 'import tkinter; from PIL import Image, ImageTk'

install: install-app install-icons install-desktop
	@printf 'Installed: %s\n' '$(BINDIR)/$(APP_ID)'
	@printf 'Desktop entry: %s\n' '$(DESKTOPDIR)/$(APP_ID).desktop'

install-app: check-deps
	install -d '$(APPDIR)' '$(BINDIR)'
	rm -rf '$(APPDIR)/assets' '$(APPDIR)/wubi_pics' '$(APPDIR)/tiger_pics'
	rm -f '$(APPDIR)'/*.md
	install -m 755 wubi_helper.py '$(APPDIR)/wubi_helper.py'
	cp -R assets '$(APPDIR)/assets'
	cp -R wubi_pics '$(APPDIR)/wubi_pics'
	cp -R tiger_pics '$(APPDIR)/tiger_pics'
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
		'Comment=Look up Tiger and Wubi codes and show key roots' \
		'Exec=$(BINDIR)/$(APP_ID)' \
		'Icon=$(APP_ID)' \
		'Terminal=false' \
		'StartupWMClass=$(APP_WM_CLASS)' \
		'StartupNotify=true' \
		'Categories=Utility;' \
		'Keywords=Tiger;Huma;Wubi;Code;Input Method;Key Roots;' > '$(DESKTOPDIR)/$(APP_ID).desktop'
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
	@printf '%s\n' 'Uninstalled.'

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
