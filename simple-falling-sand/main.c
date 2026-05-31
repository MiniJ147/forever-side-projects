#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "types.h"
#include "tick.h"

const int BLOCK_SIZE = 6; 

const char* TILE_STRINGS[] = {
    "\e[40m", // air
    "\e[43m", // sand 
    "\e[44m" // water 
};

const char* CLEAR_BACKGROUND = "\e[00m";

const uint8_t AIR_ID = 0;
const uint8_t SAND_ID = 1;
const uint8_t WATER_ID = 2;

enum {
    MAP_WIDTH = 16,
    MAP_HEIGHT = 16,
    MAP_SIZE = MAP_WIDTH * MAP_HEIGHT,
    MAP_RENDER_SIZE = MAP_SIZE * BLOCK_SIZE + MAP_HEIGHT
};

char map_data[MAP_SIZE] = {0};
char map_render[MAP_RENDER_SIZE+1] = {0};

static inline void clear_screen()
{
    printf("\033[2J");
}

static inline int map_index(int x, int y)
{
    return (y * MAP_WIDTH) + x;
}

void update_render()
{
    int render_curr = -1; // set invalid to prevent fragments
    int render_pos = 0;

    for(int y=0; y<MAP_HEIGHT; y++)
    {
        for(int x=0; x<MAP_WIDTH; x++)
        {
            uint8_t tile_curr = map_data[map_index(x,y)];
            
            // update loop to change background color
            for(int c = 0; c < BLOCK_SIZE-1 && render_curr != tile_curr; c++)
            {
                map_render[render_pos++] = TILE_STRINGS[tile_curr][c];
            }
            render_curr = tile_curr;
            map_render[render_pos++] = ' ';
        }
        map_render[render_pos++] = '\n';
    }

    // kill the string
    map_render[render_pos] = '\0';
}

int main() 
{
    clear_screen();

    // fill with default
    for(int y=0; y<MAP_HEIGHT; y++)
    {
        for(int x=0; x<MAP_WIDTH; x++)
        {
            map_data[map_index(x,y)] = AIR_ID;
        }
    }

    const int TICKS_PER_SECOND = 200;
    const double tick_dt = tick_calculate_dt(TICKS_PER_SECOND);

    struct timespec tick_timer;
    clock_gettime(CLOCK_REALTIME, &tick_timer);

    map_data[2] = SAND_ID;
    map_data[3] = WATER_ID;
    map_data[4] = SAND_ID;
    for(;;){
        if(!tick_should_update(&tick_timer, tick_dt)){
            continue;
        }

        for(int y=MAP_HEIGHT-1; y>=0; y--)
        {
            for(int x=MAP_WIDTH; x>=0; x--)
            {
                int id = map_data[map_index(x,y)];
                switch(id){
                    case SAND_ID:
                        if(y+1 < MAP_HEIGHT && map_data[map_index(x,y+1)] != SAND_ID){
                            int t = map_data[map_index(x,y)];
                            map_data[(map_index(x,y))] = map_data[(map_index(x,y+1))];
                            map_data[(map_index(x,y+1))] = t;
                        }
                    break;
                    case WATER_ID:
                    break;
                }
            }
        }

        update_render();
        printf("\033[0;0H%s",map_render);
    }

    return 0;
}
