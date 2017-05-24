# OhhPee1
This shall be a simple tool that makes file handling on your OP1 easier.

# Use it
Please be aware that this is work in progress and not yet properly usable without understanding both OP-1 and python.

clone the repo, and then install dependencies
```
pip install -r requirements.txt
./op1fun.py
```

## Concepts
### Folder Structure on the OP1
This is preset by Teenage Engineering, also we will make some opinionated assumptions

```
├── album
│   ├── side_a.aif
│   └── side_b.aif
├── drum
│   ├── <share-packname>
│   │   ├── mrcrunch.aif
│   │   ├── mrnoise.aif
│   │   ├── mrpiano.aif
│   │   └── mrvoice.aif
│   └── user # UserPack(packtype='drum')
│       ├── 1.aif
│       ├── 2.aif
│       ├── 3.aif
│       ├── 4.aif
│       ├── 5.aif
│       ├── 6.aif
│       ├── 7.aif
│       └── 8.aif
├── synth
│   ├── <share-packname>
│   │   ├── angelina.aif
│   │   ├── angelina_bg.aif
│   │   ├── baraq\ lo.aif
│   │   ├── baraq\ soft.aif
│   │   ├── bassen.aif
│   │   ├── bellas\ hi.aif
│   │   ├── bellas\ lo.aif
│   │   ├── bonga\ hi.aif
│   │   ├── bonga\ soft.aif
│   │   ├── boomping.aif
│   │   ├── boulder.aif
│   │   ├── c4llm3.aif
│   │   ├── casiodila.aif
│   │   ├── casiuno.aif
│   │   ├── data\ air.aif
│   │   ├── farfar.aif
│   │   ├── golvelius\ hi.aif
│   │   ├── golvelius\ lo.aif
│   │   ├── keypawn.aif
│   │   ├── klank.aif
│   │   ├── masteroid.aif
│   │   ├── meccanica.aif
│   │   ├── moms.aif
│   │   ├── morfar.aif
│   │   ├── morganista.aif
│   │   ├── mtrap.aif
│   │   ├── open.aif
│   │   ├── organista.aif
│   │   ├── trifork.aif
│   │   └── triple-f.aif
│   ├── snapshot
│   │   ├── 20170310_1809.aif
│   │   └── 20360812_1817.aif
│   └── user
│       ├── 1.aif
│       ├── 2.aif
│       ├── 3.aif
│       ├── 4.aif
│       ├── 5.aif
│       ├── 6.aif
│       ├── 7.aif
│       └── 8.aif
└── tape
    ├── track_1.aif
    ├── track_2.aif
    ├── track_3.aif
    └── track_4.aif
```

## note
this is not yet a usable tool or product, but more digging arround
see it as in a very first alpha state
