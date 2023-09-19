# Boot2Root
Welcome to the Boot2Root project! This project is a security course at 42 School. Boot2Root is some sort of a Capture The Flag (CTF) challenge where you will find vulnerabilities in code and exploit them to progress to your utlimate goal : **become root**.

## Project Overview
There are a total of 9 mandatory levels and 1 bonus level. Each level contains a vulnerability, and your goal is to exploit it in order to retrieve the flag. This flag will be your key to the next level.

Below are the links to the directories for each level:

[Level00](./level00/walkthrough.md) - Reverse engineering

[Level01](./level01/walkthrough.md) - Buffer overflow & shellcode

[Level02](./level02/walkthrough.md) - Format string attack - Reading memory

[Level03](./level03/walkthrough.md) - Reverse engineering

[Level04](./level04/walkthrough.md) - Buffer overflow - Ret2LibC

[Level05](./level05/walkthrough.md) - Format string attack - Writing memory & shellcode

[Level06](./level06/walkthrough.md) - Reverse engineering, keygen

[Level07](./level07/walkthrough.md) - Buffer overflow - Ret2LibC

[Level08](./level08/walkthrough.md) - Path traversal

[Level09](./level09/walkthrough.md) - Buffer overflow & dead code (Bonus level)

----

## What's Inside Each Level?
In every directory, you'll find the following files:

- walkthrough.md: An explanation of the vulnerability and how to exploit it.
- source.c: The vulnerable code written in C.
- flag: The flag you'll get after exploiting the vulnerability.

In some directories you could find some tools / scripts used to exploit the binary of the level.

There's two tools you can use on some levels :

**- getenv.c**

A file in C language, which compiles and launches on the machine, makes it possible to recover all the memory addresses of the environment variables.
All you have to do is copy / paste the code inside a file on the host computer (usually in the /tmp folder) then:

``gcc getenv.c -o getenv``
``./getenv``
> 0x7ffe3945ff4c - XDG_RUNTIME_DIR=/run/user/1000
0x7ffe3945ff6b - DISPLAY=:1
0x7ffe3945ff76 - LANG=fr_FR.UTF-8
[...]

**- find_offset.py**

It is a small script in python, which will generate a pattern of the length of your choice, then search for the address transmitted by GDB at the time of the segfault to indicate the offset concerned (the EIP).
No need to run the script on the host computer, you can just use it from your computer (Python must be installed):

``python3 find_offset.py``
> Enter the pattern length: **100**
Pattern: A0A1A2A3A4A5A6A7A8A9B0B1B2B3B4B5B6B7B8B9C0C1C2C3C4C5C6C7C8C9D0D1D2D3D4D5D6D7D8D9E0E1E2E3E4E5E6E7E8E9

Copy / paste the pattern inside the target.

>Enter the address to find: **0xXXXXXXXX**

And put the adress gived by GDB.

If the script does't find the result it will show **Pattern not found in the generated pattern**, else :

> Offset found at: **XXXXXX**

----

## Getting Started
Start with Level00 and read the walkthrough.md to understand the nature of the vulnerability.
Inspect the vulnerable.c file to study the code.
Use your knowledge and skills to exploit the vulnerability and retrieve the flag from the code.
Use the retrieved flag to gain access to the next level.
Remember, the goal is to understand the vulnerabilities and learn how to prevent them in the future. Good luck and happy hacking!

----

## Contribute
Feel free to submit pull requests or issues if you find any mistakes or have suggestions for improvements.

----

**Authors are:**
- [Julien Branchet](https://github.com/blablupo)
- [Jean-michel Bertin](https://github.com/jmbertin)

----

**Note: Ensure that you follow ethical hacking guidelines. Do not use the knowledge gained here for malicious intentions. Always seek permission before attempting to exploit vulnerabilities in any system.**
