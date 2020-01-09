import argparse
import ldap
import ldap.modlist
import concurrent.futures

parser = argparse.ArgumentParser(description="This is an ldap user counter")

parser.add_argument('-s', '--server', dest='server')
parser.add_argument('-b', '--base', dest='base')
parser.add_argument('-bu', '--binduser', dest='binduser')
parser.add_argument('-bp', '--bindpass', dest='bindpass')
parser.add_argument('-cs', '--chunksize', dest='chunksize')

# collect your args
args = parser.parse_args()
server = args.server
base = args.base
binduser = args.binduser
bindpass = args.bindpass
chunksize = args.chunksize


# create connection
con = ldap.initialize('ldap://' + server)

# bind connection
con.simple_bind_s("cn=" + binduser, bindpass)


criteria = "(&(objectClass=posixAccount)(uid=user*))"
attributes = ['uid']
result = con.search_s(base, ldap.SCOPE_SUBTREE, criteria, attributes)

results = [entry for dn, entry in result if isinstance(entry, dict)]


def divide_chunks(listofusers, chunk):
    # looping till length l
    for i in range(0, len(listofusers), chunk):
        yield listofusers[i:i + chunk]


def delete_users(list_of_dicts):
    # results is a list of dictionaries
    for dict in list_of_dicts:
        # get values for each dictionary
        for value in dict.values():
          dn = "uid=" + value[0] + ",ou=people,dc=example,dc=com"
          print(dn)
          con = ldap.initialize('ldap://master-us-west-2-a.ldap.hosted.labgear.io')
          con.simple_bind_s("cn=Directory Manager", "changeme")
          con.delete_s(dn)


# break original list into list of chunksize lists
chunks = list(divide_chunks(results, int(chunksize)))

# create a thread for each chunk (up to 1000)
with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
      fs = [executor.submit(delete_users, chunk) for chunk in chunks]
      concurrent.futures.wait(fs)
