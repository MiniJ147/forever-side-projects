/*
Experiment ideas:
1) run for a specific number of seconds. Does theortical ticks equal the true ticks. If not why not?
2) do you get more performance from sleeping inbetween dt calls and if so at what differintal? Does accuracy change (experiment 1)?
*/
#include <_time.h>
#include <math.h>
#include <stdio.h>
#include <time.h>

static inline double calculate_dt(double ticks_per_second)
{
    return (1000.0 / ticks_per_second); // ticks per ms
} 
static inline double time_to_ms(struct timespec time)
{
    return (double)time.tv_sec * 1000.0 + (double)time.tv_nsec / 1000000.0;
}

int should_update(struct timespec* time_past, double dt)
{
    struct timespec now;
    clock_gettime(CLOCK_REALTIME, &now);
    double time_now_ms = time_to_ms(now);

    double time_past_ms = time_to_ms(*time_past);

    if(time_now_ms - time_past_ms >= dt){
        *time_past = now;
        return 1;
    }

    return 0;
}
 
int main(){
    struct timespec time_past, simulation_start, simulation_end;
    clock_gettime(CLOCK_REALTIME, &time_past);


    unsigned int tick_total = 0;
    double tick_rate = 0;

    int simulation_req_time_sec = 0; // requested time
    double simulation_time_sec = 0; // actual time (round up)
    unsigned int simulation_time_tick = 0;
    
    // gather input
    printf("How many ticks per second?\n>>> ");
    scanf("%lf", &tick_rate);

    printf("Enter Simulation Time (Seconds):\n>>> ");
    scanf("%d", &simulation_req_time_sec);

    // calculations
    double tick_dt = calculate_dt(tick_rate);
    simulation_time_tick = (int)ceil(tick_rate * simulation_req_time_sec); // round up
    simulation_time_sec =  (double)simulation_time_tick / tick_rate;

    printf("\nChosen tick rate %lf per second\n", tick_rate);
    printf("(Rounded Up) Running for %.4f seconds (or) for %u ticks.\n", simulation_time_sec, simulation_time_tick);
    printf("Will Update every %.4f(ms)\n\n",tick_dt);
   

    clock_gettime(CLOCK_REALTIME, &simulation_start);
    while(tick_total <= simulation_time_tick){
        if(!should_update(&time_past, tick_dt)){
            continue;
        }

        // printf("tick: %u\n", ++tick_total);
        tick_total++;
    }
    clock_gettime(CLOCK_REALTIME, &simulation_end);
    double elasped_time_sec = (time_to_ms(simulation_end) - time_to_ms(simulation_start)) / 1000.0;

    printf("Expected Time: %lf | Got: %lf | %1f%% of Error\n", 
           simulation_time_sec, elasped_time_sec,((elasped_time_sec / simulation_time_sec) - 1.0) * 100);

    return 0;
}
