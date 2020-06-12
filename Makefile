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

uploadweb:
	for file in ${SRCFILES} ; do \
		./webrepl_cli.py -p 1111 ${SRCDIR}/$${file} 192.168.4.1:/$${file}; \
	done

uploadmainweb:
	./webrepl_cli.py -p 1111 ${SRCDIR}/main.py 192.168.4.1:/main.py
