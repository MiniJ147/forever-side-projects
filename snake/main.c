#include <stdio.h>
#include "map.h"
#include "snake.h"
#include "tick.h"
#include <unistd.h>
#include <termios.h>
#include <sys/select.h>

static struct termios oldt;

void enable_raw_mode()
{
    struct termios newt;

    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;

    newt.c_lflag &= ~(ICANON | ECHO);

    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
}

void disable_raw_mode()
{
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
}

int read_input_timeout(int timeout_ms)
{
    fd_set set;
    struct timeval timeout;

    FD_ZERO(&set);
    FD_SET(STDIN_FILENO, &set);

    timeout.tv_sec = timeout_ms / 1000;
    timeout.tv_usec = (timeout_ms % 1000) * 1000;

    int rv = select(STDIN_FILENO + 1, &set, NULL, NULL, &timeout);

    if(rv > 0)
    {
        return getchar();
    }

    return -1;
}

int main(){
    enable_raw_mode();

    // clear screen first thing
    printf("\033[2J"); 

    // init tick
    const int TICKS_PER_SECOND = 5;
    const double tick_dt = tick_calculate_dt(TICKS_PER_SECOND);

    struct timespec tick_timer;
    clock_gettime(CLOCK_REALTIME, &tick_timer);

    const int NUM_APPLES = 2;
    Map map = map_create(10,10);
    for(int i=0; i<NUM_APPLES; i++)
    {
        map_spawn_apple(&map);
    }
    Snake snake = snake_create(map.width * map.height);

    // gameplay loop
    for(;;){
        if(!tick_should_update(&tick_timer, tick_dt)){
            continue;
        }
        
        if(!snake_tick(&snake, &map))
            break;

        map_render(map);

        // TODO: change input logic out for a clean function
        char new_dir = read_input_timeout(100);

        switch(new_dir)
        {
            case SNAKE_DIR_UP:
                if(snake.dir == SNAKE_DIR_DOWN)
                    continue;
            break;
            case SNAKE_DIR_DOWN:
                if(snake.dir == SNAKE_DIR_UP)
                    continue;
            break;
            case SNAKE_DIR_LEFT:
                if(snake.dir == SNAKE_DIR_RIGHT)
                    continue;
            break;
            case SNAKE_DIR_RIGHT:
                if(snake.dir == SNAKE_DIR_LEFT)
                    continue;
            break;
            default:
                continue;
        }

        snake.dir = new_dir;
    }

    printf("GAME OVER! MAX SIZE: %u\n", snake.queue_size);

    return 0;
}