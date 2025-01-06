# Put the Fries in the Bag!

<h2><b>PLAY THE GAME HERE: https://danielmitrache.github.io/PTFITB/</b></h2>

## Overview
"Put the Fries in the Bag!" is a Web Python-based game (compiled to WebAssembly) where the player navigates a character to collect fries and place them in a bag while avoiding obstacles. The game is a parody of the computer science student life jokes. While being a parody game, it features fun and balanced gameplay, well thought-out design and endless replayabilty, making it the perfect time killer.

## Technologies Used
- Python and Pygame library - for writing the actual game
- WebAssembly and Pygbag - for making the game web compatible
- Object-Oriented Programming (OOP) - for organizing and structuring code efficiently
- Git and GitHub - for version control and collaboration
- HTML - for web interface design and layout
- Testing and Debugging - using techniques such as unit testing to ensure code quality
- Data Structures and Algorithms - for validating new levels

## Features
- **Player Movement**: Move the player using the `W`, `A`, `S`, `D` keys
- **Pause Functionality**: Pause the game by pressing the `ESC` key
- **Timer**: A countdown timer that stops when the game is paused and also alerts the player when low on time
- **Obstacles**: Avoid walls, shower obstacles, deodorant projectiles and girls chasing you
- **Collectibles**: Collect fries and place them in the bag to score points
- **Random Level Generation**: Infinite levels randomly generated validated by a BFS path-finding algorithm
- **Difficulty Levels**: The game becomes more challenging as you score more points
- **High Score**: Keep track of your high score
- **Game Over Screen**: Displays the score and high score with options to restart or exit
- **Main Menu Screen**: Displays controls when loading the game
- **Background Music Tracks**: A variety of music tracks looped over the game
- **Sound Effects**: A lot of fun sound effects generated by me
- **Mute/Unmute Music/SFX**: Options to mute or unmute the background tracks or the sound effects
- **Animated Background**: Rainbow background that gets more colorful as the player progresses

## How the difficulty works
The four things that can kill you are:
 - Showers
 - Flying deodorant
 - The girl chasing you
 - The timer
<ol>
  <li>At level 1 there are only 3 showers and the timer starts off with 15 seconds that refresh at every level.</li>
  <li>At level 2 a deodorant spawns which has a repeated timer of 3 seconds set to it. It launches across the map at a set speed every time the timer goes off</li>
  <li>At level 5 a girl that chases you spawns. She has a set speed and cannot pass through walls, but can pass through showers</li>
  <li>The difficulty increases as follows (keep in mind every stat has a max/min that keeps the game possible):
    <ol>
      <li>Every 5 levels the deodorant speed increases, its launch interval timer decreases and the level timer decreases</li>
      <li>Every ten levels a new shower appears</li>
      <li>Every 20 levels the girl speed increases</li>
    </ol>
  </li>
</ol>
<h3> <b>The game remains balanced by keeping track of certain distances to make sure the player does not face situations impossible to escape</b> </h3>

## Installation
```bash
git clone <repository-url> # Change the repository-url with the actual URL
cd <project-directory>
pip install -r requirements.txt
 ```
