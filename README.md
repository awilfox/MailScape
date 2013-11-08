# MailScape Python Beta

Because I hate every single email client available for Linux.

## Design goals

* Super simple
* UI based on old Netscape because it's familiar and easy (and UI assets are NPL)

## Uses

* Python built-ins (smtplib, configparser, email)
* PyQt4 (UI)

## How to run

```
git clone git://github.com/CorgiDude/MailScape.git
cd MailScape/mailscape
PYTHONPATH=.. python3 -m mailscape.qtui
```

## TODO

* figure out how to load resources properly (.qrc?)
* fix attach UI
* implement a way to address things
* configuration UI

## Configuration

Very easy, ini-like.  Example:

```
[servers]
mail.wilcox-tech.com = Wilcox Technologies Mail

[mail.wilcox-tech.com]
name = Andrew Wilcox
email = AWilcox@Wilcox-Tech.com
user = AWilcox
password = Super secret password
tls = True
```
