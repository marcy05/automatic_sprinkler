@startuml

title 02 Garden Run Flow

start

if (is_tank_full() ?) then (yes)

    note right
    is_tank_full() just read the PIN 28,
    if < 3V it returns False.
    end note

    :pump_deactivation_sem = True;

    if (is_watering_moment() ?) then (yes)
        :pump_cycle();
        :watering_timer = current time;
    endif

else (no)
    if (pump_deactivation_sem) then (yes)
        :deactivate_all_pumps();
    endif

endif

if (is_sensor_reading_moment() ?) then (yes)
    :reading_sensors();
    :set sensor_reading_timer;
endif

if (is_log_moment() ?) then (yes)
    :run garbage collector;
    :log system alive;
    :get evaluate_data_from_telegram();
    if (tg answer == ForcedExit) then (yes)
        :retun "ForcedExit";
        stop
    else (no)
    endif
else (no)
endif

end



:is_watering_moment;

if (daily_watering_done) then (no)
    if (now - watering_timer >= watering_period) then (yes)
        if (NTP time sync done) then (yes)
            if (is_evening) then (yes)
                :daily_watering_done = True;
                :return True;
                stop
            else (no)
                :return False;
                stop
            endif
        else (no)
            :log NTP not sync;
            :daily_watering_done = True;
            :return True;
            stop
        endif
    else (no)
        :return False;
        stop
    endif
else (no)
    :return False;
    stop
endif

:is_evening;
: get time and date;
if (Jan, Feb, Mar, Apr, May, Oct, Nov, Dec) then (yes)
    if (current hour >= 18) then (yes)
        :retun True;
        stop
    else (no)
    endif
else (no)
endif

if (May, Jun; Jul, Sep) then (yes)
    if (current hour >= 19) then (yes)
        :return True;
        stop
    else (no)
    endif
else (no)
endif

:return False;

end


:evaluate_data_from_telegram(self);
:t_msg = telegram.read_once();

if (t_msg not None) then (yes)
    if (t_msg == "/system_stop") then (yes)
        :return ForcedExit;
        stop
    else (no)
    endif

    if (t_msg == "<general message>") then (yes)
        :<general implementation>;
        note
        The implementation depends on
        the message selected
    end note
        stop
    else (no)
    endif

else (no)
    :log no new messages;
endif

end


:pump_cycle();

repeat :for iteration in watering_iterations;
    repeat :for pump in pumps;
        if (pump get_active_status()) then (yes)
            :pump watering();
        else (no)
            :log inactive pump;
            note right
                This pump will be skipped
            end note
        endif
    repeat while (more pump?) is (yes)

repeat while (more iteration? ) is (yes)

end

@enduml