package main

import (
	"io/ioutil"
	"log"
	"os"

	"github.com/davecgh/go-spew/spew"
	"gopkg.in/yaml.v2"
)

type LoadCity struct {
	Name    string   `yaml:"name"`
	Disease string   `yaml:"disease"`
	Edges   []string `yaml:"edges"`
}

type LoadedYaml struct {
	Cities []LoadCity `yaml:"cities"`
}

func load_yaml() LoadedYaml {
	file, err := os.Open("./board.yml")
	if err != nil {
		log.Fatalf("File load error: %v", err)
	}
	defer file.Close()

	b, err := ioutil.ReadAll(file)
	if err != nil {
		log.Fatalf("File read error: %v", err)
	}

	loadedYaml := LoadedYaml{}
	err = yaml.Unmarshal(b, &loadedYaml)

	if err != nil {
		log.Fatalf("YAML parse error: %v", err)
	}

	yamlToBoard(loadedYaml)
	return loadedYaml
}

func make_sib(c1 City, c2 City) (City, City) {
	c1.edges = append(c1.edges, &c2)
	c2.edges = append(c2.edges, &c1)
	return c1, c2
}

func yamlToBoard(y LoadedYaml) []City {
	var board []City
	var board_map = make(map[string]City)
	diseases := map[string]Disease{
		"Blue":   Blue,
		"Black":  Black,
		"Yellow": Yellow,
		"Red":    Red,
	}

	for _, loadCity := range y.Cities {
		gameCity := City{
			name:   loadCity.Name,
			d_type: diseases[loadCity.Disease],
		}

		board_map[loadCity.Name] = gameCity
	}

	for _, loadCity := range y.Cities {
		gameCity := board_map[loadCity.Name]

		for _, siblingCity := range gameCity.edges {
			gameCity, _ = make_sib(gameCity, *siblingCity)
		}

		board_map[loadCity.Name] = gameCity
	}

	spew.Dump(board_map)
	return board
}
