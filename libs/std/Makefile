OUTPUT = ../../taipan/libs/std
NAME = $(OUTPUT)/libstd.a

SRCS = std.c
ICDS = include/std.h
OBJS = $(addprefix bin/, $(SRCS:.c=.o))

CC = clang
CFLAGS = -Wall -Wextra -Werror -pedantic -Ofast

all: copy-include $(NAME)

bin/%.o: src/%.c
	mkdir -p $(@D)
	$(CC) $(CFLAGS) -c $< -o $@ -I include

$(NAME): $(OBJS)
	ar rc $(NAME) $(OBJS)

copy-include:
	@cp -r include $(OUTPUT)

clean:
	$(RM) -r bin

fclean: clean
	$(RM) $(NAME)

re: fclean $(NAME)

.PHONY: all clean fclean re copy-include
