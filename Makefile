# Pyslvs Makefile

# author: Yuan Chang
# copyright: Copyright (C) 2016-2018
# license: AGPL
# email: pyslvs@gmail.com

all: test

build: launch_kmol.py core/*.py
	@echo ---Kmol Editor Build---
ifeq ($(OS),Windows_NT)
	pyinstaller -w -F $< -i ./icons/kmol.ico \
--hidden-import=PyQt5 \
--hidden-import=PyQt5.sip \
--hidden-import=PyQt5.QtPrintSupport
	$(eval VERSION = $(shell python -c "from core.info import __version__; print(__version__)"))
	$(eval COMPILERVERSION = $(shell python -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())"))
	$(eval SYSVERSION = $(shell python -c "import platform; print(platform.machine().lower())"))
	rename .\dist\launch_kmol.exe kmol-editor-$(VERSION).$(COMPILERVERSION)-$(SYSVERSION).exe
else
	bash ./appimage_recipe.sh
endif
	@echo ---Done---

test: build
ifeq ($(OS),Windows_NT)
	$(eval EXE = $(shell dir dist /b))
	./dist/$(EXE) --test
else
	$(eval APPIMAGE = $(shell ls -1 out))
	./out/$(APPIMAGE) --test
endif

clean:
ifeq ($(OS),Windows_NT)
	-rd build /s /q
	-rd dist /s /q
	-del launch_kmol.spec
else
	-rm -f -r ENV
	-rm -f -r out
endif
