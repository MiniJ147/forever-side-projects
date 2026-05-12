#pragma once
#include "types.h"
#include "map.h"
#include <stdlib.h>

const char SNAKE_DIR_UP = 'w';
const char SNAKE_DIR_DOWN = 's';
const char SNAKE_DIR_LEFT = 'a';
const char SNAKE_DIR_RIGHT = 'd';

const int SNAKE_DEAD = 0;
const int SNAKE_ALIVE = 1;

typedef struct 
{
    UVec2* body;
    u32 body_size_max;

    // queue for body
    u32 queue_head;
    u32 queue_tail;
    u32 queue_size;

    char dir;
} Snake;

Snake snake_create(u32 snake_max_size)
{
    // bounds check
    if(snake_max_size <= 1)
    {
        printf("INVALID SIZE\n");
        exit(EXIT_FAILURE);
    }

    Snake snake;

    // declaring body
    snake.body = (UVec2*)malloc(sizeof(UVec2) * snake_max_size);
    snake.body_size_max = snake_max_size;

    // setting body init size
    snake.queue_size = 1;
    snake.body[0] = (UVec2){2,2};

    snake.queue_head = 0;
    snake.queue_tail = 1;

    // set inti direction
    snake.dir = SNAKE_DIR_RIGHT;

    return snake;
}

void snake_destroy(Snake* snake)
{
    free(snake->body);
}

UVec2 snake_get_head(Snake* snake)
{
    return snake->body[(snake->queue_tail - 1) % snake->body_size_max];
}

void snake_add_body(Snake* snake, UVec2 new_loc)
{
    // add to queue
    u32 new_idx = snake->queue_tail;
    snake->body[new_idx] = new_loc;

    snake->queue_size += 1;
    snake->queue_tail = (snake->queue_tail + 1) % snake->body_size_max;
}

UVec2 snake_pop_tail(Snake* snake)
{
    u32 idx = snake->queue_head;
    UVec2 res = snake->body[idx];

    snake->queue_head = (idx + 1) % snake->body_size_max;
    snake->queue_size -= 1;

    return res;
}

/* 
0 snake is dead - 1 snake is alive
assume snake is always alive
Tick Order:
Move - (check valid and add body)
Update Direction Based on Input
*/
int snake_tick(Snake* snake, Map* map)
{
    UVec2 head = snake_get_head(snake); 
    UVec2 new_head;

    switch(snake->dir)
    {
        case SNAKE_DIR_DOWN:
            new_head = uvec_add(head, (UVec2){0,1});
        break;
        case SNAKE_DIR_UP:
            new_head = uvec_add(head, (UVec2){0,-1});
        break;
        case SNAKE_DIR_LEFT:
            new_head = uvec_add(head, (UVec2){-1,0});
        break;
        case SNAKE_DIR_RIGHT:
            new_head = uvec_add(head, (UVec2){1,0});
        break;
        default:
            printf("INVALID DIRECTION SWITCH\n");
            exit(EXIT_FAILURE);
        break;
    }

    // check bounds of new head
    if(new_head.x < 0 || new_head.x >= map->width)
    {
        return SNAKE_DEAD;
    }
    if(new_head.y < 0 || new_head.y >= map->height)
    {
        return SNAKE_DEAD;
    }

    // grab titles and update map
    char next_tile = map_get_tile(map, new_head);
    switch(next_tile)
    {   
        case MAP_TILE_SNAKE_BODY:
            return SNAKE_DEAD;
        case MAP_TILE_APPLE:
            snake_add_body(snake, new_head);
            map_set_tile(map, new_head, MAP_TILE_SNAKE_BODY);
            map_spawn_apple(map);
            break;
        case MAP_TILE_EMPTY: {
            UVec2 tail_pos = snake_pop_tail(snake);
            map_set_tile(map, tail_pos, MAP_TILE_EMPTY);

            snake_add_body(snake, new_head);

            map_set_tile(map, new_head, MAP_TILE_SNAKE_BODY);
            break;
        }
        default: 
            printf("ERROR INVALID MAP TILE\n");
            exit(EXIT_FAILURE);
            return SNAKE_DEAD;
    }

    return SNAKE_ALIVE;
}