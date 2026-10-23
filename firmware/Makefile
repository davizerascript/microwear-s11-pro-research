ROOT := $(abspath ..)
JIELI_TOOLCHAIN ?= $(ROOT)/work/toolchain/jieli-linux-toolchains-20260730.1/pi32v2
CC := $(JIELI_TOOLCHAIN)/bin/clang
OUT_DIR ?= $(ROOT)/work/build-pi32v2
TARGET_FLAGS := -target pi32v2 -mcpu=r3
CFLAGS := -std=c99 -Wall -Wextra -Werror -ffreestanding -fno-builtin -fno-common -O0
CPPFLAGS := -Iinclude

.PHONY: compile-check
compile-check: $(OUT_DIR)/main.o

$(OUT_DIR)/main.o: src/main.c include/board_port.h
	@test -x "$(CC)" || { echo "JieLi clang não encontrado: $(CC)" >&2; exit 2; }
	mkdir -p "$(OUT_DIR)"
	"$(CC)" $(TARGET_FLAGS) $(CPPFLAGS) $(CFLAGS) -c "$<" -o "$@"
	file "$@"
	readelf -h "$@" | grep -E 'Class:|Data:|Type:|Machine:|Flags:'
