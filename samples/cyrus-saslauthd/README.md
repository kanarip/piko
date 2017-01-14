## How to Dick Around With This

* Ensure to have the fixtures loaded, or know a valid username and password.

* Have this running somewhere:

```
$ saslauthd -a httpform -V -d \
    -O samples/cyrus-saslauthd/saslauthd.conf \
    -m samples/cyrus-saslauthd
```

* Run an SASL authentication test:

```
$ testsaslauthd -u john.doe@example.com -p simple \
    -f samples/cyrus-saslauthd/mux
```
