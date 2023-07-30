# Automatic Sprinkler
The project is intended to let your plant to survive while you are on holiday and you do not have any intention to buy built-in mechanism that prevent you to expand and adjust the system to your needs.

If you find this project it means that you are going to build it :)

# Getting started

## Folder Structure

The Repository is structure so that:

|Folder|Content description|
|-|-|
|/3d_files|It contans all the stl files that you need to print for the project.|
|/Board|It contains the reference schematics of the PCB|
|/Board/Production/|It contains the different files for fabrication or editing|
|/SourceCode|It contains all the developend source code|
|/SourceCode/src/ + sprinkler.py|It is the code needed for the Raspberry Pi Pico W to control the PCB board. The *src* folder has to be uploaded on the microcontroller while the *sprinkerl.py* can be executed locally for tests or uploaded on the target as well.|
|/SourceCode/Scripts/|It contains some tests that can be executed to test the wiring.|
|/SourceCode/optional_source|It contains the code that can be used to create a controller with another Raspberry Pico W. It is intended to force the pump activation. The folder Raspberry_Pi_2 contains the code to set up a small server to monitor the data with Grafana.|
|/SourceCode/doc|It contains some additional references.|

## Bill of Material for the PCB and water buffer.

|Item #|Description|Quantity|Cost ~€/piece|Reference|
|-|-|-|-|-|
|1|Raspberry Pi Pico w|1|5,08|[Link](https://www.kubii.com/it/le-schede-raspberry-pi/3205-raspberry-pi-pico-w-h-wh-3272496311589.html#/477-version_pico-pico?src=raspberrypi)|
|2|Multiplexer analogico CD74HC4067|2|1,30|[Link](https://www.amazon.it/gp/product/B09B4213T3/ref=ox_sc_act_title_1?smid=A2ETWJBO4PH7XN&psc=1)|
|3|Relay 3V with Optocoupler|7|3,60|[Link](https://www.amazon.it/gp/product/B07PLQNSW2/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)|
|4|Buck converter|1|2,20|[Link](https://www.amazon.it/gp/product/B0B4S3T48P/ref=ewc_pr_img_1?smid=A1RRESHOTNJOS4&psc=1)|
|5|JST-XH 2,54mm 3pin|7|n/a|[Link](https://www.amazon.it/gp/product/B07RP6876C/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)|
|6|JST-XH 2,54mm 2pin|7|n/a|[Link](https://www.amazon.it/gp/product/B07RP6876C/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)|
|7|Diode IN4001|7|n/a|[Link](https://www.amazon.it/gp/product/B07Q8RPBVY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)|
|8|Mini water pumps 3V/5V|7|2,20|[Link](https://www.amazon.it/dp/B09Z28NFT3?psc=1&ref=ppx_yo2ov_dt_b_product_details)|
|9|Pin header connector female|Some|10|[Link](https://www.amazon.it/Headers-Breakaway-Connector-Prototype-intestazione/dp/B07CC4V9ZY/ref=sr_1_1?keywords=2%2C54+female&qid=1690740762&sr=8-1)|
|10|DC connector DC-0055.5x2.1mm|1|0,10|[Link](https://it.aliexpress.com/item/1005001688314286.html?spm=a2g0o.order_list.order_list_main.12.12bd3696ZkNGgU&gatewayAdapt=glo2ita)|
|11|Power supply 5V 2A|1|7,00|[Link](https://www.amazon.it/gp/product/B09DSWL12H/ref=ewc_pr_img_1?smid=A1LPCHZ6DX1HO3&psc=1)|
|12|(optional) Led green|2|n/a|[Link](https://www.amazon.it/gp/product/B07DPJ23YT/ref=ewc_pr_img_1?smid=A3BZ3PT9ZR43MC&psc=1)|
|13|(optional) Box case|1|n/a|[3d_file](3d_files/case_half1.STL)|
|14|(optional) Box case cover|1|n/a|[3d_file](3d_files/case_half2.STL)|
|15|Water frame buffer|1|n/a|[3d_file](3d_files/frame_buffer.STL)|
|16|Water frame buffer top|1|n/a|[3d_file](3d_files/frame_buffer_top.STL)|
|17|Pump holders|2|n/a|[3d_file](3d_files/pump_buffer.STL)|
|18|Holder top|2|n/a|[3d_file](3d_files/holder_top.STL)|
|19|Relay support|2|n/a|[3d_file](3d_files/support_relay.STL)|
|20|(optional) PCB to be printed|1|n/a|[PCB](Board/Schematic_Automatic_Sprinkler_2023-07-30.pdf)|


## Software

The file must be named ***main.py*** in order to be executed directly at the start-up of the shield.

## How to start to test the softwarre

* Copy the */src* folder that you find the SourceCode folder to your Raspberry Pico W

* Copy / execute the file *sprinkler.py* . If you want that it will be executed automatically at the startup you have to copy the file *sprinkler.py* to Raspberry Pico and rename it as *main.py*

# Licence

Please check the dedicated file in *main* branch.