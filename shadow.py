# Authors : Arnaud Boyé (@YNRA), Thomas Dejeanne (@Gomonriou)
# Year : 2021
# Description : [School project] Small script to attempt a password attack on a shadow file. 
# Passwords need to be hashed in MD5, otherwise you'll have to change some lines and replace md5 with the algorithm needed.

#!/usr/bin/python3

# Import mandatory librairies
import time, sys, os
import multiprocessing
from hashlib import md5
from string import ascii_lowercase, ascii_letters, digits
from itertools import product
from datetime import timedelta


# Globial variables
punctuation = ";@_#"
constraint = ascii_letters + digits + punctuation
output = open("./password.txt", "a+")

def menu():
    print("""
   _____ _               _                                     _    _             
  / ____| |             | |                                   | |  (_)            
 | (___ | |__   __ _  __| | _____      __   ___ _ __ __ _  ___| | ___ _ __   __ _ 
  \___ \| '_ \ / _` |/ _` |/ _ \ \ /\ / /  / __| '__/ _` |/ __| |/ / | '_ \ / _` |
  ____) | | | | (_| | (_| | (_) \ V  V /  | (__| | | (_| | (__|   <| | | | | (_| |
 |_____/|_| |_|\__,_|\__,_|\___/ \_/\_/    \___|_|  \__,_|\___|_|\_\_|_| |_|\__, |
                                                                             __/ |
                                                                            |___/ 
Press Ctrl+C at any time to abort.
Results are stored in password.txt in current folder.
  """)
    
    valid_input = False

    while not valid_input:
        attack_mode = input("Please choose between brute force [1] or dictionnary attack [2] : ")
        if attack_mode == '1':
            print("\nYou choose brute force attack ! ")
            attack_mode = bruteForce
            valid_input = True
        elif attack_mode == '2':
            attack_mode == dictionnary
            valid_input = True
            print("\nYou choose dictionnary attack ! ")
        else:
            print("\nIncorrect option !")
       
    main(attack_mode)        

# Main fonction: creates processes (4) for multiprocessing if attack mode is brute force. Useless for dictionnary attack.
def main(attack_mode):
    users = extractHashs()
    
    if attack_mode == bruteForce:
        # 1 process for ascii lowercase, and 3 processes for lowercase, uppercase, digits, punctuation, with different length
        process_1 = multiprocessing.Process(target=bruteForce, args=(users, ascii_lowercase, 6, 13))
        process_2 = multiprocessing.Process(target=bruteForce, args=(users, constraint, 6, 8))
        process_3 = multiprocessing.Process(target=bruteForce, args=(users, constraint, 9, 11))
        process_4 = multiprocessing.Process(target=bruteForce, args=(users, constraint, 12, 13))
        processes = [process_1, process_2, process_3, process_4]

        print("\n#####################################\nPlease wait, cracking in progress ...\n#####################################\n")
        
        # Starts the processes, and waits for them to complete.
        for process in processes:
            process.start()
        for process in processes:
            process.join()
    else:
        print("\n#####################################\nPlease wait, cracking in progress ...\n#####################################\n")       
        dictionnary(users)


# Retrieve users and corresponding hash from shadow file, write them in array (users)
def extractHashs():
    time.sleep(0.5)
    print("\n[+] Initializing ...\n[+] Looking for valid usernames and passwords in shadow  ...")
    users = []
    file = input("Please select the path of the shadow file (default : in the current folder) : ")
    with open(file, "r") as shadow:
        for line in shadow.readlines():
            if len(line) > 1:
                line = line.replace("\n","").split(":")
                
                if not line[1] in ["x", "*", "!"]:
                    user, hash = line[0], line[1][3:]
                    users.append([user, hash])
                    print("[+] Found valid password ! User = {} | Hash = {}".format(user, hash))
                    time.sleep(0.5)

        if users == []:
            print("[!] No hashs were found in this file ! ")
            sys.exit()

        return users

# Brute force : creates words generator, iterates through [users] and generator, compares hash and word. 
# If found, displays password in and writes it in result.txt
def bruteForce(users, alphabet, start, stop):
    start_time = time.time()
    count = 0

    # Iterates from 6 to 12 and through every combinations of given letters
    for length in range(start, stop):
        for word in product(alphabet, repeat=length):
            count += 1
            word = ''.join(word)
            digest = md5(word.encode()).hexdigest()

            # Waits for similarities between a word and a hash
            # When found, prints the result, writes it into file, and removes username and hash for users list
            for login in users:
                if digest in login:
                    user = login[0]
                    delta = time.time() - start_time
                    delta = timedelta(seconds=round(delta))
                    result = "[+] Password '{}' cracked in {} for {} ! Well done !".format(word, delta, user)
                    output.write(result+'\n')
                    users.remove(login)
                    print(f"\n{result}\n[+] {count} combinations were calculated !\n[-] Removing user '{user}' from list to crack ...")
                
    if users == []:
        print(f"Done ! It took {delta} seconds to crack all of the passwords !")
        sys.exit()

# Dictionnary attack : same as brute force, except we iterate through a dictionnary instead of generate words.
def dictionnary(users):
    start = time.time()

    # Opens dictionnary file, reads every line, compares with hash in users. 
    # Encoding option in not useful for "dico_mini_fr", but required for wordlists like infamous "rockyou".
    dictionnary = input("Please select the path of a dictionnary")
    with open(dictionnary, encoding = "ISO-8859-1") as dictionnary:    
        for password in dictionnary.readlines():
            password = password.replace("\n","")
            digest = md5(password.encode()).hexdigest()

            # Waits for similarities between a word and a hash
            # When found, prints the result, writes it into file, and removes username and hash for users list
            for login in users:
                if digest in login:
                    user = login[0]
                    delta = time.time() - start
                    delta = timedelta(seconds=round(delta))
                    result = "[+] Password '{}' cracked in {} for {} ! Well done !".format(password, delta, user)
                    output.write(result+'\n')
                    users.remove(login)
                    print(result)

        if users == []:
            print(f"Done ! It took {delta} seconds to crack all of the passwords !")
            sys.exit()
        else:
            print("[!] No matching password in this dictionnary for these users :")
            for login in users:
                print(login[0])
            sys.exit()
  
# Launch 
if __name__ == "__main__":
    os.system("clear")
    menu()


