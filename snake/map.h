#pragma once
#include <stdlib.h>
#include <stdio.h>
#include "types.h"
#include <time.h>

typedef struct
{
    u32 width;
    u32 height;
    char* render;
} Map;

const char MAP_TILE_EMPTY = '.';
const char MAP_TILE_APPLE = 'A';
const char MAP_TILE_SNAKE_BODY = '#';

Map map_create(u32 width, u32 height);
void map_render(Map m);
void map_destroy(Map* map);

static inline u32 map_index(Map* m, UVec2 pos)
{
    u32 x = pos.x, y = pos.y;
    return (y % m->height) * (m->width + 1) + x;
}

static inline void map_set_tile(Map* m, UVec2 pos, char val)
{
    u32 idx = map_index(m, pos);
    m->render[idx] = val;
}
static inline char map_get_tile(Map* m, UVec2 pos)
{
    u32 idx = map_index(m, pos);
    return m->render[idx];
}
static inline char map_set_and_get_tile(Map* m, UVec2 pos, char val)
{
    char org = map_get_tile(m, pos);
    map_set_tile(m, pos, val);
    return org;
}

void map_destroy(Map* map)
{
    free(map->render);
}

// TODO: this will infinite loop once the spots run out and due to the tick order we don't have a win state
//       this should be fixed and also performance will get worse as spots shrink due to conflicts. 
void map_spawn_apple(Map* map)
{
    srand(time(NULL));
    
    UVec2 pos;
    do
    {
        pos.x = rand() % map->width;
        pos.y = rand() % map->height;
    }while(map_get_tile(map, pos) != MAP_TILE_EMPTY);

    map_set_tile(map, pos, MAP_TILE_APPLE);
}

Map map_create(u32 width, u32 height)
{
    Map m;

    // map dimensions
    m.width = width;
    m.height = height;

    // +1 on width for \n
    u32 size = (width+1) * height;
    m.render = (char*)malloc(sizeof(char) * size);
    for(u32 i=0; i<size; i++)
    {
        m.render[i] = MAP_TILE_EMPTY; // default
    }

    // set new lines
    for(u32 y=0; y<m.height; y++)
    {
        m.render[map_index(&m, (UVec2){m.width, y})] = '\n';
    }

    return m;
}

void map_render(Map map)
{
    printf("\033[0;0H%s",map.render);
}
