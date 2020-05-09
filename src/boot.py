# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import webrepl
webrepl.start()

import network
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
