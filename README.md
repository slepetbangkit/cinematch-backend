# Cinematch Backend 🍿

### Backend Service for the Cinematch mobile app.

Cinematch is a social media application designed for movie lovers. It allows users to share their thoughts about movies, create personalized movie lists, receive movie recommendations, and connect with others. Cinematch also features an AI-powered recommendation engine that provides users with curated movie lists based on their tastes.

## Features
- **Movie Search**: Find and see movie details easily using the search functionality.
- **Personalized Recommendations**: Get movie suggestions tailored to your preferences.
- **Movie Lists**: Create and manage your own movie lists.
- **Social Sharing**: Share your movie thoughts and reviews with friends.
- **AI-Generated Playlists**: Enjoy blend playlists with other users generated by our AI based on your movie tastes combined.
- **User Profiles**: Customize your profile and connect with other movie enthusiasts.

## Installation

- Clone this repository (with HTTPS preferred)
  ```bash
  $ git clone https://gitlab.com/slepetbangkit/cinematch-backend
  ```
- Activate virtualenv, or create one if none has been created
  ```bash
  $ virtualenv env
  ```
- Install required packages
  ```bash
  $ pip install -r requirements.txt
  ```
- Create a .env file
- ```
  # For production purposes. The API uses an SQLite locally
  PGDATABASE=
  PGHOST=
  PGPASSWORD=
  PGPORT=
  PGUSER=
  
  PRODUCTION=
  DEBUG=
  SECRET_KEY=
  APP_URL=
  GS_PROJECT_ID=
  GS_SERVICE_ACCOUNT_KEY=
  GS_BUCKET_NAME=
  TMDB_API_KEY=
  ```
- Migrate if needed
  ```bash
  $ python manage.py migrate
  ```
- Run the server in your local (`localhost:8000`)
  ```bash
  $ python manage.py runserver
  ```

## Development

- Create a new branch from `master` with:

  ```bash
  $ git checkout -b <your_name/scope>
  ```

  - example:
    - `bambang/admin`

- Do your changes, then push to remote repository to be merged

  ```bash
  $ git add .
  $ git commit -m "<tag>(<scope>): <description>"
  $ git push origin <your branch>
  ```

  - examples of a _good_ commit message:
    - `feature(admin): Implemented admin model`
    - `fix(auth): Fix logging in not returning token`
    - `refactor(vote): Optimize searching`

- Submit merge request on the remote repository, wait for approvals, then merge if approved. You don't have to squash/delete the source branch after merge.
- After merge:
  ```bash
  $ git checkout master (or the target branch on the merge request)
  $ git pull origin master
  ```
- **Repeat**


## Deployment to GCR
- Build the image
  ```bash
  $ docker build -t <image_name>
  $ docker tag <image_name> asia-southeast2-docker.pkg.dev/cinematch-c241-ps352/cinematch-c241-ps352/<image-name-to-be>
  $ docker push asia-southeast2-docker.pkg.dev/cinematch-c241-ps352/cinematch-c241-ps352/<image-name-to-be>
  ```

