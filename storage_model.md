**Storage model**
For prefixes: 
- prefix hash (guild: prefix)

For library:
- library hash (channel/author.id+id: value) 
- list of id's corresponding to author.id/channel.id 

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

**For DM's:** 
- have a list, which makes `#label league` possible
    author0.id = [author0.id:id0, author0.id:id1, ... author0.id:idN]
- then also we have a hash table 
    table = {author:id0:'text0 label0', author4:id0:'text5 label5'}

*Discord command and corresponding redis call: in a DM*

discord> #save lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

redis> HSET myhash author.id:lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

discord> #id lux-support

redis> HGET author.id:lux-support 
https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

*Discord command and corresponding redis call: in a channel*

discord> #save lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

redis> HSET myhash channel.id:lux-support https://www.mobafire.com/mobafire.com/lux-support/best-player-NA league

**Python command to get first word in a sentance**
python> s = 'Hello World'
python> s.split()[0]
'Hello'