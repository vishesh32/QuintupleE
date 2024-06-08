wait=60

cd Software/server
# rm -rf exact.csv polling.csv
# touch exact.csv polling.csv
# timeout $wait python3 test_sync.py & timeout $wait python3 external_sync.py
# python3 avg_sync.py
# python3 external_sync.py
python3 main.py