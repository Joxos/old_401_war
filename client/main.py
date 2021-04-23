import json
import random
import socket
import sys

from PySide6 import QtCore
from PySide6 import QtUiTools
from PySide6 import QtWidgets


def recvpkg(client: socket.socket) -> dict:
    # to receive a whole package
    end_flag = b"EOP"
    recieved = ""
    while end_flag not in recieved:
        recieved += client.recv(1024).decode()
    return json.loads(recieved[:-3])


def sendpkg(client: socket.socket, msg: dict):
    # to send a whole package
    client.sendall(bytes(json.dumps(msg)))
    client.send(b"EOP")


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # some useful variables
        self.server_host = ("0.0.0.0", 1901)

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

    @QtCore.Slot()
    def sqp_say_sth(self):
        self.window.spq_word.setText(random.choice([
            "起来了啊，把内务和卫生都做好了再走啊！",
            "起起起！",
            "起不来都是借口。",
            "没完了是吧？！",
            "你没签？那你漏了啊！",
            "没完了在哪里！"
        ]))

    @QtCore.Slot()
    def register(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(self.server_host)
        sendpkg(server, {"status": "register", "username": username, "password": password})
        package = recvpkg(server)
        if package["status"] == "success":
            print("Right!")
        else:
            print("Failed!")

    @QtCore.Slot()
    def login(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(self.server_host)
        sendpkg(server, {"status": "login", "username": username, "password": password})
        package = recvpkg(server)
        if package["status"] == "success":
            print("Right!")
        else:
            print("Failed!")

    @QtCore.Slot()
    def delete(self):
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(self.server_host)
        sendpkg(server, {"status": "delete", "username": username, "password": password})
        package = recvpkg(server)
        if package["status"] == "success":
            print("Right!")
        else:
            print("Failed!")


if __name__ == '__main__':
    # initialize the application
    app = QtWidgets.QApplication(sys.argv)

    window = MyWindow()
    window.window.show()

    sys.exit(app.exec_())
