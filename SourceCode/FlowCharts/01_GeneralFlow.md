@startuml

title 01 Sprinkler General Flow

:Create HwInterface object
to reset all mux;

:Define Garden object my_garden
* Init Backend
* Init timers;

:Turn on status led;

repeat
    :my_garden.run();
repeat while (Forced exit from telegram?) is (yes)
    :Log event;
    :Reset all mux;
stop

@enduml