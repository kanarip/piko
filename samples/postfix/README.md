## How to Dick Around With This

*   Either know the domains and their statuses, or use the fixtures. The examples
    listed here use fixtures.

*   Lookup a domain name space that exists, and is deemed "active":

```
$ postmap -q doefamily.org mysql:./samples/postfix/mydestination.cf
doefamily.org
```

*   Lookup a recipient that is supposed to exist:

```
$ postmap -q john@doefamily.org mysql:./samples/postfix/local_recipient_maps.cf
john@doefamily.org
```
