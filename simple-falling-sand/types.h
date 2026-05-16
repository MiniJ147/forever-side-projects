#pragma once

typedef unsigned int u32;

typedef struct 
{
    u32 x;
    u32 y;
} UVec2;

UVec2 uvec_add(UVec2 a, UVec2 b)
{
    a.x += b.x;
    a.y += b.y;

    return a;
}
