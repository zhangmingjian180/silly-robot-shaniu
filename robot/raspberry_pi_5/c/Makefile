default: main.o opration.o 
	gcc -static -o a.out opration.o main.o

main.o:
	gcc -c main.c -o main.o

opration.o:
	gcc -c opration.c -o opration.o

clean:
	rm opration.o
	rm main.o
	rm a.out
