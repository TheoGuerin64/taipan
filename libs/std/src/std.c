#include <stdio.h>

#include "../include/std.h"

inline void print_number(double number) {
    printf("%lf\n", number);
}

inline void print_string(const char *string) {
    printf("%s\n", string);
}

inline void input_number(double *number) {
    if (!scanf("%lf", number))
        *number = 0;
}
