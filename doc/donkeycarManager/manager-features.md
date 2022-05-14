# Donkey Car (booth) Manager Features

This document describe all features handeled by the DonkeyCarManager tool. Let's say we want to organise
a donkeycar event, with a track and you will let visitors drive several RC cars (using ps4 controllers) so that they can discorver IA with a tangible and gaming experience.

In our case we were organizing on DonkeyCar booth with a track on a booth during Nante Maker Campus.
As we wanted to be well prepared we decided to build tools around DonkeyCar to management several cars at a time and let as most visitors as possible discover them and play a bit with them.

We have 2 types of actors :

* Visitor : people participating to the event and willing to play with cars
* Staff : experts in DonkeyCar managing the track/booth/cars.

Display / Devices :

* Visitor's registration tablet : a tablet with a simple form so that the visitors can register to participate simply using a pseudo.
* Staff computeur : used by staff members only to manage visitors / cars.
* Score screen or main screen : huge TV display (connected to a computer) used to display current track / runs informations to all visitors and drivers.
* Cars : RC Car with donkey car installed.

See [architecture diagram](../DonkeycarBoothManagerArchitecture.drawio) for more informations about the interactions of all those actors / devices.

## Features

| N | Feature title | Actors | Detailed descriptions | Devices | 
|--- |--- |--- |--- |--- |
| F1 | Register visitor/player | Visitor | As a visitor wanting to play with cars I would like to register myself using a nickname/pseudo (not already used !!), so that I can come back later when it's my turn. | Registration tablet |
| F2 | View if some turns is near (in the waiting list) | Visitor / Staff | As visitor waiting for my turn I would like to see next players nicknames displayed (next 5 players) to see if my turn is near. | Main screen |
| F3 | View players last/best lap timings | Visitors | Players currently playing should see their 2 last turn timings and their brest one. | Main screen |
| F4 | View drive remaining time | Visitors | For each running cars we need to display a countdown with the remaining drive time. | Main screen |
| F5 | View running cars info (nickname running it, color, car name) | Visitor | Always display running cars details : car's name, car color, player nickname using it. | Main screen |
| F6 | Start drive countdown when car start running | Visitor | When a car is assigned, it's remaining time to play counter / timer, should start only when the user start moving the car | Main screen / car / controller |
| F7 | Delete a player from the waiting list | Staff | If someone doesn't come we need to be able to delete it from the waiting list and from the car he might be automatically assigned to. | Staff computer |
| F8 | Insert a player before/after an other player | Staff | Staff might need to make some demonstrations after someone so they need the ablility to insert someone at the begining or after someone | Staff Computer |
| F9 | Put a car in maintenance | Staff | If a car is broken are need diagnostic, the car will be started should be visible in staff tools but not asigned to any visitors and not visible on the main screen. | Staff computer |
| F10 | Limit throttle by cars | Staff | Need a cursor to limit throttle or prefefined levels | Staff computer |
| F11 | Stop one car | Staff | Stop control by visitor controller and all engines | Staff computer |
| F12 | View one car camera stream | Staff | - | Staff computer |

 
