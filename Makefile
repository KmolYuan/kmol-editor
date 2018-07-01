#Pyslvs Makefile

#author: Yuan Chang
#copyright: Copyright (C) 2016-2018
#license: AGPL
#email: pyslvs@gmail.com

all: build

build: launch_kmol.py
	@echo ---Kmol Editor Build---
ifeq ($(OS),Windows_NT)
	pyinstaller -F $< -i ./icons/kmol.ico --hidden-import=PyQt5
	$(eval VERSION = $(shell python -c "from core.info import __version__; print(__version__)"))
	$(eval COMPILERVERSION = $(shell python -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())"))
	$(eval SYSVERSION = $(shell python -c "import platform; print(platform.machine().lower())"))
	rename .\dist\launch_kmol.exe kmol-editor-$(VERSION).$(COMPILERVERSION)-$(SYSVERSION).exe
else
	bash ./appimage_recipe.sh
endif
	@echo ---Done---

clean:
ifeq ($(OS),Windows_NT)
	-rd build /s /q
	-rd dist /s /q
	-del launch_kmol.spec
else
	-rm -f -r ENV
	-rm -f -r out
endif
