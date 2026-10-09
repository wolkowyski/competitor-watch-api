@echo off
echo ========================================================
echo Initializing Git repository for CompetitorWatch API...
echo ========================================================

git init
git config user.name "Braian Wolkowyski"
git config user.email "braianwolkowyski@gmail.com"

git add .
git commit -m "feat: complete 10x Solution - CompetitorWatch API (FlyRank Capstone)"

echo.
echo ========================================================
echo Git commit created successfully!
echo To push to your GitHub repo, run:
echo.
echo   git remote add origin https://github.com/braianwolkowyski/competitor-watch-api.git
echo   git branch -M main
echo   git push -u origin main
echo ========================================================
pause
