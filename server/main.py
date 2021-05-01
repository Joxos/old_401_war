import asyncio
import hashlib
import json


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


async def auth(reader, writer):
    data = await reader.read(1000)
    package = json.loads(data.decode())
    addr = writer.get_extra_info('peername')
    print(f"[*] Accept connection from {addr}")
    if package['status'] == "register":
        # register the user
        success = register(package['username'], package['password'])
        if success:
            writer.write(json.dumps({"status": "success"}).encode("utf-8"))
        else:
            writer.write(json.dumps({"status": "failed"}).encode("utf-8"))
    elif package['status'] == "login":
        # login and play
        success = login(package['username'], package['password'])
        if success:
            writer.write(json.dumps({"status": "success"}).encode("utf-8"))
            # play
        else:
            writer.write(json.dumps({"status": "failed"}).encode("utf-8"))
    elif package['status'] == "delete":
        # delete the user
        success = delete(package['username'], package['password'])
        if success:
            writer.write(json.dumps({"status": "success"}).encode("utf-8"))
        else:
            writer.write(json.dumps({"status": "failed"}).encode("utf-8"))
    await writer.drain()
    writer.close()


async def main():
    auth_server = await asyncio.start_server(auth, "127.0.0.1", 1901)
    addr = auth_server.sockets[0].getsockname()
    print(f'[*] Serving on {addr}')
    async with auth_server:
        await auth_server.serve_forever()


asyncio.run(main())
