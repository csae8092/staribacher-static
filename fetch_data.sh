# bin/bash

rm -rf data
wget https://github.com/csae8092/staribacher-data/archive/refs/heads/main.zip
unzip main

mv ./staribacher-data-main/data .
rm main.zip
rm -rf ./staribacher-data-main
./dl_imprint.sh

echo "some preprocessing"

find ./data/editions/ -type f -name "*.xml"  -print0 | xargs -0 sed -i -e 's@ref="per:@ref="#per__@g'

add-attributes -g "./data/editions/*.xml" -b "https://id.acdh.oeaw.ac.at/staribacher"
add-attributes -g "./data/indices/*.xml" -b "https://id.acdh.oeaw.ac.at/staribacher"

echo "write back-elements"
python add_back_elements.py