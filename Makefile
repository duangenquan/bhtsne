CC = gcc
CPP = g++
PYTHON_VERSION = 2.7
PYTHON_INCLUDE = `python -c "import distutils.sysconfig as c; print(c.PREFIX)"`/include/python$(PYTHON_VERSION)/ /usr/local/Cellar/boost/1.66.0/include

IDIRS = -I$(PYTHON_INCLUDE) -I.
DEFINES = -D_ISOC99_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_POSIX_C_SOURCE=200112 -D_XOPEN_SOURCE=600 -DPIC -DZLIB_CONST -D_GNU_SOURCE=1 -D_REENTRANT -D__STDC_CONSTANT_MACROS
CFLAGS = -fomit-frame-pointer -fPIC -pthread -Wall -Wextra -DNDEBUG -O3 -g -rdynamic $(IDIRS) $(DEFINES)

LIBRARIES = -L`python -c "import distutils.sysconfig as c; print(c.PREFIX)"`/lib -L/usr/local/Cellar/boost-python/1.66.0_1/lib/ -lboost_python -lpython$(PYTHON_VERSION)

CPPFLAGS = -std=c++11 $(CFLAGS)

LFLAGS = -lm -lstdc++ -llzma -lz -ldl -lpthread
LDFLAGS = $(LIBRARIES) $(LFLAGS)


core = ./src/core
wrapper = ./src/wrapper

SOURCES = $(wildcard $(core)/*.cpp) $(wildcard $(wrapper)/*.cpp) 

EXECUTABLE = ./libpytsne.so

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
	@$(CPP) -shared -Wl $(OBJECTS) $(LDFLAGS) -o $@

