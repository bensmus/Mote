**Storage model**
For prefixes: 
- prefix_hash {guild: prefix}

For library:
- library_hash {channel/author.id+id: value}
- Set of id's corresponding to author.id/channel.id 
    - Adding an id is handled automatically (we don't have to think about duplicates)

**Unique id's provided by Discord API**
ctx.author.id <--- unique (for storing DM library)
channel.id <--- unique (for storing channel library)

**Redis code for hash table**
redis> HSET myhash field1 "Hello"
(integer) 1
redis> HGET myhash field1
"Hello"
redis> 

**Redis code for set**
redis> SADD myset "Hello"
(integer) 1
redis> SMEMBERS myset
"Hello"
redis> 

*Discord command and corresponding redis call: in a DM*

discord> #save lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

redis> HSET myhash author.id:lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA 

discord> #id lux-support

redis> HGET author.id:lux-support 
https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

