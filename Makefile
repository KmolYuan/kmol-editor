# Pyslvs Makefile

# author: Yuan Chang
# copyright: Copyright (C) 2016-2018-2019
# license: AGPL
# email: pyslvs@gmail.com

all: test

ifeq ($(OS),Windows_NT)
    PYVER = $(shell python -c "import sys; print('{v[0]}{v[1]}'.format(v=list(sys.version_info[:2])))")
    EDITORVER = $(shell python -c "from core.info import __version__; print(__version__)")
    COMPILERVER = $(shell python -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())")
    SYSVER = $(shell python -c "import platform; print(platform.machine().lower())")
    SPELLPATH = $(shell python -c "import spellchecker; print(spellchecker.__path__[0])")
else
    PYVER = $(shell python3 -c "import sys; print('{v[0]}{v[1]}'.format(v=list(sys.version_info[:2])))")
    EDITORVER = $(shell python3 -c "from core.info import __version__; print(__version__)")
    COMPILERVER = $(shell python3 -c "import platform; print(''.join(platform.python_compiler().split(\" \")[:2]).replace('.', '').lower())")
    SYSVER = $(shell python3 -c "import platform; print(platform.machine().lower())")
    SPELLPATH = $(shell python3 -c "import spellchecker; print(spellchecker.__path__[0])")
endif
EXENAME = kmol-editor-$(EDITORVER).$(COMPILERVER)-$(SYSVER)


build: launch_kmol.py
	@echo ---Kmol Editor Build---
ifeq ($(OS),Windows_NT)
	pyinstaller -w -F $< -i ./icons/kmol.ico -n "Kmol Editor" \
--hidden-import=PyQt5.QtPrintSupport \
--add-data=$(SPELLPATH)\resources;spellchecker\resources
	rename ".\dist\Kmol Editor.exe" $(EXENAME).exe
else ifeq ($(shell uname),Darwin)
	pyinstaller -w -F $< -i ./icons/kmol.icns -n "Kmol Editor" \
--hidden-import=PyQt5.QtPrintSupport \
--add-data=$(SPELLPATH)/resources:spellchecker/resources
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
	-del *.spec
else ifeq ($(shell uname),Darwin)
	-rm -f -r build
	-rm -f -r dist
	-rm -f *.spec
else
	-rm -f -r ENV
	-rm -f -r out
endif
