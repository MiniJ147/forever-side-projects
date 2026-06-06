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
    "\e[44m" // water 
};

const char* CLEAR_BACKGROUND = "\e[00m";

const uint8_t AIR_ID = 0;
const uint8_t SAND_ID = 1;
const uint8_t WATER_LEFT_ID = 2;
const uint8_t WATER_RIGHT_ID = 3;

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
            tile_curr = tile_curr == WATER_RIGHT_ID ? WATER_LEFT_ID : tile_curr;
            
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

static inline void tick(int x, int y)
{
    int from = map_index(x,y);
    int id = map_data[from];
    switch(id){
        case SAND_ID: {
            if(y+1 >= MAP_HEIGHT){
                break;
            }
            
            if(map_data[map_index(x,y+1)] != SAND_ID){
                map_data[(map_index(x,y))] = map_data[(map_index(x,y+1))];
                map_data[(map_index(x,y+1))] = id;
                break;
            }
            else if(x+1 < MAP_WIDTH && map_data[map_index(x+1,y+1)] != SAND_ID){
                map_data[(map_index(x,y))] = map_data[(map_index(x+1,y+1))];
                map_data[(map_index(x+1,y+1))] = id;
            }
            else if(x-1 >= 0 && map_data[map_index(x-1,y+1)] != SAND_ID){
                map_data[(map_index(x,y))] = map_data[(map_index(x-1,y+1))];
                map_data[(map_index(x-1,y+1))] = id;
            }
            break;
        }
        case WATER_LEFT_ID: {
            int to = map_index(x,y+1);
            if(y+1 < MAP_HEIGHT && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = id;
                break;
            }

            to = map_index(x-1, y);
            if(x-1 >= 0 && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = id;
                break;
            }

            to = map_index(x+1, y);
            if(x+1 < MAP_WIDTH && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = WATER_RIGHT_ID;
                break;
            } 
            break;
        }
        case WATER_RIGHT_ID: {
            int to = map_index(x,y+1);
            if(y+1 < MAP_HEIGHT && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = id;
                break;
            }

            to = map_index(x+1, y);
            if(x+1 < MAP_WIDTH && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = id;
                break;
            }

            to = map_index(x-1, y);
            if(x-1 >= 0 && map_data[to] == AIR_ID){
                map_data[from] = map_data[to];
                map_data[to] = WATER_LEFT_ID;
                break;
            }
            break;
        }
    }
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

    const int TICKS_PER_SECOND = 20;
    const double tick_dt = tick_calculate_dt(TICKS_PER_SECOND);

    struct timespec tick_timer;
    clock_gettime(CLOCK_REALTIME, &tick_timer);

    int iter = 0;
    for(;;){
        if(!tick_should_update(&tick_timer, tick_dt)){
            continue;
        }
        if(iter > 0)
            map_data[map_index(8,10)] = WATER_LEFT_ID;
        map_data[map_index(0,10)] = SAND_ID;
        map_data[map_index(15,10)] = SAND_ID;
        // map_data[MAP_WIDTH-1] = iter++ & 1 ? WATER_ID : map_data[MAP_WIDTH-1];
        // map_data[5] = iter++ & 1 ? SAND_ID : map_data[1];


        for(int y=MAP_HEIGHT-1; y>=0; y--)
        {
            for(int x=MAP_WIDTH-1; x>=0; x--)
            {
                tick(x,y);
            }
        }

        if(map_data[map_index(0,10)] == SAND_ID)
            iter++;

        update_render();
        printf("\033[0;0H%s",map_render);
    }

    return 0;
}
