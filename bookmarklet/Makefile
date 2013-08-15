SPIDER_TARGET = spider.js
SPIDER_SOURCES = \
	json2.js \
	jquery.js \
	spider.coffee.js \
	utils.coffee.js \
	extractor.coffee.js \
	ui.coffee.js \
	capture.coffee.js \

.PHONY: all
all: $(SPIDER_TARGET)

$(SPIDER_TARGET): $(SPIDER_SOURCES)
	cat $(SPIDER_SOURCES) | closure --warning_level QUIET > $(SPIDER_TARGET)

%.coffee.js: %.coffee
	cat $< | coffee -c -s > $<.js

.PHONY: clean
clean:
	find . -iname \*.coffee.js -exec rm -f {} \;
	rm -f $(SPIDER_TARGET)

