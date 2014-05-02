# 设置你要生成的dex的文件名, 必须是.dex .jar .zip .apk结尾或者是一个目录
# Set the file name of your dex package, it must end with one of: .dex .jar .zip .apk or be a directory:
DX_PKG = test.dex

# 设置你的java编译器
# Set your java compiler here:
JAVAC = javac

# 设置你的dx编译器
# Set your dx compiler here:
DXC = tool/dx

# 设置你的编译选项
JFLAGS = -Djava.ext.dirs=lib -sourcepath src -encoding UTF-8 
DFLAGS = --dex --verbose --no-strict --output=$(DX_PKG)


# 用法：
# make new: 在你的工程目录下生成src, bin子目录。
# 如果你定义的类包含在某个包里：请自己在src下建立相应的目录层次。
# 最终的目录结构如下：
# ├── test.jar
# ├── bin
# │     └── com
# │           └── bugless
# │                 └── Entry.class
# ├── makefile
# └── src
#        └── com
#             └── bugless
#                   └── Entry.java

# make build: 编译，在bin目录下生成 java classes。
# make clean: 清理编译结果，以便重新编译
# make rebuild: 清理编译结果，重新编译。
# make dex: 生成可执行的dex。

# show help message by default
Default:
	@echo "make build: build project."
	@echo "make clean: clear classes generated."
	@echo "make rebuild: rebuild project."
	@echo "make dex: package your project into a executable dex."

build:
	@mkdir -pv src bin
	$(JAVAC) -cp bin -d bin $(JFLAGS) src/com/bugless/Entry.java

rebuild: clean build

.PHONY: clean jar

clean:
	rm -frv bin/*
	rm -rf $(DX_PKG)

dex: build
	$(DXC) $(DFLAGS) bin