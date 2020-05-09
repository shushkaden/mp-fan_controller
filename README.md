esptool.py --port /dev/cu.SLAB_USBtoUART erase_flash
esptool.py --chip esp32 --port /dev/cu.SLAB_USBtoUART --baud 460800 write_flash -z 0x1000 /Users/d_shushkevich/micropython/esp32/esp32-idf4-20191220-v1.12.bin

screen /dev/cu.SLAB_USBtoUART 115200


# check free space
import uos
fs_stat = uos.statvfs('/')
fs_size = fs_stat[0] * fs_stat[2]
fs_free = fs_stat[0] * fs_stat[3]
print("File System Size {:,} - Free Space {:,}".format(fs_size, fs_free))

uos.listdir('sensor_log')

# get log file
ampy get sensor_log/log_2020-05-03_21-40-50.csv sensor_log/log_2020-05-03_21-40-50.csv