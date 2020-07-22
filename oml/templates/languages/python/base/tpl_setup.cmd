::##### DO NOT EDIT BELOW THIS LINE #####
@echo off
(conda env update -p .oml\env\{{namespace}} -f env-prod.yml --prune
.oml\env\{{namespace}}\python.exe setup.py install --prefix .oml\env\{{namespace}})
::##### DO NOT EDIT ABOVE THIS LINE #####

::##### ADD CUSTOM COMMANDS BELOW #####
