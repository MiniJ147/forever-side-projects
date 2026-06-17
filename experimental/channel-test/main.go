package main

import (
	"fmt"
	"log"
	"time"
)

var processTime time.Duration = time.Second
var numWorkers int = 10
var queue chan int = make(chan int)

func enqueue_self(id int) {
	go func(id int) {
		time.Sleep(processTime)
		log.Printf("%d pushed into channel and ready to process\n", id)
		queue <- id
	}(id)
}

func main() {
	fmt.Println("Hello world!")
	for range numWorkers {
		go func() {

		}()
	}

	time.Sleep(time.Hour) // kill after an hour idc
}
