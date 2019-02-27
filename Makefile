
run-grobid-stamp:
	docker run -d --rm --name grobid-run-1 -p 5000:8070 lfoppiano/grobid:0.5.4
	until curl -s http://localhost:5000/api/isalive | grep -x true; \
		do echo -n .; sleep 1; done
	touch $@

.PHONY: stop
stop:
	docker rm -f grobid-run-1
	rm run-grobid-stamp

sarjat2018/fetch-stamp: sarjat2018/sarjat2018.seq
	./fetch.py $< sarjat2018/pdf/
	touch $@

sarjat2018/analyse-stamp: sarjat2018/fetch-stamp run-grobid-stamp
	python3 grobid-client.py --config grobid-client-config.json \
		--input sarjat2018/pdf/ --output sarjat2018/tei/ \
		processHeaderDocument

