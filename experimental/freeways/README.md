# Freeways Solver

Fun Puzzle Game - [Steam Page](https://store.steampowered.com/app/780210/Freeways/)

Can I build a solver for the levels within this game? Idk so we will leave in experimental until I can test feasibility.

```bash
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy
```


What do we have so far?

We have a vibe-coded prototype that allows us to build the data layout, and solves using Parametric Cubic Bézier Curves.

While it works for super super **SUPER** simple levels, it fails if it gets slightly complicated. This is a consequence of trying to solve for each individual **in** rather then optimizing for merges and combinations of roads. 

We also need to update the *level_labeler* to support blocking off regions of the map so that the bot doesn't think it can build there.

We have a lot of work to do, but a simple *(vibe-coded)* POC for a couple levels 