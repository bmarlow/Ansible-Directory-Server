import argparse
import ldap
import ldap.modlist
import concurrent.futures


parser = argparse.ArgumentParser(description="This is an ldap user counter")

parser.add_argument('-s', '--server', dest='server')
parser.add_argument('-b', '--base', dest='base')
parser.add_argument('-bu', '--binduser', dest='binduser')
parser.add_argument('-bp', '--bindpass', dest='bindpass')
parser.add_argument('-be', '--begin', dest='begin')
parser.add_argument('-en', '--end', dest='end')
parser.add_argument('-l', '--location', dest='location')

# collect your args
args = parser.parse_args()
server = args.server
base = args.base
binduser = args.binduser
bindpass = args.bindpass
begin = args.begin
end = args.end
location = args.location


# create list of user numbers
users = list(range(int(begin), int(end)))

chunk = 50


def divide_chunks(user_list, chunk_size):
    # Yield successive n-sized chunks from l looping till length l
    for i in range(0, len(user_list), chunk_size):
        yield user_list[i:i + chunk_size]


def create_users(user_chunk):
    # create connection
    con = ldap.initialize('ldap://' + server)

    # bind connection
    con.simple_bind_s("cn=" + binduser, bindpass)

    for user in user_chunk:

        dn = "uid=user" + str(user) + "," + location
        modlist = {
                "objectClass": ["nsAccount", "nsOrgPerson", "nsPerson", "posixAccount"],
                "uid": ["user" + str(user)],
                "cn": ["user" + str(user)],
                "displayName": ["user" + str(user)],
                "legalName": ["user" + str(user)],
                "uidNumber": [str(user)],
                "gidNumber": [str(user)],
                "userPassword": ["changeme"],
                "loginShell": ["/bin/bash"],
                "homeDirectory": ["/home/user" + str(user)],
        }

        # addModList transforms your dictionary into a list that is conform to ldap input.
        result = con.add_s(dn, ldap.modlist.addModlist(modlist))
        print("user" + str(user) + " Successfully added")


chunks = list(divide_chunks(users, chunk))

# loop for debugging
# for chunk in chunks:
#    create_users(chunk)


with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    fs = [executor.submit(create_users, chunk) for chunk in chunks]
    concurrent.futures.wait(fs)
