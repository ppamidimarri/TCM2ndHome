# TCM2ndHome

This is an extension of my [TeslaCamMerge project](https://github.com/ppamidimarri/TeslaCamMerge) to support two home locations, with a main home and a weekend home. 

A Jetson Nano runs at the main home and a Pi 4B runs at the weekend home. Both devices host an SMB share with the exact same credentials. When I park at the weekend home, the Pi Zero W in the car archives the clips, and then Jetson Nano at the main home pulls those files from the weekend home's Pi 4B and merges them.


