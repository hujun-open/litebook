rd /q /s build
rd /q /s dist
rd /q /s output
python build.py
xcopy /Y /E /I kadp .\dist\kadp
xcopy /Y /E /I jieba .\dist\jieba
copy /Y mainlist.txt .\dist\