# Cinematch Backend

### Backend Service for the Cinematch mobile app.

## Installation

- Clone this repository (with HTTPS preferred)
  ```bash
  $ git clone https://gitlab.com/tsanny/cinematch-backend
  ```
- Activate virtualenv, or create one if none has been created
  ```bash
  $ virtualenv env
  ```
- Install required packages
  ```bash
  $ pip install -r requirements.txt
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


# API Documentation

## Acknowledgements

- **Developer** :
- **Product Owner** :

