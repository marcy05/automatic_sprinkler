# Automatic Sprinkler
The projec is intended to let your plant to survive while you are on holiday and you do not have any intention to buy built-in mechanism that prevent you to expand and adjust the system to your needs.

If you find this project it means that you are going to build it :) 

# Getting started

## Hardware needed

* Raspberry Pi Pico W (the Pico should work fine as well)

* 2x 16 channel analog multiplexer CD74HC4067 [Link](https://www.amazon.it/gp/product/B0814WWPKN/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1)

* 7x Relay 3.3V with optocoupler [Link](https://www.amazon.it/gp/product/B07PLQNSW2/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)

* 7x water pump 3V / 5V [Link](https://www.amazon.it/gp/product/B082PM8L6X/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&th=1)

* Some connectors

* Some cables

* Power supply connector DC-005 [Link](https://www.amazon.it/Sourcing-Alimentazione-connettore-Femmina-Supporto/dp/B07KYBRJXQ/ref=sr_1_6?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=K79VMFLPMOE0&keywords=DC-005&qid=1675707821&sprefix=dc-005%2Caps%2C954&sr=8-6)

* 1x DC-DC buck converter [Link](https://www.amazon.it/gp/product/B0823P6PW6/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

## Circuit creation

It is possible to use the file [Sprinkler_v3_20221229.pdf](Board/Sprinkler_v3_20221229.pdf) to create the circuit on your own or you can use the files in [Production](Board/Production/) to manufacture the board yourselfe.


## Software

The file must be named ***main.py*** in order to be executed directly at the start-up of the shield.