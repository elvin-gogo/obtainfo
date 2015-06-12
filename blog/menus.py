#!/usr/bin/env python
# -*- coding: utf-8 -*-

from menu import Menu, MenuItem

Menu.add_item("main", MenuItem(title="首页", url="/", slug="home"))

Menu.add_item("main", MenuItem(title="影视大全", url='http://movie.obtainfo.com/', slug="collect"))

Menu.add_item("main", MenuItem("每日推荐", '/categories/day/', slug="day"))
Menu.add_item("main", MenuItem("电影精选", '/categories/selection/', slug="selection"))
Menu.add_item("main", MenuItem("画质预览", '/categories/preview/', slug="preview"))
Menu.add_item("main", MenuItem("学习园地", '/categories/manual/', slug="manual"))
Menu.add_item("main", MenuItem("音乐欣赏", '/categories/music/', slug="music"))
Menu.add_item("main", MenuItem("常用软件", '/categories/soft/', slug="soft"))
Menu.add_item("main", MenuItem("技术博客", '/categories/techblog/', slug="techblog"))

Menu.add_item("main", MenuItem("关于", '/flatpages/about/', slug="about"))

Menu.add_item("main", MenuItem("联系",'/flatpages/contact/', slug="contact"))

Menu.add_item("main", MenuItem("留言 / 求片", '/flatpages/guestbook/', slug="guestbook"))
