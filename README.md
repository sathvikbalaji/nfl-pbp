# nfl-pbp

## Models

The models (located in `/src/`) were created using a Multinomial Linear Regression model from `scikit-learn`. Each play, series, drive and game model was trained using play-by-play information from the 2020-2021 NFL Season.

## API

Games are simulated in a worker process using `rq`, and simulation results are stored in Postgres. Game results are returned and rendered using Flask. The application is deployed to Heroku at [https://dry-thicket-88951.herokuapp.com](https://dry-thicket-88951.herokuapp.com/). 