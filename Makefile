
run-grobid-stamp:
	docker run -d --rm --name grobid-run-1 -p 5000:8070 lfoppiano/grobid:0.5.4
	until curl -s http://localhost:5000/api/isalive | grep -x true; \
		do echo -n .; sleep 1; done
	touch $@

.PHONY: stop
stop:
	docker rm -f grobid-run-1
	rm run-grobid-stamp

sarjat2019/fetch-stamp: sarjat2019/sarjat2019.seq
	./fetch.py $< sarjat2019/pdf/
	touch $@

