# gocomics

gocomics downloader

## Installation

    $ pip install gocomics

## Requirements

* bs4
* grequests

## Usage

    $ # List all comics
    $ gocomics ls

    $ # Downloads all calvin and hobbes comics to ~/Downloads/calvinandhobbes
    $ gocomics fetch calvinandhobbes

    $ # Downloads calvin-hobbes comics [1999-01-03..2012-10-20] to /tmp/calvin-hobbes
    $ gocomics fetch --start=1999-01-03 --end=2012-10-20 --output-dir=/tmp/calvin-hobbes calvinandhobbes

