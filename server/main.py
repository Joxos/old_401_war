import hashlib
import json
import socket
import sys
import threading


def delete(username, password) -> bool:
    # delete the user
    print("[*] Try to delete user {} with password {}.".format(username, password))
    with open("users.json", 'r') as checker:
        all_users = json.load(checker)
        if username in all_users.keys() and hashlib.sha512(
                bytes(password, 'utf-8')).hexdigest() == all_users[username]:
            del all_users[username]
            with open("users.json", 'w') as deleter:
                json.dump(all_users, deleter)
            print("[*] User {} deleted.".format(username))
            return True
        else:
            print("[!] Failed to delete user {}.".format(username))
            return False


def login(username, password) -> bool:
    # verify the login
    print("[*] Try to login as {} with password {}.".format(username, password))
    with open("users.json", 'r') as checker:
        all_users = json.load(checker)
        if username in all_users.keys() and hashlib.sha512(bytes(password, 'utf-8')).hexdigest() == all_users[username]:
            print("[*] User {} logined.".format(username))
            return True
        else:
            print("[!] User {} failed to login.".format(username))
            return False


def register(username, password) -> bool:
    # register
    print("[*] Try to register {} with password {}.".format(username, password))
    with open("users.json", 'r') as checker:
        all_users = json.load(checker)
        # if user is already exist
        if username in all_users.keys():
            print("[!] Register failed.")
            return False
        # add the user
        all_users[username] = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
        # write the data
        with open("users.json", 'w') as writer:
            json.dump(all_users, writer)
            print("[*] User {} registered successfully.".format(username))
            return True


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


class Server:

    def __init__(self, host):
        self.host = host
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Setting up the server socket...", end='')
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Done!")
        self.threads = {}

    def start(self, listen):
        # self check
        try:
            self.server_socket.bind(self.host)
        except OSError:
            print("[!] The port is already in use.")
            sys.exit(0)
        print("[*] Port binding successfully.")
        try:
            self.server_socket.listen(1)
        except socket.error:
            print("[!] Failed to listen at the port.")
            sys.exit(1)

        # start listening
        self.server_socket.listen(listen)
        print("[*] Successfully listen at the port.")
        print("[*] Waiting for connection...")

        # main loop of listening
        try:
            while True:
                client, address = self.server_socket.accept()
                print("[*] Accept connection from {}:{}".format(address[0], address[1]))
                client_handler = threading.Thread(target=self.main, args=(client,))
                client_handler.start()
                self.threads[client] = client_handler
        except KeyboardInterrupt:
            print("[*] User exit.")

    def main(self, client):
        # main logic of the game
        package = recvpkg(client)
        if package['status'] == "register":
            # register the user
            success = register(package['username'], package['password'])
            if success:
                sendpkg(client, {"status": "success"})
            else:
                sendpkg(client, {"status": "failed"})
        elif package['status'] == "login":
            # login and play
            success = login(package['username'], package['password'])
            if success:
                sendpkg(client, {"status": "success"})
                # play
            else:
                sendpkg(client, {"status": "failed"})
        elif package['status'] == "delete":
            # delete the user
            success = delete(package['username'], package['password'])
            if success:
                sendpkg(client, {"status": "success"})
            else:
                sendpkg(client, {"status": "failed"})


if __name__ == "__main__":
    # startup the server
    server = Server(("0.0.0.0", 1901))
    server.start(5)
