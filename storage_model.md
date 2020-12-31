**Storage model**
For prefixes: 
- prefix hash {guild: prefix}

For library:
- library hash {channel/author.id+id: value}
- sorted set of id's corresponding to author.id/channel.id 
    - sorted set so that adding an id is handled automatically (we don't have to think about duplicates)

**Unique id's provided by Discord API**
ctx.author.id <--- unique (for storing DM library)
channel.id <--- unique (for storing channel library)

**Redis code for hash table**
redis> HSET myhash field1 "Hello"
(integer) 1
redis> HGET myhash field1
"Hello"
redis> 

**Prefix changing is the only thing that should be done server wide, don't allow prefix changing for DM's**

*Discord command and corresponding redis call: in a DM*

discord> #save lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

redis> HSET myhash author.id:lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA 

discord> #id lux-support

redis> HGET author.id:lux-support 
https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

