import asyncio
import hashlib
import json
import random
import sys

from PySide6 import QtCore
from PySide6 import QtUiTools
from PySide6 import QtWidgets
from guietta import Gui, _


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

        # load welcome.ui and close the file
        self.loader = QtUiTools.QUiLoader()
        self.window = self.loader.load(self.ui_file)
        self.ui_file.close()
        # if window isn't opened or is empty, then exit.
        if not self.window:
            print(self.loader.errorString())
            sys.exit(-1)

        # connect some buttons
        self.window.cheer.clicked.connect(self.sqp_say_sth)
        self.window.register_account.clicked.connect(self.register)
        self.window.login.clicked.connect(self.login)
        self.window.del_account.clicked.connect(self.delete)
        self.window.dev_options.clicked.connect(self.dev_options_configuration)

    async def auth(self, auth_type):
        """Get and authoricate the account information."""
        reader, writer = await asyncio.open_connection(self.server_host[0], self.server_host[1])
        username = self.window.username_input.toPlainText()
        password = self.window.passwd_input.toPlainText()
        writer.write(json.dumps({"status": auth_type, "username": username,
                                 "password": hashlib.sha512(bytes(password, "utf-8")).hexdigest()}).encode("utf-8"))
        data = await reader.read(1000)
        writer.close()
        package = json.loads(data.decode())
        # give a message to the user
        if package['status'] == "success":
            if auth_type == "register":
                Gui(["你起来了。"],
                    ["（注册成功）"]).run()
            elif auth_type == "login":
                Gui(["你要去饭堂？饭堂还没开mer呢！"],
                    ["（游戏正在开发中）"]).run()
            elif auth_type == "delete":
                Gui(["你又睡下了。"],
                    ["（删除账号成功）"]).run()
        elif package['status'] == "failed":
            if auth_type == "register":
                Gui(["你起不来。"],
                    ["（注册失败）"]).run()
            elif auth_type == "login":
                Gui(["你被司普青拦住了：“现在还没到点。”"],
                    ["（登陆失败）"]).run()
            elif auth_type == "delete":
                Gui(["你被司普青又叫起来了。"],
                    ["（删除账号失败）"]).run()

    @QtCore.Slot()
    def sqp_say_sth(self):
        """Randomly choose a sentence of spq."""
        self.window.spq_word.setText(random.choice([
            "起来了啊，把内务和卫生都做好了再走啊！",
            "起起起！",
            "起不来都是借口。",
            "没完了是吧？！",
            "没完了在哪里！"
        ]))

    @QtCore.Slot()
    def register(self):
        """Register the account in the remote."""
        asyncio.run(self.auth("register"))

    @QtCore.Slot()
    def login(self):
        """Authoricate the login."""
        asyncio.run(self.auth("login"))

    @QtCore.Slot()
    def delete(self):
        """Delete the account in the remote."""
        asyncio.run(self.auth("delete"))

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
