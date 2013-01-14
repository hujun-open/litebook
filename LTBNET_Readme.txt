LTBNET (litebook 3.0 beta1)
(c)2012 Hu Jun	

1.概述
LTBNET是一个点对点的图书共享网络，litebook的用户可以在这个网络中分享和下载图书。这个网络不依赖于中央服务器，所有的资源都还是存在分享者的机器上，下载者直接从分享者的机器上下载。
－ LTBNET支持基于文件名的搜索。
－ LTBNET本身是一个基于UDP的协议，下载采用HTTP协议。
－ LTBNET随litebook一同发行，litebook从3.0 beta1开始支持这一网络



2. 运行
－ LTBNET随着litebook一同启动和关闭
－ LTBNET以独立进程的方式运行
－ LTBNET缺省使用UDP端口50200；内置的WEB服务器缺省使用TCP端口8000。这两个端口都可以在litebook“选项”对话框中修改。
－ litebook会使用UPNP协议自动添加NAT端口转发，用户也可以手工在路由器上添加以上两个端口的转发。注意：如果端口转发没有创建的话，LTBNET无法工作。
－ 图书共享目录目前采用WEB服务器的共享根目录，此目录下的所有后缀名为['txt','html','htm','epub','umd','jar','zip','rar']都会被共享。
－ LTBNET搜索是通过litebook文件菜单中的“搜索LTBNET”进行
－ 搜索到结果之后，可以直接下载，下载进度可以在litebook文件菜单中的“下载管理器”中查看

3. 监控
系统提供一个基于命令行方式的监控界面，可以对查看当前LTBNET进程的运行信息，以及关闭进程。
运行方法：
－ Windows：在litebook安装目录下有一个“kadp”的子目录，其中有一个"kadp.exe"文件，运行“kadp.exe -debug"
－ Linux or MAC OSX：在litebook安装目录下，运行"python KADP.py -debug"
命令：
"d 0":开启LOG
"stop":关闭进程
"end":退出
(以下命令需要先执行d 0)
"pc 0":列出当前所有的contact 
"pr 0":列出当前已知的所有资源
"printme 0":列出当前的端口号和自己的NodeID

4.和作者联系
Email:	litebook.author@gmail.com
WWW:	http://code.google.com/p/litebook-project/