#!/usr/bin/env python

import os
import re
import sleekxmpp
import socket
import sys
import time

import config


def FilterBadChars(s):
    s = re.sub('\x03[0-9]{1,2}(,[0-9]{1,2})?|[\x02\x03\x0f\x16\x1d\x1f]', '', s)
    return re.sub('[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f]', '\ufffd', s)


class XMPPBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        try:
            if msg['type'] not in ('chat', 'normal'):
                return
            if " (IRC): " in msg["body"]:
                return

            from_jid = msg['from'].bare
            for i in config.XMPP['forward']:
                if i[0] == from_jid:
                    for l in msg['body'].splitlines():
                        sys.stderr.write('< %s\n' % l)
                        xmpp.send_message(mto=i[1], mbody=msg, mtype='chat')
        except UnicodeEncodeError:
            pass
        except socket.error:
            try:
                self.disconnect(wait=True)
            except:
                pass
            time.sleep(10)
            sys.stderr.write("Restarting...\n")
            try:
                os.execlp("python3", "python3", __file__)
            except:
                os.execlp("python", "python", __file__)
        except Exception as e:
            sys.stderr.write('Exception: %s\n' % e)

if __name__ == '__main__':
    try:
        xmpp = XMPPBot(config.XMPP['JID'], config.XMPP['password'])
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0004')  # Data Forms
        xmpp.register_plugin('xep_0060')  # PubSub
        xmpp.register_plugin('xep_0199')  # XMPP Ping
        if xmpp.connect((config.XMPP['server'], config.XMPP['port'])):
            xmpp.process(block=False)
        else:
            exit()
        else:
            raise socket.error
    except KeyboardInterrupt:
        xmpp.disconnect(wait=True)
    except UnicodeEncodeError:
        pass
    except SystemExit:
        raise
    except socket.error:
        try:
            xmpp.disconnect(wait=True)
        except:
            pass
        time.sleep(10)
        sys.stderr.write("Restarting...\n")
        try:
            os.execlp("python3", "python3", __file__)
        except:
            os.execlp("python", "python", __file__)
    except Exception as e:
        sys.stderr.write('Exception: %s\n' % e)

# vim: et ft=python sts=4 sw=4 ts=4
