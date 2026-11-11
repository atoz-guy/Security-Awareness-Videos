# Cyber Awareness Videos 🛡️

Short, scroll-stopping videos that explain cybersecurity threats in plain language, made for small business owners, website owners, and everyday people. No technical background needed.

Each video is built to be posted on social media (Facebook, LinkedIn and others) next to a short written post that explains what to do.

## Why this exists

You don't need to be a cybersecurity expert to take cybersecurity seriously. Often, protecting your business starts with knowing the right question to ask. These clips aim to get that question in front of people in about 5 seconds.

## Videos

| Topic | What it covers | Formats | Folder | Posted |
|---|---|---|---|---|
| **PHP2Shell** | A PHP flaw that can let attackers into vulnerable web servers without a password. Ask your host: *"Is my PHP patched?"* | Facebook 4:5, LinkedIn 1:1 | [`php2shell/`](php2shell/) | [Facebook](https://www.facebook.com/100006015724701/videos/1001228402349456/) |

*More topics coming soon.*

## Repository layout

Each topic has its own folder containing:

- the finished videos (`.mp4`)
- the script that generates them, so anyone can tweak the text and re-render
- a `README.md` with the post text, a preview, and how to rebuild

```
cyber-awareness-videos/
├── README.md
└── <topic>/
    ├── README.md
    ├── make_snip.py
    ├── requirements.txt
    ├── preview.png
    └── *.mp4
```

## Using these videos

You're welcome to share these clips to help raise awareness. Please don't present them as official guidance from any vendor. Always check with your hosting provider or IT support about your own setup.

## Making your own

The videos are generated with Python (Pillow + ffmpeg). No video editor is needed. See any topic folder for instructions.
