#!/usr/bin/env bash
java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 1 leki_2017_a.pdf -o leki-a.csv -r -a 165,0,1000,1000
java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 2-1746 leki_2017_a.pdf -o leki-a-1.csv -r -a 95,0,1000,1000
cat leki-a-1.csv >> leki-a.csv

java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 1 leki_2017_b.pdf -o leki-b.csv -r -a 155,0,1000,1000
java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 2-359 leki_2017_b.pdf -o leki-b-1.csv -r -a 115,0,1000,1000
cat leki-b-1.csv >> leki-b.csv

java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 1 leki_2017_c.pdf -o leki-c.csv -r -a 140,0,1000,1000
java -jar tabula-0.9.2-jar-with-dependencies.jar --pages 2-248 leki_2017_c.pdf -o leki-c-1.csv -r -a 105,0,1000,1000
cat leki-c-1.csv >> leki-c.csv
