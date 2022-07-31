package main

import (
	"fmt"
	"os"
)


func entries() {

}

func main() {
    db_username := os.Getenv("DB_USERNAME")
    db_password := os.Getenv("DB_PASSWORD")
    db_port := 5432
    db_name := "cmdb"

	fmt.Println("hello world")
}
