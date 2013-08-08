rd /q /s build
rd /q /s dist
rd /q /s output
python build.py
xcopy /Y /E /I kadp E:\hujun\litebook\tobuild\svn3\s2\litebook\dist\kadp
xcopy /Y /E /I jieba E:\hujun\litebook\tobuild\svn3\s2\litebook\dist\jieba
copy /Y mainlist.txt E:\hujun\litebook\tobuild\svn3\s2\litebook\dist