SRCDIR = src
SRCFILES = $(shell ls ${SRCDIR})

ls:
	ampy ls -r

upload:
	for file in ${SRCFILES} ; do \
		echo "Uploading " $${file}; \
		ampy put ${SRCDIR}/$${file} $${file}; \
	done

uploadmain:
	ampy put ${SRCDIR}/main.py main.py
