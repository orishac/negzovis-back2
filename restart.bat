cd %1
git pull
cd %2
git pull
call npm install
call npm run build
ECHO y | rmdir /s %3
move %2/build %3
httpd -k restart