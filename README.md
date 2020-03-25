# Sort It 3D A\* Solver

![screenshot](./scr.jpg)

Sort It 3D ([App Store](https://apps.apple.com/us/app/sort-it-3d/id1493125671), [Google Play](https://play.google.com/store/apps/details?id=com.game.sortit3d&hl=en)) is a puzzle game where player is supposed to sort the balls in tubes by color. I wrote an A\* solver that's based on the color diversity as heuristics. To use the solver, simply

```bash
python3 ballsort.py problems.txt
```

and it will tell you how to move the balls in seconds!

See

```bash
python3 ballsort.py -h
```

for detailed help.