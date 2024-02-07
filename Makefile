build:
	docker-compose build

clean:
	rm -rf .ncbi && \
	rm -rf output/* && touch output/.gitkeep && \
	rm -rf plots/* && touch output/.gitkeep && \
	rm run.log && touch run.log