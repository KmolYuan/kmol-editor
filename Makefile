# Pyslvs Makefile

# author: Yuan Chang
# copyright: Copyright (C) 2016-2018
# license: AGPL
# email: pyslvs@gmail.com

all: test

ifeq ($(OS),Windows_NT)
    PYVER = $(shell python -c "import sys; print('{v[0]}{v[1]}'.format(v=list(sys.version_info[:2])))")
    PYSLVSVER = $(shell python -c "from core.info import __version__; print(\"{}.{:02}.{}\".format(*__version__))")
    COMPILERVER = $(shell python -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())")
    SYSVER = $(shell python -c "import platform; print(platform.machine().lower())")
else
    PYVER = $(shell python3 -c "import sys; print('{v[0]}{v[1]}'.format(v=list(sys.version_info[:2])))")
    PYSLVSVER = $(shell python3 -c "from core.info import __version__; print(\"{}.{:02}.{}\".format(*__version__))")
    COMPILERVER = $(shell python3 -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())")
    SYSVER = $(shell python3 -c "import platform; print(platform.machine().lower())")
endif
EXENAME = kmol-editor-$(PYSLVSVER).$(COMPILERVER)-$(SYSVER)

build: launch_kmol.py
	@echo ---Kmol Editor Build---
ifeq ($(OS),Windows_NT)
	pyinstaller -w -F $< -i ./icons/kmol.ico -n "Kmol Editor" \
--hidden-import=PyQt5 \
--hidden-import=PyQt5.sip \
--hidden-import=PyQt5.QtPrintSupport
	rename ".\dist\Kmol Editor.exe" $(EXENAME).exe
else ifeq ($(shell uname),Darwin)
	pyinstaller -w -F $< -i ./icons/kmol.icns -n "Kmol Editor"
	mv "dist/Kmol Editor" dist/$(EXENAME)
	chmod +x dist/$(EXENAME)
	mv "dist/Kmol Editor.app" dist/$(EXENAME).app
	zip -r dist/$(EXENAME).app.zip dist/$(EXENAME).app
else
	bash ./appimage_recipe.sh
endif
	@echo ---Done---

test: build
ifeq ($(OS),Windows_NT)
	./dist/$(EXENAME) --test
else ifeq ($(shell uname),Darwin)
	./dist/$(EXENAME) --test
else
	$(eval APPIMAGE = $(shell ls -1 out))
	./out/$(APPIMAGE) --test
endif

clean:
ifeq ($(OS),Windows_NT)
	-rd build /s /q
	-rd dist /s /q
	-del launch_kmol.spec
else ifeq ($(shell uname),Darwin)
	-rm -f -r build
	-rm -f -r dist
	-rm -f *.spec
else
	-rm -f -r ENV
	-rm -f -r out
endif
