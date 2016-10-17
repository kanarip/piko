=========
Candlepin
=========

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
