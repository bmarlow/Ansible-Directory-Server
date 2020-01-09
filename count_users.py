import argparse
import ldap
import ldap.modlist
import concurrent.futures
import sys

parser = argparse.ArgumentParser(description="This is an ldap user counter")

parser.add_argument('-s', '--servers', dest='servers_string')
parser.add_argument('-b', '--base', dest='base')
parser.add_argument('-bu', '--binduser', dest='binduser')
parser.add_argument('-bp', '--bindpass', dest='bindpass')
parser.add_argument('-f', '--file', dest='file')


# collect your args
args = parser.parse_args()
servers_string = args.servers_string
base = args.base
binduser = args.binduser
bindpass = args.bindpass
file = args.file

if servers_string and file:
    print("You may select the -s or the -f argument, not both.")
    sys.exit(1)


def read_servers(server_file):

    with open(server_file, 'r') as f:
        # create dict from yaml file
        servers = f.read().splitlines()

    return servers


def convert_string_to_list(string):
    li = list(string.split(","))
    return li


def count_users(server):
    # create connection
    con = ldap.initialize("ldap://" + server)

    # bind connection
    con.simple_bind_s("cn=" + binduser, bindpass)
    criteria = "(&(objectClass=posixAccount)(uid=user*))"
    attributes = ['uid']
    result = con.search_s(base, ldap.SCOPE_SUBTREE, criteria, attributes)

    results = [entry for dn, entry in result if isinstance(entry, dict)]

    number_of_users = len(results)

    print(server.upper() + ": " + str(number_of_users) + " users in the LDAP server")


if file:
    servers = read_servers(file)
elif servers_string:
    servers = convert_string_to_list(servers_string)


# used if the loop needs to be debugged
# for server in servers:
#    count_users(server)

# spin off a thread for each server and do the searches simultaneously
with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    fs = [executor.submit(count_users, server) for server in servers]
    concurrent.futures.wait(fs)


print("Finished...")
