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

// Node for body control (linked-list queue)
typedef struct Node Node;
struct Node
{
    UVec2 pos;
    Node* next;
};

Node* node_create(UVec2 pos, Node* next)
{
    Node* c = (Node*)malloc(sizeof(Node));
    c->pos = pos;
    c->next = next;
    return c;
}

void node_free(Node* node)
{
    free(node);
}

typedef struct Snake Snake;
struct Snake
{
    UVec2* body;
    u32 body_size_max;

    // queue for body
    Node* q_head;
    Node* q_tail;
    u32 queue_size;

    char dir;
};


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
    snake.queue_size = 2;
    Node* snake_head = node_create((UVec2){2,2}, NULL);
    Node* snake_tail = node_create((UVec2){1,2}, snake_head);

    snake.q_head = snake_tail;
    snake.q_tail = snake_head;

    // set inti direction
    snake.dir = SNAKE_DIR_RIGHT;

    return snake;
}

void snake_destroy(Snake* snake)
{
    free(snake->body);

    Node* curr = snake->q_head;
    while(curr != NULL)
    {
        Node* old = curr;
        curr = curr->next;
        free(old);
    }
}

// the queue tail is the head of the snake
UVec2 snake_get_head(Snake* snake)
{
    return snake->q_tail->pos;
}

// We grab the tail (q_head) of the snake and put it in the front (q_tail)
// while advancing the queue 
// Does not validate move, but just performs it
void snake_move_body(Snake* snake, Map* map, UVec2 new_pos)
{
    Node* s_tail = snake->q_head; 
    map_set_tile(map, s_tail->pos, MAP_TILE_EMPTY); // clear old tail
    map_set_tile(map, new_pos, MAP_TILE_SNAKE_BODY); // put new pos

    // move head forward
    snake->q_head = s_tail->next;

    // update s_tail
    s_tail->pos = new_pos;
    s_tail->next = NULL;

    // update stored q_tail
    snake->q_tail->next = s_tail;
    snake->q_tail = s_tail;
}

void snake_eat_apple(Snake* snake, Map* map, UVec2 apple_pos)
{
    Node* new_body = node_create(apple_pos, NULL);
    map_set_tile(map, apple_pos, MAP_TILE_SNAKE_BODY);
    snake->queue_size++;

    // update snake head
    snake->q_tail->next = new_body;
    snake->q_tail = new_body;

    map_spawn_apple(map);
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
            snake_eat_apple(snake, map, new_head);
            break;
        case MAP_TILE_EMPTY: {
            snake_move_body(snake, map, new_head);
            break;
        }
        default: 
            printf("ERROR INVALID MAP TILE\n");
            exit(EXIT_FAILURE);
            return SNAKE_DEAD;
    }

    return SNAKE_ALIVE;
}