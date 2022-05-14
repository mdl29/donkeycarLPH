# DonkeyCarManager - Redis data structure

Base on features detailed here : [Donkey Car (booth) Manager Features](./redis-data-structure.md).

This document describe ressources and how they are stored in Redis.

## Ressources

### Car

Represent a booted car, `{{carname}}` is the hostname of the car.

| Field | Type | Description | Redis key name/pattern |
|--- |--- |--- |--- |
| ip | `string` | Current car IP addr. Eg: `192.168.1.200` | car:`{{carname}}`:ip |
| state | `'DRIVE'\|'RECORING'\|'AI_ASSISTED'\|'MAINTAINANCE'` (string) | Current car IP addr. Eg: `192.168.1.200` | car:`{{carname}}`:state |
| color | `string` | Car color code HEX. Eg: `FF0000` | car:`{{carname}}`:color |
| player | `string` | Current player nickname/pseudo. Eg: `benvii` | car:`{{carname}}`:player |

*Maybe [hashes](https://redis.io/docs/manual/data-types/data-types-tutorial/#hashes) should be used here.*


### Player

Represent a visitor that has registered with a unique `{{pseudo}}`.

| Field | Type | Description | Redis key name/pattern |
|--- |--- |--- |--- |
| registerTimestamp | EPOCH timestamp in seconds, `int` | Current car IP addr. Eg: `1652565920` | player:`{{pseudo}}`:register-timestamp |

*We might have more data to store about the player, for now i don't see more*.

*Maybe [hashes](https://redis.io/docs/manual/data-types/data-types-tutorial/#hashes) should be used here.*


### PlayerPool

Represent the waiting player list (linkedlist as we are using redis).

| Redis key name | Type | Description |
|--- |--- |--- | 
| playerpool | `List` | List of string, each value is the player nickname, new waiting players are added at the tail (last to be serve, last registered), old players (first in) should be pop from the head |

### TODO

* Store Timelaps, maybe an object to represent a "car drive / run" (with unique ID uuid) by a user that will refered to a time laps (List) containing all evaluated timestamps for each lap.
* We need the time when the drive mode was started to display a countdown, could be store as a field of the current cur/drive hashes