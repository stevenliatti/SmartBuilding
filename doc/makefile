CC=xelatex -shell-escape
REPORT=report

$(REPORT).pdf: $(REPORT).tex report/*.tex bib.bib img/*
	$(CC) $(REPORT).tex
	makeglossaries $(REPORT)
	bibtex $(REPORT)
	$(CC) $(REPORT).tex
	$(CC) $(REPORT).tex
	make mostlyclean

docker_run:
	docker run -it --rm -v "$$PWD":/docs -w /docs aergus/latex bash

mostlyclean:
	rm -rf _minted-* *.log *.aux *.out *.lof *.lol *.toc *.bbl *.blg
	rm -rf *.nav *.snm *.glg *.glo *.gls *.glsdefs *.ist *.lot *.vrb *.pyg

clean:
	rm -f *.pdf
	rm -rf _minted-* *.log *.aux *.out *.lof *.lol *.toc *.bbl *.blg
	rm -rf *.nav *.snm *.glg *.glo *.gls *.glsdefs *.ist *.lot *.vrb *.pyg
