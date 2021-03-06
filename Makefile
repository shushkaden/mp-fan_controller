TTY=/dev/cu.SLAB_USBtoUART
FIRMWARE=/Users/d_shushkevich/micropython/esp32/esp32-idf4-20191220-v1.12.bin
SRCDIR = src
SRCDIRS = $(shell find ${SRCDIR} ! -path ${SRCDIR} -type d | cut -d'/' -f2- | sort)
SRCFILES = $(shell find ${SRCDIR} -type f | cut -d'/' -f2- | sort)

ls: killscreen
	ampy ls -r

upload: killscreen
	for dir in ${SRCDIRS} ; do \
		echo "mkdir " $${dir}; \
		ampy mkdir $${dir} --exists-okay; \
	done
	for file in ${SRCFILES} ; do \
		echo "Uploading " $${file}; \
		ampy put ${SRCDIR}/$${file} $${file}; \
	done

uploadmain: killscreen
	ampy put ${SRCDIR}/main.py main.py

uploadsettings: killscreen
	ampy put ${SRCDIR}/settings.py settings.py

uploadweb:
	for file in ${SRCFILES} ; do \
		./webrepl_cli.py -p 1111 ${SRCDIR}/$${file} 192.168.4.1:/$${file}; \
	done

uploadmainweb:
	./webrepl_cli.py -p 1111 ${SRCDIR}/main.py 192.168.4.1:/main.py

erase: killscreen
	esptool.py --port $(TTY) erase_flash

write_flash: killscreen
	esptool.py --port $(TTY) erase_flash
	esptool.py --chip esp32 --port $(TTY) --baud 460800 write_flash -z 0x1000 $(FIRMWARE)

# use this to connect to the serial port
# to exit the screen, ctrl-A k
# DO NOT USE ctrl-A d, else the tty stays busy
screen:
	screen -S upython $(TTY) 115200

killscreen:
	@if screen -ls | grep -q upython; then screen -X -S upython quit; fi
