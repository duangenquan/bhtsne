CC = gcc
CPP = g++

IDIRS = -I.
DEFINES = -D_ISOC99_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_POSIX_C_SOURCE=200112 -D_XOPEN_SOURCE=600 -DPIC -DZLIB_CONST -D_GNU_SOURCE=1 -D_REENTRANT -D__STDC_CONSTANT_MACROS
CFLAGS = -fomit-frame-pointer -fPIC -pthread -Wall -Wextra -DNDEBUG -O2 -g -rdynamic -fopenmp $(IDIRS) $(DEFINES)

LIBRARIES = -L/usr/lib

CPPFLAGS = -std=c++11 $(CFLAGS)

LFLAGS = -lm -lstdc++ -llzma -lz -ldl -lpthread -lgomp

LDFLAGS = $(LIBRARIES) $(LFLAGS)

core = ./src/core
main = ./src/main

SOURCES = $(wildcard $(core)/*.cpp) $(wildcard $(main)/*.cpp)

EXECUTABLE = ./bh_tsne

OBJECTS = $(patsubst %.cpp,%.o,$(SOURCES))

all: $(SOURCES) $(EXECUTABLE)

%.o : %.c
	@echo Compiling: $< 
	@$(CC) $(CFLAGS) -c $< -o $@

%.o : %.cpp
	@echo Compiling: $< 
	@$(CPP) $(CPPFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS)
	rm -f $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	@echo Linking: $@
	@$(CPP) $(OBJECTS) $(LDFLAGS) -o $@

