package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

const routeFile = "routes.json"

type Router struct {
	routes map[string]string
}

// Route go link
func (r *Router) route(w http.ResponseWriter, req *http.Request) {
	target := req.URL.Path
	if len(target) <= 1 {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	target = target[1:] // trim extra /

	targetURL, ok := r.routes[target]
	if !ok {
		fmt.Println("could not find")
		w.WriteHeader(http.StatusNotFound)
		return
	}

	http.Redirect(w, req, targetURL, http.StatusFound)
}

func initRoutes() *Router {
	router := Router{}
	router.routes = make(map[string]string)

	content, err := os.ReadFile(routeFile)
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	type Entry struct {
		GoLink     string `json:"go-link"`
		TargetLink string `json:"target-link"`
	}

	type RouteFile struct {
		Entries []Entry `json:"entries"`
	}

	var routeData RouteFile
	err = json.Unmarshal(content, &routeData)
	if err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	fmt.Println("Building Routes...")
	for _, e := range routeData.Entries {
		if v, ok := router.routes[e.GoLink]; ok {
			log.Fatalf("duplicated go links: %s currently targets %s\n", e.GoLink, v)
		}

		fmt.Printf("%s --> %s\n", e.GoLink, e.TargetLink)
		router.routes[e.GoLink] = e.TargetLink
	}
	fmt.Println("Finished Building Routes")
	return &router
}

func main() {
	router := initRoutes()
	mux := http.NewServeMux()

	mux.HandleFunc("GET /{id}", router.route)
	http.ListenAndServe(":80", mux)
}
