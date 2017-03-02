#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import sys
import telnetlib
import uao_decode
from time import sleep


HOST = "ptt.cc"


def get_account():
    uid = raw_input("Enter ur ptt id: ")
    pw = getpass.getpass()

    return {'id': uid, 'password': pw}


def ptt_to_utf8(ptt_msg):
    return ptt_msg.decode('uao_decode').encode('utf8')


class PttIo:
    def __init__(self, tn, user, time_limit):
        self.tn = tn
        self.account = user['id']
        self.password = user['password']
        self.time_limit = time_limit
        self.buffer = ''

    def clear_buffer(self):
        self.buffer = ''

    def expect_action(self, expected, res):
        msg, buf, telnet = '', self.buffer, self.tn
        step = 1

        for _ in xrange(0, self.time_limit, step):
            sleep(step)
            buf += telnet.read_very_eager()
            msg = ptt_to_utf8(buf)

            if expected in msg:
                print msg
                enter_msg(self.tn, res)

                self.clear_buffer()
                return

        print msg
        timeout_exit()

    def optional_expect(self, expected_acts):
        buf, telnet = self.buffer, self.tn
        step = 1

        for _ in xrange(0, self.time_limit, step):
            sleep(step)
            buf += telnet.read_very_eager()
            msg = ptt_to_utf8(buf)

            matched = [x for x in expected_acts if x[0] in msg]
            if matched:
                print msg
                enter_msg(self.tn, matched[0][1])
                self.clear_buffer()
                return

        self.buffer = buf

    def login(self):
        self.expect_action("註冊", self.account)
        self.expect_action("請輸入您的密碼", self.password)

    def give_money(self, name, money):
        # Assert in ptt store page
        self.expect_action("給其他人Ptt幣", '0')
        self.expect_action("這位幸運兒的id", name)
        self.expect_action("請輸入金額", money)
        self.optional_expect([["請輸入您的密碼", self.password]])
        self.expect_action("要修改紅包袋嗎", 'n')
        self.expect_action("按任意鍵繼續", '')


def enter_msg(tn, msg):
    tn.write(msg + "\r\n")


def timeout_exit():
    print "Can not get response in time."
    exit()


def main():
    user = get_account()
    tn = telnetlib.Telnet(HOST)

    ptt = PttIo(tn, user, 5)

    ptt.login()

    ptt.optional_expect([["請按任意鍵繼續", ""],
                         ["刪除其他", "y"]])

    ptt.optional_expect([["錯誤嘗試的記錄", "y"]])

    print '....'

    ptt.expect_action("主功能表", 'p')
    ptt.expect_action("網路遊樂場", 'p')

    ptt.give_money('lintsu', '10')

    while True:
        sleep(1)
        buf = tn.read_very_eager()
        msg = ptt_to_utf8(buf)
        print msg


if __name__ == '__main__':
    main()
