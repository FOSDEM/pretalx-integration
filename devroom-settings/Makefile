all: localecompile
LNGS:=`find devroom_settings/locale/ -mindepth 1 -maxdepth 1 -type d -printf "-l %f "`

localecompile:
	django-admin compilemessages

localegen:
	django-admin makemessages -l de_DE -i build -i dist -i "*egg*" $(LNGS)

.PHONY: all localecompile localegen
