from machine import Pin


class Button:
    pin = None
    value = 1
    action = None

    def __init__(self, pin, action):
        self.action = action
        self.pin = Pin(pin, Pin.IN)
        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.callback)

    def callback(self, _):
        new_value = self.pin.value()
        if self.value == 1 and new_value == 0:
            self.action()

        self.value = new_value

# USAGE
""""
from button import Button

button_pin = 36

def print_message():
    print('Message')

Button(button_pin, print_message)
"""


class Toggle:
    pin = None
    value = 1
    action = None
    cancel_action = None

    def __init__(self, pin, action, cancel_action):
        self.action = action
        self.cancel_action = cancel_action
        self.pin = Pin(pin, Pin.IN)
        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.callback)

    def callback(self, _):
        new_value = self.pin.value()
        if self.value == 1 and new_value == 0:
            self.action()

        if self.value == 0 and new_value == 1:
            self.cancel_action()

        self.value = new_value


# USAGE
""""
from button import Toggle

toggle_pin = 36

def print_123():
    print('123')

def print_abc():
    print('abc')

Toggle(toggle_pin, print_123, print_abc)
"""