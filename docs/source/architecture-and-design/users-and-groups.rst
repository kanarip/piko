================
Users and Groups
================

When people interact with the |name| system, it creates two separate things:

#.  An :py:class:`Account <piko.db.model.Account>`,

#.  A :py:class:`Person <piko.db.model.Person>`.

Users as such as divided in to :py:class:`Accounts <piko.db.model.Account>`
and actual human beings (:py:class:`Persons <piko.db.model.Person>`).

Accounts are collected in to :py:class:`Groups <piko.db.model.Group>` to which
Persons have authorization levels -- for those Accounts not associated with
another Person.

As such, an example family man called John may have a personal twitter account
`@john`, a family account `john@doe.org`, a personal account `john@gmail.com`,
a professional account `john@example.com`, and a corporate twitter account
`@exampleinc`.

.. table::

    +-----------+-----------------------+---------------+
    | Person    | Account               | Group         |
    +===========+=======================+===============+
    | John      | `john@gmail.com`      | Doe Family    |
    +-----------+-----------------------+---------------+
    |           | `john@example.com`    | Example, Inc. |
    +-----------+-----------------------+---------------+
    |           | `@john`               | NULL          |
    +-----------+-----------------------+---------------+
    | Jane      | `jane@gmail.com`      | Doe Family    |
    +-----------+-----------------------+---------------+
    |           | `@jane`               | NULL          |
    +-----------+-----------------------+---------------+
    | Joe       | `joe@gmail.com`       | NULL          |
    +-----------+-----------------------+---------------+
    |           | `joe@example.com`     | Example, Inc. |
    +-----------+-----------------------+---------------+
    | NULL      | `@exampleinc`         | Example, Inc. |
    +-----------+-----------------------+---------------+

User Registration
=================

How does an account become a person?

Logins: The Automated Kind
==========================

-> Oauth.

Logins: The Interactive Kind
============================

Web interface. Second factor for account used to log in on the account or on
the person.

Group Membership
================

.. seealso::

    *   Notification Channels
