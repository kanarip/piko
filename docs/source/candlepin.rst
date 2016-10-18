=========
Candlepin
=========

A user registers a customer entitity.

A customer obtains an entitlement. This entitlement is attached to a product, and provides a maximum quantity for such entitlement.

A system is registered. A system attaches a subscription, which must correspond to one or more valid entitlements.

.. TODO:: Fix entitlement inheritance (eg. a *Fasttrack* channel requires a base release channel)

**Customer**

    Virtual property users linking accounts to the customer account,
    amended with roles such as admin, tech. contact, project manager,
    .

    *   id
    *   name

**Entitlement**

    *   id
    *   product_id
    *   system_id

**Product**

    *   id
    *   key
    *   name

**Subscription**

    *   entitlement_id
    *   system_id

**System**

    *   id
    *   uuid
    *   customer_id
