import hashlib
import json
import random
import socket
import sys

from PySide6 import QtCore
from PySide6 import QtUiTools
from PySide6 import QtWidgets
from guietta import Gui, _


def recvpkg(client: socket.socket) -> dict:
    # to receive a whole package
    end_flag = "EOP"
    recieved = ""
    while end_flag not in recieved:
        recieved += client.recv(1024).decode()
    return json.loads(recieved[:-3])


def sendpkg(client: socket.socket, msg: dict):
    # to send a whole package
    client.sendall(bytes(json.dumps(msg), "utf-8"))
    client.send(b"EOP")


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # some useful variables
        self.server_host = ("127.0.0.1", 1901)

        # open welcome.ui
        self.ui_file = QtCore.QFile("welcome.ui")
        if not self.ui_file.open(QtCore.QIODevice.ReadOnly):
            print(f"Cannot open welcome.ui: {self.ui_file.errorString()}")
            sys.exit(-1)

        # load welcome.ui and close it
        self.loader = QtUiTools.QUiLoader()
        self.window = self.loader.load(self.ui_file)
        self.ui_file.close()
        # if window isn't opened, then exit.
        if not self.window:
            print(self.loader.errorString())
            sys.exit(-1)

        # connect something
        self.window.cheer.clicked.connect(self.sqp_say_sth)
        self.window.register_account.clicked.connect(self.register)
        self.window.login.clicked.connect(self.login)
        self.window.del_account.clicked.connect(self.delete)
        self.window.dev_options.clicked.connect(self.dev_options_configuration)

    @QtCore.Slot()
    def sqp_say_sth(self):
        self.window.spq_word.setText(random.choice([
            "起来了啊，把内务和卫生都做好了再走啊！",
            "起起起！",
            "起不来都是借口。",
            "没完了是吧？！",
            "没完了在哪里！"
        ]))

    @QtCore.Slot()
    def register(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect(self.server_host)
        except ConnectionRefusedError:
            Gui(["服务器起不来了！"]).run()
        else:
            sendpkg(server, {"status": "register", "username": username,
                             "password": hashlib.sha512(bytes(password, 'utf-8')).hexdigest()})
            package = recvpkg(server)
            if package["status"] == "success":
                Gui(["你起来了。"],
                    ["（注册成功）"]).run()
            else:
                Gui(["你起不来。"],
                    ["（注册失败）"]).run()

    @QtCore.Slot()
    def login(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect(self.server_host)
        except ConnectionRefusedError:
            Gui(["服务器起不来了！"]).run()
        else:
            sendpkg(server, {"status": "login", "username": username,
                             "password": hashlib.sha512(bytes(password, 'utf-8')).hexdigest()})
            package = recvpkg(server)
            if package["status"] == "success":
                Gui(["你要去饭堂？饭堂还没开mer呢！"],
                    ["（游戏正在开发中）"]).run()
            else:
                Gui(["你被司普青拦住了：“现在还没到时间。”"],
                    ["（注册失败）"]).run()

    @QtCore.Slot()
    def delete(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect(self.server_host)
        except ConnectionRefusedError:
            Gui(["服务器起不来了！"]).run()
        else:
            sendpkg(server, {"status": "delete", "username": username,
                             "password": hashlib.sha512(bytes(password, 'utf-8')).hexdigest()})
            package = recvpkg(server)
            if package["status"] == "success":
                Gui(["你又睡下了。"],
                    ["（删除账号成功）"]).run()
            else:
                Gui(["你被司普青又叫起来了。"],
                    ["（删除账号失败）"]).run()

    def assingment(self, gui, *args):
        self.server_host = (gui.ip, int(gui.port))

    @QtCore.Slot()
    def dev_options_configuration(self):
        gui = Gui(["开发者工具"],
                  ["服务器IP：", "__ip__"],
                  ["服务器端口号：", "__port__"],
                  [["ensure"]])
        gui.ip, gui.port = self.server_host
        gui.events([_],
                   [_, _],
                   [_, _],
                   [self.assingment])
        gui.run()


if __name__ == '__main__':
    # initialize the application
    app = QtWidgets.QApplication(sys.argv)

    window = MyWindow()
    window.window.show()

    sys.exit(app.exec_())
