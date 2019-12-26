report.pdf: report.md my_highlight.theme
	pandoc -s --highlight-style my_highlight.theme $< -o $@

docker_run:
	docker run -it --rm -v "$$PWD":/docs --user $$(id -u):$$(id -g) thxbb12/pandoc:2.6 bash