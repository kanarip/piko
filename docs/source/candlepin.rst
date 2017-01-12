=========
Candlepin
=========

Candlepin is an application for system and service entitlement management.

It's intended use is for ISVs to be able to put software products on mirrors,
behind a lock and key.

The lock would consist of a requirement for the client of the mirror to
authenticate itself with a valid client TLS certificate that is not
revoked to obtain access -- the key.

Customers and Entitlements
==========================

A customer is entitled to consume updates to the software suite provided by the
ISV. The initial use or continued use of a product deployment that does not
hold a valid subscription is of no concern -- the entitlement is not a license,
since the software is Free Software. Instead, the entitlement is a subscription
to continued support and updates to the product.

When a customer registers a request to entitlement, this can be either of two
things;

#.  A test installation to get an idea of the product,

#.  An installation that is going to get carried forward (indefinitely).

For the first use-case, it is paramount to provide access to the product
without requiring manual intervention on the side of ISV. However, certain
information must be obtained from the customer and registered, so that a
Sales & Marketing department retains the opportunity to follow up with the
potential customer.

It is also important to know this temporary entitlement is just that --
temporary. After the initial entitlement expires, the customer should not be
allowed to refresh its entitlement without prior approval of the ISV.

For the second use-case, it is paramount for the customer to be able to get
started without manual intervention on the side of the ISV being required.
However, since the entitlement is over a pro-longed period of time, a refresh
of the entitlement should be allowed.

The implication is that all entitlements are temporary. An extension to any
client SSL certificate validity will require the customer to re-download the
certificate, and may therefore as well be an entirely new certificate.

Customer Registration
=====================

A customer as such does not register -- instead, an existing user account
registers a customer entity. Let us pretend the registration occurs on the
basis of an email address.

#.  John Doe creates an account `john.doe@example.org` [#]_.

#.  John Doe registers a customer entity *Exanple, Inc.* [#]_.

    .. NOTE::

        This automatically includes a minimal form of contact information for
        the customer entity, namely John's email address.

    .. NOTE::

        The customer entity will need to be provided as a type of group rather
        than a candlepin-specific customer entity.

#.  John Doe registers a system `kolab01.example.org` to run a product.

#.  The customer entity is issued an entitlement for that product to run on
    tht system, that is valid for two months.

    .. TODO::

        Is there a maximum quantity associated with the entitlement?

#.  John Doe configures the system and installs the product.

#.  Unless John Doe has the entitlement for the customer entity extended, the
    refresh of the client SSL certificate that provides the system access to
    the mirror is not allowed.

A :py:class:`Person <piko.db.model.Person>` registers one or more
:py:class:`Accounts <piko.db.model.Account>` -- using any of these accounts
creates the :py:class:`Session <piko.db.model.Session>` user entity.

A user registers a :py:class:`Customer <piko.apps.candlepin.db.model.Customer>` entitity.

A customer obtains an :py:class:`entitlement <piko.apps.candlepin.db.model.Entitlement>`.

This entitlement is attached to a product, and provides a maximum quantity for
such entitlement.

A system is registered. A system attaches a subscription, which must correspond
to one or more valid entitlements.

.. rubric:: Footnotes

.. [#]

    See :py:class:`piko.db.model.Account`

.. [#]

    See :py:class:`piko.apps.candlepin.db.model.Customer`

