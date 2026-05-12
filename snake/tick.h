#pragma once
#include <time.h>

static inline double tick_calculate_dt(double ticks_per_second)
{
    return (1000.0 / ticks_per_second); // ticks per ms
} 
static inline double tick_time_to_ms(struct timespec time)
{
    return (double)time.tv_sec * 1000.0 + (double)time.tv_nsec / 1000000.0;
}

int tick_should_update(struct timespec* time_past, double dt)
{
    struct timespec now;
    clock_gettime(CLOCK_REALTIME, &now);
    double time_now_ms = tick_time_to_ms(now);

    double time_past_ms = tick_time_to_ms(*time_past);

    if(time_now_ms - time_past_ms >= dt){
        *time_past = now;
        return 1;
    }

    return 0;
}