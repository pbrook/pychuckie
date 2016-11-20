ZIPFILE = chuckie.zip
INSTALLDIR = /media/$(USER)/PYBFLASH/apps/pbrook~ChuckieEgg

SRC = $(shell cat manifest)

all: $(ZIPFILE)

$(ZIPFILE): manifest $(SRC)
	rm -f $(ZIPFILE)
	cat manifest | zip -@ $(ZIPFILE)

install: $(ZIPFILE)
	mkdir -p $(INSTALLDIR)
	unzip -o $(ZIPFILE) -d $(INSTALLDIR)
	sync

foo:
	echo $(FOO)
