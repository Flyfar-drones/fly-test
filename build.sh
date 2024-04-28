#/bin/sh

rm -rf ./package
mkdir ./package
sleep 2

pyinstaller --onefile --windowed --name=flytest --specpath ./package/spec --distpath ./package/dist --workpath ./package/build ./src/main.py