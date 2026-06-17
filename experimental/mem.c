#include <stdio.h>

unsigned char bytes[1024];
typedef struct {
    int a;
    int b;
    int c;
} Foo;

int main(){
    unsigned char* ptr = bytes;

    // alloc 4 bytes for int
    int* a = (int*)ptr; ptr += 4;
    *a = 4;
    int* b = (int*)ptr; ptr += 4;
    *b = 5;
    int* c = (int*)ptr; ptr += 4;
    *c = 6;

    Foo v = *(Foo*)a;
    printf("%d %d %d\n", v.a, v.b, v.c);

    return 0;
}