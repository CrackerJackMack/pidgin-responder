#!/usr/bin/env python
# -*- coding: UTF8 -*-

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gobject
import re
import time
import random
#from pprint import pprint as pp


class YoloBot(object):
    def __init__(self, dbus_session):
        self._bus = dbus_session
        self.purple = None
        self.last_yolo = {}
        self.timer = 900  # seconds
        self.conversation = {}
        self.throttle = []
        self.regexs = {}

        obj = self._bus.get_object(
                "im.pidgin.purple.PurpleService",
                "/im/pidgin/purple/PurpleObject")
        self.purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

        self._register_chat()

    def get_chat(self, conversation):
        if conversation in self.conversation:
            return self.conversation[conversation]

        self.conversation[conversation] = \
                self.purple.PurpleConversationGetChatData(conversation)
        return self.conversation[conversation]

    def _register_chat(self):
        self._bus.add_signal_receiver(
            self.recv_chat_message,
            dbus_interface="im.pidgin.purple.PurpleInterface",
            signal_name="ReceivedChatMsg")

    def recv_chat_message(self, account, sender, message, conversation, flags):
        if conversation not in self.last_yolo:
            self.last_yolo[conversation] = 0

        for search, options in self.regexs.iteritems():
            if re.search(search, message, flags=re.I):
                self.yolo_cast(conversation, search, options,
                        throttle=lambda: search in self.throttle)

    def yolo_cast(self, conv_id, search, options, throttle=False):
        now = time.time()
        if throttle and (now - self.last_yolo.get(search, 0)) >= self.timer:
            # Maybe...
            if random.choice([True, False]):
                return
            self.last_yolo[search] = now

        conv = self.get_chat(conv_id)
        self.purple.PurpleConvChatSend(conv, random.choice(options))

    def register(self, search, options, throttle=False):
        self.regexs[search] = options
        if throttle:
            self.throttle.append(search)


def main():
    DBusGMainLoop(set_as_default=True)
    session = dbus.SessionBus()
    loop = gobject.MainLoop()

    yolos = []
    with open('yolo.txt', 'rb') as yblock:
        yolos.append(yblock.read())
    yolos.append(u'Y̬̱̲̱͇̬̙ͩͯͩ̀͐ͯͮO̴̷̙ͦͯ̈́ͨͩḼ̝̟̻̍ͭO͔̟͓̎͊̅͊ͥ͡')
    yolos.append(u'You Only YOLO Once!')

    thanks = [
        u'Anytime!',
        u"you're welcome",
        u'all in a days work',
        u'you bet!'
    ]

    y = YoloBot(session)
    y.register("#?yolo", yolos, throttle=True)
    y.register("thanks?|thx", thanks)

    print("Running")
    loop.run()


if __name__ == "__main__":
    main()
