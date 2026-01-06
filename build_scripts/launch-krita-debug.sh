#!/bin/bash

#/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=krita --file-forwarding org.kde.krita
flatpak run --devel --command=sh org.kde.krita -c "gdb /app/bin/krita"