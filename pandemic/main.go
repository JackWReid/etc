package main

type Disease int

const (
	Blue Disease = 1 + iota
	Black
	Yellow
	Red
)

type PlayerCardDeck []*City
type InfectionCardDeck []*City
type PlayerDiscardPile []*City
type InfectionDiscardPile []*City

type City struct {
	name     string
	d_type   Disease
	inf_lvl  int
	edges    []*City
	res_cntr bool
}

type Player struct {
	loc   *City
	moves int
}

func infect(c City) City {
	if c.inf_lvl < 3 {
		c.inf_lvl = c.inf_lvl + 1
	}
	return c
}

func create_map() []City {
	var game_map []City

	kh := City{
		name:   "Khartoum",
		d_type: Yellow,
	}

	ks := City{
		name:   "Kinshasa",
		d_type: Yellow,
	}

	lg := City{
		name:   "Lagos",
		d_type: Yellow,
	}

	ks, kh = make_sib(ks, kh)
	lg, kh = make_sib(lg, kh)
	lg, ks = make_sib(lg, ks)
	game_map = append(game_map, ks)
	game_map = append(game_map, kh)
	game_map = append(game_map, lg)
	return game_map
}

func main() {
	// game_map := create_map()
	// ganners := Player{
	// 	loc: &game_map[0],
	// }
	load_yaml()
}
